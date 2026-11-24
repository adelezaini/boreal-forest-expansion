"""Style test: mark where broadleaf or needleleaf trees gain in the LCC-modified cells.

Writes into sandbox/test_vegetation_outlines_outputs/ only (not paper output).

Changes are LCC - CTRL surfdata, PCT_NAT_PFT x PCT_NATVEG / 100 (percentage points of the grid cell).
Needleleaf = CLM PFTs 1, 2, 3; broadleaf deciduous trees = PFTs 6, 7, 8.
Each modified cell takes the group with the larger gain, if that gain exceeds THRESHOLD.
"""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import cartopy.crs as ccrs
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from cartopy.util import add_cyclic_point
from scipy.ndimage import gaussian_filter
from shapely.geometry import box
from shapely.ops import unary_union

from boreal_forest_expansion.analysis.regions import load_modified_cells
from boreal_forest_expansion.plotting import forcing_maps as fm
from boreal_forest_expansion.plotting import palette as pal
from boreal_forest_expansion.plotting.common import ax_map_properties, cut_extent_Orthographic
from boreal_forest_expansion.plotting.style import set_default_style

OUT = Path(__file__).resolve().parent / "test_vegetation_outlines_outputs"
SURF = Path("/cluster/shared/noresm/inputdata/lnd/clm2/surfdata_map")
CTRL_SURF = SURF / "release-clm5.0.18" / "surfdata_1.9x2.5_hist_78pfts_CMIP6_simyr2000_c190304.nc"
LCC_SURF = SURF / "surfdata_1.9x2.5_SSP5-8.5_2100_78pfts_LPJGUESS.nc"
NEEDLELEAF, BROADLEAF = [1, 2, 3], [6, 7, 8]
THRESHOLD = 1.0  # percentage points of the grid cell
START, END = 2001, 2025


def load_classes():
    """Woody changes and class map: 0 small, 1 broadleaf replaces, 2 broadleaf gains, 3 needleleaf gains."""
    with xr.open_dataset(CTRL_SURF, decode_times=False) as c, xr.open_dataset(LCC_SURF, decode_times=False) as l:
        change = ((l["PCT_NAT_PFT"] - c["PCT_NAT_PFT"]) * l["PCT_NATVEG"] / 100).load()
        area = (l["AREA"] * l["LANDFRAC_PFT"]).load()
        lat, lon = l["LATIXY"].values[:, 0], l["LONGXY"].values[0, :]
    coords = {"lat": lat, "lon": lon}
    grid = xr.Dataset(coords=coords)
    modified = load_modified_cells(fm.MODIFIED_CELLS, grid)
    wrap = lambda a: xr.DataArray(a, coords=coords, dims=("lat", "lon"))
    d_needle = wrap(change.isel(natpft=NEEDLELEAF).sum("natpft").values)
    d_broad = wrap(change.isel(natpft=BROADLEAF).sum("natpft").values)
    area = wrap(area.values)

    broad_wins = (d_broad > THRESHOLD) & (d_broad > d_needle) & modified
    needle_wins = (d_needle > THRESHOLD) & (d_needle >= d_broad) & modified
    replaces = broad_wins & (d_needle < -THRESHOLD)
    classes = xr.zeros_like(d_needle, dtype=int)
    classes = classes.where(~broad_wins, 2).where(~replaces, 1).where(~needle_wins, 3)
    return d_broad.where(modified), d_needle.where(modified), classes.where(modified), modified, area


def outline_lines(mask: xr.DataArray):
    """Outer boundaries of the marked grid cells as lon/lat lines, without the artificial seam."""
    lat, lon = mask["lat"].values, mask["lon"].values
    dlon = np.diff(lon).mean()
    lat_edges = np.r_[lat[0], 0.5 * (lat[:-1] + lat[1:]), lat[-1]]
    lon_edges = lon[0] - dlon / 2 + dlon * np.arange(lon.size + 1)  # neighbours share exact edges
    boxes = [box(lon_edges[j], lat_edges[i], lon_edges[j + 1], lat_edges[i + 1])
             for i, j in zip(*np.nonzero(mask.values))]
    merged = unary_union(boxes)
    polygons = getattr(merged, "geoms", [merged])
    west, east = lon_edges[0], lon_edges[-1]
    lines = []
    for polygon in polygons:
        for ring in [polygon.exterior, *polygon.interiors]:
            xy = np.asarray(ring.coords)
            on_seam = (np.isclose(xy[:-1, 0], west) & np.isclose(xy[1:, 0], west)) | (
                np.isclose(xy[:-1, 0], east) & np.isclose(xy[1:, 0], east))
            start = 0
            for k in np.nonzero(on_seam)[0]:
                if k >= start:
                    lines.append(xy[start:k + 1])
                start = k + 1
            lines.append(xy[start:])
    return [line for line in lines if len(line) > 1]


def draw_outline(ax, lines, color, lw=1.1, ls="-", halo="white", halo_extra=1.3):
    effects = [pe.Stroke(linewidth=lw + halo_extra, foreground=halo), pe.Normal()]
    for xy in lines:
        ax.plot(xy[:, 0], xy[:, 1], color=color, lw=lw, ls=ls, transform=ccrs.PlateCarree(),
                path_effects=effects, solid_joinstyle="miter", zorder=6)


def legend_handle(color, label, lw=1.6, ls="-", halo="white", halo_extra=1.3):
    return Line2D([], [], color=color, lw=lw, ls=ls, label=label,
                  path_effects=[pe.Stroke(linewidth=lw + halo_extra, foreground=halo), pe.Normal()])


def base_map(ax):
    cut_extent_Orthographic(ax, lat=45.0)
    ax_map_properties(ax, alpha=0.25, coastlines=False, gridlines=False, ocean=False, land=True,
                      borders=False, rivers=False)


def figure_classes(d_broad, d_needle, classes, modified, area):
    fig, axes = plt.subplots(1, 3, figsize=(13, 5.2), subplot_kw={"projection": ccrs.Orthographic(0, 90)})
    for ax, da, title in zip(axes[:2], (d_broad, d_needle),
                             ("Broadleaf deciduous trees", "Needleleaf trees")):
        base_map(ax)
        p = da.plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree(), cmap="RdBu_r", vmin=-30, vmax=30,
                               add_colorbar=False, zorder=1)
        ax.coastlines(linewidth=0.6, zorder=3)
        ax.set_title(title, fontsize=11, fontweight="semibold")
        fig.colorbar(p, ax=ax, orientation="horizontal", shrink=0.8, pad=0.04, ticks=np.arange(-30, 31, 10),
                     label="LCC − CTRL [% of grid cell]")

    colors = ["#CCCCCC", pal.ORANGE, pal.GOLD, pal.TEAL]
    ax = axes[2]
    base_map(ax)
    classes.plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree(), cmap=ListedColormap(colors),
                            norm=BoundaryNorm(np.arange(-0.5, 4.5), 4), add_colorbar=False, zorder=1)
    ax.coastlines(linewidth=0.6, zorder=3)
    ax.set_title("Dominant change", fontsize=11, fontweight="semibold")
    names = ["Small woody gain (≤1 point)", "Broadleaf replaces needleleaf", "Broadleaf gains most",
             "Needleleaf gains most"]
    ax.legend(handles=[Patch(color=c, label=n) for c, n in zip(colors, names)], loc="upper center",
              bbox_to_anchor=(0.5, -0.04), ncol=2, frameon=False, fontsize=8.5)
    fig.savefig(OUT / "vegetation_classes.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    total = float(area.where(modified).sum())
    rows = [{"class": n, "cells": int((classes == k).sum()),
             "share_of_modified_area_pct": round(100 * float(area.where(classes == k).sum()) / total, 1)}
            for k, n in enumerate(names)]
    table = pd.DataFrame(rows)
    table.to_csv(OUT / "vegetation_classes.csv", index=False)
    print(table.to_string(index=False))


def load_total_forcing():
    panel = next(p for p in fm.forcing_panels("NET") if p.key == "total")
    pairs = {"lcc": "LCC_PD", "ctrl": "CTRL_PD"}
    for attempt in range(1, 9):  # NIRD reads fail intermittently with "HDF error"
        try:
            return panel, pairs, fm.panel_difference(panel, pairs, START, END).load()
        except (OSError, RuntimeError) as err:
            print(f"read attempt {attempt} failed: {err}", flush=True)
            if attempt == 8:
                raise
            time.sleep(10 * attempt)


def divider_lines(classes, area, sigma=(1.0, 1.5), min_valid=0.15, min_km=500.0):
    """Single border between the broadleaf (+1) and needleleaf (-1) regions.

    Gaussian smoothing that ignores unclassified cells (periodic in longitude), zero contour,
    pieces shorter than min_km dropped. Returns the lines and the share of classified area on
    the correct side of the smoothed border.
    """
    score = np.where(classes.isin([1, 2]), 1.0, np.where(classes == 3, -1.0, 0.0))
    valid = (score != 0).astype(float)
    numerator = gaussian_filter(score, sigma=sigma, mode=("nearest", "wrap"))
    weight = gaussian_filter(valid, sigma=sigma, mode=("nearest", "wrap"))
    smooth = np.where(weight > min_valid, numerator / np.where(weight > 0, weight, 1), np.nan)

    lat, lon = classes["lat"].values, classes["lon"].values
    cyclic, lon_c = add_cyclic_point(smooth, coord=lon)
    fig, ax = plt.subplots()
    contour = ax.contour(lon_c, lat, cyclic, levels=[0.0])
    segments = contour.allsegs[0]
    plt.close(fig)

    def length_km(xy):
        dx = np.diff(xy[:, 0]) * np.cos(np.deg2rad(0.5 * (xy[:-1, 1] + xy[1:, 1])))
        return 111.2 * np.hypot(dx, np.diff(xy[:, 1])).sum()

    lines = [xy for xy in segments if len(xy) > 1 and length_km(xy) >= min_km]
    marked = score != 0
    correct = np.sign(np.nan_to_num(smooth)) == score
    agreement = 100 * float(area.values[marked & correct].sum() / area.values[marked].sum())
    print(f"divider: kept {len(lines)} of {len(segments)} pieces, "
          f"{sum(map(length_km, lines)):.0f} km; {agreement:.1f} % of classified area on the correct side")
    return lines


def figure_divider(classes, area):
    lines = divider_lines(classes, area)
    panel, pairs, d = load_total_forcing()
    vmax = fm.symmetric_vmax(d.mean("year"))
    styles = [("Black line", dict(color="black", lw=1.2, halo="white", halo_extra=0.8)),
              ("Gold line", dict(color=pal.GOLD, lw=1.4, halo="#222222", halo_extra=0.7))]
    fig, axes = fm.map_grid(1, 2)
    for ax, (title, style) in zip(axes[0], styles):
        fm._plot_panel(ax, panel, pairs, START, END, 45.0, 45.0, True, 0.05, vmax=vmax, d=d)
        ax.set_title(title, fontsize=9.5, fontweight="semibold")
        draw_outline(ax, lines, **style)
    fig.suptitle(f"Broadleaf / needleleaf border on total net forcing, LCC_PD − CTRL_PD, {START}–{END}",
                 fontsize=11)
    fig.savefig(OUT / "divider_options.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def figure_smoothing(classes, area):
    """Black border without halo at four smoothing levels (sigma in latitude cells; longitude = 1.5 x)."""
    panel, pairs, d = load_total_forcing()
    vmax = fm.symmetric_vmax(d.mean("year"))
    levels = [(0.0, "No smoothing"), (0.4, "Light (σ = 0.4 cells)"), (0.6, "Medium (σ = 0.6 cells)"),
              (0.8, "Stronger (σ = 0.8 cells)")]
    fig, axes = fm.map_grid(2, 2, titles_every_row=True)
    for ax, (s, title) in zip(axes.flat, levels):
        print(title, end=": ")
        lines = divider_lines(classes, area, sigma=(s, 1.5 * s))
        fm._plot_panel(ax, panel, pairs, START, END, 45.0, 45.0, True, 0.05, vmax=vmax, d=d)
        ax.set_title(title, fontsize=9.5, fontweight="semibold")
        for xy in lines:
            ax.plot(xy[:, 0], xy[:, 1], color="black", lw=1.0, transform=ccrs.PlateCarree(), zorder=6)
    fig.suptitle(f"Border smoothing on total net forcing, LCC_PD − CTRL_PD, {START}–{END}", fontsize=11)
    fig.savefig(OUT / "divider_smoothing.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def figure_overlays(classes):
    broad = outline_lines(classes.isin([1, 2]))
    needle = outline_lines(classes == 3)
    panel, pairs, d = load_total_forcing()
    vmax = fm.symmetric_vmax(d.mean("year"))

    styles = [
        ("A  Orange and teal", dict(color=pal.ORANGE), dict(color=pal.TEAL)),
        ("B  Black, solid and dashed", dict(color="black"), dict(color="black", ls=(0, (2.2, 1.2)))),
        ("C  Gold and plum, dark edge", dict(color=pal.GOLD, halo="#222222", halo_extra=0.9),
         dict(color=pal.PLUM, halo="#222222", halo_extra=0.9)),
    ]
    fig, axes = fm.map_grid(1, 3)
    for ax, (title, broad_style, needle_style) in zip(axes[0], styles):
        fm._plot_panel(ax, panel, pairs, START, END, 45.0, 45.0, True, 0.05, vmax=vmax, d=d)
        ax.set_title(title, fontsize=9.5, fontweight="semibold")
        draw_outline(ax, broad, **broad_style)
        draw_outline(ax, needle, **needle_style)
        ax.legend(handles=[legend_handle(label="Broadleaf", **broad_style),
                           legend_handle(label="Needleleaf", **needle_style)],
                  loc="upper center", bbox_to_anchor=(0.5, -0.50), ncol=2, frameon=False, fontsize=8)
    fig.suptitle(f"Outline test on total net forcing, LCC_PD − CTRL_PD, {START}–{END}", fontsize=12)
    fig.savefig(OUT / "outline_options.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    set_default_style()
    d_broad, d_needle, classes, modified, area = load_classes()
    if "smoothing" in sys.argv[1:]:
        figure_smoothing(classes, area)
    elif "divider" in sys.argv[1:]:
        figure_divider(classes, area)
    else:
        figure_classes(d_broad, d_needle, classes, modified, area)
        figure_overlays(classes)
