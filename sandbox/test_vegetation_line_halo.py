"""Style test: semi-transparent white edge under the vegetation border and modified-cell line.

Rows = variables (LCC_FUT - CTRL_FUT), columns = edge options. One figure per line colour.
The edge is one continuous white line under each line, so it does not break at the dashes.
Writes into sandbox/test_vegetation_outlines_outputs/ only (not paper output).
"""
import sys
from dataclasses import replace
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "src"), str(HERE)]

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import xarray as xr

import test_vegetation_final_lines as tf
import test_vegetation_line_colours as tc
import test_vegetation_modified_edges as tm
import test_vegetation_outlines as tv
from boreal_forest_expansion.plotting import forcing_maps as fm
from boreal_forest_expansion.plotting.style import set_default_style

COLOURS = {"black": "#000000", "petroleum": "#0F3D4C"}
EDGES = [("No white edge", 0.0), ("White edge, 70 % transparent", 0.3), ("White edge, 30 % transparent", 0.7)]
EDGE_EXTRA = 1.0  # total extra width of the white line, points
VARIABLES = [(fm.CONTEXT_PANELS, "sfmterp"), (fm.SNOW_ALBEDO_PANELS, "albedo_mam"), (fm.SNOW_ALBEDO_PANELS, "tlai")]
PAIRS = {"case1": "LCC_FUT", "case2": "CTRL_FUT"}


def draw_line(ax, xy, colour, width, alpha, **style):
    if alpha > 0:
        ax.plot(xy[:, 0], xy[:, 1], color="white", alpha=alpha, lw=width + EDGE_EXTRA, solid_capstyle="round",
                solid_joinstyle="round", transform=ccrs.PlateCarree(), zorder=4.5)
    ax.plot(xy[:, 0], xy[:, 1], color=colour, lw=width, transform=ccrs.PlateCarree(), zorder=6, **style)


def main():
    set_default_style()
    _, _, classes, modified, area = tv.load_classes()
    version = classes.where(classes != 2, 3)
    with xr.open_dataset(tv.LCC_SURF, decode_times=False) as s:
        landfrac = s["LANDFRAC_PFT"].load().values
    full, lon_c = tm.modified_contour(modified)
    edges = tm.land_edges(full, modified, landfrac > tf.LAND_LIMIT, lon_c)
    panels = [replace(next(p for p in group if p.key == key), case1_role="case1", case2_role="case2")
              for group, key in VARIABLES]
    data = [tc.read(panel, PAIRS) for panel in panels]
    border = None
    for colour_name, colour in COLOURS.items():
        fig, axes = fm.map_grid(len(panels), len(EDGES), titles_every_row=True)
        for i, (panel, d) in enumerate(zip(panels, data)):
            vmax = fm.symmetric_vmax(d.mean("year").where(d["lat"] >= 45.0))
            for j, (name, alpha) in enumerate(EDGES):
                ax = axes[i, j]
                fm._plot_panel(ax, panel, PAIRS, tv.START, tv.END, 45.0, 45.0, True, tc.FDR_ALPHA, vmax=vmax, d=d)
                ax.set_title(f"{name}\n{panel.title}" if i == 0 else panel.title, fontsize=8.5, fontweight="semibold")
                if border is None:
                    border = tf.final_border(version, area, ax)
                    edges = tf.trim_modified(edges, ax)
                for xy in edges:
                    draw_line(ax, xy, colour, tm.MODIFIED_WIDTH, alpha)
                for xy in border:
                    draw_line(ax, xy, colour, tm.BORDER_WIDTH, alpha, ls=tm.BORDER_DASH)
        fig.suptitle(f"White edge test, {colour_name} lines: LCC_FUT − CTRL_FUT, {tv.START}–{tv.END}", fontsize=12, y=1.0)
        fig.savefig(tv.OUT / f"line_halo_{colour_name}.png", dpi=200, bbox_inches="tight")
        plt.close(fig)


if __name__ == "__main__":
    main()
