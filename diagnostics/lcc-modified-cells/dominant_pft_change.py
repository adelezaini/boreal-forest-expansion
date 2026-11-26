"""Dominant natural-vegetation PFT in CTRL and LCC surface data, and where it changes (user 2026-11-25).

Dominant = largest PCT_NAT_PFT (share of the natural-vegetation land unit), PFTs grouped in 6 types.
Writes region_cells_outputs/dominant_pft_change.png and prints the CTRL -> LCC transition table of the modified cells.
Usage: dominant_pft_change.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parents[1] / "src")]

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

import vegetation_helpers as vh
from boreal_forest_expansion.plotting import forcing_maps as fm
from boreal_forest_expansion.plotting import palette as pal
from boreal_forest_expansion.plotting.style import set_default_style

OUT = HERE / "region_cells_outputs" / "dominant_pft_change.png"
TYPES = [  # label, CLM natural PFTs, colour (project palette, no gold: no total here)
    ("Needleleaf evergreen trees", [1, 2], pal.NAVY),
    ("Needleleaf deciduous trees", [3], pal.TEAL),
    ("Broadleaf deciduous trees", [6, 7, 8], pal.ORANGE),
    ("Shrubs", [9, 10, 11], pal.PLUM),
    ("Grasses", [12, 13, 14], pal.RED),
    ("Bare ground", [0], "#8C8C8C"),   # broadleaf evergreen (PFTs 4-5) never dominant >= 45N
]
SAME = "#E6E6E6"   # modified cell, same dominant type


def dominant_type(pct, natveg):
    """Index into TYPES of the dominant PFT; NaN where there is no natural vegetation."""
    pft = pct.argmax("natpft").values
    out = np.full(pft.shape, np.nan)
    for k, (_, pfts, _) in enumerate(TYPES):
        out[np.isin(pft, pfts)] = k
    return np.where(natveg > 0, out, np.nan), pft


def main():
    set_default_style()
    with xr.open_dataset(vh.CTRL_SURF, decode_times=False) as c, xr.open_dataset(vh.LCC_SURF, decode_times=False) as l:
        t_ctrl, p_ctrl = dominant_type(c["PCT_NAT_PFT"], c["PCT_NATVEG"].values)
        t_lcc, p_lcc = dominant_type(l["PCT_NAT_PFT"], l["PCT_NATVEG"].values)
        area = (l["AREA"] * l["LANDFRAC_PFT"]).values
        lat, lon = l["LATIXY"].values[:, 0], l["LONGXY"].values[0, :]
    with xr.open_dataset(fm.VEGETATION_REGIONS) as r:
        region = r["region"].values
    modified = region >= 0
    changed = modified & (t_ctrl != t_lcc)
    share = 100 * area[changed].sum() / area[modified].sum()
    print(f"dominant type changes in {changed.sum()} of {modified.sum()} modified cells ({share:.1f} % of their land area)")
    for v, name in [(1, "replacement"), (2, "net tree gain"), (0, "little tree gain")]:
        s = region == v
        print(f"  {name:16s} {int((changed & s).sum()):4d} / {int(s.sum())}")
    names = [t[0] for t in TYPES]
    print(pd.crosstab(pd.Categorical(np.array(names)[t_ctrl[modified].astype(int)], names),
                      pd.Categorical(np.array(names)[t_lcc[modified].astype(int)], names),
                      rownames=["CTRL"], colnames=["LCC"], dropna=False).to_string())
    print("PFT-level CTRL->LCC (changed cells):",
          pd.Series(list(zip(p_ctrl[changed], p_lcc[changed]))).value_counts().to_dict())

    n = len(TYPES)
    cmap = ListedColormap([col for _, _, col in TYPES] + [SAME])
    norm = BoundaryNorm(np.arange(-0.5, n + 1), n + 1)
    lines = json.loads(vh.LINES_FILE.read_text())
    lines = {k: [np.asarray(xy) for xy in lines[k]] for k in ("border", "modified")}
    new = np.where(changed, t_lcc, np.where(modified, n, np.nan))
    panels = [("CTRL", t_ctrl), ("LCC", t_lcc), ("Change: new dominant type", new)]

    fig, axes = plt.subplots(1, 3, figsize=(14, 6.2), subplot_kw={"projection": ccrs.Orthographic(0, 90)})
    for ax, (title, field) in zip(axes, panels):
        vh.base_map(ax)
        ax.pcolormesh(lon, lat, np.ma.masked_invalid(field), cmap=cmap, norm=norm, transform=ccrs.PlateCarree(),
                      shading="nearest", zorder=1)
        ax.coastlines(linewidth=0.4, color="#8C8C8C", zorder=3)
        vh.add_lines(ax, lines)
        ax.set_title(title, fontsize=13, fontweight="semibold")
    axes[2].text(0.5, -0.04, f"dominant type changes in {changed.sum()} of {modified.sum()} modified cells\n"
                 f"({share:.0f} % of their land area)", transform=axes[2].transAxes, ha="center", va="top",
                 fontsize=10.5)
    fig.suptitle("Dominant natural-vegetation PFT (largest PCT_NAT_PFT), CTRL and LCC surface data",
                 fontsize=14, fontweight="bold", y=0.99)
    handles = [Patch(color=col, label=label) for label, _, col in TYPES]
    handles += [Patch(color=SAME, label="Modified cell, same dominant type (right panel)"),
                Line2D([], [], color="k", lw=vh.MODIFIED_WIDTH, label="Solid line: limit of perturbed cells"),
                Line2D([], [], color="k", lw=vh.BORDER_WIDTH, ls=vh.BORDER_DASH,
                       label="Dashed line: replacement / net-tree-gain border")]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=10)
    fig.subplots_adjust(bottom=0.2, top=0.97, wspace=0.04)
    fig.savefig(OUT, dpi=250, bbox_inches="tight")
    print("saved", OUT)


if __name__ == "__main__":
    main()
