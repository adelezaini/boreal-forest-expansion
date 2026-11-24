"""Which modified cells belong to each vegetation region, and what the regional numbers look like.

Two ways to define the regions:
  by class: broadleaf replaces needleleaf / other tree gain / little tree gain, as in vegetation_classes.png.
  by line:  two regions that follow the final dashed line. Small patches with no dashed line around them join the
            region around them, and little-gain cells join the region they reach without crossing the line.

Monoterpene numbers use the same method as the maps: cos-lat mean of the yearly differences, 95 % t-interval.
Writes into sandbox/vegetation_regions/region_cells_outputs/ only (not paper output).
"""
import json
import sys
from collections import deque
from dataclasses import replace
from pathlib import Path

HERE = Path(__file__).resolve().parent
SANDBOX = HERE.parent
sys.path[:0] = [str(SANDBOX.parent / "src"), str(SANDBOX)]

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from shapely import STRtree
from shapely.geometry import LineString

import test_vegetation_line_colours as tc
import test_vegetation_outlines as tv
import test_vegetation_real_figures as tr
from boreal_forest_expansion.plotting import forcing_maps as fm
from boreal_forest_expansion.plotting import palette as pal
from boreal_forest_expansion.plotting.style import set_default_style

OUT = HERE / "region_cells_outputs"
LITTLE, BROADLEAF, OTHER = 0, 1, 2
NAMES = {BROADLEAF: "Broadleaf replaces needleleaf", OTHER: "Other tree gain", LITTLE: "Little tree gain"}
COLOURS = {BROADLEAF: pal.ORANGE, OTHER: pal.TEAL, LITTLE: "#CCCCCC"}
MAX_PATCH_CELLS = 10  # larger patches keep their class even with no dashed line around them
CONTRASTS = {"PD": ("LCC_PD", "CTRL_PD"), "FUT": ("LCC_FUT", "CTRL_FUT")}


def neighbours(i, j, shape):
    """Four neighbours on the lat-lon grid, periodic in longitude."""
    if i > 0:
        yield i - 1, j
    if i < shape[0] - 1:
        yield i + 1, j
    yield i, (j - 1) % shape[1]
    yield i, (j + 1) % shape[1]


def crossing_test(border, lat, lon):
    """Function telling whether the step between two cell centres crosses the dashed line."""
    tree = STRtree([LineString(xy) for xy in border])
    cache = {}

    def crosses(a, b):
        key = (min(a, b), max(a, b))
        if key not in cache:
            lon_a, lon_b = lon[a[1]], lon[b[1]]
            if abs(lon_a - lon_b) > 180:  # step across the 0/360 seam
                lon_b += 360 if lon_a > lon_b else -360
            step = LineString([(lon_a, lat[a[0]]), (lon_b, lat[b[0]])])
            cache[key] = tree.query(step, predicate="intersects").size > 0
        return cache[key]
    return crosses


def components(labels, value):
    """Groups of 4-connected cells with this label."""
    todo = set(zip(*np.nonzero(labels == value)))
    while todo:
        start = todo.pop()
        group, queue = [start], deque([start])
        while queue:
            for cell in neighbours(*queue.popleft(), labels.shape):
                if cell in todo:
                    todo.remove(cell)
                    group.append(cell)
                    queue.append(cell)
        yield group


def regions_by_line(by_class, crosses):
    """Two regions (-1 outside the modified cells) that follow the dashed line."""
    labels = by_class.copy()
    moved_patches = 0
    for value, other in ((BROADLEAF, OTHER), (OTHER, BROADLEAF)):
        for group in list(components(labels, value)):
            contacts = [(c, n) for c in group for n in neighbours(*c, labels.shape) if labels[n] == other]
            if contacts and len(group) <= MAX_PATCH_CELLS and not any(crosses(c, n) for c, n in contacts):
                for cell in group:
                    labels[cell] = other
                moved_patches += 1

    remaining = set(zip(*np.nonzero(labels == LITTLE)))
    while remaining:  # little-gain cells take the region of the neighbours they reach without crossing the line
        update = {}
        for cell in remaining:
            near = [labels[n] for n in neighbours(*cell, labels.shape)
                    if labels[n] in (BROADLEAF, OTHER) and not crosses(cell, n)]
            if near:
                update[cell] = BROADLEAF if near.count(BROADLEAF) > near.count(OTHER) else OTHER
        if not update:
            break
        for cell, value in update.items():
            labels[cell] = value
        remaining -= set(update)
    isolated = len(remaining)
    for cell in remaining:  # cut off from both regions: nearest region cell
        rows, cols = np.nonzero(np.isin(labels, (BROADLEAF, OTHER)))
        dlon = np.abs(cols - cell[1])
        k = np.argmin((rows - cell[0]) ** 2 + np.minimum(dlon, labels.shape[1] - dlon) ** 2)
        labels[cell] = labels[rows[k], cols[k]]
    print(f"by line: {moved_patches} small patches moved, {isolated} isolated little-gain cells placed by distance")
    return labels


def read_difference(panel, pairs, lat, lon):
    d = tc.read(panel, pairs)
    if not (np.allclose(d["lat"], lat, atol=1e-9) and np.allclose(d["lon"], lon, atol=1e-9)):
        raise ValueError("model and surface-data grids differ")
    return d.assign_coords(lat=lat, lon=lon)


def table(maps, panel, lat, lon, cell_km2):
    rows = []
    fields = {period: read_difference(panel, {"case1": c1, "case2": c2}, lat, lon)
              for period, (c1, c2) in CONTRASTS.items()}
    weights = np.cos(np.deg2rad(lat))[:, None] * np.ones(cell_km2.shape)
    for version, labels in maps.items():
        groups = [("All modified cells", labels >= 0)] + [(NAMES[v], labels == v) for v in NAMES if (labels == v).any()]
        for name, mask in groups:
            row = {"regions": version, "region": name, "cells": int(mask.sum()),
                   "area_share_%": 100 * weights[mask].sum() / weights[labels >= 0].sum()}
            for period, d in fields.items():
                where = xr.DataArray(mask, coords={"lat": lat, "lon": lon}, dims=("lat", "lon"))
                mean, half = fm.regional_mean_interval(d.where(where))
                row[f"{period}_mean_mg_m2_d"], row[f"{period}_ci95"] = mean, half
                yearly = (d.where(where) * xr.DataArray(cell_km2, coords=where.coords)).sum(("lat", "lon"))
                row[f"{period}_total_Tg_yr"] = float(yearly.mean()) * 1e6 * 365 / 1e15  # mg/m2/d * km2
            rows.append(row)
    return pd.DataFrame(rows)


def main():
    set_default_style()
    OUT.mkdir(exist_ok=True)
    _, _, classes, modified, _ = tv.load_classes()
    lat, lon = classes["lat"].values, classes["lon"].values
    with xr.open_dataset(tv.LCC_SURF, decode_times=False) as s:
        print("AREA units:", s["AREA"].attrs.get("units"))
        cell_km2 = s["AREA"].load().values
    raw = classes.values
    by_class = np.full(raw.shape, -1)
    by_class[raw == 0], by_class[raw == 1], by_class[(raw == 2) | (raw == 3)] = LITTLE, BROADLEAF, OTHER
    stored = json.loads(tr.LINES_FILE.read_text())
    lines = {k: [np.asarray(xy) for xy in stored[k]] for k in ("border", "modified")}
    by_line = regions_by_line(by_class, crossing_test(lines["border"], lat, lon))
    maps = {"by class": by_class, "by line": by_line}
    changed = (by_class != by_line) & (by_class >= 0)
    print(f"cells that differ: {changed.sum()} of {(by_class >= 0).sum()}, "
          f"of which little-gain {(changed & (by_class == LITTLE)).sum()}")

    fig, axes = plt.subplots(1, 2, figsize=(12, 6.6), subplot_kw={"projection": ccrs.Orthographic(0, 90)})
    colours = ListedColormap([COLOURS[LITTLE], COLOURS[BROADLEAF], COLOURS[OTHER]])
    for ax, (name, labels) in zip(axes, maps.items()):
        tv.base_map(ax)
        ax.pcolormesh(lon, lat, np.ma.masked_less(labels, 0), cmap=colours, norm=BoundaryNorm([-0.5, 0.5, 1.5, 2.5], 3),
                      transform=ccrs.PlateCarree(), shading="nearest", zorder=1)
        ax.coastlines(linewidth=0.4, color="#8C8C8C", zorder=3)
        tr.add_lines(ax, lines)
        ax.set_title(f"Regions {name}", fontsize=12, fontweight="semibold")
    rows, cols = np.nonzero(changed)
    axes[1].scatter(lon[cols], lat[rows], s=2.5, c="k", linewidths=0, transform=ccrs.PlateCarree(), zorder=7)
    handles = [Patch(color=COLOURS[v], label=NAMES[v]) for v in (BROADLEAF, OTHER, LITTLE)]
    handles += [Line2D([], [], color="k", marker=".", ls="", ms=4, label="Cell placed differently from its class"),
                Line2D([], [], color="k", lw=tr.tm.BORDER_WIDTH, ls=tr.tm.BORDER_DASH, label="Dashed border"),
                Line2D([], [], color="k", lw=tr.tm.MODIFIED_WIDTH, label="Limit of perturbed cells")]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=9)
    fig.subplots_adjust(bottom=0.14, top=0.93, wspace=0.03)
    fig.savefig(OUT / "region_cells.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    panel = replace(next(p for p in fm.CONTEXT_PANELS if p.key == "sfmterp"), case1_role="case1", case2_role="case2")
    result = table(maps, panel, lat, lon, cell_km2)
    result.to_csv(OUT / "region_monoterpene.csv", index=False)
    print(result.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
