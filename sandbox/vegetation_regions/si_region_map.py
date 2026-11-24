"""Supplementary figure: the vegetation regions used for the regional means (by class), with the two map lines.

Writes region_cells_outputs/si_region_classes.png and prints cell counts and land-area shares per class.
Usage: si_region_map.py [copy-to-folder]
"""
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent.parent / "src"), str(HERE.parent)]

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

import test_vegetation_outlines as tv
import test_vegetation_real_figures as tr
from boreal_forest_expansion.plotting import palette as pal
from boreal_forest_expansion.plotting.style import set_default_style

OUT = HERE / "region_cells_outputs" / "si_region_classes.png"
CLASSES = [  # value in load_classes, label, colour
    (1, "Broadleaf expansion (broadleaf replaces needleleaf)", pal.ORANGE),
    (3, "Needleleaf expansion (needleleaf gain)", pal.TEAL),
    (2, "Needleleaf-expansion region: broadleaf gain without replacement", "#9CC3BD"),
    (0, "Little tree gain (≤ 1 pp, left out)", "#CCCCCC"),
]


def main():
    set_default_style()
    _, _, classes, modified, area = tv.load_classes()
    c, a = classes.values, area.values
    total = np.nansum(a[c >= 0])
    for value, label, _ in CLASSES:
        s = c == value
        print(f"{label:65s} cells {s.sum():4d}  land area {100 * np.nansum(a[s]) / total:5.1f} %")
    print(f"all modified cells {int((c >= 0).sum())}, land area {total:.3e} (AREA × LANDFRAC_PFT units)")

    lines = json.loads(tr.LINES_FILE.read_text())
    lines = {k: [np.asarray(xy) for xy in lines[k]] for k in ("border", "modified")}
    order = [v for v, _, _ in CLASSES]
    index = np.full(c.shape, np.nan)
    for k, v in enumerate(order):
        index[c == v] = k
    fig = plt.figure(figsize=(6.2, 7.0))
    ax = fig.add_axes([0.03, 0.2, 0.94, 0.78], projection=ccrs.Orthographic(0, 90))
    tv.base_map(ax)
    ax.pcolormesh(classes["lon"], classes["lat"], np.ma.masked_invalid(index),
                  cmap=ListedColormap([col for _, _, col in CLASSES]), norm=BoundaryNorm(np.arange(-0.5, 4), 4),
                  transform=ccrs.PlateCarree(), shading="nearest", zorder=1)
    ax.coastlines(linewidth=0.4, color="#8C8C8C", zorder=3)
    tr.add_lines(ax, lines)
    handles = [Patch(color=col, label=label) for _, label, col in CLASSES]
    handles += [Line2D([], [], color="k", lw=tr.tm.MODIFIED_WIDTH, label="Solid line: limit of perturbed cells"),
                Line2D([], [], color="k", lw=tr.tm.BORDER_WIDTH, ls=tr.tm.BORDER_DASH,
                       label="Dashed line: broadleaf/needleleaf expansion border (drawn for display)")]
    fig.legend(handles=handles, loc="lower center", ncol=1, frameon=False, fontsize=8.5)
    fig.savefig(OUT, dpi=250, bbox_inches="tight")
    print("saved", OUT)
    if len(sys.argv) > 1:
        dest = Path(sys.argv[1]) / "vegetation_regions_by_class.png"
        shutil.copyfile(OUT, dest)
        print("copied to", dest)


if __name__ == "__main__":
    main()
