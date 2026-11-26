"""Vegetation regions of the modified cells, used for the regional means under all result maps.

Run once; plotting/forcing_maps.py reads vegetation_regions.nc. Definition (user 2026-11-24; draft Supplementary
Sect. S1): tree-cover change = (LCC - CTRL) PCT_NAT_PFT x PCT_NATVEG / 100, in percentage points (pp) of the grid
cell, for needleleaf trees (CLM PFTs 1-3) and broadleaf deciduous trees (PFTs 6-8). For each modified cell:
  1 broadleaf expansion:  broadleaf gain > 1 pp, larger than the needleleaf gain, and needleleaf loss > 1 pp
  2 needleleaf expansion: every other cell whose larger gain exceeds 1 pp (mostly needleleaf; incl. broadleaf gain
                          without needleleaf loss). Names: user 2026-11-25 19:41 (back from "replacement"/"net tree gain")
  0 little tree gain:     neither gain exceeds 1 pp (left out of the regional means)
 -1 not modified
Same classes as sandbox/test_vegetation_outlines.load_classes (1 = class 1; 2 = classes 2 + 3).
The map lines (vegetation_map_lines.json, edited by hand in sandbox/test_vegetation_real_figures.py) are for display
only and are not used here.

Usage: python build_vegetation_regions.py
"""
import os
import sys
from pathlib import Path

import numpy as np
import xarray as xr

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from boreal_forest_expansion.analysis.regions import load_modified_cells  # noqa: E402

SURF = Path("/cluster/shared/noresm/inputdata/lnd/clm2/surfdata_map")
CTRL_SURF = SURF / "release-clm5.0.18" / "surfdata_1.9x2.5_hist_78pfts_CMIP6_simyr2000_c190304.nc"
LCC_SURF = SURF / "surfdata_1.9x2.5_SSP5-8.5_2100_78pfts_LPJGUESS.nc"
NEEDLELEAF, BROADLEAF = [1, 2, 3], [6, 7, 8]
THRESHOLD = 1.0  # pp of the grid cell
OUT = HERE / "vegetation_regions.nc"


def main():
    with xr.open_dataset(CTRL_SURF, decode_times=False) as c, xr.open_dataset(LCC_SURF, decode_times=False) as l:
        change = ((l["PCT_NAT_PFT"] - c["PCT_NAT_PFT"]) * l["PCT_NATVEG"] / 100).load()
        lat, lon = l["LATIXY"].values[:, 0], l["LONGXY"].values[0, :]
    coords = {"lat": lat, "lon": lon}
    modified = load_modified_cells(HERE / "modified_cells.nc", xr.Dataset(coords=coords)).values
    d_needle = change.isel(natpft=NEEDLELEAF).sum("natpft").values
    d_broad = change.isel(natpft=BROADLEAF).sum("natpft").values

    broad_wins = (d_broad > THRESHOLD) & (d_broad > d_needle) & modified
    needle_wins = (d_needle > THRESHOLD) & (d_needle >= d_broad) & modified
    region = np.where(modified, 0, -1).astype("int8")
    region[broad_wins | needle_wins] = 2
    region[broad_wins & (d_needle < -THRESHOLD)] = 1

    ds = xr.Dataset(
        {"region": (("lat", "lon"), region, {
            "long_name": "vegetation region of the LCC-modified cells",
            "flag_values": "-1 0 1 2",
            "flag_meanings": "not_modified little_tree_gain broadleaf_expansion needleleaf_expansion"}),
         "d_broadleaf": (("lat", "lon"), np.where(modified, d_broad, np.nan), {"units": "pp of grid cell",
                         "long_name": "LCC - CTRL broadleaf deciduous tree cover (PFTs 6-8)"}),
         "d_needleleaf": (("lat", "lon"), np.where(modified, d_needle, np.nan), {"units": "pp of grid cell",
                          "long_name": "LCC - CTRL needleleaf tree cover (PFTs 1-3)"})},
        coords=coords,
        attrs={"threshold_pp": THRESHOLD, "ctrl_surfdata": str(CTRL_SURF), "lcc_surfdata": str(LCC_SURF),
               "created_by": "diagnostics/lcc-modified-cells/build_vegetation_regions.py"})
    tmp = OUT.with_suffix(".tmp.nc")   # write then rename: notebooks may be reading OUT
    ds.to_netcdf(tmp)
    os.replace(tmp, OUT)
    for v, name in [(0, "little tree gain"), (1, "broadleaf expansion"), (2, "needleleaf expansion")]:
        print(f"{name:22s} {int((region == v).sum()):5d} cells")
    print(f"modified {int(modified.sum())} cells -> {OUT}")


if __name__ == "__main__":
    main()
