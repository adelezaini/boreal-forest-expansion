"""Layout test: regional means (broadleaf / needleleaf expansion) on the real figures.

Regions = by class (region_cells.py): broadleaf exp. = broadleaf replaces needleleaf; needleleaf exp. = other
tree gain (needleleaf gain + 47 broadleaf-gain cells). Little-gain cells (tree gain <= 1 pp) are in neither.
Numbers = cos-lat mean of the yearly differences over the region, 95 % t-interval (as the 45-90°N mean).

Layouts:
  two_lines  45-90°N mean as now, then one line per region, smaller
  one_line   45-90°N mean as now, then both regions on one line
  side       all three numbers in a block to the right of each map, nothing under the map
Usage: test_region_numbers.py ghan | context [layout ...]   (default all three layouts; output in region_numbers_outputs/)
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SANDBOX = HERE.parent
sys.path[:0] = [str(SANDBOX.parent / "src"), str(SANDBOX)]

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
import xarray as xr

import test_vegetation_outlines as tv
import test_vegetation_real_figures as tr
from boreal_forest_expansion.plotting import forcing_maps as fm
from boreal_forest_expansion.plotting.style import set_default_style

OUT = HERE / "region_numbers_outputs"
LABELS = ("broadleaf exp.", "needleleaf exp.")
REGION_FONTSIZE = 10.5
DEFAULTS = {k: getattr(fm, k) for k in ("CBAR_OFFSET", "UNDER_CBAR", "MAP_COL_GAP")}
LAYOUTS = {  # inches; "subtitle" = what the numbers are
    "two_lines": dict(CBAR_OFFSET=0.92, UNDER_CBAR=1.75),
    "one_line": dict(CBAR_OFFSET=0.68, UNDER_CBAR=1.51, MAP_COL_GAP=1.15),
    "side": dict(CBAR_OFFSET=0.22, UNDER_CBAR=1.05, MAP_COL_GAP=1.75),
}
def subtitle_a(mean_lat_min, years=None):
    """Subtitle option A as edited by the user (2026-11-24): the three numbers under the maps, in their order."""
    region = f"{mean_lat_min:g}–90°N" if mean_lat_min is not None else "global"
    n = f"{years} " if years else ""
    head = rf"$\mathit{{Maps}}$: {years}-year mean · " if years else ""
    return (rf"{head}$\mathit{{Under\ the\ maps}}$: area-weighted mean ± 95 % CI of the {n}yearly means "
            f"over {region}, broadleaf- and needleleaf-expansion cells*")


FOOTNOTE = "*cells with ≤ 1 pp tree gain left out (Supplementary Sect. S1)"
FOOTNOTE_FONTSIZE = 10


def add_footnote_on_save():
    """Put FOOTNOTE under everything else in the figure, left-aligned, just before saving."""
    plain_savefig = Figure.savefig

    def savefig(fig, *args, **kwargs):
        if not any(t.get_text() == FOOTNOTE for t in fig.texts):
            box = fig.get_tightbbox(fig.canvas.get_renderer())  # inches
            W, H = fig.get_size_inches()
            fig.text(box.x0 / W, (box.y0 - 0.12) / H, FOOTNOTE, ha="left", va="top", fontsize=FOOTNOTE_FONTSIZE)
        return plain_savefig(fig, *args, **kwargs)
    Figure.savefig = savefig


def region_masks():
    _, _, classes, _, _ = tv.load_classes()
    return {LABELS[0]: classes == 1, LABELS[1]: (classes == 2) | (classes == 3)}


def add_region_numbers(layout, masks):
    plain = fm._plot_panel

    def panel(ax, *args, **kwargs):
        d = plain(ax, *args, **kwargs)
        texts = []
        for label, mask in masks.items():
            m = mask.assign_coords(lat=d["lat"], lon=d["lon"])  # same grid, checked in region_cells.py
            texts.append((label, fm._format_interval(*fm.regional_mean_interval(d.where(m)))))
        map_h = ax.get_position().height * ax.figure.get_figheight()
        under = [t for t in ax.texts if t.get_position()[1] < 0]  # the 45-90°N mean
        y0 = -0.26 / map_h  # the 45-90°N mean where it is now (0.5 x default CBAR_OFFSET)
        for t in under:
            t.set_y(y0)
        pt = 1 / 72 / map_h  # one point in axes units
        if layout == "two_lines":
            for k, (label, value) in enumerate(texts):
                ax.text(0.5, y0 - (17 + 15 * k) * pt, f"{label}: {value}", transform=ax.transAxes,
                        ha="center", va="center", fontsize=REGION_FONTSIZE)
        elif layout == "one_line":
            ax.text(0.5, y0 - 16 * pt, "  •  ".join(f"{l}: {v}" for l, v in texts), transform=ax.transAxes,
                    ha="center", va="center", fontsize=8.5)
        else:  # side: move the 45-90°N mean into the block
            main = under[0].get_text() if under else ""
            for t in under:
                t.remove()
            lines = [f"45–90°N:\n{main}"] + [f"{l}:\n{v}" for l, v in texts]
            ax.text(1.02, 0.0, "\n".join(lines), transform=ax.transAxes, ha="left", va="bottom",
                    fontsize=REGION_FONTSIZE, linespacing=1.35)
        return d

    fm._plot_panel = panel
    return plain


def main():
    job = sys.argv[1]
    set_default_style()
    OUT.mkdir(exist_ok=True)
    lines = json.loads(tr.LINES_FILE.read_text())
    fm.mean_subtitle = subtitle_a
    add_footnote_on_save()
    tr.wrap_panels({k: [np.asarray(xy) for xy in lines[k]] for k in ("border", "modified")})
    cache, read = {}, fm.yearly_difference  # read each field once for the three layouts

    def cached(*args, **kwargs):
        key = repr((args, sorted(kwargs.items())))
        if key not in cache:
            cache[key] = read(*args, **kwargs)
        return cache[key]
    fm.yearly_difference = cached

    masks = region_masks()
    for layout, values in LAYOUTS.items():
        if len(sys.argv) > 2 and layout not in sys.argv[2:]:
            continue
        for k, v in {**DEFAULTS, **values}.items():
            setattr(fm, k, v)
        plain = add_region_numbers(layout, masks)
        figdir = OUT / layout
        figdir.mkdir(exist_ok=True)
        if job == "ghan":
            fm.make_ghan_contrast_figure(fm.contrast("LCC-CTRL_FUT"), "NET", tr.START, tr.END, figdir=figdir)
        else:
            fm.make_contrast_grid_figure("interactive", fm.CONTEXT_PANELS, "context", start_year=tr.START,
                                         end_year=tr.END, figdir=figdir)
        fm._plot_panel = plain
        plt.close("all")
        print(f"{job} {layout} done", flush=True)


if __name__ == "__main__":
    main()
