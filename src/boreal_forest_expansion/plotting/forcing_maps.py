"""
Forcing and BVOC-context map plotting utilities.

This module assumes postprocessed files are saved as:

    [casealias]_[variableclass]_[startyr]_[endyr].nc

in:

    /cluster/home/adelez/BOREAL-FOREST-EXPANSION/data/postprocessed-diagnostics

It is designed to work after postprocess/postprocess.py has created files like:

    CTRL_RADIATIVE_2000_2009.nc
    LCC-PD_RADIATIVE_2000_2009.nc
    LCC-PD-fBVOC_RADIATIVE_2000_2009.nc
    LCC-FUT_RADIATIVE_2000_2009.nc
    LCC-FUT-fBVOC_RADIATIVE_2000_2009.nc
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import xarray as xr

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from boreal_forest_expansion.plotting.common import (
    ax_map_properties,
    cut_extent_Orthographic,
)


POSTPROCESSED_DIR = Path(
    "/cluster/home/adelez/BOREAL-FOREST-EXPANSION/data/postprocessed-diagnostics"
)

FIGURE_DIR = Path(
    "/cluster/home/adelez/BOREAL-FOREST-EXPANSION/results/figures"
)


# =============================================================================
# Case and plot definitions
# =============================================================================

ALIASES = {
    "CTRL": "CTRL",
    "LCC-PD": "LCC-PD",
    "LCC-PD-fBVOC": "LCC-PD-fBVOC",
    "LCC-FUT": "LCC-FUT",
    "LCC-FUT-fBVOC": "LCC-FUT-fBVOC",
}


BVOC_PAIRS = {
    "PD": {
        "lcc": "LCC-PD",
        "fbvoc": "LCC-PD-fBVOC",
        "ctrl": "CTRL",
    },
    "FUT": {
        "lcc": "LCC-FUT",
        "fbvoc": "LCC-FUT-fBVOC",
        "ctrl": "CTRL",
    },
}


@dataclass(frozen=True)
class MapPanel:
    key: str
    title: str
    variable_class: str
    variable: str
    case1_role: str
    case2_role: str
    units: str = "W m$^{-2}$"
    long_label: str | None = None
    vmax: float | None = None


FORCING_PANELS = [
    MapPanel(
        key="albedo",
        title="ALBEDO / SW CLEAR-SKY FORCING",
        variable_class="RADIATIVE",
        variable="SFC_ALBEDO_FORCING_CLEAR", #"SW_rest_Ghan" - incouding other things (eg chemistry), but the other is more a proxy
        case1_role="lcc",
        case2_role="ctrl",
        long_label="Shortwave clean clear-sky residual forcing",
        vmax=10.0,
    ),
    MapPanel(
        key="total",
        title="TOTAL RADIATIVE FORCING",
        variable_class="RADIATIVE",
        variable="FTOT_Ghan",
        case1_role="lcc",
        case2_role="ctrl",
        long_label="Net TOA radiative forcing",
        vmax=6.0,
    ),
    MapPanel(
        key="bvoc_total",
        title="BVOC-RELATED FORCING",
        variable_class="RADIATIVE",
        variable="FTOT_Ghan",
        case1_role="lcc",
        case2_role="fbvoc",
        long_label="Net BVOC-related radiative forcing",
        vmax=2.0,
    ),
    MapPanel(
        key="bvoc_cloud",
        title="BVOC-SOA-CLOUD FORCING",
        variable_class="RADIATIVE",
        variable="NCFT_Ghan",
        case1_role="lcc",
        case2_role="fbvoc",
        long_label="Net cloud-mediated BVOC/SOA forcing",
        vmax=2.0,
    ),
    MapPanel(
        key="bvoc_direct",
        title="BVOC-DIRECT SOA FORCING",
        variable_class="RADIATIVE",
        variable="DIR_Ghan",
        case1_role="lcc",
        case2_role="fbvoc",
        long_label="Net direct aerosol/SOA forcing",
        vmax=2.0,
    ),
    MapPanel(
        key="bvoc_residual",
        title="BVOC CHEMISTRY / RESIDUAL FORCING",
        variable_class="RADIATIVE",
        variable="FREST_Ghan",
        case1_role="lcc",
        case2_role="fbvoc",
        long_label="Clean clear-sky residual forcing",
        vmax=2.0,
    ),
]


CONTEXT_PANELS = [
    MapPanel(
        key="sfisop",
        title="ISOPRENE EMISSIONS",
        variable_class="BVOC",
        variable="SFISOP",
        case1_role="lcc",
        case2_role="fbvoc",
        units="kg m$^{-2}$ s$^{-1}$",
        long_label="Surface isoprene flux",
        vmax=1e-11,
    ),
    MapPanel(
        key="sfmterp",
        title="MONOTERPENE EMISSIONS",
        variable_class="BVOC",
        variable="SFMTERP",
        case1_role="lcc",
        case2_role="fbvoc",
        units="kg m$^{-2}$ s$^{-1}$",
        long_label="Surface monoterpene flux",
        vmax=1e-1,
    ),
    MapPanel(
        key="soa_tot",
        title="TOTAL SOA BURDEN",
        variable_class="SOA",
        variable="cb_SOA_TOT_mgm2",
        case1_role="lcc",
        case2_role="fbvoc",
        units="mg m$^{-2}$",
        long_label="Total SOA column burden",
    ),
    MapPanel(
        key="n_aer",
        title="AEROSOL NUMBER",
        variable_class="AEROSOL",
        variable="N_AER",
        case1_role="lcc",
        case2_role="fbvoc",
        units="",
        long_label="Total aerosol number",
    ),
    MapPanel(
        key="fctl",
        title="LIQUID CLOUD FRACTION",
        variable_class="CLOUDPROP",
        variable="FCTL",
        case1_role="lcc",
        case2_role="fbvoc",
        units="fraction",
        long_label="Liquid cloud fraction",
    ),
    MapPanel(
        key="actrel",
        title="ACTIVATED EFFECTIVE RADIUS",
        variable_class="CLOUDPROP",
        variable="ACTREL_incld",
        case1_role="lcc",
        case2_role="fbvoc",
        units="",
        long_label="In-cloud activated effective radius",
    ),
    MapPanel(
        key="actnl",
        title="ACTIVATED DROPLET NUMBER",
        variable_class="CLOUDPROP",
        variable="ACTNL_incld",
        case1_role="lcc",
        case2_role="fbvoc",
        units="# cm$^{-3}$",
        long_label="In-cloud activated droplet number",
    ),
    MapPanel(
        key="lwp",
        title="LIQUID WATER PATH",
        variable_class="CLOUDPROP",
        variable="TGCLDLWP_gm2",
        case1_role="lcc",
        case2_role="fbvoc",
        units="g m$^{-2}$",
        long_label="Cloud liquid water path",
    ),
    MapPanel(
        key="et",
        title="ET / SURFACE WATER FLUX",
        variable_class="METEOROLOGY",
        variable="QFLX_mmday",
        case1_role="lcc",
        case2_role="fbvoc",
        units="mm day$^{-1}$",
        long_label="Evapotranspiration / surface water flux",
    ),
]

# =============================================================================
# Loading and differencing
# =============================================================================

def filename(alias: str, variable_class: str, start_year: int, end_year: int) -> Path:
    return POSTPROCESSED_DIR / f"{alias}_{variable_class}_{start_year}_{end_year}.nc"


def open_class(alias: str, variable_class: str, start_year: int, end_year: int) -> xr.Dataset:
    path = filename(alias, variable_class, start_year, end_year)
    if not path.exists():
        raise FileNotFoundError(f"Missing postprocessed file: {path}")
    return xr.open_dataset(path)


def squeeze_to_map(da: xr.DataArray) -> xr.DataArray:
    """
    Convert a DataArray to lat-lon if possible.

    If a variable still has lev, use the lowest model level as a pragmatic
    near-surface map. For true column diagnostics, prefer postprocessed
    column variables.
    """
    da_ = da

    for dim in ["time", "year"]:
        if dim in da_.dims:
            da_ = da_.mean(dim)

    if "lev" in da_.dims:
        da_ = da_.isel(lev=-1)

    drop_dims = [dim for dim in da_.dims if dim not in ["lat", "lon"]]
    if drop_dims:
        da_ = da_.squeeze(drop=True)

    if not {"lat", "lon"}.issubset(da_.dims):
        raise ValueError(f"Cannot make map from {da.name}; dimensions are {da.dims}")

    return da_


def difference_map(
    case1: str,
    case2: str,
    variable_class: str,
    variable: str,
    start_year: int,
    end_year: int,
) -> xr.DataArray:
    ds1 = open_class(case1, variable_class, start_year, end_year)
    ds2 = open_class(case2, variable_class, start_year, end_year)

    if variable not in ds1:
        raise KeyError(f"{variable} not found in {filename(case1, variable_class, start_year, end_year)}")
    if variable not in ds2:
        raise KeyError(f"{variable} not found in {filename(case2, variable_class, start_year, end_year)}")

    da1 = squeeze_to_map(ds1[variable])
    da2 = squeeze_to_map(ds2[variable])

    diff = da1 - da2
    diff.name = f"{variable}_{case1}_minus_{case2}"
    diff.attrs["units"] = da1.attrs.get("units", "")
    diff.attrs["long_name"] = f"{variable}: {case1} - {case2}"

    return diff

def clear_sky_surface_albedo(ds: xr.Dataset) -> xr.DataArray:
    """
    Compute clear-sky surface albedo from surface shortwave fluxes.

    alpha_clear = FSUSC / FSDSC
                = (FSDSC - FSNSC) / FSDSC

    Requires:
        FSDSC: clear-sky downwelling SW at surface
        FSNSC: clear-sky net SW at surface

    Returns
    -------
    xr.DataArray
        Clear-sky surface albedo, unitless.
    """
    required = ["FSDSC", "FSNSC"]
    missing = [v for v in required if v not in ds]
    if missing:
        raise KeyError(f"Missing variables for clear-sky surface albedo: {missing}")

    fsdsc = squeeze_to_map(ds["FSDSC"])
    fsnsc = squeeze_to_map(ds["FSNSC"])

    fsusc = fsdsc - fsnsc
    alpha = (fsusc / fsdsc).where(fsdsc > 1.0)

    alpha.name = "ALBEDO_SFC_CLEAR"
    alpha.attrs["long_name"] = "clear-sky surface albedo"
    alpha.attrs["units"] = "1"

    return alpha

# =============================================================================
# Temporary evaluating albedo here
# =============================================================================

def surface_albedo_forcing_proxy_difference(
    case1: str,
    case2: str,
    variable_class: str,
    start_year: int,
    end_year: int,
) -> xr.DataArray:
    """
    Approximate clear-sky surface albedo forcing.

    For case1 - case2:

        dF = - FSDSC_case2 * (alpha_case1 - alpha_case2)

    Positive values mean lower albedo / more absorbed shortwave / warming.

    This is a surface shortwave forcing proxy, not a full TOA forcing.
    """
    ds1 = open_class(case1, variable_class, start_year, end_year)
    ds2 = open_class(case2, variable_class, start_year, end_year)

    alpha1 = clear_sky_surface_albedo(ds1)
    alpha2 = clear_sky_surface_albedo(ds2)

    fsdsc_ref = squeeze_to_map(ds2["FSDSC"])

    dalpha = alpha1 - alpha2
    forcing = -fsdsc_ref * dalpha

    forcing.name = f"SFC_ALBEDO_FORCING_CLEAR_{case1}_minus_{case2}"
    forcing.attrs["long_name"] = (
        f"clear-sky surface albedo forcing proxy: {case1} - {case2}"
    )
    forcing.attrs["units"] = "W m-2"

    return forcing

def panel_difference_map(
    case1: str,
    case2: str,
    variable_class: str,
    variable: str,
    start_year: int,
    end_year: int,
) -> xr.DataArray:
    """
    Return the map for a panel.

    Most panels are simple case1 - case2 differences.
    Some panels are derived on the fly, such as the temporary
    surface albedo forcing proxy.
    """
    if variable == "SFC_ALBEDO_FORCING_CLEAR":
        return surface_albedo_forcing_proxy_difference(
            case1=case1,
            case2=case2,
            variable_class=variable_class,
            start_year=start_year,
            end_year=end_year,
        )

    return difference_map(
        case1=case1,
        case2=case2,
        variable_class=variable_class,
        variable=variable,
        start_year=start_year,
        end_year=end_year,
    )

# =============================================================================
# Averaging and plotting helpers
# =============================================================================
"""
def spatial_weights_for_mean(ds_or_da, lat_min=None, lat_max=None):
    
    Return safe latitude weights for spatial means.

    Uses gw if available, otherwise reconstructs cos(lat) weights.
    
    obj = ds_or_da

    if "gw" in obj:
        weights = obj["gw"]
    else:
        weights = xr.DataArray(
            np.cos(np.deg2rad(obj["lat"])),
            coords={"lat": obj["lat"]},
            dims=("lat",),
            name="lat_weights",
        )

    if lat_min is not None:
        weights = weights.where(weights["lat"] >= lat_min, drop=True)

    if lat_max is not None:
        weights = weights.where(weights["lat"] <= lat_max, drop=True)

    if "time" in weights.dims:
        weights = weights.isel(time=0, drop=True)

    if "year" in weights.dims:
        weights = weights.isel(year=0, drop=True)

    return weights.fillna(0)

def weighted_spatial_mean(da, lat_min=None, lat_max=None):
    da_sub = da

    if lat_min is not None:
        da_sub = da_sub.where(da_sub["lat"] >= lat_min, drop=True)

    if lat_max is not None:
        da_sub = da_sub.where(da_sub["lat"] <= lat_max, drop=True)

    weights = spatial_weights_for_mean(da_sub, lat_min=None, lat_max=None)

    spatial_dims = [dim for dim in ("lat", "lon") if dim in da_sub.dims]

    return da_sub.weighted(weights).mean(spatial_dims)
"""
def area_weighted_mean(da, lat_min=None, lat_max=None, dims=("lat", "lon")):
    """
    Area-weighted mean for regular lat-lon data.

    Uses cos(lat) weights. This works when postprocessed files have lat/lon
    but no gw or GRIDAREA.
    """
    da_sub = da

    if lat_min is not None:
        da_sub = da_sub.where(da_sub["lat"] >= lat_min, drop=True)

    if lat_max is not None:
        da_sub = da_sub.where(da_sub["lat"] <= lat_max, drop=True)

    weights = xr.DataArray(
        np.cos(np.deg2rad(da_sub["lat"])),
        coords={"lat": da_sub["lat"]},
        dims=("lat",),
        name="area_weights",
    ).fillna(0)

    mean_dims = [dim for dim in dims if dim in da_sub.dims]

    return da_sub.weighted(weights).mean(mean_dims)

def symmetric_vmax(da: xr.DataArray, q: float = 0.98, fallback: float = 1.0) -> float:
    values = np.asarray(da.values)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return fallback
    vmax = float(np.nanquantile(np.abs(values), q))
    if vmax == 0 or not np.isfinite(vmax):
        return fallback
    return vmax


def format_forcing_mean(value: float) -> str:
    """
    Cleaner mean formatting for figure annotations.

    Examples:
        11.123 -> +11.1
        1.734  -> +1.7
        -0.593 -> -0.59
        -0.024 -> -0.02
    """
    value = float(value)

    if abs(value) >= 10:
        return f"{value:+.1f}"
    elif abs(value) >= 1:
        return f"{value:+.1f}"
    else:
        return f"{value:+.2f}"


def plot_single_boreal_panel(
    ax,
    da: xr.DataArray,
    title: str,
    units: str | None = None,
    vmax: float | None = None,
    cmap: str = "RdBu_r",
    extent_lat: float = 45.0,
    add_cbar: bool = True,
    cbar_label: str | None = None,
    mean_lat_min: float | None = 45.0,
    shade_ocean: bool = True,
    ocean_alpha: float = 0.75,
    ocean_facecolor: str = "white",
    ocean_zorder: int = 2,
):
    """
    Plot one polar boreal map panel.

    Parameters
    ----------
    shade_ocean:
        If True, overlay an ocean mask above the data.
    ocean_alpha:
        Transparency of the ocean mask.
        0 = no visible ocean shading, 1 = fully opaque.
    ocean_facecolor:
        Colour used for ocean shading.
    add_cbar:
        If True, add an individual colourbar for this panel.
    """
    if vmax is None:
        vmax = symmetric_vmax(da)

    norm = mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)

    cut_extent_Orthographic(ax, lat=extent_lat)

    ax_map_properties(
        ax,
        alpha=0.25,
        coastlines=False,
        gridlines=False,
        ocean=False,
        land=True,
        borders=False,
        rivers=False,
    )

    p = da.plot.pcolormesh(
        ax=ax,
        x="lon",
        y="lat",
        transform=ccrs.PlateCarree(),
        cmap=cmap,
        norm=norm,
        add_colorbar=False,
        zorder=1,
    )

    if shade_ocean:
        ax.add_feature(
            cfeature.OCEAN,
            facecolor=ocean_facecolor,
            edgecolor="none",
            alpha=ocean_alpha,
            zorder=ocean_zorder,
        )

    ax.coastlines(linewidth=0.6, zorder=ocean_zorder + 1)

    ax.set_title(
        title,
        fontsize=9.5,
        fontweight="semibold",
        pad=5,
    )

    mean_val = area_weighted_mean(da, lat_min=mean_lat_min)
    unit_text = units or da.attrs.get("units", "")

    ax.text(
        0.5,
        -0.12,
        f"mean: {format_forcing_mean(mean_val)} {unit_text}",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=7.8,
        fontweight="semibold",
        color="black",
    )

    cb = None

    if add_cbar:
        cb = plt.colorbar(
            p,
            ax=ax,
            orientation="horizontal",
            pad=0.085,
            shrink=0.88,
            aspect=24,
            extend="both",
        )

        cb.ax.xaxis.set_ticks_position("bottom")
        cb.ax.xaxis.set_label_position("bottom")
        cb.ax.tick_params(
            axis="x",
            bottom=True,
            top=False,
            labelbottom=True,
            labeltop=False,
            labelsize=7,
            pad=2,
        )

        if cbar_label is None:
            cbar_label = unit_text

        cb.set_label(cbar_label, fontsize=7, labelpad=3)

    return p, norm, cb


# =============================================================================
# Composite figures
# =============================================================================

def add_grouped_horizontal_colorbar(
    fig,
    axes_group,
    cmap,
    vmax,
    label,
    ticks=None,
    pad=0.075,
    height=0.035,
    extend="both",
    tick_labelsize=7,
    labelsize=8,
):
    """
    Add one horizontal colorbar spanning a group of axes.

    axes_group can be one axis or a list/array of axes.
    """
    axes_group = np.atleast_1d(axes_group)

    boxes = [ax.get_position() for ax in axes_group]

    x0 = min(box.x0 for box in boxes)
    x1 = max(box.x1 for box in boxes)
    y0 = min(box.y0 for box in boxes)

    cax = fig.add_axes([x0, y0 - pad, x1 - x0, height])

    norm = mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)
    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])

    cb = fig.colorbar(
        sm,
        cax=cax,
        orientation="horizontal",
        extend=extend,
        ticks=ticks,
    )

    cb.ax.tick_params(labelsize=tick_labelsize, pad=2)
    cb.set_label(label, fontsize=labelsize, labelpad=3)

    return cb

def make_forcing_summary_figure(
    experiment: str,
    start_year: int,
    end_year: int,
    extent_lat: float = 45.0,
    mean_lat_min: float | None = 45.0,
    figsize: tuple[float, float] = (19, 5.2),
    save: bool = True,
    figdir: Path = FIGURE_DIR,
    dpi: int = 300,
    cmap: str = "RdBu_r",
    add_cbar: bool = True,
    shade_ocean: bool = True,
    ocean_alpha: float = 0.75,
    ocean_facecolor: str = "white",
):
    """
    Create six-panel forcing decomposition figure.

    experiment:
        "PD" or "FUT"

    Ocean shading can be regulated with:
        shade_ocean=True/False
        ocean_alpha=0.0 to 1.0
        ocean_facecolor="white", "lightgrey", etc.

    Each panel gets its own individual colourbar when add_cbar=True.
    """
    if experiment not in BVOC_PAIRS:
        raise ValueError(f"experiment must be one of {list(BVOC_PAIRS)}")

    pairs = BVOC_PAIRS[experiment]

    fig, axes = plt.subplots(
        1,
        len(FORCING_PANELS),
        figsize=figsize,
        subplot_kw={"projection": ccrs.Orthographic(0, 90)},
        constrained_layout=True,
    )

    for ax, panel in zip(axes, FORCING_PANELS):
        case1 = pairs[panel.case1_role]
        case2 = pairs[panel.case2_role]

        da = panel_difference_map(
            case1=case1,
            case2=case2,
            variable_class=panel.variable_class,
            variable=panel.variable,
            start_year=start_year,
            end_year=end_year,
        )

        label = panel.long_label or panel.variable

        plot_single_boreal_panel(
            ax=ax,
            da=da,
            title=panel.title,
            units=panel.units,
            vmax=panel.vmax,
            cmap=cmap,
            extent_lat=extent_lat,
            mean_lat_min=mean_lat_min,
            add_cbar=add_cbar,
            cbar_label=f"{label}\n[{panel.units}]",
            shade_ocean=shade_ocean,
            ocean_alpha=ocean_alpha,
            ocean_facecolor=ocean_facecolor,
        )

    fig.suptitle(
        f"{experiment}: radiative forcing decomposition ({start_year}–{end_year})",
        fontsize=14,
        fontweight="bold",
        y=1.03,
    )

    if save:
        figdir.mkdir(parents=True, exist_ok=True)
        path = figdir / f"{experiment}_forcing_decomposition_{start_year}_{end_year}.png"
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        print(f"Saved {path}")

    return fig, axes


def make_context_maps_figure(
    experiment: str,
    start_year: int,
    end_year: int,
    panels: Iterable[MapPanel] = CONTEXT_PANELS,
    extent_lat: float = 45.0,
    mean_lat_min: float | None = 45.0,
    figsize: tuple[float, float] = (13, 13),
    ncols: int = 3,
    save: bool = True,
    figdir: Path = FIGURE_DIR,
    dpi: int = 300,
    cmap: str = "RdBu_r",
    add_cbar: bool = True,
    shade_ocean: bool = True,
    ocean_alpha: float = 0.75,
    ocean_facecolor: str = "white",
):
    """
    Create BVOC/SOA/cloud/context map figure for LCC-X - LCC-X-fBVOC.

    Each panel gets its own colourbar when add_cbar=True.
    Ocean shading is controlled by shade_ocean, ocean_alpha, and ocean_facecolor.
    """
    if experiment not in BVOC_PAIRS:
        raise ValueError(f"experiment must be one of {list(BVOC_PAIRS)}")

    pairs = BVOC_PAIRS[experiment]
    panels = list(panels)
    nrows = int(np.ceil(len(panels) / ncols))

    fig, axes = plt.subplots(
        nrows,
        ncols,
        figsize=figsize,
        subplot_kw={"projection": ccrs.Orthographic(0, 90)},
        constrained_layout=True,
    )

    axes = np.asarray(axes).ravel()

    for ax, panel in zip(axes, panels):
        case1 = pairs[panel.case1_role]
        case2 = pairs[panel.case2_role]

        try:
            da = panel_difference_map(
                case1=case1,
                case2=case2,
                variable_class=panel.variable_class,
                variable=panel.variable,
                start_year=start_year,
                end_year=end_year,
            )
        except Exception as exc:
            ax.set_axis_off()
            ax.set_title(f"{panel.title}\nmissing", fontsize=9)
            print(f"Skipping {panel.key}: {exc}")
            continue

        vmax = panel.vmax or symmetric_vmax(da)

        plot_single_boreal_panel(
            ax=ax,
            da=da,
            title=panel.title,
            units=panel.units,
            vmax=vmax,
            cmap=cmap,
            extent_lat=extent_lat,
            mean_lat_min=mean_lat_min,
            add_cbar=add_cbar,
            cbar_label=f"{panel.long_label or panel.variable}\n[{panel.units}]",
            shade_ocean=shade_ocean,
            ocean_alpha=ocean_alpha,
            ocean_facecolor=ocean_facecolor,
        )

    for ax in axes[len(panels):]:
        ax.set_axis_off()

    fig.suptitle(
        f"{experiment}: BVOC/SOA/cloud context maps ({start_year}–{end_year})",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )

    if save:
        figdir.mkdir(parents=True, exist_ok=True)
        path = figdir / f"{experiment}_bvoc_context_maps_{start_year}_{end_year}.png"
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        print(f"Saved {path}")

    return fig, axes