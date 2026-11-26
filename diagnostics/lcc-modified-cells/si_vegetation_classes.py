"""SI figure of the vegetation regions (user 2026-11-25), draft Supplementary Sect. S1.

(a), (b): LCC - CTRL broadleaf deciduous and needleleaf tree cover, as in
sandbox/test_vegetation_outlines_outputs/vegetation_classes.png; (c): the region classes (CLASSES below).
Also prints cell counts and land-area shares per class (the table of Supplementary Sect. S1). Every panel has the solid limit of the perturbed cells and the dashed
broadleaf/needleleaf expansion border (diagnostics/lcc-modified-cells/vegetation_map_lines.json, display only).
Writes region_cells_outputs/si_vegetation_classes.png. The reference figures vegetation_classes.png and
vegetation_classes_with_lines.py/.png stay as they are. Usage: si_vegetation_classes.py [copy-to-folder]
(copied as vegetation_regions_by_class.png)
"""
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parents[1] / "src")]

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

import vegetation_helpers as vh
from boreal_forest_expansion.plotting import palette as pal
from boreal_forest_expansion.plotting.style import set_default_style

OUT = HERE / "region_cells_outputs" / "si_vegetation_classes.png"
CLASSES = [  # value in load_classes, label, colour; framed around needleleaf, map region in brackets (user 2026-11-25)
    (3, "Needleleaf expansion (needleleaf-exp. region)", pal.TEAL),
    (2, "No needleleaf loss, but broadleaf gains (needleleaf-exp. region)", "#9CC3BD"),
    (1, "Needleleaf decrease, replaced by broadleaf (broadleaf-exp. region)", pal.ORANGE),
    (0, "Little tree gain (≤ 1 pp, left out from regional means)", "#CCCCCC"),
]


def print_class_table(classes, area):
    """Cells and share of the modified land area (AREA × LANDFRAC_PFT) per class."""
    c, a = classes.values, area.values
    total = np.nansum(a[c >= 0])
    for value, label, _ in CLASSES:
        s = c == value
        print(f"{label:65s} cells {s.sum():4d}  land area {100 * np.nansum(a[s]) / total:5.1f} %")
    print(f"all modified cells {int((c >= 0).sum())}, land area {total:.3e} (AREA × LANDFRAC_PFT units)")


def main():
    set_default_style()
    d_broad, d_needle, classes, _, area = vh.load_classes()
    print_class_table(classes, area)
    lines = json.loads(vh.LINES_FILE.read_text())
    lines = {k: [np.asarray(xy) for xy in lines[k]] for k in ("border", "modified")}

    fig, axes = plt.subplots(1, 3, figsize=(13, 5.6), subplot_kw={"projection": ccrs.Orthographic(0, 90)})
    for ax, da, title in zip(axes[:2], (d_broad, d_needle),
                             ("(a) Broadleaf deciduous trees", "(b) Needleleaf trees")):
        vh.base_map(ax)
        p = da.plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree(), cmap="RdBu_r", vmin=-30, vmax=30,
                               add_colorbar=False, zorder=1)
        ax.coastlines(linewidth=0.4, color="#8C8C8C", zorder=3)
        vh.add_lines(ax, lines)
        ax.set_title(title, fontsize=11, fontweight="semibold")
        cb = fig.colorbar(p, ax=ax, orientation="horizontal", shrink=0.8, pad=0.04, ticks=np.arange(-30, 31, 10))
        cb.set_label("LCC − CTRL tree cover [pp of grid cell]", fontsize=9.5)
        cb.ax.tick_params(labelsize=8.5)

    ax = axes[2]
    c = classes.values
    index = np.full(c.shape, np.nan)
    for k, (value, _, _) in enumerate(CLASSES):
        index[c == value] = k
    vh.base_map(ax)
    ax.pcolormesh(classes["lon"], classes["lat"], np.ma.masked_invalid(index),
                  cmap=ListedColormap([col for _, _, col in CLASSES]),
                  norm=BoundaryNorm(np.arange(-0.5, len(CLASSES)), len(CLASSES)),
                  transform=ccrs.PlateCarree(), shading="nearest", zorder=1)
    ax.coastlines(linewidth=0.4, color="#8C8C8C", zorder=3)
    vh.add_lines(ax, lines)
    ax.set_title("(c) Regions", fontsize=11, fontweight="semibold")
    ax.legend(handles=[Patch(color=col, label=label) for _, label, col in CLASSES],
              loc="upper center", bbox_to_anchor=(0.5, -0.03), ncol=1, frameon=False, fontsize=8.5)

    fig.legend(handles=[Line2D([], [], color="k", lw=vh.MODIFIED_WIDTH, label="Solid line: limit of perturbed cells"),
                        Line2D([], [], color="k", lw=vh.BORDER_WIDTH, ls=vh.BORDER_DASH,
                               label="Dashed line: broadleaf/needleleaf expansion border (drawn for display)")],
               loc="upper center", bbox_to_anchor=(0.36, 0.08), ncol=1, frameon=False, fontsize=8.5)
    fig.savefig(OUT, dpi=250, bbox_inches="tight")
    print("saved", OUT)
    if len(sys.argv) > 1:
        dest = Path(sys.argv[1]) / "vegetation_regions_by_class.png"
        shutil.copyfile(OUT, dest)
        print("copied to", dest)


if __name__ == "__main__":
    main()
