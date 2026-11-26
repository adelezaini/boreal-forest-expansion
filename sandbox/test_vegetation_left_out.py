"""Show what the final vegetation border leaves out (yellow cells in the needleleaf area).

Writes into sandbox/test_vegetation_outlines_outputs/ only (not paper output).
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "src"), str(HERE)]

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from shapely import contains_xy
from shapely.geometry import Polygon

import test_vegetation_border_styles as ts
import test_vegetation_bvoc as tb
import test_vegetation_outlines as tv
import test_vegetation_yellow_versions as ty
from boreal_forest_expansion.plotting import forcing_maps as fm
from boreal_forest_expansion.plotting import palette as pal
from boreal_forest_expansion.plotting.style import set_default_style

KINDS = {"loop": ("Small closed loop", pal.RED), "box": ("Your deleted boxes", pal.GOLD),
         "short": ("Short fragment", pal.PLUM), "added": ("Added to close the gap", pal.NAVY)}
SIBERIA_REDRAWN = (98.0, 105.5, 54.5, 60.0)  # raw border here is replaced by the smoothed route
DASH, WIDTH = (0, (2.2, 1.0)), 0.7


def inside_boxes(xy, ax):
    left, top, right, bottom = tb.MAP_PIXELS
    boxes = [((x0 - left) / (right - left), (bottom - y1) / (bottom - top),
              (x1 - left) / (right - left), (bottom - y0) / (bottom - top)) for x0, y0, x1, y1 in tb.REMOVE_BOXES]
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    p = ax.projection.transform_points(ccrs.PlateCarree(), xy[:, 0], xy[:, 1])
    fx, fy = (p[:, 0] - xlim[0]) / (xlim[1] - xlim[0]), (p[:, 1] - ylim[0]) / (ylim[1] - ylim[0])
    return np.any([(fx >= a) & (fx <= c) & (fy >= b) & (fy <= d) for a, b, c, d in boxes], axis=0)


def left_out(raw, ax):
    """(kind, line) for every part of the unfiltered border that the final line does not draw."""
    out = []
    for xy in raw:
        km = ts.length_km(xy)
        closed = np.allclose(xy[0], xy[-1])
        if km < ts.MIN_PIECE_KM:
            if closed or not (ty.in_kola(xy[0]) and ty.in_kola(xy[-1])):
                out.append(("loop" if closed else "short", xy))
            continue
        if closed and km < ts.MAX_LOOP_KM:
            out.append(("loop", xy))
            continue
        inside = inside_boxes(xy, ax)
        breaks = np.nonzero(np.diff(inside.astype(int)))[0] + 1
        for run in np.split(np.arange(len(xy)), breaks):
            if len(run) < 2:
                continue
            if inside[run[0]]:
                out.append(("box", xy[run]))
            elif ts.length_km(xy[run]) < ts.MIN_PIECE_KM:
                out.append(("short", xy[run]))
    return out


def segment_keys(xy):
    p = [tuple(q) for q in np.round(xy, 6).tolist()]
    return [frozenset(pair) for pair in zip(p[:-1], p[1:])]


def runs(xy, flags):
    """Stretches of a line whose segments are flagged."""
    flags = np.asarray(flags, dtype=int)
    starts = np.nonzero(np.diff(np.r_[0, flags]) == 1)[0]
    ends = np.nonzero(np.diff(np.r_[flags, 0]) == -1)[0]
    return [xy[a:b + 2] for a, b in zip(starts, ends)]


def compare_with_final(raw, final, ax):
    """Parts of the unfiltered border not drawn in `final`, and parts of `final` that are not in it."""
    raw_keys = {k for xy in raw for k in segment_keys(xy)}
    final_keys = {k for xy in final for k in segment_keys(xy)}
    removed = []
    for xy in raw:
        for part in runs(xy, [k not in final_keys for k in segment_keys(xy)]):
            lon, lat = part[:, 0].mean(), part[:, 1].mean()
            if SIBERIA_REDRAWN[0] <= lon <= SIBERIA_REDRAWN[1] and SIBERIA_REDRAWN[2] <= lat <= SIBERIA_REDRAWN[3]:
                continue
            whole_loop = np.allclose(xy[0], xy[-1]) and len(part) == len(xy)
            removed.append(("loop" if whole_loop else "box" if inside_boxes(part, ax).mean() > 0.5 else "short", part))
    added = [part for xy in final for part in runs(xy, [k not in raw_keys for k in segment_keys(xy)])]
    return removed, added


def enclosed_cells(xy, classes):
    if not np.allclose(xy[0], xy[-1]) or len(xy) < 4:
        return np.nan, np.nan
    lon2, lat2 = np.meshgrid(classes["lon"].values, classes["lat"].values)
    inside = contains_xy(Polygon(xy), lon2, lat2)
    return int((inside & (classes.values == 1)).sum()), int((inside & (classes.values == 3)).sum())


def load_monoterpene():
    panel = next(p for p in fm.CONTEXT_PANELS if p.key == "sfmterp")
    for attempt in range(1, 9):  # NIRD reads fail intermittently with "HDF error"
        try:
            return fm.panel_difference(panel, {"lcc": "LCC_FUT", "fbvoc": "CTRL_FUT"}, tv.START, tv.END).load().mean("year")
        except (OSError, RuntimeError) as err:
            print(f"read attempt {attempt} failed: {err}", flush=True)
            if attempt == 8:
                raise
            time.sleep(10 * attempt)


def main():
    set_default_style()
    _, _, classes, modified, area = tv.load_classes()
    version = classes.where(classes != 2, 3)
    field = load_monoterpene()

    fig, axes = plt.subplots(1, 2, figsize=(14, 7.6), subplot_kw={"projection": ccrs.Orthographic(0, 90)})
    for ax in axes:
        tv.base_map(ax)
    import test_vegetation_real_figures as tr  # imported here: it imports this module
    stored = json.loads((tv.OUT / "vegetation_map_lines.json").read_text())
    lines = {k: [np.asarray(xy) for xy in stored[k]] for k in ("border", "modified")}
    raw = tv.divider_lines(version, area, sigma=(0.0, 0.0), min_km=0.0)
    removed, added = compare_with_final(raw, lines["border"], axes[0])
    print(f"raw {sum(map(ts.length_km, raw)):.0f} km; final {sum(map(ts.length_km, lines['border'])):.0f} km; "
          f"left out {sum(ts.length_km(xy) for _, xy in removed):.0f} km; added {sum(map(ts.length_km, added)):.0f} km")

    with tr.xr.open_dataset(tv.LCC_SURF, decode_times=False) as surf:
        landfrac = surf["LANDFRAC_PFT"].load().values
    full, lon_c = tr.tm.modified_contour(modified)
    land_lines = tr.tm.land_edges(full, modified, landfrac > tr.tf.LAND_LIMIT, lon_c)
    final_modified = {k for xy in lines["modified"] for k in segment_keys(xy)}
    modified_out = [part for xy in land_lines for part in runs(xy, [k not in final_modified for k in segment_keys(xy)])]
    print(f"modified line on land {sum(map(ts.length_km, land_lines)):.0f} km = drawn "
          f"{sum(map(ts.length_km, lines['modified'])):.0f} km + removed {sum(map(ts.length_km, modified_out)):.0f} km "
          f"in {len(modified_out)} pieces")

    rows = []
    for kind, xy in removed:
        broad, needle = enclosed_cells(xy, version)
        rows.append({"why": KINDS[kind][0], "km": round(ts.length_km(xy)), "lat": round(float(xy[:, 1].mean()), 1),
                     "lon_E": round(float(xy[:, 0].mean()), 1), "enclosed_broadleaf_cells": broad,
                     "enclosed_needleleaf_cells": needle})
    table = pd.DataFrame(rows).sort_values(["why", "km"], ascending=[True, False])
    table.to_csv(tv.OUT / "border_left_out.csv", index=False)
    print(table.to_string(index=False))
    print(table.groupby("why")["km"].agg(["count", "sum"]))

    colors = ["#DE7A3A", "#5D9A92", "#E6E6E6"]
    code = xr_code = version.where(version != 0, 2).where(version != 1, 0).where(version != 3, 1)
    axes[0].pcolormesh(version["lon"], version["lat"], code.values, cmap=ListedColormap(colors),
                       norm=BoundaryNorm([-0.5, 0.5, 1.5, 2.5], 3), transform=ccrs.PlateCarree(),
                       shading="nearest", zorder=1)
    axes[1].pcolormesh(field["lon"], field["lat"], field.values, cmap="RdBu_r", vmin=-0.88, vmax=0.88,
                       transform=ccrs.PlateCarree(), shading="nearest", zorder=1)
    for ax, title in zip(axes, ("Vegetation regions", "Monoterpene emissions, LCC_FUT − CTRL_FUT")):
        ax.coastlines(linewidth=0.4, color="#8C8C8C", zorder=3)
        ax.set_title(title, fontsize=12, fontweight="semibold")
        tr.add_lines(ax, lines)
        for kind, xy in removed:
            ax.plot(xy[:, 0], xy[:, 1], color=KINDS[kind][1], lw=2.0, transform=ccrs.PlateCarree(), zorder=7)
        for xy in added:
            ax.plot(xy[:, 0], xy[:, 1], color=KINDS["added"][1], lw=2.0, transform=ccrs.PlateCarree(), zorder=7)
        for xy in modified_out:
            ax.plot(xy[:, 0], xy[:, 1], color=pal.RED, lw=1.1, ls=":", transform=ccrs.PlateCarree(), zorder=7)
    handles = [Patch(color=colors[0], label="Broadleaf replaces needleleaf"),
               Patch(color=colors[1], label="No needleleaf loss, tree gain"), Patch(color=colors[2], label="Little tree gain"),
               Line2D([], [], color="k", lw=WIDTH, ls=DASH, label="Final border"),
               Line2D([], [], color="k", lw=0.5, label="Modified-cell line, land only")]
    handles += [Line2D([], [], color=c, lw=2.0, label=n) for n, c in KINDS.values()]
    handles += [Line2D([], [], color=pal.RED, lw=1.1, ls=":", label="Modified-cell line removed"),
                Line2D([], [], color="#8C8C8C", lw=0.4, label="Coastline")]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=9)
    fig.subplots_adjust(bottom=0.12, top=0.93, wspace=0.03)
    fig.savefig(tv.OUT / "border_left_out.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
