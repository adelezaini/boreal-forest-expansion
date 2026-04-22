from __future__ import annotations

import numpy as np
import xarray as xr

from .metadata import infer_lat_lon_names


def region_to_dataset_lon_bounds(
    lon_min: float,
    lon_max: float,
    ds_lon: xr.DataArray,
) -> tuple[float, float, bool]:
    """
    Translate region longitude bounds into the dataset's longitude convention.
    """
    lon_values = np.asarray(ds_lon.values)

    if np.nanmax(lon_values) > 180.0:
        a = lon_min % 360.0
        b = lon_max % 360.0
    else:
        a = lon_min
        b = lon_max

    crosses = a > b
    return a, b, crosses


def subset_region(da: xr.DataArray, region_bounds) -> xr.DataArray:
    """
    Subset a DataArray to a latitude/longitude box.
    """
    if region_bounds is None:
        return da

    lat_name, lon_name = infer_lat_lon_names(da)
    if lat_name is None or lon_name is None:
        raise ValueError(f"Cannot subset region for {da.name}: lat/lon dims not found")

    lat_min, lat_max, lon_min, lon_max = region_bounds

    da_sub = da.where((da[lat_name] >= lat_min) & (da[lat_name] <= lat_max), drop=True)

    a, b, crosses = region_to_dataset_lon_bounds(lon_min, lon_max, da_sub[lon_name])

    if crosses:
        da_sub = da_sub.where((da_sub[lon_name] >= a) | (da_sub[lon_name] <= b), drop=True)
    else:
        da_sub = da_sub.where((da_sub[lon_name] >= a) & (da_sub[lon_name] <= b), drop=True)

    return da_sub


def collapse_extra_dims(da: xr.DataArray) -> xr.DataArray:
    """
    Average over all dimensions except time and horizontal coordinates.
    """
    lat_name, lon_name = infer_lat_lon_names(da)

    keep = {"time"}
    if lat_name is not None:
        keep.add(lat_name)
    if lon_name is not None:
        keep.add(lon_name)

    extra_dims = [d for d in da.dims if d not in keep]
    if extra_dims:
        da = da.mean(dim=extra_dims, skipna=True)

    return da


def weighted_mean_latlon(da: xr.DataArray) -> xr.DataArray:
    """
    Compute an area-weighted mean over latitude and longitude.
    """
    lat_name, lon_name = infer_lat_lon_names(da)

    if lat_name is None or lon_name is None:
        other_dims = [d for d in da.dims if d != "time"]
        return da.mean(dim=other_dims, skipna=True) if other_dims else da

    weights = np.cos(np.deg2rad(da[lat_name]))
    return da.weighted(weights).mean(dim=[lat_name, lon_name], skipna=True)


def reduce_series(da: xr.DataArray, region_bounds) -> xr.DataArray:
    """
    Reduce a gridded variable to a regional mean time series.
    """
    da = collapse_extra_dims(da)
    da = subset_region(da, region_bounds)
    da = weighted_mean_latlon(da)
    return da
