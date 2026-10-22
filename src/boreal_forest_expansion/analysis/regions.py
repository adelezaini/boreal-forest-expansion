"""Mask of the land-cover-modified cells on the CAM grid."""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

log = logging.getLogger(__name__)


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
