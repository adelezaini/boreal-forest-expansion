"""Style test: modified-cell line only where modified cells meet unmodified land (monoterpene maps).

Columns: full outline; line against any land cell; line against cells that are at least half land.
Vegetation border: dashed, width 0.7, yellow cells in the needleleaf area.
Writes into sandbox/test_vegetation_outlines_outputs/ only (not paper output).
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "src"), str(HERE)]

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from cartopy.util import add_cyclic_point

import test_vegetation_border_styles as ts
import test_vegetation_bvoc as tb
import test_vegetation_outlines as tv
import test_vegetation_yellow_versions as ty
from boreal_forest_expansion.plotting import forcing_maps as fm
from boreal_forest_expansion.plotting.style import set_default_style

BORDER_DASH, BORDER_WIDTH = (0, (2.2, 1.0)), 0.7
MODIFIED_WIDTH = 0.5
VERSIONS = [("Full modified outline", None), ("Against any land", 0.0), ("Against cells ≥ 50 % land", 0.5)]


def modified_contour(modified):
    data, lon_c = add_cyclic_point(modified.astype(float).values, coord=modified["lon"].values)
    fig, ax = plt.subplots()
    segments = ax.contour(lon_c, modified["lat"].values, data, levels=[0.5]).allsegs[0]
    plt.close(fig)
    return [xy for xy in segments if len(xy) > 1], lon_c


def faces_land(point, modified, land, lon_c):
    """True if the unmodified cell on this contour vertex is land."""
    lat, nlon = modified["lat"].values, modified["lon"].size
    x, y = point
    i = int(np.abs(lat - y).argmin())
    if abs(lat[i] - y) < 1e-6:  # between two longitudes
        j = int(np.searchsorted(lon_c, x)) - 1
        cells = [(i, j % nlon), (i, (j + 1) % nlon)]
    else:  # between two latitudes
        j = int(np.abs(lon_c - x).argmin()) % nlon
        k = int(np.searchsorted(lat, y)) - 1
        cells = [(k, j), (k + 1, j)]
    return any(land[c] and not modified.values[c] for c in cells)


def land_edges(lines, modified, land, lon_c):
    kept = []
    for xy in lines:
        flag = np.array([faces_land(p, modified, land, lon_c) for p in xy])
        use = flag[:-1] & flag[1:]
        start = None
        for k, value in enumerate(np.r_[use, False]):
            if value and start is None:
                start = k
            elif not value and start is not None:
                kept.append(xy[start:k + 1])
                start = None
    return kept


def main():
    set_default_style()
    _, _, classes, modified, area = tv.load_classes()
    with xr.open_dataset(tv.LCC_SURF, decode_times=False) as s:
        landfrac = s["LANDFRAC_PFT"].load().values
    full, lon_c = modified_contour(modified)
    variants = [full if t is None else land_edges(full, modified, landfrac > t, lon_c) for _, t in VERSIONS]
    for (name, _), lines in zip(VERSIONS, variants):
        print(f"{name}: {len(lines)} pieces, {sum(map(ts.length_km, lines)):.0f} km")

    panel = next(p for p in fm.CONTEXT_PANELS if p.key == "sfmterp")
    fig, axes = tb.emission_grid([panel] * len(VERSIONS))
    border = ty.border_for(classes.where(classes != 2, 3), area, axes[0, 0])
    for j, ((name, threshold), lines) in enumerate(zip(VERSIONS, variants)):
        axes[0, j].set_title(name, fontsize=10, fontweight="semibold")
        for ax in axes[:, j]:
            for xy in lines:
                ax.plot(xy[:, 0], xy[:, 1], color="k", lw=MODIFIED_WIDTH, transform=ccrs.PlateCarree(), zorder=5)
            for xy in border:
                ax.plot(xy[:, 0], xy[:, 1], color="k", lw=BORDER_WIDTH, ls=BORDER_DASH,
                        transform=ccrs.PlateCarree(), zorder=6)
    fig.savefig(tv.OUT / "modified_edges_monoterpene.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
