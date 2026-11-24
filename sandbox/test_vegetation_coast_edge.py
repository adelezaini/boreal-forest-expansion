"""Style test: white edge under the land-ocean coastline, with the final vegetation lines on top.

Rows = variables (LCC_FUT - CTRL_FUT), columns = coastline edge options.
Writes into sandbox/test_vegetation_outlines_outputs/ only (not paper output).
"""
import json
import sys
from dataclasses import replace
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "src"), str(HERE)]

import matplotlib.pyplot as plt
import numpy as np

import test_vegetation_line_colours as tc
import test_vegetation_line_halo as th
import test_vegetation_outlines as tv
import test_vegetation_real_figures as tr
from boreal_forest_expansion.plotting import forcing_maps as fm
from boreal_forest_expansion.plotting.style import set_default_style

EDGES = [("Coast: no white edge", 0.0), ("Coast: white edge, 70 % transparent", 0.3),
         ("Coast: white edge, 30 % transparent (as the lines)", 0.7)]
COAST_WIDTH = 0.6  # width of the black coastline in the figure functions
COAST_EDGE_ZORDER = 2.9  # above the map colours, under the black coastline and the hatching
VARIABLES = [(fm.CONTEXT_PANELS, "soa_tot"), (fm.forcing_panels("NET"), "total"),
             (fm.SNOW_ALBEDO_PANELS, "tlai"), (fm.SNOW_ALBEDO_PANELS, "albedo_mam")]
PAIRS = {"case1": "LCC_FUT", "case2": "CTRL_FUT"}


def main():
    set_default_style()
    lines = json.loads(tr.LINES_FILE.read_text())
    lines = {k: [np.asarray(xy) for xy in lines[k]] for k in ("border", "modified")}
    panels = [replace(next(p for p in group if p.key == key), case1_role="case1", case2_role="case2")
              for group, key in VARIABLES]
    data = [tc.read(panel, PAIRS) for panel in panels]
    fig, axes = fm.map_grid(len(panels), len(EDGES), titles_every_row=True)
    for i, (panel, d) in enumerate(zip(panels, data)):
        vmax = fm.symmetric_vmax(d.mean("year").where(d["lat"] >= 45.0))
        for j, (name, alpha) in enumerate(EDGES):
            ax = axes[i, j]
            fm._plot_panel(ax, panel, PAIRS, tv.START, tv.END, 45.0, 45.0, True, tc.FDR_ALPHA, vmax=vmax, d=d)
            ax.set_title(f"{name}\n{panel.title}" if i == 0 else panel.title, fontsize=8.5, fontweight="semibold")
            if alpha > 0:
                ax.coastlines(color="white", alpha=alpha, linewidth=COAST_WIDTH + th.EDGE_EXTRA,
                              zorder=COAST_EDGE_ZORDER)
            tr.add_lines(ax, lines)
    fig.suptitle(f"Coastline white edge test: LCC_FUT − CTRL_FUT, {tv.START}–{tv.END}", fontsize=12, y=1.0)
    fig.savefig(tv.OUT / "coast_edge_test.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
