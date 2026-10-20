"""Area weights and region masks on the CAM grid.

Weights: CAM `gw` (Gaussian/latitude weights) if present, else GRIDAREA, else cos(lat).
All are proportional to cell area on the regular f19 grid (b), so regional means and
area fractions agree whichever is used.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

log = logging.getLogger(__name__)


def area_weights(ds: xr.Dataset) -> xr.DataArray:
    """2-D (lat, lon) weights proportional to cell area, normalised to sum 1."""
    if "gw" in ds:
        w = ds["gw"]
        if "time" in w.dims:
            w = w.isel(time=0, drop=True)
        w = w.broadcast_like(ds["lon"]).transpose("lat", "lon")
        source = "gw"
    elif "GRIDAREA" in ds:
        w = ds["GRIDAREA"]
        if "time" in w.dims:
            w = w.isel(time=0, drop=True)
        source = "GRIDAREA"
    else:
        w = np.cos(np.deg2rad(ds["lat"])).broadcast_like(ds["lon"]).transpose("lat", "lon")
        source = "cos(lat)"
    w = (w / w.sum()).load()
    w.name = "area_weight"
    w.attrs["source"] = source
    return w


def band_mask(ds: xr.Dataset, lat_min: float, lat_max: float) -> xr.DataArray:
    """True for cells whose centre lies in [lat_min, lat_max]."""
    lat2d = ds["lat"].broadcast_like(ds["lon"]).transpose("lat", "lon")
    return ((lat2d >= lat_min) & (lat2d <= lat_max)).rename("mask")


def load_modified_cells(path: str | Path, ds: xr.Dataset, tol_deg: float = 1e-3) -> xr.DataArray:
    """Mask of land-cover-modified cells on the grid of `ds`.

    Accepts the cache written by build_modified_cells (modified_cells.nc, variable
    `modified`) or its CSV twin (columns lat, lon_360). Cells are matched by
    coordinate within `tol_deg`; any unmatched cell raises (never a nearest-neighbour
    regrid, consistent with equilibrium.modified_mask).
    """
    path = Path(path)
    if path.suffix == ".nc":
        with xr.open_dataset(path) as m:
            m = m.load()
        lat2d, lon2d = xr.broadcast(m["lat"], m["lon"])
        sel = m["modified"].values.astype(bool)
        lats, lons = lat2d.values[sel], lon2d.values[sel] % 360
    elif path.suffix == ".csv":
        t = pd.read_csv(path)
        lats, lons = t["lat"].to_numpy(), t["lon_360"].to_numpy() % 360
    else:
        raise ValueError(f"Expected .nc or .csv, got {path}")

    glat, glon = ds["lat"].values, ds["lon"].values % 360
    i = np.abs(glat[None, :] - lats[:, None]).argmin(axis=1)
    dlon = np.abs(glon[None, :] - lons[:, None])
    dlon = np.minimum(dlon, 360 - dlon)
    j = dlon.argmin(axis=1)
    err = np.maximum(np.abs(glat[i] - lats), dlon[np.arange(len(j)), j])
    if np.any(err > tol_deg):
        raise ValueError(f"{(err > tol_deg).sum()} modified cells do not match the grid within {tol_deg} deg")

    mask = np.zeros((glat.size, glon.size), dtype=bool)
    mask[i, j] = True
    log.info("Modified cells: %d from %s", mask.sum(), path.name)
    return xr.DataArray(mask, coords={"lat": ds["lat"], "lon": ds["lon"]}, dims=("lat", "lon"), name="modified")


def default_regions(ds: xr.Dataset, modified: xr.DataArray) -> dict[str, xr.DataArray]:
    """Regions for the far-field check.

    tropics, SH_extratropics: far from the land-cover change (all modified cells are
    north of 46 N (a, modified_cells.csv)); modified_cells: where the BVOC signal is
    expected, shown for scale; NH_45_90_rest: unmodified cells north of 45 N (near
    field, reached by transport); global: everything.
    """
    regions = {
        "modified_cells": modified,
        "NH_45_90_rest": band_mask(ds, 45, 90) & ~modified,
        "tropics": band_mask(ds, -30, 30),
        "SH_extratropics": band_mask(ds, -90, -30.0001),
        "global": xr.ones_like(modified, dtype=bool),
    }
    for name in ("tropics", "SH_extratropics"):
        if bool((regions[name] & modified).any()):
            raise ValueError(f"Region {name} overlaps modified cells: not a far-field region")
    return regions


def area_fraction(weights: xr.DataArray, mask: xr.DataArray) -> float:
    return float(weights.where(mask).sum())


def regional_mean(da: xr.DataArray, weights: xr.DataArray, mask: xr.DataArray) -> xr.DataArray:
    """Area-weighted mean over the cells where mask is True (keeps other dims, e.g. year)."""
    w = weights.where(mask, 0.0)
    return da.weighted(w).mean(("lat", "lon"))
