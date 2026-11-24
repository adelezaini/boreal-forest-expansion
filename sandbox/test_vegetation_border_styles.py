"""Style test: vegetation border + modified-cell outline in the background-aerosol contour style.

Both lines are plain black contours of a cell mask (`ax.contour`, as `outline_modified` in
diagnostics/background-aerosol/background_aerosol_lcc_ctrl_pd_fut_online.ipynb).
Writes into sandbox/test_vegetation_outlines_outputs/ only (not paper output).
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "src"), str(HERE)]

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
from cartopy.util import add_cyclic_point

import test_vegetation_bvoc as tb
import test_vegetation_outlines as tv
from boreal_forest_expansion.plotting import forcing_maps as fm
from boreal_forest_expansion.plotting.style import set_default_style

DASH = (0, (3.5, 2.0))
MIN_PIECE_KM = 300.0
MAX_LOOP_KM = 1000.0
OPTIONS = [  # title, vegetation border (style, width), modified cells (style, width)
    ("A  Border dashed, modified solid", (DASH, 0.9), ("-", 0.5)),
    ("B  Border solid, modified dashed", ("-", 0.9), (DASH, 0.5)),
    ("C  Both solid, border thicker", ("-", 1.0), ("-", 0.5)),
]


def length_km(xy):
    dx = np.diff(xy[:, 0]) * np.cos(np.deg2rad(0.5 * (xy[:-1, 1] + xy[1:, 1])))
    return 111.2 * np.hypot(dx, np.diff(xy[:, 1])).sum()


def clip_marked(lines, ax):
    """Remove the parts of the border inside the three boxes the user deleted."""
    left, top, right, bottom = tb.MAP_PIXELS
    boxes = [((x0 - left) / (right - left), (bottom - y1) / (bottom - top),
              (x1 - left) / (right - left), (bottom - y0) / (bottom - top)) for x0, y0, x1, y1 in tb.REMOVE_BOXES]
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    kept = []
    for xy in lines:
        if np.allclose(xy[0], xy[-1]) and length_km(xy) < MAX_LOOP_KM:  # small isolated diamonds
            print(f"dropped closed loop, {length_km(xy):.0f} km, near {xy[:, 1].mean():.0f}°N {xy[:, 0].mean():.0f}°E")
            continue
        p = ax.projection.transform_points(ccrs.PlateCarree(), xy[:, 0], xy[:, 1])
        fx, fy = (p[:, 0] - xlim[0]) / (xlim[1] - xlim[0]), (p[:, 1] - ylim[0]) / (ylim[1] - ylim[0])
        inside = np.any([(fx >= a) & (fx <= c) & (fy >= b) & (fy <= d) for a, b, c, d in boxes], axis=0)
        breaks = np.nonzero(np.diff(inside.astype(int)))[0] + 1
        for run in np.split(np.arange(len(xy)), breaks):
            if not inside[run[0]] and len(run) > 1 and length_km(xy[run]) >= MIN_PIECE_KM:
                kept.append(xy[run])
    print(f"border pieces: {len(lines)} before, {len(kept)} after the deletions")
    return kept


def draw(ax, border, modified, option):
    _, (border_style, border_width), (modified_style, modified_width) = option
    data, lon = add_cyclic_point(modified.astype(float).values, coord=modified["lon"].values)
    ax.contour(lon, modified["lat"].values, data, levels=[0.5], colors="k", linewidths=modified_width,
               linestyles=[modified_style], transform=ccrs.PlateCarree(), zorder=5)
    for xy in border:
        ax.plot(xy[:, 0], xy[:, 1], color="k", lw=border_width, ls=border_style, transform=ccrs.PlateCarree(),
                zorder=6)


def main():
    set_default_style()
    _, _, classes, modified, area = tv.load_classes()
    raw = tv.divider_lines(classes, area, sigma=(0.0, 0.0), min_km=MIN_PIECE_KM)
    border = None
    for key, name in (("sfisop", "isoprene"), ("sfmterp", "monoterpene")):
        panel = next(p for p in fm.CONTEXT_PANELS if p.key == key)
        fig, axes = tb.emission_grid([panel] * len(OPTIONS))
        if border is None:
            border = clip_marked(raw, axes[0, 0])
        for j, option in enumerate(OPTIONS):
            axes[0, j].set_title(option[0], fontsize=10, fontweight="semibold")
            for ax in axes[:, j]:
                draw(ax, border, modified, option)
        fig.savefig(tv.OUT / f"border_styles_{name}.png", dpi=200, bbox_inches="tight")
        plt.close(fig)


if __name__ == "__main__":
    main()
