"""
Ghan-style radiative decomposition helpers.

This module is separate from transform.py because Ghan decomposition is a
specific radiative diagnostic, not a general unit/metadata transform.

Native CAM variables are not overwritten. New variables are suffixed `_Ghan`.
"""

from __future__ import annotations

import xarray as xr


REQUIRED_GHAN_VARS = ["FLNT", "FSNT", "FLNT_DRF", "FLNTCDRF", "FSNT_DRF", "FSNTCDRF"]


def has_ghan_inputs(ds: xr.Dataset) -> bool:
    return all(var in ds.data_vars for var in REQUIRED_GHAN_VARS)


def missing_ghan_inputs(ds: xr.Dataset) -> list[str]:
    return [var for var in REQUIRED_GHAN_VARS if var not in ds.data_vars]


def add_ghan_decomposition(ds: xr.Dataset, strict: bool = False) -> xr.Dataset:
    """
    Add Ghan decomposition diagnostics.

    Parameters
    ----------
    ds
        Dataset containing required radiative fields.
    strict
        If True, raise an error when required variables are missing. If False,
        return the input dataset unchanged and print a warning.
    """
    ds_ = ds.copy(deep=False)
    missing = missing_ghan_inputs(ds_)

    if missing:
        msg = f"Cannot compute Ghan decomposition; missing variables: {missing}"
        if strict:
            raise KeyError(msg)
        print(f"Warning: {msg}")
        return ds_

    # Total TOA fluxes. CAM convention: FSNT downward positive shortwave,
    # FLNT upward positive longwave. Net downward is FSNT - FLNT.
    ds_["SWTOT_Ghan"] = ds_["FSNT"]
    ds_["SWTOT_Ghan"].attrs["long_name"] = "shortwave total flux at TOA"
    ds_["SWTOT_Ghan"].attrs["units"] = ds_["FSNT"].attrs.get("units", "W/m2")

    ds_["LWTOT_Ghan"] = -ds_["FLNT"]
    ds_["LWTOT_Ghan"].attrs["long_name"] = "longwave total flux at TOA, downward positive"
    ds_["LWTOT_Ghan"].attrs["units"] = ds_["FLNT"].attrs.get("units", "W/m2")

    ds_["FTOT_Ghan"] = ds_["FSNT"] - ds_["FLNT"]
    ds_["FTOT_Ghan"].attrs["long_name"] = "net TOA flux, downward positive"
    ds_["FTOT_Ghan"].attrs["units"] = ds_["FSNT"].attrs.get("units", "W/m2")

    # Direct aerosol radiative components.
    ds_["SWDIR_Ghan"] = ds_["FSNT"] - ds_["FSNT_DRF"]
    ds_["SWDIR_Ghan"].attrs["long_name"] = "shortwave aerosol direct radiative flux, Ghan decomposition"
    ds_["SWDIR_Ghan"].attrs["units"] = ds_["FSNT"].attrs.get("units", "W/m2")

    ds_["LWDIR_Ghan"] = -(ds_["FLNT"] - ds_["FLNT_DRF"])
    ds_["LWDIR_Ghan"].attrs["long_name"] = "longwave aerosol direct radiative flux, Ghan decomposition"
    ds_["LWDIR_Ghan"].attrs["units"] = ds_["FLNT"].attrs.get("units", "W/m2")

    ds_["DIR_Ghan"] = ds_["SWDIR_Ghan"] + ds_["LWDIR_Ghan"]
    ds_["DIR_Ghan"].attrs["long_name"] = "net aerosol direct radiative flux, Ghan decomposition"
    ds_["DIR_Ghan"].attrs["units"] = ds_["SWDIR_Ghan"].attrs.get("units", "W/m2")

    # Cloud radiative components in clean-sky diagnostics.
    ds_["SWCF_Ghan"] = ds_["FSNT_DRF"] - ds_["FSNTCDRF"]
    ds_["SWCF_Ghan"].attrs["long_name"] = "shortwave cloud radiative flux, Ghan decomposition"
    ds_["SWCF_Ghan"].attrs["units"] = ds_["FSNT_DRF"].attrs.get("units", "W/m2")

    ds_["LWCF_Ghan"] = -(ds_["FLNT_DRF"] - ds_["FLNTCDRF"])
    ds_["LWCF_Ghan"].attrs["long_name"] = "longwave cloud radiative flux, Ghan decomposition"
    ds_["LWCF_Ghan"].attrs["units"] = ds_["FLNT_DRF"].attrs.get("units", "W/m2")

    ds_["NCFT_Ghan"] = ds_["SWCF_Ghan"] + ds_["LWCF_Ghan"]
    ds_["NCFT_Ghan"].attrs["long_name"] = "net cloud radiative flux, Ghan decomposition"
    ds_["NCFT_Ghan"].attrs["units"] = ds_["SWCF_Ghan"].attrs.get("units", "W/m2")

    # Clear-sky clean remainder, useful for surface/albedo/greenhouse components.
    ds_["SW_rest_Ghan"] = ds_["FSNTCDRF"]
    ds_["SW_rest_Ghan"].attrs["long_name"] = "shortwave clean clear-sky residual flux"
    ds_["SW_rest_Ghan"].attrs["units"] = ds_["FSNTCDRF"].attrs.get("units", "W/m2")

    ds_["LW_rest_Ghan"] = -ds_["FLNTCDRF"]
    ds_["LW_rest_Ghan"].attrs["long_name"] = "longwave clean clear-sky residual flux, downward positive"
    ds_["LW_rest_Ghan"].attrs["units"] = ds_["FLNTCDRF"].attrs.get("units", "W/m2")

    ds_["FREST_Ghan"] = ds_["FSNTCDRF"] - ds_["FLNTCDRF"]
    ds_["FREST_Ghan"].attrs["long_name"] = "net clean clear-sky residual flux"
    ds_["FREST_Ghan"].attrs["units"] = ds_["FSNTCDRF"].attrs.get("units", "W/m2")

    return ds_


# Backward-compatible alias for older notebooks/scripts.
aerosol_cloud_forcing_scomposition_Ghan = add_ghan_decomposition