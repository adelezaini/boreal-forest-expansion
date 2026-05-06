"""
General postprocessing utilities for selected NorESM/CAM output.

This module is intentionally general. It should not contain CH4-specific
chemistry diagnostics or Ghan-specific radiative decomposition.

Responsibilities:
- open selected concatenated files
- fix CAM/CLM monthly timestamps
- safe variable selection
- weighted annual/climatological means
- general display/derived variables
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping

import numpy as np
import xarray as xr


# -----------------------------------------------------------------------------
# Opening and time handling
# -----------------------------------------------------------------------------

def fix_cam_time(ds: xr.Dataset, timetype: str = "datetime64") -> xr.Dataset:
    """
    Fix monthly CAM/CLM timestamps using time bounds.

    NorESM/CAM monthly history files often store time at the end of the
    averaging interval. This function moves the timestamp to the 15th day
    of the corresponding month, which makes annual/seasonal grouping safer.

    Parameters
    ----------
    ds
        Input dataset with `time_bnds` or `time_bounds`.
    timetype
        "datetime64" or "DatetimeNoLeap".

    Returns
    -------
    xr.Dataset
        Dataset with corrected `time` coordinate. If no time bounds are found,
        the dataset is returned unchanged.
    """
    ds_ = ds.copy(deep=False)

    if "time_bounds" in ds_.data_vars:
        ds_ = ds_.rename_vars({"time_bounds": "time_bnds"})
    if "hist_interval" in ds_.dims:
        ds_ = ds_.rename_dims({"hist_interval": "nbnd"})

    if "time_bnds" not in ds_.variables:
        return ds_

    if timetype == "DatetimeNoLeap":
        from cftime import DatetimeNoLeap

        months = ds_.time_bnds.isel(nbnd=0).dt.month.values
        years = ds_.time_bnds.isel(nbnd=0).dt.year.values
        dates = [DatetimeNoLeap(int(year), int(month), 15) for year, month in zip(years, months)]
    elif timetype == "datetime64":
        dates = list(ds_.time_bnds.isel(nbnd=0).values + np.timedelta64(14, "D"))
    else:
        raise ValueError("timetype must be 'datetime64', 'DatetimeNoLeap', or None")

    return ds_.assign_coords({"time": ("time", dates, ds_.time.attrs)})


def open_selected_dataset(
    path: str | Path,
    fix_timestamp: str | None = "datetime64",
    chunks: Mapping[str, int] | None = None,
) -> xr.Dataset:
    """
    Open one selected/concatenated NetCDF file produced by
    select_concat_cam_raw_output.sh.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Selected output file not found: {path}")

    if chunks is None:
        chunks = {"time": 12}

    ds = xr.open_dataset(path, chunks=chunks)

    if fix_timestamp is not None:
        ds = fix_cam_time(ds, timetype=fix_timestamp)

    return ds


# -----------------------------------------------------------------------------
# Safe selection and averaging
# -----------------------------------------------------------------------------

def present_vars(ds: xr.Dataset, variables: Iterable[str]) -> list[str]:
    """Return variables from `variables` that are present in `ds`."""
    return [var for var in variables if var in ds.data_vars]


def missing_vars(ds: xr.Dataset, variables: Iterable[str]) -> list[str]:
    """Return variables from `variables` that are absent from `ds`."""
    return [var for var in variables if var not in ds.data_vars]


def select_present(ds: xr.Dataset, variables: Iterable[str], warn: bool = True) -> xr.Dataset:
    """Select only variables that exist in a dataset."""
    variables = list(variables)
    present = present_vars(ds, variables)
    missing = missing_vars(ds, variables)

    if warn and missing:
        print(f"Warning: {len(missing)} requested variables missing: {missing}")

    if not present:
        return xr.Dataset(coords={coord: ds[coord] for coord in ds.coords})

    return ds[present]


def month_length_weights(ds: xr.Dataset) -> xr.DataArray:
    """Normalized month-length weights within each year."""
    if "time" not in ds.coords:
        raise ValueError("Dataset has no time coordinate; cannot compute month-length weights.")

    month_length = ds.time.dt.days_in_month
    return month_length.groupby("time.year") / month_length.groupby("time.year").sum()


def annual_mean(ds: xr.Dataset) -> xr.Dataset:
    """
    Month-length weighted annual mean for monthly output.

    Variables without a `time` dimension are preserved unchanged.
    """
    time_vars = [var for var in ds.data_vars if "time" in ds[var].dims]
    static_vars = [var for var in ds.data_vars if "time" not in ds[var].dims]

    pieces = []

    if time_vars:
        weights = month_length_weights(ds)
        annual = (ds[time_vars] * weights).groupby("time.year").sum(dim="time")
        pieces.append(annual)

    if static_vars:
        pieces.append(ds[static_vars])

    if not pieces:
        return xr.Dataset(coords=ds.coords)

    return xr.merge(pieces, compat="override")


def climatology(ds: xr.Dataset, start_year: int | None = None, end_year: int | None = None) -> xr.Dataset:
    """
    Mean over annual diagnostics.

    Variables without a `year` dimension are preserved unchanged.
    """
    ds_ = ds
    if "year" in ds_.coords:
        if start_year is not None or end_year is not None:
            ds_ = ds_.sel(year=slice(start_year, end_year))

    year_vars = [var for var in ds_.data_vars if "year" in ds_[var].dims]
    static_vars = [var for var in ds_.data_vars if "year" not in ds_[var].dims]

    pieces = []
    if year_vars:
        pieces.append(ds_[year_vars].mean("year", keep_attrs=True))
    if static_vars:
        pieces.append(ds_[static_vars])

    if not pieces:
        return xr.Dataset(coords={coord: ds_[coord] for coord in ds_.coords if coord != "year"})

    return xr.merge(pieces, compat="override")


# -----------------------------------------------------------------------------
# General transformations
# -----------------------------------------------------------------------------

def add_display_unit_variables(ds: xr.Dataset) -> xr.Dataset:
    """
    Add display-oriented variables without overwriting native model variables.

    This function is safe for plotting products. Budget diagnostics should use
    native variables unless explicitly documented otherwise.
    """
    ds_ = ds.copy(deep=False)

    # Temperature
    if "T" in ds_:
        ds_["T_C"] = ds_["T"] - 273.15
        ds_["T_C"].attrs["long_name"] = "air temperature"
        ds_["T_C"].attrs["units"] = "degC"

    if "TREFHT" in ds_:
        ds_["TREFHT_C"] = ds_["TREFHT"] - 273.15
        ds_["TREFHT_C"].attrs["long_name"] = "2 m air temperature"
        ds_["TREFHT_C"].attrs["units"] = "degC"

    # Wind speed
    if {"U", "V"}.issubset(ds_.data_vars):
        ds_["WIND_SPEED"] = np.sqrt(ds_["U"] ** 2 + ds_["V"] ** 2)
        ds_["WIND_SPEED"].attrs["long_name"] = "wind speed"
        ds_["WIND_SPEED"].attrs["units"] = ds_["U"].attrs.get("units", "m/s")

    # Cloud fractions to percent, without overwriting original fractions.
    for var in ["CLDTOT", "CLDLOW", "CLDMED", "CLDHGH"]:
        if var in ds_:
            out = f"{var}_pct"
            ds_[out] = ds_[var] * 100.0
            ds_[out].attrs["long_name"] = f"{ds_[var].attrs.get('long_name', var)}"
            ds_[out].attrs["units"] = "%"

    # Liquid water variables for display.
    if "CLDLIQ" in ds_:
        ds_["CLDLIQ_mgkg"] = ds_["CLDLIQ"] * 1.0e6
        ds_["CLDLIQ_mgkg"].attrs["long_name"] = ds_["CLDLIQ"].attrs.get("long_name", "cloud liquid water")
        ds_["CLDLIQ_mgkg"].attrs["units"] = "mg/kg"

    for var in ["TGCLDLWP", "TGCLDIWP", "TGCLDCWP"]:
        if var in ds_:
            out = f"{var}_gm2"
            ds_[out] = ds_[var] * 1.0e3
            ds_[out].attrs["long_name"] = ds_[var].attrs.get("long_name", var)
            ds_[out].attrs["units"] = "g/m2"

    # Aerosol/SOA display variables.
    for var in ["SOA_A1", "SOA_NA"]:
        if var in ds_:
            out = f"{var}_ugkg"
            ds_[out] = ds_[var] * 1.0e9
            ds_[out].attrs["long_name"] = ds_[var].attrs.get("long_name", var)
            ds_[out].attrs["units"] = "ug/kg"

    for var in ["cb_SOA_A1", "cb_SOA_NA", "cb_SOA_A1_OCW", "cb_SOA_NA_OCW"]:
        if var in ds_:
            out = f"{var}_mgm2"
            ds_[out] = ds_[var] * 1.0e6
            ds_[out].attrs["long_name"] = ds_[var].attrs.get("long_name", var)
            ds_[out].attrs["units"] = "mg/m2"

    # CDNC display conversion.
    if "CDNUMC" in ds_:
        ds_["CDNUMC_1e6cm2"] = ds_["CDNUMC"] * 1.0e-10
        ds_["CDNUMC_1e6cm2"].attrs["long_name"] = ds_["CDNUMC"].attrs.get("long_name", "column cloud droplet number")
        ds_["CDNUMC_1e6cm2"].attrs["units"] = "1e6 cm-2"

    return ds_


def add_general_derived_variables(ds: xr.Dataset) -> xr.Dataset:
    """Add general derived variables, conditionally and safely."""
    ds_ = ds.copy(deep=False)

    if {"NO", "NO2"}.issubset(ds_.data_vars):
        ds_["NOx"] = ds_["NO"] + ds_["NO2"]
        ds_["NOx"].attrs["long_name"] = "NO + NO2"
        ds_["NOx"].attrs["units"] = ds_["NO"].attrs.get("units", "")

    if {"cb_SOA_NA", "cb_SOA_A1"}.issubset(ds_.data_vars):
        ds_["cb_SOA_dry"] = ds_["cb_SOA_NA"] + ds_["cb_SOA_A1"]
        ds_["cb_SOA_dry"].attrs["long_name"] = "dry SOA burden column (cb_SOA_NA + cb_SOA_A1)"
        ds_["cb_SOA_dry"].attrs["units"] = ds_["cb_SOA_NA"].attrs.get("units", "")

    if {"AREL", "FREQL"}.issubset(ds_.data_vars):
        ds_["AREL_incld"] = (ds_["AREL"] / ds_["FREQL"]).where(ds_["FREQL"] != 0)
        ds_["AREL_incld"].attrs["long_name"] = "in-cloud liquid effective radius"
        ds_["AREL_incld"].attrs["units"] = ds_["AREL"].attrs.get("units", "")

    if {"AWNC", "FREQL"}.issubset(ds_.data_vars):
        ds_["AWNC_incld"] = (ds_["AWNC"] / ds_["FREQL"] * 1.0e-6).where(ds_["FREQL"] != 0)
        ds_["AWNC_incld"].attrs["long_name"] = "in-cloud cloud water number concentration"
        ds_["AWNC_incld"].attrs["units"] = "#/cm3"

    if {"ACTNL", "FCTL"}.issubset(ds_.data_vars):
        ds_["ACTNL_incld"] = (ds_["ACTNL"] / ds_["FCTL"] * 1.0e-6).where(ds_["FCTL"] != 0)
        ds_["ACTNL_incld"].attrs["long_name"] = "in-cloud activated droplet number concentration"
        ds_["ACTNL_incld"].attrs["units"] = "#/cm3"

    if {"ACTREL", "FCTL"}.issubset(ds_.data_vars):
        ds_["ACTREL_incld"] = (ds_["ACTREL"] / ds_["FCTL"]).where(ds_["FCTL"] != 0)
        ds_["ACTREL_incld"].attrs["long_name"] = "in-cloud activated effective radius"
        ds_["ACTREL_incld"].attrs["units"] = ds_["ACTREL"].attrs.get("units", "")

    # Total SOA column burden
    soa_burden_terms = [var for var in ["cb_SOA_LV", "cb_SOA_NA", "cb_SOA_SV"] if var in ds_]
    if soa_burden_terms:
        ds_["cb_SOA_TOT"] = sum(ds_[var] for var in soa_burden_terms)
        ds_["cb_SOA_TOT"].attrs["long_name"] = "total SOA column burden"
        ds_["cb_SOA_TOT"].attrs["units"] = ds_[soa_burden_terms[0]].attrs.get("units", "kg/m2")

        ds_["cb_SOA_TOT_mgm2"] = ds_["cb_SOA_TOT"] * 1.0e6
        ds_["cb_SOA_TOT_mgm2"].attrs["long_name"] = "total SOA column burden"
        ds_["cb_SOA_TOT_mgm2"].attrs["units"] = "mg/m2"


    # Total aerosol number concentration from modal number concentrations
    nconc_terms = [f"NCONC{i:02d}" for i in range(1, 15) if f"NCONC{i:02d}" in ds_]
    if nconc_terms:
        ds_["N_AER"] = sum(ds_[var] for var in nconc_terms)
        ds_["N_AER"].attrs["long_name"] = "total aerosol number concentration from NCONC01-NCONC14"
        ds_["N_AER"].attrs["units"] = ds_[nconc_terms[0]].attrs.get("units", "")


    # ET from QFLX
    if "QFLX" in ds_:
        # CAM QFLX is usually kg/m2/s, numerically equivalent to mm/s for water.
        ds_["QFLX_mmday"] = ds_["QFLX"] * 86400.0
        ds_["QFLX_mmday"].attrs["long_name"] = "evapotranspiration / surface water flux"
        ds_["QFLX_mmday"].attrs["units"] = "mm/day"

    return ds_


def transform_dataset(ds: xr.Dataset, add_display_units: bool = True) -> xr.Dataset:
    """
    Apply general transformations in a consistent order.

    Native model variables are preserved. New variables are added with explicit
    names and units.
    """
    ds_ = add_general_derived_variables(ds)
    if add_display_units:
        ds_ = add_display_unit_variables(ds_)
    return ds_