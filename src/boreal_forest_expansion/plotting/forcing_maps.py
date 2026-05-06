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
        variable="SFC_ALBEDO_FORCING_CLEAR",#"SW_rest_Ghan",
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
        vmax=1e-11,
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
    ocean_alpha: float = 0.45,
):
    if vmax is None:
        vmax = symmetric_vmax(da)

    norm = mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)

    cut_extent_Orthographic(ax, lat=extent_lat)

    # Background land/coast setup, below the data
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

    # Plot the actual data
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

    # Semi-transparent ocean overlay ABOVE the data
    ax.add_feature(
        cfeature.OCEAN,
        facecolor="white",
        edgecolor="none",
        alpha=ocean_alpha,
        zorder=2,
    )

    # Coastlines above both data and ocean shading
    ax.coastlines(linewidth=0.6, zorder=3)

    ax.set_title(title, fontsize=10, fontweight="bold", pad=4)

    mean_val = area_weighted_mean(da, lat_min=mean_lat_min)
    unit_text = units or da.attrs.get("units", "")

    ax.text(
        0.5,
        -0.18,
        f"{mean_val:+.3g} {unit_text}",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=9,
        fontweight="bold",
        color="dimgray",
    )

    if add_cbar:
        cb = plt.colorbar(
            p,
            ax=ax,
            orientation="horizontal",
            pad=0.04,
            shrink=0.86,
            aspect=28,
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
        cb.set_label(cbar_label, fontsize=7)

    return p


# =============================================================================
# Composite figures
# =============================================================================

def make_forcing_summary_figure(
    experiment: str,
    start_year: int,
    end_year: int,
    extent_lat: float = 45.0,
    mean_lat_min: float | None = 45.0,
    figsize: tuple[float, float] = (18, 4.2),
    save: bool = True,
    figdir: Path = FIGURE_DIR,
    dpi: int = 300,
):
    """
    Create six-panel forcing decomposition figure.

    experiment:
        "PD" or "FUT"
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
            extent_lat=extent_lat,
            mean_lat_min=mean_lat_min,
            cbar_label=f"{label}\n[{panel.units}]",
        )

    fig.suptitle(
        f"{experiment}: radiative forcing decomposition ({start_year}–{end_year})",
        fontsize=14,
        fontweight="bold",
        y=1.05,
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
    figsize: tuple[float, float] = (13, 12),
    ncols: int = 3,
    save: bool = True,
    figdir: Path = FIGURE_DIR,
    dpi: int = 300,
):
    """
    Create BVOC/SOA/cloud/context map figure for LCC-X - LCC-X-fBVOC.
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
            da = difference_map(
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
            extent_lat=extent_lat,
            mean_lat_min=mean_lat_min,
            cbar_label=f"{panel.long_label or panel.variable}\n[{panel.units}]",
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