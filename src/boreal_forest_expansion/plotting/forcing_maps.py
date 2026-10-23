"""
Forcing and BVOC-context map plotting utilities.

Reads the monthly files written by the postprocess package (postprocess/run_all_parallel.sh):

    [alias]_[component]_[category]_[startyr]-[endyr].nc

in data/processed-data/postprocessing, e.g. LCC_PD_atm_RADIATIVE_2001-2009.nc.
Each file holds monthly means (time = midpoint of the time bounds, spin-up dropped).

Maps show the mean over years of paired yearly differences (case1 - case2). The members
are nudged to the same winds, so year y of case1 is compared with year y of case2.
Stippling marks cells where the paired t-test passes the Benjamini-Hochberg false
discovery rate (alpha_FDR = 0.10, Wilks 2016), counted over the cells drawn on the map.
The text under each panel is the area-weighted mean north of `mean_lat_min`, with a 95%
t-interval across the yearly regional means.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import xarray as xr
from scipy import stats

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.util import add_cyclic_point

from boreal_forest_expansion.plotting.common import (
    ax_map_properties,
    cut_extent_Orthographic,
)
from boreal_forest_expansion.postprocess.averaging import record_days
from boreal_forest_expansion.analysis.stats import cellwise_pvalue, fdr_mask


REPO_DIR = Path("/cluster/home/adelez/BOREAL-FOREST-EXPANSION")

POSTPROCESSED_DIR = REPO_DIR / "data" / "processed-data" / "postprocessing"

FIGURE_DIR = REPO_DIR / "results" / "figures"


# =============================================================================
# Case and plot definitions
# =============================================================================

# Total = lcc - ctrl, BVOC = lcc - fbvoc. Each period uses its own CTRL, so the FUT
# total does not contain the 2100 background (SST, GHG, emissions) change.
# fbvoc alias suffix = run the prescribed emissions come from; _IM = ISOP and MTERP only.
# LCC_FUT_fBVOC_PD_IM is fixed at CTRL_PD, so BVOC_FUT = LCC + climate change. Switch to
# LCC_PD_fBVOC_PD / LCC_FUT_fBVOC_FUT (all 19 MEGAN species) once those runs exist.
# The processed files still carry the old aliases LCC_{PD,FUT}_fBVOC (= the _PD_IM runs);
# switch to the _PD_IM names once the files are renamed.
BVOC_PAIRS = {
    "PD": {
        "lcc": "LCC_PD",
        "fbvoc": "LCC_PD_fBVOC",
        "ctrl": "CTRL_PD",
    },
    "FUT": {
        "lcc": "LCC_FUT",
        "fbvoc": "LCC_FUT_fBVOC",
        "ctrl": "CTRL_FUT",
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
    component: str = "atm"


def forcing_panels(band: str = "NET") -> list[MapPanel]:
    """Six-panel forcing layout; `band` = "NET", "SW" or "LW" selects the Ghan terms."""
    if band not in ("NET", "SW", "LW"):
        raise ValueError("band must be 'NET', 'SW' or 'LW'")
    b = band
    return [
        MapPanel(
            key="albedo",
            title="ALBEDO / SW CLEAR-SKY FORCING",
            variable_class="RADIATIVE",
            variable="SFC_ALBEDO_FORCING_CLEAR",  # f"SW_clearclean" also holds other clear-sky changes (e.g. chemistry)
            case1_role="lcc",
            case2_role="ctrl",
            long_label="Clear-sky surface albedo forcing (proxy)",
            vmax=10.0,
        ),
        MapPanel(
            key="total",
            title=f"TOTAL RADIATIVE FORCING ({b})",
            variable_class="RADIATIVE",
            variable=f"{b}_toa",
            case1_role="lcc",
            case2_role="ctrl",
            long_label=f"{b} TOA radiative forcing",
            vmax=6.0,
        ),
        MapPanel(
            key="bvoc_total",
            title=f"BVOC-RELATED FORCING ({b})",
            variable_class="RADIATIVE",
            variable=f"{b}_toa",
            case1_role="lcc",
            case2_role="fbvoc",
            long_label=f"{b} BVOC-related radiative forcing",
            vmax=2.0,
        ),
        MapPanel(
            key="bvoc_cloud",
            title=f"BVOC-SOA-CLOUD FORCING ({b})",
            variable_class="RADIATIVE",
            variable=f"{b}_cre_clean",
            case1_role="lcc",
            case2_role="fbvoc",
            long_label=f"{b} cloud-mediated BVOC/SOA forcing",
            vmax=2.0,
        ),
        MapPanel(
            key="bvoc_direct",
            title=f"BVOC-DIRECT SOA FORCING ({b})",
            variable_class="RADIATIVE",
            variable=f"{b}_dir",
            case1_role="lcc",
            case2_role="fbvoc",
            long_label=f"{b} direct aerosol/SOA forcing",
            vmax=2.0,
        ),
        MapPanel(
            key="bvoc_residual",
            title=f"BVOC CHEMISTRY / RESIDUAL FORCING ({b})",
            variable_class="RADIATIVE",
            variable=f"{b}_clearclean",
            case1_role="lcc",
            case2_role="fbvoc",
            long_label=f"{b} clean clear-sky residual forcing",
            vmax=2.0,
        ),
    ]


FORCING_PANELS = forcing_panels("NET")


CONTEXT_PANELS = [
    MapPanel(
        key="sfisop",
        title="ISOPRENE EMISSIONS",
        variable_class="BVOC",
        variable="SFISOP_mgm2d",
        case1_role="lcc",
        case2_role="fbvoc",
        units="mg m$^{-2}$ d$^{-1}$",
        long_label="Surface isoprene flux",
    ),
    MapPanel(
        key="sfmterp",
        title="MONOTERPENE EMISSIONS",
        variable_class="BVOC",
        variable="SFMTERP_mgm2d",
        case1_role="lcc",
        case2_role="fbvoc",
        units="mg m$^{-2}$ d$^{-1}$",
        long_label="Surface monoterpene flux",
    ),
    MapPanel(
        key="soa_tot",
        title="TOTAL SOA BURDEN",
        variable_class="SOA",
        variable="SOA_cb_mgm2",
        case1_role="lcc",
        case2_role="fbvoc",
        units="mg m$^{-2}$",
        long_label="SOA column burden (A1 + NA, interstitial)",
    ),
    MapPanel(
        key="n_aer",
        title="AEROSOL NUMBER",
        variable_class="SOA",
        variable="N_AER",
        case1_role="lcc",
        case2_role="fbvoc",
        units="cm$^{-3}$",
        long_label="Aerosol number, lowest model level",
    ),
    MapPanel(
        key="fctl",
        title="LIQUID CLOUD FRACTION",
        variable_class="CLOUDPROP",
        variable="FCTL",
        case1_role="lcc",
        case2_role="fbvoc",
        units="fraction",
        long_label="Fractional occurrence of cloud-top liquid",
    ),
    MapPanel(
        key="actrel",
        title="ACTIVATED EFFECTIVE RADIUS",
        variable_class="CLOUDPROP",
        variable="ACTREL_incld",
        case1_role="lcc",
        case2_role="fbvoc",
        units="µm",
        long_label="In-cloud cloud-top droplet effective radius",
    ),
    MapPanel(
        key="actnl",
        title="ACTIVATED DROPLET NUMBER",
        variable_class="CLOUDPROP",
        variable="ACTNL_incld",
        case1_role="lcc",
        case2_role="fbvoc",
        units="cm$^{-3}$",
        long_label="In-cloud cloud-top droplet number",
    ),
    MapPanel(
        key="lwp",
        title="LIQUID WATER PATH",
        variable_class="CLOUDPROP",
        variable="TGCLDLWP_gm2",
        case1_role="lcc",
        case2_role="fbvoc",
        units="g m$^{-2}$",
        long_label="Grid-box cloud liquid water path",
    ),
    MapPanel(
        key="et",
        title="EVAPOTRANSPIRATION",
        variable_class="ET",
        variable="QFLX_mmday",
        case1_role="lcc",
        case2_role="fbvoc",
        units="mm day$^{-1}$",
        long_label="Evapotranspiration (land)",
        component="lnd",
    ),
]

INCLOUD_MIN_FRAC = 0.01   # same default as postprocess.derived.incloud


# =============================================================================
# Loading
# =============================================================================

def filename(alias: str, variable_class: str, start_year: int, end_year: int,
             component: str = "atm") -> Path:
    return POSTPROCESSED_DIR / f"{alias}_{component}_{variable_class}_{start_year}-{end_year}.nc"


def open_class(alias: str, variable_class: str, start_year: int, end_year: int,
               component: str = "atm") -> xr.Dataset:
    path = filename(alias, variable_class, start_year, end_year, component)
    if not path.exists():
        raise FileNotFoundError(f"Missing postprocessed file: {path}")
    return xr.open_dataset(path)


def to_map(da: xr.DataArray) -> xr.DataArray:
    """Keep (time, lat, lon). 3-D fields use the lowest model level (near-surface)."""
    if "lev" in da.dims:
        da = da.isel(lev=-1)
    extra = [d for d in da.dims if d not in ("time", "lat", "lon")]
    if extra:
        raise ValueError(f"Cannot make map from {da.name}; dimensions are {da.dims}")
    return da


def annual_mean(da: xr.DataArray, ds: xr.Dataset) -> xr.DataArray:
    """Calendar-year means weighted by record length (days); only complete years."""
    days = record_days(ds)
    year = ds["time"].dt.year
    n = days.groupby(year).count()
    if not (n == 12).all():
        raise ValueError(f"Incomplete years in {ds.attrs.get('alias', '?')}: {dict(zip(n.year.values, n.values))}")
    return (da * days).groupby(year).sum("time") / days.groupby(year).sum("time")


def _require(ds: xr.Dataset, names: Iterable[str], what: str):
    missing = [v for v in names if v not in ds]
    if missing:
        raise KeyError(f"{what}: missing {missing} in {ds.attrs.get('alias', '?')} {ds.attrs.get('category', '')}")


def _incloud(ds: xr.Dataset, var: str, scale: float = 1.0) -> xr.DataArray:
    """Yearly in-cloud value: annual_mean(var) / annual_mean(FCTL), as derived.incloud(dim='time')."""
    _require(ds, [var, "FCTL"], f"{var}_incld")
    num, frac = annual_mean(ds[var], ds), annual_mean(ds["FCTL"], ds)
    return (num / frac).where(frac >= INCLOUD_MIN_FRAC) * scale


# Yearly (year, lat, lon) fields derived from one run. Values are converted to plot units.
YEARLY_DERIVED = {
    "SW_toa": lambda ds: annual_mean(ds["FSNT"], ds),
    "LW_toa": lambda ds: annual_mean(-ds["FLNT"], ds),
    "SFISOP_mgm2d": lambda ds: annual_mean(ds["SFISOP"], ds) * 1e6 * 86400,
    "SFMTERP_mgm2d": lambda ds: annual_mean(ds["SFMTERP"], ds) * 1e6 * 86400,
    "SOA_cb_mgm2": lambda ds: annual_mean(ds["SOA_cb"], ds) * 1e6,
    "TGCLDLWP_gm2": lambda ds: annual_mean(ds["TGCLDLWP"], ds) * 1e3,
    "QFLX_mmday": lambda ds: annual_mean(ds["QFLX_EVAP_TOT"], ds) * 86400,
    "ACTREL_incld": lambda ds: _incloud(ds, "ACTREL"),
    "ACTNL_incld": lambda ds: _incloud(ds, "ACTNL", scale=1e-6),          # m-3 -> cm-3
}


def yearly_field(ds: xr.Dataset, variable: str) -> xr.DataArray:
    if variable in YEARLY_DERIVED:
        return YEARLY_DERIVED[variable](ds)
    _require(ds, [variable], variable)
    return annual_mean(to_map(ds[variable]), ds)


def surface_albedo_forcing_proxy(ds1: xr.Dataset, ds2: xr.Dataset) -> xr.DataArray:
    """
    Monthly clear-sky surface albedo forcing proxy for case1 - case2:

        dF = - FSDSC_case2 * (alpha_case1 - alpha_case2),   alpha = (FSDSC - FSNSC) / FSDSC

    Positive = lower albedo, more absorbed shortwave (warming). Computed month by month,
    so the albedo change is weighted by the insolation of that month (snow masking in
    spring counts more than in winter). Surface proxy, not a TOA forcing.
    """
    for ds in (ds1, ds2):
        _require(ds, ["FSDSC", "FSNSC"], "clear-sky surface albedo")

    def alpha(ds):
        return ((ds["FSDSC"] - ds["FSNSC"]) / ds["FSDSC"]).where(ds["FSDSC"] > 1.0)

    # Months without sunlight give NaN albedo but carry no forcing: set them to 0
    return (-ds2["FSDSC"] * (alpha(ds1) - alpha(ds2))).fillna(0.0).where(ds2["FSDSC"].notnull())


def yearly_difference(
    case1: str,
    case2: str,
    variable_class: str,
    variable: str,
    start_year: int,
    end_year: int,
    component: str = "atm",
) -> xr.DataArray:
    """Paired yearly differences case1 - case2, dims (year, lat, lon)."""
    ds1 = open_class(case1, variable_class, start_year, end_year, component)
    ds2 = open_class(case2, variable_class, start_year, end_year, component)
    if not np.array_equal(ds1["time"].values, ds2["time"].values):
        raise ValueError(f"{case1} and {case2} have different time axes")

    if variable == "SFC_ALBEDO_FORCING_CLEAR":
        diff = annual_mean(surface_albedo_forcing_proxy(ds1, ds2), ds2)
        units = "W m-2"
    else:
        diff = yearly_field(ds1, variable) - yearly_field(ds2, variable)
        units = ds1[variable].attrs.get("units", "") if variable in ds1 else ""

    diff.name = f"{variable}_{case1}_minus_{case2}"
    diff.attrs.update(units=units, long_name=f"{variable}: {case1} - {case2}")
    return diff


def difference_map(*args, **kwargs) -> xr.DataArray:
    """Mean over years of yearly_difference (same arguments)."""
    d = yearly_difference(*args, **kwargs)
    return d.mean("year").assign_attrs(d.attrs).rename(d.name)


# =============================================================================
# Statistics
# =============================================================================

# Cell-wise t-test and FDR: boreal_forest_expansion.analysis.stats (cellwise_pvalue, fdr_mask)

def area_weighted_mean(da, lat_min=None, lat_max=None, dims=("lat", "lon")):
    """
    Area-weighted mean for regular lat-lon data (cos-lat weights; NaN cells skipped,
    so land-only fields give a land mean).
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


def regional_mean_interval(d: xr.DataArray, lat_min=None, conf: float = 0.95):
    """Mean and t-interval half-width of the yearly regional means of `d` (year, lat, lon)."""
    r = area_weighted_mean(d, lat_min=lat_min).values
    n = r.size
    half = stats.t.ppf(0.5 + conf / 2, n - 1) * r.std(ddof=1) / np.sqrt(n)
    return float(r.mean()), float(half)


# =============================================================================
# Plotting helpers
# =============================================================================

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

    if abs(value) >= 1:
        return f"{value:+.1f}"
    elif abs(value) >= 0.01 or value == 0:
        return f"{value:+.2f}"
    else:
        return f"{value:+.1e}"


def _format_interval(mean: float, half: float) -> str:
    if abs(mean) >= 1 or half >= 1:
        return f"{mean:+.1f} ± {half:.1f}"
    if abs(mean) >= 0.01 or half >= 0.01:
        return f"{mean:+.2f} ± {half:.2f}"
    return f"{mean:+.1e} ± {half:.0e}"


def add_stippling(ax, sig: xr.DataArray, style: str = "dots", color="black", size: float = 0.6,
                  zorder=4):
    """Mark the cells where `sig` is True.

    style:
        "dots"    small dot at each marked cell centre; longitudes are thinned with
                  1/cos(lat) so the dot spacing stays roughly even towards the pole
        "contour" thin outline around marked areas
        "hatch"   dense dotted hatching of marked areas (old look)
        "lines"   thin dense diagonal lines (/////, line width 0.3); default colour dim grey.
                  The forcing maps use it on the NON-significant cells (IPCC AR6 look).
    """
    lat, lon = sig["lat"].values, sig["lon"].values
    if style == "dots":
        stride = np.maximum(1, np.round(1 / np.cos(np.deg2rad(np.clip(np.abs(lat), 0, 87)))).astype(int))
        keep = (np.arange(lon.size)[None, :] % stride[:, None]) == 0
        yy, xx = np.nonzero(sig.values & keep)
        ax.scatter(lon[xx], lat[yy], s=size, c=color, linewidths=0, alpha=0.7,
                   transform=ccrs.PlateCarree(), zorder=zorder)
        return
    data, lon_c = add_cyclic_point(sig.astype(float).values, coord=lon)
    if style == "contour":
        ax.contour(lon_c, lat, data, levels=[0.5], colors=color, linewidths=0.5,
                   transform=ccrs.PlateCarree(), zorder=zorder)
    elif style in ("hatch", "lines"):
        cs = ax.contourf(lon_c, lat, np.where(data > 0.5, 1.0, np.nan), levels=[0.5, 1.5],
                         colors="none", hatches=["...." if style == "hatch" else "/////"],
                         transform=ccrs.PlateCarree(), zorder=zorder)
        cs.set_edgecolor("dimgrey" if style == "lines" and color == "black" else color)
        cs.set_linewidth(0.0)
        if style == "lines":
            cs.set_hatch_linewidth(0.3)
    else:
        raise ValueError(f"unknown stippling style {style!r}")


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
    shade_ocean: bool = False,
    ocean_alpha: float = 0.75,
    ocean_facecolor: str = "white",
    ocean_zorder: int = 2,
    sig: xr.DataArray | None = None,
    sig_style: str = "dots",
    mean_text: str | None = None,
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
    sig:
        Boolean map; True cells are marked (drawn above the ocean shading).
    sig_style:
        "dots", "contour", "hatch" or "lines", see add_stippling.
    mean_text:
        Text under the panel; default is the area-weighted mean of `da`.
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

    if sig is not None and bool(sig.any()):
        add_stippling(ax, sig, style=sig_style, zorder=ocean_zorder + 2)

    ax.set_title(
        title,
        fontsize=9.5,
        fontweight="semibold",
        pad=5,
    )

    unit_text = units or da.attrs.get("units", "")
    if mean_text is None:
        mean_text = f"mean: {format_forcing_mean(area_weighted_mean(da, lat_min=mean_lat_min))}"

    ax.text(
        0.5,
        -0.12,
        f"{mean_text} {unit_text}",
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


def _plot_panel(ax, panel, pairs, start_year, end_year, extent_lat, mean_lat_min,
                stipple, fdr_alpha, vmax=None, **kwargs):
    """Compute and draw one panel; returns the yearly differences."""
    case1, case2 = pairs[panel.case1_role], pairs[panel.case2_role]
    d = yearly_difference(case1, case2, panel.variable_class, panel.variable,
                          start_year, end_year, panel.component)
    da = d.mean("year")

    sig = None
    if stipple:   # True or a style name: "lines" (default), "dots", "contour", "hatch"
        p = cellwise_pvalue(d)
        region = d["lat"] >= extent_lat
        sig = fdr_mask(p, alpha=fdr_alpha, within=region)
        kwargs["sig_style"] = "lines" if stipple is True else stipple
        if kwargs["sig_style"] == "lines":   # "lines" marks the NON-significant cells
            sig = (~sig) & np.isfinite(p) & region

    m, half = regional_mean_interval(d, lat_min=mean_lat_min)
    region = f"≥{mean_lat_min:g}°N" if mean_lat_min is not None else "global"
    plot_single_boreal_panel(
        ax=ax,
        da=da,
        title=panel.title,
        units=panel.units,
        vmax=vmax or panel.vmax or symmetric_vmax(da),
        extent_lat=extent_lat,
        mean_lat_min=mean_lat_min,
        cbar_label=f"{panel.long_label or panel.variable}\n[{panel.units}]",
        sig=sig,
        mean_text=f"mean {region}: {_format_interval(m, half)}",
        **kwargs,
    )
    return d


# =============================================================================
# Composite figures
# =============================================================================

def make_forcing_summary_figure(
    experiment: str,
    start_year: int,
    end_year: int,
    band: str = "NET",
    extent_lat: float = 45.0,
    mean_lat_min: float | None = 45.0,
    figsize: tuple[float, float] = (19, 5.2),
    save: bool = True,
    figdir: Path = FIGURE_DIR,
    dpi: int = 300,
    cmap: str = "RdBu_r",
    add_cbar: bool = True,
    shade_ocean: bool = False,
    ocean_alpha: float = 0.75,
    ocean_facecolor: str = "white",
    transparent_background: bool = True,
    stipple: bool | str = True,
    fdr_alpha: float = 0.10,
):
    """
    Create six-panel forcing decomposition figure.

    experiment:
        "PD" or "FUT"
    band:
        "NET", "SW" or "LW" for the five Ghan panels (the albedo proxy is always SW).

    Ocean shading can be regulated with:
        shade_ocean=True/False
        ocean_alpha=0.0 to 1.0
        ocean_facecolor="white", "lightgrey", etc.

    Each panel gets its own individual colourbar when add_cbar=True.
    """
    if experiment not in BVOC_PAIRS:
        raise ValueError(f"experiment must be one of {list(BVOC_PAIRS)}")

    pairs = BVOC_PAIRS[experiment]
    panels = forcing_panels(band)

    fig, axes = plt.subplots(
        1,
        len(panels),
        figsize=figsize,
        subplot_kw={"projection": ccrs.Orthographic(0, 90)},
        constrained_layout=True,
    )

    for ax, panel in zip(axes, panels):
        _plot_panel(
            ax, panel, pairs, start_year, end_year, extent_lat, mean_lat_min,
            stipple, fdr_alpha,
            cmap=cmap,
            add_cbar=add_cbar,
            shade_ocean=shade_ocean,
            ocean_alpha=ocean_alpha,
            ocean_facecolor=ocean_facecolor,
        )

    fig.suptitle(
        f"{experiment}: radiative forcing decomposition, {band} ({start_year}–{end_year})",
        fontsize=14,
        fontweight="bold",
        y=1.03,
    )

    if save:
        figdir.mkdir(parents=True, exist_ok=True)
        path = figdir / f"{experiment}_forcing_decomposition_{band}_{start_year}_{end_year}.png"
        fig.savefig(path, dpi=dpi, bbox_inches="tight", transparent=transparent_background)
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
    shade_ocean: bool = False,
    ocean_alpha: float = 0.75,
    ocean_facecolor: str = "white",
    stipple: bool | str = True,
    fdr_alpha: float = 0.10,
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
        try:
            _plot_panel(
                ax, panel, pairs, start_year, end_year, extent_lat, mean_lat_min,
                stipple, fdr_alpha,
                cmap=cmap,
                add_cbar=add_cbar,
                shade_ocean=shade_ocean,
                ocean_alpha=ocean_alpha,
                ocean_facecolor=ocean_facecolor,
            )
        except (FileNotFoundError, KeyError) as exc:
            ax.set_axis_off()
            ax.set_title(f"{panel.title}\nmissing", fontsize=9)
            print(f"Skipping {panel.key}: {exc}")
            continue

    for ax in axes[len(panels):]:
        ax.set_axis_off()

    fig.suptitle(
        f"{experiment}: BVOC/SOA/cloud context maps, LCC − LCC_fBVOC ({start_year}–{end_year})",
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
