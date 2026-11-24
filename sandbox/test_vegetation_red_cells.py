"""Why are some strongly positive forcing cells outside the needleleaf region? (sandbox diagnostic)

Uses LCC_PD - CTRL_PD, 2001-2025, and the classes of test_vegetation_outlines.py.
"Red" = FDR-significant total net forcing above RED_LIMIT.
"""
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "src"), str(HERE)]

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch
from shapely.geometry import LineString
from shapely.ops import linemerge

import test_vegetation_outlines as tv
from boreal_forest_expansion.plotting import forcing_maps as fm
from boreal_forest_expansion.plotting import palette as pal
from boreal_forest_expansion.plotting.style import set_default_style

OUT = tv.OUT
RED_LIMIT = 0.5  # W m-2
PFT_GROUPS = {"needleleaf": [1, 2, 3], "broadleaf": [6, 7, 8], "shrub": [9, 10, 11], "grass": [12, 13, 14], "bare": [0]}


def retry(function, tries=8):
    for attempt in range(1, tries + 1):
        try:
            return function()
        except (OSError, RuntimeError) as err:
            print(f"read attempt {attempt} failed: {err}", flush=True)
            if attempt == tries:
                raise
            time.sleep(10 * attempt)


def pft_changes(template):
    def read():
        with xr.open_dataset(tv.CTRL_SURF, decode_times=False) as c, xr.open_dataset(tv.LCC_SURF, decode_times=False) as l:
            change = ((l["PCT_NAT_PFT"] - c["PCT_NAT_PFT"]) * l["PCT_NATVEG"] / 100).load()
            base = (c["PCT_NAT_PFT"] * c["PCT_NATVEG"] / 100).load()
        return change, base
    change, base = retry(read)
    wrap = lambda a: xr.DataArray(a, coords=template.coords, dims=template.dims)
    out = {f"d_{k}": wrap(change.isel(natpft=v).sum("natpft").values) for k, v in PFT_GROUPS.items()}
    out["ctrl_needleleaf"] = wrap(base.isel(natpft=PFT_GROUPS["needleleaf"]).sum("natpft").values)
    out["ctrl_broadleaf"] = wrap(base.isel(natpft=PFT_GROUPS["broadleaf"]).sum("natpft").values)
    out["d_tree"] = out["d_needleleaf"] + out["d_broadleaf"]
    return out


def exact_border(classes):
    """Grid-cell edges where a broadleaf cell touches a needleleaf cell (no smoothing)."""
    lat, lon = classes["lat"].values, classes["lon"].values
    dlon = np.diff(lon).mean()
    lon_edges = lon[0] - dlon / 2 + dlon * np.arange(lon.size + 1)
    lat_edges = np.r_[lat[0], 0.5 * (lat[:-1] + lat[1:]), lat[-1]]
    group = np.where(classes.isin([1, 2]), 1, np.where(classes == 3, 2, 0))
    pieces = []
    for i in range(lat.size):
        for j in range(lon.size):
            east = (j + 1) % lon.size
            if {group[i, j], group[i, east]} == {1, 2}:
                x = lon_edges[j + 1]
                pieces.append(LineString([(x, lat_edges[i]), (x, lat_edges[i + 1])]))
            if i + 1 < lat.size and {group[i, j], group[i + 1, j]} == {1, 2}:
                y = lat_edges[i + 1]
                pieces.append(LineString([(lon_edges[j], y), (lon_edges[j + 1], y)]))
    merged = linemerge(pieces)
    return [np.asarray(g.coords) for g in getattr(merged, "geoms", [merged])]


def main():
    OUT.mkdir(exist_ok=True)
    set_default_style()
    _, _, classes, modified, area = tv.load_classes()
    panel, pairs, d = tv.load_total_forcing()
    albedo_panel = next(p for p in fm.forcing_panels("NET") if p.key == "albedo")
    d_albedo = retry(lambda: fm.panel_difference(albedo_panel, pairs, tv.START, tv.END).load())
    total = d.mean("year")
    albedo = d_albedo.mean("year")
    dlat = np.abs(classes["lat"].values - total["lat"].values).max()
    dlon = np.abs(classes["lon"].values - total["lon"].values).max()
    print(f"CLM vs CAM grid: max difference lat {dlat:.2e}, lon {dlon:.2e} deg")
    if max(dlat, dlon) > 1e-3:
        raise ValueError("CLM and CAM grids differ")
    same_grid = {"lat": total["lat"], "lon": total["lon"]}
    classes, modified, area = [x.assign_coords(same_grid) for x in (classes, modified, area)]
    p = fm.cellwise_pvalue(d)
    sig = fm.fdr_mask(p, alpha=0.05, within=d["lat"] >= 45.0)
    red = (total > RED_LIMIT) & sig & modified
    veg = pft_changes(total)

    groups = {
        "Needleleaf region, red": (classes == 3) & red,
        "Needleleaf region, not red": (classes == 3) & ~red,
        "Broadleaf replaces needleleaf, red": (classes == 1) & red,
        "Broadleaf replaces needleleaf, not red": (classes == 1) & ~red,
        "Broadleaf gains most, red": (classes == 2) & red,
        "Broadleaf gains most, not red": (classes == 2) & ~red,
        "Little tree gain, red": (classes == 0) & red,
        "Little tree gain, not red": (classes == 0) & ~red,
    }
    rows = []
    weights = area.fillna(0)
    for name, mask in groups.items():
        row = {"group": name, "cells": int(mask.sum())}
        if row["cells"]:
            mean = lambda x: float(x.where(mask).weighted(weights).mean())
            row |= {"lat": round(mean(total["lat"] * xr.ones_like(total)), 1), "forcing": round(mean(total), 2),
                    "albedo_forcing": round(mean(albedo), 2)}
            row |= {k: round(mean(v), 1) for k, v in veg.items()}
        rows.append(row)
    table = pd.DataFrame(rows)
    table.to_csv(OUT / "red_cells_by_class.csv", index=False)
    pd.set_option("display.width", 250, "display.max_columns", 30)
    print(table.to_string(index=False))

    for name, keep in {"modified": modified, "broadleaf classes": classes.isin([1, 2]),
                       "needleleaf class": classes == 3}.items():
        f = total.values[keep.values]
        print(f"corr with forcing, {name}: " + ", ".join(
            f"{k} {np.corrcoef(veg[k].values[keep.values], f)[0, 1]:+.2f}" for k in
            ("d_needleleaf", "d_broadleaf", "d_tree", "d_grass", "d_bare")) +
              f", albedo forcing {np.corrcoef(albedo.values[keep.values], f)[0, 1]:+.2f}")

    lines = exact_border(classes)
    print("exact border pieces:", len(lines))
    vmax = fm.symmetric_vmax(total)
    fig, axes = fm.map_grid(1, 2)
    ax = axes[0, 0]
    fm._plot_panel(ax, panel, pairs, tv.START, tv.END, 45.0, 45.0, True, 0.05, vmax=vmax, d=d)
    ax.set_title("Zero smoothing", fontsize=9.5, fontweight="semibold")
    for xy in lines:
        ax.plot(xy[:, 0], xy[:, 1], color="black", lw=1.0, transform=ccrs.PlateCarree(), zorder=6)

    ax = axes[0, 1]
    tv.base_map(ax)
    where = xr.where(red & (classes == 3), 1, np.nan)
    where = where.where(~(red & classes.isin([1, 2])), 2).where(~(red & (classes == 0)), 3)
    colors = [pal.TEAL, pal.ORANGE, pal.PLUM]
    classes.notnull().where(modified).plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree(), add_colorbar=False,
                                                     cmap=ListedColormap(["#E6E6E6"]), zorder=1)
    where.plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree(), cmap=ListedColormap(colors),
                          norm=BoundaryNorm([0.5, 1.5, 2.5, 3.5], 3), add_colorbar=False, zorder=2)
    ax.coastlines(linewidth=0.6, zorder=3)
    for xy in lines:
        ax.plot(xy[:, 0], xy[:, 1], color="black", lw=1.0, transform=ccrs.PlateCarree(), zorder=6)
    ax.set_title(f"Significant forcing > {RED_LIMIT} W m$^{{-2}}$", fontsize=9.5, fontweight="semibold")
    ax.legend(handles=[Patch(color=c, label=n) for c, n in zip(colors, ("Needleleaf region", "Broadleaf region",
                                                                        "Little tree gain"))],
              loc="upper center", bbox_to_anchor=(0.5, -0.04), ncol=3, frameon=False, fontsize=7.5)
    fig.suptitle(f"Vegetation border and red cells, LCC_PD − CTRL_PD, {tv.START}–{tv.END}", fontsize=11)
    fig.savefig(OUT / "red_cells_zero_smoothing.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
