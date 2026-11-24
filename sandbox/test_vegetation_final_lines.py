"""Style test: candidate final lines on the isoprene and monoterpene maps.

Vegetation border: dashed, width 0.7, yellow cells in the needleleaf area, west Alaska kept, no Kola link.
Modified cells: solid, width 0.5, only where they meet unmodified cells that are mostly land.
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

import test_vegetation_border_styles as ts
import test_vegetation_bvoc as tb
import test_vegetation_left_out as tl
import test_vegetation_modified_edges as tm
import test_vegetation_outlines as tv
from boreal_forest_expansion.plotting import forcing_maps as fm
from boreal_forest_expansion.plotting.style import set_default_style

WEST_ALASKA = (190.0, 215.0, 54.0, 72.0)  # lon0, lon1 (degrees E), lat0, lat1
LAND_LIMIT = 0.5
# Boxes marked by the user on the second screenshot (2026-11-21): no modified-cell line inside them.
MODIFIED_MAP_PIXELS = (43, 0, 1350, 1290)  # left, top, right, bottom of the map circle in that screenshot
MODIFIED_REMOVE_BOXES = {"Canadian Arctic and Greenland": (332, 562, 662, 995), "southern Scandinavia": (777, 1023, 918, 1193)}


def trim_modified(lines, ax):
    """Remove the parts of the modified-cell line inside MODIFIED_REMOVE_BOXES."""
    left, top, right, bottom = MODIFIED_MAP_PIXELS
    boxes = [((x0 - left) / (right - left), (bottom - y1) / (bottom - top),
              (x1 - left) / (right - left), (bottom - y0) / (bottom - top))
             for x0, y0, x1, y1 in MODIFIED_REMOVE_BOXES.values()]
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    kept = []
    for xy in lines:
        p = ax.projection.transform_points(ccrs.PlateCarree(), xy[:, 0], xy[:, 1])
        fx, fy = (p[:, 0] - xlim[0]) / (xlim[1] - xlim[0]), (p[:, 1] - ylim[0]) / (ylim[1] - ylim[0])
        inside = np.any([(fx >= a) & (fx <= c) & (fy >= b) & (fy <= d) for a, b, c, d in boxes], axis=0)
        breaks = np.nonzero(np.diff(inside.astype(int)))[0] + 1
        kept += [xy[run] for run in np.split(np.arange(len(xy)), breaks) if len(run) > 1 and not inside[run[0]]]
    print(f"modified line: {sum(map(ts.length_km, lines)):.0f} km → {sum(map(ts.length_km, kept)):.0f} km, "
          f"{len(lines)} → {len(kept)} pieces")
    return kept


def in_west_alaska(xy):
    lon, lat = xy[:, 0].mean(), xy[:, 1].mean()
    return WEST_ALASKA[0] <= lon <= WEST_ALASKA[1] and WEST_ALASKA[2] <= lat <= WEST_ALASKA[3]


def final_border(version, area, ax):
    """All border pieces except short fragments, small loops and marked boxes outside west Alaska."""
    raw = tv.divider_lines(version, area, sigma=(0.0, 0.0), min_km=0.0)
    restored = [xy for kind, xy in tl.left_out(raw, ax) if kind in ("loop", "box") and in_west_alaska(xy)]
    for xy in restored:
        print(f"west Alaska restored: {ts.length_km(xy):.0f} km near {xy[:, 1].mean():.1f}°N {xy[:, 0].mean():.1f}°E")
    kept = []
    for xy in raw:
        km, closed = ts.length_km(xy), np.allclose(xy[0], xy[-1])
        if km < ts.MIN_PIECE_KM or (closed and km < ts.MAX_LOOP_KM):
            continue
        inside = tl.inside_boxes(xy, ax)
        breaks = np.nonzero(np.diff(inside.astype(int)))[0] + 1
        for run in np.split(np.arange(len(xy)), breaks):
            if len(run) > 1 and not inside[run[0]] and ts.length_km(xy[run]) >= ts.MIN_PIECE_KM:
                kept.append(xy[run])
    border = kept + restored
    print(f"final border: {len(border)} pieces, {sum(map(ts.length_km, border)):.0f} km, no Kola link")
    return border


def main():
    set_default_style()
    _, _, classes, modified, area = tv.load_classes()
    version = classes.where(classes != 2, 3)
    with xr.open_dataset(tv.LCC_SURF, decode_times=False) as s:
        landfrac = s["LANDFRAC_PFT"].load().values
    full, lon_c = tm.modified_contour(modified)
    edges = tm.land_edges(full, modified, landfrac > LAND_LIMIT, lon_c)
    print(f"modified line: {len(edges)} pieces, {sum(map(ts.length_km, edges)):.0f} km")

    panels = [p for p in fm.CONTEXT_PANELS if p.key in ("sfisop", "sfmterp")]
    fig, axes = tb.emission_grid(panels)
    border = final_border(version, area, axes[0, 0])
    edges = trim_modified(edges, axes[0, 0])
    for ax in axes.flat:
        for xy in edges:
            ax.plot(xy[:, 0], xy[:, 1], color="k", lw=tm.MODIFIED_WIDTH, transform=ccrs.PlateCarree(), zorder=5)
        for xy in border:
            ax.plot(xy[:, 0], xy[:, 1], color="k", lw=tm.BORDER_WIDTH, ls=tm.BORDER_DASH,
                    transform=ccrs.PlateCarree(), zorder=6)
    fig.savefig(tv.OUT / "final_lines_bvoc.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
