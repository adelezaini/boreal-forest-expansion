"""Style test: black lines with a white edge (30 % transparent) on the six line_colours variables.

Rows = variables, columns = LCC_PD - CTRL_PD and LCC_FUT - CTRL_FUT (each panel on its own scale, as line_colours).
Writes into sandbox/test_vegetation_outlines_outputs/ only (not paper output).
"""
import sys
from dataclasses import replace
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "src"), str(HERE)]

import matplotlib.pyplot as plt
import xarray as xr

import test_vegetation_final_lines as tf
import test_vegetation_line_colours as tc
import test_vegetation_line_halo as th
import test_vegetation_modified_edges as tm
import test_vegetation_outlines as tv
from boreal_forest_expansion.plotting import forcing_maps as fm
from boreal_forest_expansion.plotting.style import set_default_style

COLOUR = "#000000"
EDGE_ALPHA = 0.7  # 30 % transparent


def main():
    set_default_style()
    _, _, classes, modified, area = tv.load_classes()
    version = classes.where(classes != 2, 3)
    with xr.open_dataset(tv.LCC_SURF, decode_times=False) as s:
        landfrac = s["LANDFRAC_PFT"].load().values
    full, lon_c = tm.modified_contour(modified)
    edges = tm.land_edges(full, modified, landfrac > tf.LAND_LIMIT, lon_c)
    panels = [replace(next(p for p in group if p.key == key), case1_role="case1", case2_role="case2")
              for group, key in tc.VARIABLES]
    fig, axes = fm.map_grid(len(panels), len(tc.CONTRASTS), titles_every_row=True)
    border = None
    for j, (period, (case1, case2)) in enumerate(tc.CONTRASTS.items()):
        pairs = {"case1": case1, "case2": case2}
        for i, panel in enumerate(panels):
            d = tc.read(panel, pairs)
            vmax = fm.symmetric_vmax(d.mean("year").where(d["lat"] >= 45.0))
            ax = axes[i, j]
            fm._plot_panel(ax, panel, pairs, tv.START, tv.END, 45.0, 45.0, True, tc.FDR_ALPHA, vmax=vmax, d=d)
            ax.set_title(f"{case1} − {case2}\n{panel.title}" if i == 0 else panel.title, fontsize=8.5,
                         fontweight="semibold")
            if border is None:
                border = tf.final_border(version, area, ax)
                edges = tf.trim_modified(edges, ax)
            for xy in edges:
                th.draw_line(ax, xy, COLOUR, tm.MODIFIED_WIDTH, EDGE_ALPHA)
            for xy in border:
                th.draw_line(ax, xy, COLOUR, tm.BORDER_WIDTH, EDGE_ALPHA, ls=tm.BORDER_DASH)
            print(f"{period} {panel.key} done", flush=True)
    fig.suptitle(f"Black lines, white edge 30 % transparent, {tv.START}–{tv.END}", fontsize=12, y=1.0)
    fig.savefig(tv.OUT / "line_style_black_edge30.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
