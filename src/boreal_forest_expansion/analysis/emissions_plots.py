"""Figures for D2 (MEGAN emission budget).

  plot_q1_shares   - share of each compound group in all MEGAN emissions, 3 weightings
  plot_q2_deltas   - Delta E (LCC - CTRL) per group, 3 weightings, 95% intervals
  plot_delta_maps  - maps north of 45 N of the Delta carbon flux: ISOP+MTERP vs all others
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

from . import megan
from .emissions import WEIGHTINGS
from .farfield_plots import GRID, INK, INK2, _coastlines_available, HAS_CARTOPY

if HAS_CARTOPY:
    import cartopy.crs as ccrs

# Same entity -> same colour as in D1 (modified cells blue). Global = neutral.
REGION_COLOR = {"modified_cells": "#2a78d6", "global": "#8a8984", "NH_45_90": "#6250d6", "tropics": "#eb6834"}
CONTRAST_COLORS = ["#2a78d6", "#eb6834", "#1baf7a"]     # fixed order: slots 1-3
GROUP_ORDER = list(megan.GROUPS) + ["ALL OTHERS"]
WEIGHT_TITLE = {"mass": "mass", "carbon": "carbon (total OH demand, b)",
                "koh": "OH reactivity at T_ref (local, b)"}


def _style(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.axvline(0, color=INK2, lw=0.8)


def plot_q1_shares(q1: pd.DataFrame, member: str, regions=("global", "modified_cells")) -> plt.Figure:
    groups = list(megan.GROUPS)
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.4), sharey=True, constrained_layout=True)
    y = np.arange(len(groups))
    h = 0.8 / len(regions)
    for ax, w in zip(axes, WEIGHTINGS):
        sub = q1[(q1.member == member) & (q1.weighting == w)]
        for k, r in enumerate(regions):
            s = sub[sub.region == r].set_index("group").reindex(groups)["share_pct"]
            ys = y - 0.4 + h * (k + 0.5)
            ax.barh(ys, s, h * 0.9, color=REGION_COLOR[r], label=r.replace("_", " "))
            for yy, v in zip(ys, s):
                if np.isfinite(v):
                    ax.text(v + 1, yy, f"{v:.1f}%", va="center", fontsize=7, color=INK2)
        _style(ax)
        ax.set_xlim(0, 115)
        ax.set_title(WEIGHT_TITLE[w], fontsize=9, color=INK)
        ax.set_xlabel("share of all MEGAN emissions (%)", fontsize=8, color=INK2)
    axes[0].set_yticks(y, groups, fontsize=8, color=INK)
    axes[0].invert_yaxis()
    axes[0].legend(frameon=False, fontsize=8, loc="lower right")
    fig.suptitle(f"Q1 - composition of MEGAN emissions in {member}", fontsize=10, color=INK)
    return fig


def plot_q2_deltas(q2: pd.DataFrame, contrasts: list[str], region: str = "global") -> plt.Figure:
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.8), sharey=True, constrained_layout=True)
    y = np.arange(len(GROUP_ORDER))
    h = 0.8 / len(contrasts)
    for ax, w in zip(axes, WEIGHTINGS):
        sub = q2[(q2.region == region) & (q2.weighting == w)]
        for k, cn in enumerate(contrasts):
            s = sub[sub.contrast == cn].set_index("group").reindex(GROUP_ORDER)
            ys = y - 0.4 + h * (k + 0.5)
            ax.barh(ys, s["delta"], h * 0.9, color=CONTRAST_COLORS[k % 3], label=cn)
            err = np.vstack([s["delta"] - s["ci_lo"], s["ci_hi"] - s["delta"]])
            ax.errorbar(s["delta"], ys, xerr=err, fmt="none", ecolor=INK2, elinewidth=0.9, capsize=2)
        _style(ax)
        ax.set_title(WEIGHT_TITLE[w], fontsize=9, color=INK)
        ax.set_xlabel(f"$\\Delta$E ({WEIGHTINGS[w]})", fontsize=8, color=INK2)
    axes[0].set_yticks(y, GROUP_ORDER, fontsize=8, color=INK)
    axes[0].invert_yaxis()
    for ax in axes:
        ax.axhline(len(megan.GROUPS) - 0.5, color=GRID, lw=1)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside upper center", ncol=len(contrasts), frameon=False, fontsize=8)
    fig.suptitle(f"Q2 - change in MEGAN emissions, {region.replace('_', ' ')} "
                 "(bars: mean, whiskers: 95% interval over years)", fontsize=9, color=INK2, y=-0.04)
    return fig


def plot_delta_maps(maps: dict[str, xr.Dataset], modified: xr.DataArray | None = None,
                    lat_min: float = 45, vmax_quantile: float = 0.99) -> plt.Figure:
    names = list(maps)
    cols = ["ISOP+MTERP", "others"]
    fig = plt.figure(figsize=(8.2, 3.6 * len(names)), constrained_layout=True)
    axes = np.empty((len(names), 2), dtype=object)
    for i in range(len(names)):
        for j in range(2):
            kw = {"projection": ccrs.NorthPolarStereo()} if HAS_CARTOPY else {}
            axes[i, j] = fig.add_subplot(len(names), 2, 2 * i + j + 1, **kw)
    tr = {"transform": ccrs.PlateCarree()} if HAS_CARTOPY else {}
    # One colour scale PER PANEL: the others are much smaller than ISOP+MTERP, and the
    # LCC + climate-change contrast is much larger than the LCC-only ones.
    for j, col in enumerate(cols):
        for i, n in enumerate(names):
            vals = np.abs(maps[n][col].sel(lat=slice(lat_min, 90)).values).ravel()
            vmax = float(np.nanquantile(vals, vmax_quantile)) or 1e-6
            norm = TwoSlopeNorm(vcenter=0, vmin=-vmax, vmax=vmax)
            ax = axes[i, j]
            da = maps[n][col].sel(lat=slice(lat_min - 2, 90))
            lon = da["lon"].values
            da_c = xr.concat([da, da.isel(lon=0).assign_coords(lon=lon[0] + 360)], dim="lon")
            m = ax.pcolormesh(da_c["lon"], da_c["lat"], da_c, cmap="RdBu_r", norm=norm, shading="nearest", **tr)
            if modified is not None:
                md = modified.sel(lat=slice(lat_min - 2, 90)).astype(float)
                ax.contour(md["lon"], md["lat"], md, levels=[0.5], colors=INK, linewidths=0.5, **tr)
            if HAS_CARTOPY:
                ax.set_extent([-180, 180, lat_min, 90], ccrs.PlateCarree())
                if _coastlines_available():
                    ax.coastlines(lw=0.3, color=INK2)
            ax.set_title(f"{n}: $\\Delta$E carbon, {col}", fontsize=9, color=INK)
            cb = fig.colorbar(m, ax=ax, orientation="vertical", shrink=0.8, pad=0.02, extend="both")
            cb.set_label("g C m$^{-2}$ yr$^{-1}$", fontsize=7, color=INK2)
            cb.ax.tick_params(labelsize=7, colors=INK2)
    fig.suptitle("$\\Delta$E carbon (grid-cell mean). Note: each panel has its own colour scale",
                 fontsize=9, color=INK2)
    return fig
