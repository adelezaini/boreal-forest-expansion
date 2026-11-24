"""Diagnostic: what lies in the gaps of the dashed vegetation border over Russia.

Draws the vegetation classes, the saved border (black) and the unfiltered class border (red) over Russia, and
prints, for each gap, whether one unfiltered contour joins its two ends. Reads the saved line file, does not change it.
Writes into sandbox/test_vegetation_outlines_outputs/ only (not paper output).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "src"), str(HERE)]

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

import test_vegetation_border_styles as ts
import test_vegetation_outlines as tv
import test_vegetation_real_figures as tr
from boreal_forest_expansion.plotting.palette import PALETTE_ORDER as PALETTE
from boreal_forest_expansion.plotting.style import set_default_style

GAPS = {"central Siberia": ((98.8, 58.7), (103.8, 54.9)), "Far East": ((120.0, 53.1), (138.8, 54.9)),
        "Kola / White Sea": ((38.8, 68.2), (46.2, 69.2))}
MATCH_DEG = 0.1


def nearest(xy, point):
    return int(np.argmin(np.hypot((xy[:, 0] - point[0] + 180) % 360 - 180, xy[:, 1] - point[1])))


def joining_path(raw, a, b):
    """Shortest stretch of one unfiltered contour that passes through both ends, or None."""
    best = None
    for xy in raw:
        i, j = nearest(xy, a), nearest(xy, b)
        close = [np.hypot((xy[k, 0] - p[0] + 180) % 360 - 180, xy[k, 1] - p[1]) < MATCH_DEG
                 for k, p in ((i, a), (j, b))]
        if all(close):
            part = xy[min(i, j):max(i, j) + 1]
            if best is None or ts.length_km(part) < ts.length_km(best):
                best = part
    return best


def main():
    set_default_style()
    _, _, classes, _, area = tv.load_classes()
    version = classes.where(classes != 2, 3)
    raw = tv.divider_lines(version, area, sigma=(0.0, 0.0), min_km=0.0)
    saved = [np.asarray(xy) for xy in json.loads(tr.LINES_FILE.read_text())["border"]]
    for name, (a, b) in GAPS.items():
        path = joining_path(raw, a, b)
        direct = ts.length_km(np.array([a, b]))
        print(f"{name}: straight gap {direct:.0f} km; "
              + (f"real class border joins the ends, {ts.length_km(path):.0f} km" if path is not None
                 else "no single class border joins the ends"))
    fig = plt.figure(figsize=(11, 5))
    ax = fig.add_subplot(projection=ccrs.PlateCarree(central_longitude=90))
    ax.set_extent([25, 165, 44, 76], ccrs.PlateCarree())
    colours = ListedColormap(["#CCCCCC", PALETTE[4], PALETTE[0], PALETTE[0]])
    version.plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree(), cmap=colours, vmin=-0.5, vmax=3.5, add_colorbar=False)
    ax.coastlines(linewidth=0.6)
    for xy in raw:
        ax.plot(xy[:, 0], xy[:, 1], color=PALETTE[3], lw=0.8, transform=ccrs.PlateCarree())
    for xy in saved:
        ax.plot(xy[:, 0], xy[:, 1], color="k", lw=1.4, transform=ccrs.PlateCarree())
    for name, (a, b) in GAPS.items():
        ax.plot([a[0], b[0]], [a[1], b[1]], "o", color="k", ms=3, transform=ccrs.PlateCarree())
        ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 1, name, fontsize=8, transform=ccrs.PlateCarree())
    ax.set_title("Grey: small gain · orange: broadleaf replaces needleleaf · teal: other tree gain\n"
                 "Black: saved border · red: unfiltered class border", fontsize=9)
    fig.savefig(tv.OUT / "russia_gaps.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
