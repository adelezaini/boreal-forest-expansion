"""Style test: colours of the vegetation border and modified-cell line on several variables.

Rows = variables, columns = line colours. One figure per contrast (PD and FUT).
Writes into sandbox/test_vegetation_outlines_outputs/ only (not paper output).
"""
import sys
import time
from dataclasses import replace
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "src"), str(HERE)]

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import xarray as xr

import test_vegetation_final_lines as tf
import test_vegetation_modified_edges as tm
import test_vegetation_outlines as tv
from boreal_forest_expansion.plotting import forcing_maps as fm
from boreal_forest_expansion.plotting.style import set_default_style

COLOURS = [("Black", "#000000"), ("Dark petroleum", "#0F3D4C"), ("Dark grey", "#4A4A4A")]
CONTRASTS = {"PD": ("LCC_PD", "CTRL_PD"), "FUT": ("LCC_FUT", "CTRL_FUT")}
VARIABLES = [(fm.forcing_panels("NET"), "total"), (fm.SURFACE_ENERGY_PANELS, "trefht"),
             (fm.SNOW_ALBEDO_PANELS, "albedo_mam"), (fm.SNOW_ALBEDO_PANELS, "tlai"),
             (fm.CONTEXT_PANELS, "soa_tot"), (fm.CONTEXT_PANELS, "lwp")]
FDR_ALPHA = 0.10  # default of make_contrast_grid_figure


def read(panel, pairs):
    for attempt in range(1, 9):  # NIRD reads fail intermittently with "HDF error"
        try:
            return fm.panel_difference(panel, pairs, tv.START, tv.END).load()
        except (OSError, RuntimeError) as err:
            print(f"{panel.key}: read attempt {attempt} failed: {err}", flush=True)
            if attempt == 8:
                raise
            time.sleep(10 * attempt)


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
    border = None
    for period, (case1, case2) in CONTRASTS.items():
        pairs = {"case1": case1, "case2": case2}
        fig, axes = fm.map_grid(len(panels), len(COLOURS), titles_every_row=True)
        for i, panel in enumerate(panels):
            d = read(panel, pairs)
            vmax = fm.symmetric_vmax(d.mean("year").where(d["lat"] >= 45.0))
            for j, (name, colour) in enumerate(COLOURS):
                ax = axes[i, j]
                fm._plot_panel(ax, panel, pairs, tv.START, tv.END, 45.0, 45.0, True, FDR_ALPHA, vmax=vmax, d=d)
                ax.set_title(f"{name}\n{panel.title}" if i == 0 else panel.title, fontsize=8.5, fontweight="semibold")
                if border is None:
                    border = tf.final_border(version, area, ax)
                    edges = tf.trim_modified(edges, ax)
                for xy in edges:
                    ax.plot(xy[:, 0], xy[:, 1], color=colour, lw=tm.MODIFIED_WIDTH,
                            transform=ccrs.PlateCarree(), zorder=5)
                for xy in border:
                    ax.plot(xy[:, 0], xy[:, 1], color=colour, lw=tm.BORDER_WIDTH, ls=tm.BORDER_DASH,
                            transform=ccrs.PlateCarree(), zorder=6)
            print(f"{period} {panel.key} done", flush=True)
        fig.suptitle(f"Line colours: {case1} − {case2}, {tv.START}–{tv.END}", fontsize=13, y=1.0)
        fig.savefig(tv.OUT / f"line_colours_{period}.png", dpi=170, bbox_inches="tight")
        plt.close(fig)


if __name__ == "__main__":
    main()
