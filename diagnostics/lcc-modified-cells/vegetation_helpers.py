"""Shared helpers for the vegetation-region scripts in this folder.

Used by region_cells.py, si_vegetation_classes.py and dominant_pft_change.py.
Taken from the sandbox style tests (test_vegetation_outlines.py, test_vegetation_real_figures.py,
test_vegetation_line_colours.py, test_vegetation_line_halo.py, test_vegetation_modified_edges.py), keeping only
what these scripts need; same code and values.

Woody changes are LCC - CTRL surfdata, PCT_NAT_PFT x PCT_NATVEG / 100 (percentage points of the grid cell).
Needleleaf = CLM PFTs 1, 2, 3; broadleaf deciduous trees = PFTs 6, 7, 8.
"""
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

import cartopy.crs as ccrs
import xarray as xr

from boreal_forest_expansion.analysis.regions import load_modified_cells
from boreal_forest_expansion.plotting import forcing_maps as fm
from boreal_forest_expansion.plotting.common import ax_map_properties, cut_extent_Orthographic

SURF = Path("/cluster/shared/noresm/inputdata/lnd/clm2/surfdata_map")
CTRL_SURF = SURF / "release-clm5.0.18" / "surfdata_1.9x2.5_hist_78pfts_CMIP6_simyr2000_c190304.nc"
LCC_SURF = SURF / "surfdata_1.9x2.5_SSP5-8.5_2100_78pfts_LPJGUESS.nc"
NEEDLELEAF, BROADLEAF = [1, 2, 3], [6, 7, 8]
THRESHOLD = 1.0  # percentage points of the grid cell
START, END = 2001, 2025

# Map lines (hand-edited, display only); the same file forcing_maps.VEGETATION_LINES draws on the result maps.
LINES_FILE = HERE / "vegetation_map_lines.json"
COLOUR, EDGE_ALPHA = "#000000", 0.7  # white edge 30 % transparent
EDGE_EXTRA = 1.0  # total extra width of the white edge, points
MODIFIED_WIDTH = 0.5  # solid line: limit of perturbed cells
BORDER_DASH, BORDER_WIDTH = (0, (2.2, 1.0)), 0.7  # dashed line: replacement / net-tree-gain border


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


def base_map(ax):
    cut_extent_Orthographic(ax, lat=45.0)
    ax_map_properties(ax, alpha=0.25, coastlines=False, gridlines=False, ocean=False, land=True,
                      borders=False, rivers=False)


def draw_line(ax, xy, colour, width, alpha, **style):
    if alpha > 0:
        ax.plot(xy[:, 0], xy[:, 1], color="white", alpha=alpha, lw=width + EDGE_EXTRA, solid_capstyle="round",
                solid_joinstyle="round", transform=ccrs.PlateCarree(), zorder=4.5)
    ax.plot(xy[:, 0], xy[:, 1], color=colour, lw=width, transform=ccrs.PlateCarree(), zorder=6, **style)


def add_lines(ax, lines):
    """Solid limit of the perturbed cells + dashed replacement / net-tree-gain border (lines as numpy arrays)."""
    for xy in lines["modified"]:
        draw_line(ax, xy, COLOUR, MODIFIED_WIDTH, EDGE_ALPHA)
    for xy in lines["border"]:
        draw_line(ax, xy, COLOUR, BORDER_WIDTH, EDGE_ALPHA, ls=BORDER_DASH)


def read(panel, pairs):
    """Yearly panel difference START-END, retried because NIRD reads fail intermittently with "HDF error"."""
    for attempt in range(1, 9):
        try:
            return fm.panel_difference(panel, pairs, START, END).load()
        except (OSError, RuntimeError) as err:
            print(f"{panel.key}: read attempt {attempt} failed: {err}", flush=True)
            if attempt == 8:
                raise
            time.sleep(10 * attempt)
