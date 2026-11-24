"""Draw the two vegetation lines on the real figure functions, with all output in the sandbox.

The lines are read from one fixed file (vegetation_map_lines.json, written by `build`). The plotting
functions in src/ are not edited: their panel functions are wrapped here, for this process only.

Usage: test_vegetation_real_figures.py build | context | snow | ghan | megan
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
import xarray as xr

import test_vegetation_border_styles as ts
import test_vegetation_final_lines as tf
import test_vegetation_line_halo as th
import test_vegetation_modified_edges as tm
import test_vegetation_outlines as tv
from boreal_forest_expansion.plotting import forcing_maps as fm
from boreal_forest_expansion.plotting import megan_maps as mm
from boreal_forest_expansion.plotting.style import set_default_style

LINES_FILE = tv.OUT / "vegetation_map_lines.json"
FIG_DIR = tv.OUT / "real_figures"
COLOUR, EDGE_ALPHA = "#000000", 0.7  # white edge 30 % transparent
MAX_SQUARE_KM = 1000.0
LINES_LEGEND = "solid line: limit of perturbed vegetation cells • dashed line: broadleaf/needleleaf expansion border"
START, END = 2001, 2025


def build():
    _, _, classes, modified, area = tv.load_classes()
    version = classes.where(classes != 2, 3)
    with xr.open_dataset(tv.LCC_SURF, decode_times=False) as s:
        landfrac = s["LANDFRAC_PFT"].load().values
    full, lon_c = tm.modified_contour(modified)
    edges = tm.land_edges(full, modified, landfrac > tf.LAND_LIMIT, lon_c)
    fig = plt.figure(figsize=(3, 3))
    ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.Orthographic(0, 90))
    tv.cut_extent_Orthographic(ax, lat=45.0)
    border = tf.final_border(version, area, ax)
    edges = tf.trim_modified(edges, ax)
    plt.close(fig)
    squares = [xy for xy in edges if np.allclose(xy[0], xy[-1]) and ts.length_km(xy) < MAX_SQUARE_KM]
    for xy in squares:
        print(f"removed square: {ts.length_km(xy):.0f} km near {xy[:, 1].mean():.1f}°N {xy[:, 0].mean():.1f}°E")
    edges = [xy for xy in edges if not any(xy is square for square in squares)]
    print(f"saved: border {len(border)} pieces, {sum(map(ts.length_km, border)):.0f} km; "
          f"modified {len(edges)} pieces, {sum(map(ts.length_km, edges)):.0f} km")
    LINES_FILE.write_text(json.dumps({
        "description": "Map lines in lon/lat degrees. border = broadleaf-replaces-needleleaf vs other tree gain, "
                       "edited by hand; modified = limit of modified cells against mostly-land cells, edited by hand.",
        "border": [np.round(xy, 6).tolist() for xy in border],
        "modified": [np.round(xy, 6).tolist() for xy in edges]}))


def add_lines(ax, lines):
    for xy in lines["modified"]:
        th.draw_line(ax, xy, COLOUR, tm.MODIFIED_WIDTH, EDGE_ALPHA)
    for xy in lines["border"]:
        th.draw_line(ax, xy, COLOUR, tm.BORDER_WIDTH, EDGE_ALPHA, ls=tm.BORDER_DASH)


def wrap_panels(lines):
    plain_panel, megan_panel = fm.plot_single_boreal_panel, mm._panel

    def forcing_panel(*args, **kwargs):
        out = plain_panel(*args, **kwargs)
        add_lines(kwargs["ax"] if "ax" in kwargs else args[0], lines)
        return out

    def panel(ax, *args, **kwargs):
        kwargs["modified"] = None  # replaces the old dashed outline of all modified cells
        out = megan_panel(ax, *args, **kwargs)
        add_lines(ax, lines)
        return out

    plain_suptitle = fm.add_suptitle

    def suptitle(fig, title, mean_lat_min, fontsize=14, y=None, subtitle=None, years=None):
        text = (subtitle or fm.mean_subtitle(mean_lat_min, years)).replace(" · dashed line: modified cells", "")
        if y is not None:  # room for the extra subtitle line above the panel titles
            y += 1.6 * 0.8 * fontsize / 72 / fig.get_figheight()
        plain_suptitle(fig, title, mean_lat_min, fontsize=fontsize, y=y, subtitle=f"{text}\n{LINES_LEGEND}", years=years)

    plain_difference = fm.yearly_difference

    def robust_difference(*args, **kwargs):
        """Read one variable now, retrying it alone when NIRD gives an I/O error."""
        for attempt in range(1, 13):
            try:
                return plain_difference(*args, **kwargs).load()
            except FileNotFoundError:
                raise  # a really missing file is handled by the figure function
            except (OSError, RuntimeError) as err:
                print(f"read retry {attempt}, {args[:4]}: {err}", flush=True)
                if attempt == 12:
                    raise
                time.sleep(5 * attempt)

    fm.yearly_difference = robust_difference
    fm.plot_single_boreal_panel, mm._panel, fm.add_suptitle = forcing_panel, panel, suptitle


def run(job):
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    mm.MEGAN_FIG_DIR = FIG_DIR
    if job == "context":
        fm.make_contrast_grid_figure("interactive", fm.CONTEXT_PANELS, "context", start_year=START, end_year=END,
                                     figdir=FIG_DIR)
    elif job == "snow":
        fm.make_contrast_grid_figure("interactive", fm.SNOW_ALBEDO_PANELS, "snow_albedo", start_year=START,
                                     end_year=END, figdir=FIG_DIR)
    elif job == "ghan":
        fm.make_ghan_contrast_figure(fm.contrast("LCC-CTRL_FUT"), "NET", START, END, figdir=FIG_DIR)
    elif job == "megan":
        mm.make_attribution_maps("MTERP", "PD", "JJA")
    else:
        raise ValueError(job)


def main():
    job = sys.argv[1]
    set_default_style()
    if job == "build":
        build()
        return
    lines = json.loads(LINES_FILE.read_text())
    lines = {k: [np.asarray(xy) for xy in lines[k]] for k in ("border", "modified")}
    wrap_panels(lines)
    for attempt in range(1, 7):  # NIRD reads fail intermittently with "HDF error"
        try:
            run(job)
            print(f"{job} done", flush=True)
            return
        except (OSError, RuntimeError) as err:
            print(f"{job}: attempt {attempt} failed: {err}", flush=True)
            plt.close("all")
            if attempt == 6:
                raise
            time.sleep(15 * attempt)


if __name__ == "__main__":
    main()
