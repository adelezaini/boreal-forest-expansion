"""
Chemistry, BVOC, CH4, and ozone diagnostic helpers.

This module assumes native CAM-chem units. Do not run display-unit conversion
before these diagnostics unless you know exactly which fields changed.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
import xarray as xr

from boreal_forest_expansion.postprocess.transform import annual_mean, climatology


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

G = 9.80665
KB = 1.380649e-23
NA = 6.02214076e23
RGAS = 8.314462618
M_AIR = 28.97e-3
M_CH4 = 16.04e-3
M_O3 = 48.00e-3
SEC_PER_YEAR = 365.0 * 86400.0


# -----------------------------------------------------------------------------
# General helpers
# -----------------------------------------------------------------------------

def require_vars(ds: xr.Dataset, variables: Iterable[str]) -> None:
    missing = [var for var in variables if var not in ds.variables]
    if missing:
        raise KeyError(f"Missing required variables: {missing}")


def maybe_hpa_to_pa(da: xr.DataArray) -> xr.DataArray:
    """Convert pressure field to Pa if metadata or magnitude suggests hPa."""
    units = str(da.attrs.get("units", "")).lower()
    if units in {"hpa", "mb", "mbar", "millibar"}:
        out = da * 100.0
        out.attrs.update(da.attrs)
        out.attrs["units"] = "Pa"
        return out

    try:
        maxval = float(da.max().compute())
    except Exception:
        maxval = float(da.max())

    if maxval < 2000.0:
        out = da * 100.0
        out.attrs.update(da.attrs)
        out.attrs["units"] = "Pa"
        return out

    return da


# -----------------------------------------------------------------------------
# Pressure, air mass, and masks
# -----------------------------------------------------------------------------

def add_pressure_diagnostics(ds: xr.Dataset) -> xr.Dataset:
    """
    Add pressure, air-mass, volume, and tropospheric mask diagnostics.

    Adds:
    - PMID [Pa]
    - PINT [Pa]
    - DELP [Pa]
    - AIR_MASS [kg]
    - AIR_VOLUME [m3]
    - TROP_MASK, using TROP_P when available
    """
    require_vars(ds, ["hyam", "hybm", "hyai", "hybi", "P0", "PS", "T", "GRIDAREA"])

    ds_ = ds.copy(deep=False)

    p0 = maybe_hpa_to_pa(ds_["P0"])
    ps = maybe_hpa_to_pa(ds_["PS"])

    pmid = ds_["hyam"] * p0 + ds_["hybm"] * ps
    pint = ds_["hyai"] * p0 + ds_["hybi"] * ps

    delp = abs(pint.diff("ilev"))
    delp = delp.rename({"ilev": "lev"})
    if "lev" in ds_.coords and delp.sizes.get("lev") == ds_.sizes.get("lev"):
        delp = delp.assign_coords(lev=ds_["lev"])

    airmass = delp * ds_["GRIDAREA"] / G
    rho_air = pmid * M_AIR / (RGAS * ds_["T"])
    air_volume = airmass / rho_air

    ds_["PMID"] = pmid.assign_attrs(long_name="midpoint pressure", units="Pa")
    ds_["PINT"] = pint.assign_attrs(long_name="interface pressure", units="Pa")
    ds_["DELP"] = delp.assign_attrs(long_name="pressure thickness", units="Pa")
    ds_["AIR_MASS"] = airmass.assign_attrs(long_name="air mass per grid-cell layer", units="kg")
    ds_["AIR_VOLUME"] = air_volume.assign_attrs(long_name="air volume per grid-cell layer", units="m3")

    if "TROP_P" in ds_:
        trop_p = maybe_hpa_to_pa(ds_["TROP_P"])
        ds_["TROP_MASK"] = (pmid >= trop_p).assign_attrs(
            long_name="tropospheric mask from TROP_P; true where PMID >= TROP_P"
        )
    else:
        ds_["TROP_MASK"] = (pmid >= 20000.0).assign_attrs(
            long_name="fallback tropospheric mask; true where PMID >= 200 hPa"
        )

    return ds_


# -----------------------------------------------------------------------------
# Weighted means and burdens
# -----------------------------------------------------------------------------

def area_weighted_mean_2d(ds: xr.Dataset, var: str) -> xr.DataArray:
    require_vars(ds, [var, "GRIDAREA"])
    out = (ds[var] * ds["GRIDAREA"]).sum(("lat", "lon"), skipna=True) / ds["GRIDAREA"].sum(("lat", "lon"), skipna=True)
    out.name = f"{var}_global_mean"
    out.attrs["long_name"] = f"global area-weighted mean {var}"
    out.attrs["units"] = ds[var].attrs.get("units", "")
    return out


def mass_weighted_trop_mean(ds: xr.Dataset, var: str) -> xr.DataArray:
    require_vars(ds, [var, "AIR_MASS", "TROP_MASK"])
    w = ds["AIR_MASS"].where(ds["TROP_MASK"])
    out = (ds[var].where(ds["TROP_MASK"]) * w).sum(("lev", "lat", "lon"), skipna=True) / w.sum(("lev", "lat", "lon"), skipna=True)
    out.name = f"{var}_trop_massmean"
    out.attrs["long_name"] = f"tropospheric mass-weighted mean {var}"
    out.attrs["units"] = ds[var].attrs.get("units", "")
    return out


def gas_burden_from_vmr(ds: xr.Dataset, var: str, molar_mass: float, tropospheric_only: bool = False) -> xr.DataArray:
    require_vars(ds, [var, "AIR_MASS"])

    if tropospheric_only:
        require_vars(ds, ["TROP_MASK"])
        mask = ds["TROP_MASK"]
    else:
        mask = xr.ones_like(ds[var], dtype=bool)

    burden = (ds[var].where(mask) * ds["AIR_MASS"].where(mask) * molar_mass / M_AIR).sum(("lev", "lat", "lon"), skipna=True)
    burden.name = f"{var}_burden_trop_kg" if tropospheric_only else f"{var}_burden_kg"
    burden.attrs["units"] = f"kg {var}"
    burden.attrs["long_name"] = f"{'tropospheric' if tropospheric_only else 'global atmospheric'} {var} burden"
    return burden


# -----------------------------------------------------------------------------
# CH4 diagnostics
# -----------------------------------------------------------------------------

def ch4_burden(ds: xr.Dataset, tropospheric_only: bool = False) -> xr.DataArray:
    return gas_burden_from_vmr(ds, "CH4", M_CH4, tropospheric_only=tropospheric_only)


def ch4_oh_loss(ds: xr.Dataset) -> xr.DataArray:
    """
    Offline CH4 + OH loss integrated over the troposphere.

    Returns kg CH4 s-1.
    Assumes CH4 and OH are volume mixing ratios.
    """
    require_vars(ds, ["CH4", "OH", "T", "PMID", "AIR_VOLUME", "TROP_MASK"])

    n_air_cm3 = (ds["PMID"] / (KB * ds["T"])) / 1.0e6
    ch4_nd = ds["CH4"] * n_air_cm3
    oh_nd = ds["OH"] * n_air_cm3

    k_ch4_oh = 2.45e-12 * np.exp(-1775.0 / ds["T"])
    loss_molec_cm3_s = k_ch4_oh * ch4_nd * oh_nd
    loss_molec_s = (loss_molec_cm3_s.where(ds["TROP_MASK"]) * ds["AIR_VOLUME"] * 1.0e6).sum(("lev", "lat", "lon"), skipna=True)

    loss = loss_molec_s / NA * M_CH4
    loss.name = "CH4_OH_loss_kg_s"
    loss.attrs["long_name"] = "tropospheric CH4 loss by OH, offline recomputation"
    loss.attrs["units"] = "kg CH4 s-1"
    return loss


def add_ch4_diagnostics(ds: xr.Dataset) -> xr.Dataset:
    ds_ = ds.copy(deep=False)

    burden = ch4_burden(ds_, tropospheric_only=False)
    burden_trop = ch4_burden(ds_, tropospheric_only=True)
    loss = ch4_oh_loss(ds_)

    ds_["CH4_burden_kg"] = burden
    ds_["CH4_burden_Tg"] = (burden / 1.0e9).assign_attrs(long_name="global atmospheric CH4 burden", units="Tg CH4")
    ds_["CH4_burden_trop_kg"] = burden_trop
    ds_["CH4_burden_trop_Tg"] = (burden_trop / 1.0e9).assign_attrs(long_name="tropospheric CH4 burden", units="Tg CH4")
    ds_["CH4_OH_loss_kg_s"] = loss
    ds_["CH4_OH_loss_Tg_yr"] = (loss * SEC_PER_YEAR / 1.0e9).assign_attrs(long_name="tropospheric CH4 loss by OH", units="Tg CH4 yr-1")
    ds_["CH4_lifetime_OH_yr"] = (burden / loss / SEC_PER_YEAR).assign_attrs(long_name="CH4 lifetime with respect to tropospheric OH", units="yr")

    return ds_


# -----------------------------------------------------------------------------
# BVOC and emissions diagnostics
# -----------------------------------------------------------------------------

def global_emission_Tg_yr(ds: xr.Dataset, var: str) -> xr.DataArray:
    """Global annual-rate equivalent for a kg m-2 s-1 surface flux."""
    require_vars(ds, [var, "GRIDAREA"])
    out = (ds[var] * ds["GRIDAREA"]).sum(("lat", "lon"), skipna=True) * SEC_PER_YEAR / 1.0e9
    out.name = f"{var}_Tg_yr"
    out.attrs["long_name"] = f"global total {var} emission"
    out.attrs["units"] = "Tg yr-1"
    return out


def add_bvoc_diagnostics(ds: xr.Dataset) -> xr.Dataset:
    ds_ = ds.copy(deep=False)

    for var in ["MEG_ISOP", "MEG_MTERP", "SFISOP", "SFMTERP", "emis_ISOP", "emis_MTERP"]:
        if var in ds_:
            ds_[f"{var}_Tg_yr"] = global_emission_Tg_yr(ds_, var)

    return ds_


# -----------------------------------------------------------------------------
# Ozone diagnostics
# -----------------------------------------------------------------------------

def add_ozone_diagnostics(ds: xr.Dataset) -> xr.Dataset:
    ds_ = ds.copy(deep=False)

    if "O3" in ds_:
        burden = gas_burden_from_vmr(ds_, "O3", M_O3, tropospheric_only=True)
        ds_["O3_burden_kg"] = burden
        ds_["O3_burden_Tg"] = (burden / 1.0e9).assign_attrs(long_name="tropospheric O3 burden", units="Tg O3")

    return ds_


# -----------------------------------------------------------------------------
# Full diagnostic builders
# -----------------------------------------------------------------------------

TROP_MEAN_VARS = [
    "OH", "HO2", "H2O2", "CO", "O3", "NO", "NO2", "NOx", "NO3", "HNO3", "PAN",
    "CH2O", "ISOP", "MTERP", "T", "Q",
]

SURFACE_MEAN_VARS = [
    "CH4_SRF", "O3_SRF", "OH_SRF", "CO_SRF", "NO_SRF", "NO2_SRF", "CH2O_SRF",
    "FSDS", "SOLIN", "CLDTOT", "TREFHT", "QREFHT",
]


def make_monthly_diagnostics(ds: xr.Dataset) -> xr.Dataset:
    """
    Build compact monthly scalar diagnostics for CH4, BVOC, ozone, and chemistry.
    """
    ds_work = add_pressure_diagnostics(ds)

    if {"NO", "NO2"}.issubset(ds_work.data_vars) and "NOx" not in ds_work:
        ds_work["NOx"] = ds_work["NO"] + ds_work["NO2"]
        ds_work["NOx"].attrs["long_name"] = "NO + NO2"
        ds_work["NOx"].attrs["units"] = ds_work["NO"].attrs.get("units", "")

    ds_work = add_ch4_diagnostics(ds_work)
    ds_work = add_bvoc_diagnostics(ds_work)
    ds_work = add_ozone_diagnostics(ds_work)

    out = xr.Dataset(coords={"time": ds_work["time"]})

    scalar_vars = [
        "CH4_burden_kg", "CH4_burden_Tg", "CH4_burden_trop_kg", "CH4_burden_trop_Tg",
        "CH4_OH_loss_kg_s", "CH4_OH_loss_Tg_yr", "CH4_lifetime_OH_yr",
        "O3_burden_kg", "O3_burden_Tg",
    ]
    for var in scalar_vars:
        if var in ds_work:
            out[var] = ds_work[var]

    for var in ["MEG_ISOP", "MEG_MTERP", "SFISOP", "SFMTERP", "emis_ISOP", "emis_MTERP"]:
        derived = f"{var}_Tg_yr"
        if derived in ds_work:
            out[derived] = ds_work[derived]

    for var in TROP_MEAN_VARS:
        if var in ds_work and "lev" in ds_work[var].dims:
            out[f"{var}_trop_massmean"] = mass_weighted_trop_mean(ds_work, var)

    for var in SURFACE_MEAN_VARS:
        if var in ds_work and {"lat", "lon"}.issubset(ds_work[var].dims):
            out[f"{var}_global_mean"] = area_weighted_mean_2d(ds_work, var)

    out.attrs["description"] = "Compact monthly CH4/BVOC/O3/chemistry diagnostics from selected CAM output."
    return out


def ch4_oh_loss_3d(ds: xr.Dataset) -> xr.DataArray:
    """Local CH4 + OH loss per grid-cell layer, kg CH4 s-1."""
    ds_work = add_pressure_diagnostics(ds)
    require_vars(ds_work, ["CH4", "OH", "T", "PMID", "AIR_VOLUME", "TROP_MASK"])

    n_air_cm3 = (ds_work["PMID"] / (KB * ds_work["T"])) / 1.0e6
    k_ch4_oh = 2.45e-12 * np.exp(-1775.0 / ds_work["T"])
    loss_molec_cm3_s = k_ch4_oh * (ds_work["CH4"] * n_air_cm3) * (ds_work["OH"] * n_air_cm3)
    loss = loss_molec_cm3_s * ds_work["AIR_VOLUME"] * 1.0e6 / NA * M_CH4
    loss = loss.where(ds_work["TROP_MASK"])
    loss.name = "CH4_OH_loss_cell_kg_s"
    loss.attrs["long_name"] = "local tropospheric CH4 + OH loss"
    loss.attrs["units"] = "kg CH4 s-1 per grid-cell layer"
    return loss


def make_map_diagnostics(ds: xr.Dataset) -> xr.Dataset:
    """Build monthly map-ready diagnostics."""
    ds_work = add_pressure_diagnostics(ds)
    out = xr.Dataset(coords={"time": ds_work.time, "lat": ds_work.lat, "lon": ds_work.lon})

    loss3d = ch4_oh_loss_3d(ds_work)
    out["CH4_OH_loss_column_Tg_yr"] = (loss3d.sum("lev", skipna=True) * SEC_PER_YEAR / 1.0e9).assign_attrs(
        long_name="column-integrated CH4 + OH loss", units="Tg CH4 yr-1 per grid cell"
    )

    for var in ["OH", "O3", "CO", "NO", "NO2", "CH2O"]:
        if var in ds_work and "lev" in ds_work[var].dims:
            w = ds_work["AIR_MASS"].where(ds_work["TROP_MASK"])
            col = (ds_work[var].where(ds_work["TROP_MASK"]) * w).sum("lev", skipna=True) / w.sum("lev", skipna=True)
            out[f"{var}_trop_massmean_column"] = col.assign_attrs(
                long_name=f"tropospheric mass-weighted column mean {var}",
                units=ds_work[var].attrs.get("units", ""),
            )

    for var in ["MEG_ISOP", "MEG_MTERP", "SFISOP", "SFMTERP", "emis_ISOP", "emis_MTERP"]:
        if var in ds_work:
            out[var] = ds_work[var]

    return out


def make_annual_diagnostics(ds: xr.Dataset) -> xr.Dataset:
    return annual_mean(ds)


def make_climatology(ds: xr.Dataset, start_year: int | None = None, end_year: int | None = None) -> xr.Dataset:
    return climatology(ds, start_year=start_year, end_year=end_year)


def difference(perturbed: xr.Dataset, control: xr.Dataset, suffix: str = "diff") -> xr.Dataset:
    out = perturbed - control
    return out.rename({var: f"{var}_{suffix}" for var in out.data_vars})


def relative_difference_percent(perturbed: xr.Dataset, control: xr.Dataset, suffix: str = "reldiff_pct") -> xr.Dataset:
    out = (perturbed - control) / control * 100.0
    out = out.rename({var: f"{var}_{suffix}" for var in out.data_vars})
    for var in out.data_vars:
        out[var].attrs["units"] = "%"
    return out


def paired_comparison(perturbed: xr.Dataset, control: xr.Dataset) -> xr.Dataset:
    return xr.merge([difference(perturbed, control), relative_difference_percent(perturbed, control)], compat="override")