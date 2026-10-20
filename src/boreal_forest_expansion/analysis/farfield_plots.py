"""Figures for the D1 far-field check.

  plot_contributions  - bars: contribution to the global-mean Delta F of the modified
                        cells (signal) vs the far-field regions (artifact), per term
  plot_maps           - global maps of the time-mean Delta, FDR stippling
  plot_yearly         - year-by-year far-field means (consistency, drift)
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

from .ghan import COMPONENT_LABELS, COMPONENTS

try:
    import cartopy.crs as ccrs
    HAS_CARTOPY = True
except ImportError:  # plain lat-lon axes instead
    HAS_CARTOPY = False

# Categorical slots 1-4 of the validated reference palette (fixed order, colour follows
# the region, never its rank). Text stays in neutral inks.
REGION_STYLE = {
    "modified_cells": {"color": "#2a78d6", "label": "modified cells (LCC signal)"},
    "tropics": {"color": "#eb6834", "label": "30S-30N (far field)"},
    "SH_extratropics": {"color": "#1baf7a", "label": "90S-30S (far field)"},
    "NH_45_90_rest": {"color": "#6250d6", "label": "unmodified cells >45N (near field)"},
}
PERIOD_STYLE = {"PD": {"color": "#2a78d6"}, "FUT": {"color": "#eb6834"}}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
BAND_LABEL = {"SW": "shortwave", "LW": "longwave", "net": "net (SW + LW)"}


def _style(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.axhline(0, color=INK2, lw=0.8)


def plot_contributions(table: pd.DataFrame, regions=("modified_cells", "tropics", "SH_extratropics"),
                       periods=("PD", "FUT"), bands=("SW", "LW", "net")) -> plt.Figure:
    """Contribution to the global mean (regional mean x area fraction), 95% intervals.

    Same y-scale within a row so PD and FUT can be compared directly. Expects one
    contrast per period in `table`.
    """
    fig, axes = plt.subplots(len(bands), len(periods), figsize=(4.2 * len(periods), 2.6 * len(bands)),
                             sharey="row", squeeze=False, constrained_layout=True)
    x = np.arange(len(COMPONENTS))
    width = 0.8 / len(regions)
    for i, band in enumerate(bands):
        for j, period in enumerate(periods):
            ax = axes[i, j]
            sub = table[(table.period == period) & (table.band == band)]
            if sub.contrast.nunique() > 1:
                raise ValueError(f"{period}: several contrasts {sorted(sub.contrast.unique())}; plot them separately")
            for k, r in enumerate(regions):
                rs = sub[sub.region == r].set_index("component").reindex(COMPONENTS)
                xs = x - 0.4 + width * (k + 0.5)
                ax.bar(xs, rs["contrib"], width * 0.9, color=REGION_STYLE[r]["color"],
                       label=REGION_STYLE[r]["label"], zorder=2)
                err = np.vstack([rs["contrib"] - rs["contrib_lo"], rs["contrib_hi"] - rs["contrib"]])
                ax.errorbar(xs, rs["contrib"], yerr=err, fmt="none", ecolor=INK2, elinewidth=0.9,
                            capsize=2, zorder=3)
            _style(ax)
            ax.set_xticks(x, [COMPONENT_LABELS[c] for c in COMPONENTS], fontsize=8, color=INK)
            if i == 0:
                label = sub["contrast"].iloc[0] if len(sub) else period
                ax.set_title(f"{period}: {label}", fontsize=10, color=INK)
            if j == 0:
                ax.set_ylabel(f"{BAND_LABEL[band]}\nW m$^{{-2}}$ of global mean", fontsize=8, color=INK2)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside upper center", ncol=len(regions), frameon=False, fontsize=8)
    fig.suptitle("Contribution to the global-mean $\\Delta$F, signal vs far field "
                 "(bars: mean, whiskers: 95% interval over years)", fontsize=9, color=INK2, y=-0.02)
    return fig


_COAST_OK = None


def _coastlines_available() -> bool:
    """Natural Earth coastlines are downloaded on first use; offline nodes cannot.
    Checked once; without them the maps are drawn without coastlines."""
    global _COAST_OK
    if _COAST_OK is None:
        try:
            import cartopy.io.shapereader as shpreader
            shpreader.natural_earth(resolution="110m", category="physical", name="coastline")
            _COAST_OK = True
        except Exception:
            _COAST_OK = False
    return _COAST_OK


def _map_axes(fig, nrows, ncols):
    axes = np.empty((nrows, ncols), dtype=object)
    for i in range(nrows):
        for j in range(ncols):
            kw = {"projection": ccrs.Robinson()} if HAS_CARTOPY else {}
            axes[i, j] = fig.add_subplot(nrows, ncols, i * ncols + j + 1, **kw)
    return axes


def plot_maps(means: dict[str, xr.Dataset], sigs: dict[str, xr.Dataset], terms: list[str],
              modified: xr.DataArray | None = None, vmax_quantile: float = 0.98) -> plt.Figure:
    """Rows = terms, columns = contrasts. Diverging colour scale centred on 0, shared per row.

    The colour range is set from cells OUTSIDE the modified region (the far field is
    what D1 is about); the stronger local signal saturates (arrow ends of the colour bar).
    Dots: FDR-significant cells (alpha 0.10, global test; by construction up to ~10% of
    the dots can be false discoveries). Dashed lines: 30S and 30N. Black contour:
    modified cells.
    """
    names = list(means)
    fig = plt.figure(figsize=(4.6 * len(names) + 0.8, 2.5 * len(terms)), constrained_layout=True)
    axes = _map_axes(fig, len(terms), len(names))
    tr = {"transform": ccrs.PlateCarree()} if HAS_CARTOPY else {}
    outside = ~modified.values.astype(bool) if modified is not None else None
    for i, term in enumerate(terms):
        vals = np.concatenate([
            np.abs(means[n][term].values[outside] if outside is not None else means[n][term].values).ravel()
            for n in names])
        vmax = float(np.nanquantile(vals, vmax_quantile)) or 1e-3
        norm = TwoSlopeNorm(vcenter=0.0, vmin=-vmax, vmax=vmax)
        for j, n in enumerate(names):
            ax = axes[i, j]
            da = means[n][term]
            lon = da["lon"].values
            # close the seam at the dateline for a continuous map
            da_c = xr.concat([da, da.isel(lon=0).assign_coords(lon=lon[0] + 360)], dim="lon")
            m = ax.pcolormesh(da_c["lon"], da_c["lat"], da_c, cmap="RdBu_r", norm=norm, shading="nearest", **tr)
            sig = sigs[n][term]
            yy, xx = np.nonzero(sig.values)
            if yy.size:
                ax.scatter(lon[xx], da["lat"].values[yy], s=0.6, c=INK, linewidths=0, **tr)
            for lat0 in (-30, 30):
                ax.plot([-180, 180], [lat0, lat0], ls="--", lw=0.6, color=INK2, **tr)
            if modified is not None:
                ax.contour(modified["lon"], modified["lat"], modified.astype(float), levels=[0.5],
                           colors=INK, linewidths=0.6, **tr)
            if HAS_CARTOPY:
                if _coastlines_available():
                    ax.coastlines(lw=0.3, color=INK2)
                ax.set_global()
            if i == 0:
                ax.set_title(n, fontsize=10, color=INK)
        cb = fig.colorbar(m, ax=list(axes[i, :]), shrink=0.85, pad=0.01, extend="both")
        cb.set_label(f"$\\Delta$ {term}\nW m$^{{-2}}$", fontsize=8, color=INK2)
        cb.ax.tick_params(labelsize=7, colors=INK2)
    return fig


def plot_yearly(diffs: dict[str, xr.Dataset], weights: xr.DataArray, mask: xr.DataArray,
                terms=("total_net", "cloud_SW", "clear_SW", "clear_LW"), region_label="30S-30N",
                periods: dict[str, str] | None = None) -> plt.Figure:
    """Year-by-year regional means of the contrast. Shaded band: 95% interval of the mean."""
    from .regions import regional_mean
    from .stats import paired_summary

    fig, axes = plt.subplots(1, len(terms), figsize=(3.2 * len(terms), 2.6), constrained_layout=True,
                             squeeze=False)
    for ax, term in zip(axes[0], terms):
        for name, diff in diffs.items():
            period = (periods or {}).get(name, diff.attrs.get("period", "PD"))
            col = PERIOD_STYLE.get(period, {"color": INK2})["color"]
            s = regional_mean(diff[term], weights, mask)
            st = paired_summary(s.values)
            ax.plot(s["year"], s, marker="o", ms=4, lw=2, color=col, label=name)
            ax.axhspan(st["ci_lo"], st["ci_hi"], color=col, alpha=0.12, lw=0)
        _style(ax)
        ax.set_title(f"$\\Delta$ {term}, {region_label}", fontsize=9, color=INK)
        ax.set_xlabel("year", fontsize=8, color=INK2)
    axes[0, 0].set_ylabel("W m$^{-2}$ (regional mean)", fontsize=8, color=INK2)
    axes[0, 0].legend(frameon=False, fontsize=8)
    return fig
