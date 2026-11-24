"""Style test: border on the monoterpene maps with the yellow class on either side.

Yellow = "broadleaf gains most" (class 2 of test_vegetation_outlines.py, broadleaf gain larger than
needleleaf gain, needleleaf not clearly falling). Line style = option B of test_vegetation_border_styles.py.
Writes into sandbox/test_vegetation_outlines_outputs/ only (not paper output).
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "src"), str(HERE)]

import matplotlib.pyplot as plt
import numpy as np

import test_vegetation_border_styles as ts
import test_vegetation_bvoc as tb
import test_vegetation_outlines as tv
from boreal_forest_expansion.plotting import forcing_maps as fm
from boreal_forest_expansion.plotting.style import set_default_style

KOLA = (30.0, 50.0, 66.0, 71.0)  # lon0, lon1, lat0, lat1: the Norway-Siberia gap


def in_kola(point):
    return KOLA[0] <= point[0] <= KOLA[1] and KOLA[2] <= point[1] <= KOLA[3]


def border_for(classes, area, ax):
    """Border with the user's deletions, and the Kola pieces joined in order of longitude."""
    lines = ts.clip_marked(tv.divider_lines(classes, area, sigma=(0.0, 0.0), min_km=ts.MIN_PIECE_KM), ax)
    short = [xy for xy in tv.divider_lines(classes, area, sigma=(0.0, 0.0), min_km=0.0)
             if ts.length_km(xy) < ts.MIN_PIECE_KM and not np.allclose(xy[0], xy[-1])
             and in_kola(xy[0]) and in_kola(xy[-1])]
    lines = lines + short
    ends = sorted((tuple(p) for xy in lines for p in (xy[0], xy[-1]) if in_kola(p)), key=lambda p: p[0])
    print("Kola line ends (lon, lat):", [(round(float(x), 1), round(float(y), 1)) for x, y in ends])
    links = [np.array([ends[k], ends[k + 1]]) for k in range(0, len(ends) - 1, 2)]
    print(f"Kola links: {len(links)}, {sum(ts.length_km(x) for x in links):.0f} km; "
          f"border total {sum(ts.length_km(x) for x in lines + links):.0f} km")
    return lines + links


def main():
    set_default_style()
    _, _, classes, modified, area = tv.load_classes()
    print("yellow cells:", int((classes == 2).sum()))
    versions = [("Yellow cells in broadleaf area", classes),
                ("Yellow cells in needleleaf area", classes.where(classes != 2, 3))]
    panel = next(p for p in fm.CONTEXT_PANELS if p.key == "sfmterp")
    fig, axes = tb.emission_grid([panel, panel])
    for j, (title, version) in enumerate(versions):
        print(title)
        border = border_for(version, area, axes[0, j])
        axes[0, j].set_title(title, fontsize=10, fontweight="semibold")
        for ax in axes[:, j]:
            ts.draw(ax, border, modified, ts.OPTIONS[1])
    fig.savefig(tv.OUT / "border_yellow_versions_monoterpene.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
