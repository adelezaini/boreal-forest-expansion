from __future__ import annotations

from typing import Optional, Tuple

import xarray as xr


def infer_lat_lon_names(da: xr.DataArray) -> Tuple[Optional[str], Optional[str]]:
    """
    Infer latitude and longitude dimension names from common naming conventions.

    Parameters
    ----------
    da
        Input data array.

    Returns
    -------
    tuple of (lat_name, lon_name)
        Names of the latitude and longitude dimensions if found, otherwise None.
    """
    lat_candidates = ["lat", "latitude", "LAT", "nav_lat"]
    lon_candidates = ["lon", "longitude", "LON", "nav_lon"]

    lat_name = next((d for d in da.dims if d in lat_candidates), None)
    lon_name = next((d for d in da.dims if d in lon_candidates), None)

    if lat_name is None:
        lat_name = next((c for c in da.coords if c in lat_candidates and c in da.dims), None)
    if lon_name is None:
        lon_name = next((c for c in da.coords if c in lon_candidates and c in da.dims), None)

    return lat_name, lon_name


def get_units(da: xr.DataArray) -> str:
    """
    Return the units attribute of a DataArray as a stripped string.

    Parameters
    ----------
    da
        Input data array.

    Returns
    -------
    str
        Units string, or an empty string if unavailable.
    """
    return str(da.attrs.get("units", "")).strip()
