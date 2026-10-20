"""Weighted means for monthly NorESM output.

Why weights
-----------
- Time: monthly records have different lengths (noleap: 28-31 days). An unweighted
  .mean("time") gives February the same weight as July. Use the record length in days.
- Space: grid cells have different areas. Use `gw` (CAM latitude weights) or
  `area * landfrac` (CLM land area).

`weighted_mean(da, dims, ds)` picks these weights automatically from `ds` for the
dimensions being averaged; pass `weights=` to override.

Example
-------
>>> annual = ds.SFISOP.groupby("time.year").map(lambda x: weighted_mean(x, "time", ds))
>>> boreal = weighted_mean(ds.SFISOP.sel(lat=slice(45, 90)), ("time", "lat", "lon"), ds)

Added in review round 2 (no equivalent in the old code, which used plain .mean()).
"""
import numpy as np
import xarray as xr

from .fileio import bounds_name


def record_days(ds):
    """Length of each time record in days, from the time bounds (DataArray over time)."""
    bnds = ds[bounds_name(ds)]
    bnd_dim = bnds.dims[-1]
    days = (bnds.isel({bnd_dim: 1}) - bnds.isel({bnd_dim: 0})) / np.timedelta64(1, "D")
    return days.drop_vars(bnd_dim, errors="ignore").rename("record_days").assign_attrs(units="days")


def area_weights(ds):
    """Cell-area weights: CAM `gw` (latitude only) or CLM `area * landfrac`."""
    if "gw" in ds:
        return ds.gw
    if "area" in ds and "landfrac" in ds:
        return (ds.area * ds.landfrac).fillna(0.0)      # ocean cells: fill value -> weight 0
    raise KeyError("No area weights in dataset (need 'gw' for CAM or 'area' + 'landfrac' for CLM)")


def default_weights(ds, dims):
    """Product of the weights that apply to `dims`: record length for time, area for lat/lon."""
    dims = (dims,) if isinstance(dims, str) else tuple(dims)
    weights = None
    if "time" in dims:
        weights = record_days(ds)
    if "lat" in dims or "lon" in dims:
        area = area_weights(ds)
        weights = area if weights is None else weights * area
    return weights


def weighted_mean(da, dims, ds=None, weights=None):
    """Weighted mean of `da` over `dims`.

    weights : explicit weights; if None, default_weights(ds, dims) is used (needs `ds`).
              NaNs in `da` are excluded and the remaining weights renormalised.
    """
    if weights is None:
        if ds is None:
            raise ValueError("Pass `ds` (for default weights) or explicit `weights`")
        weights = default_weights(ds, dims)
    if weights is None:                       # dims without a natural weight (e.g. 'lev')
        return da.mean(dims)
    _, weights = xr.align(da, weights, join="left")   # e.g. da is a subset (season, region)
    return da.weighted(weights.fillna(0.0)).mean(dims)
