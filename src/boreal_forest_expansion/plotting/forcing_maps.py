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

from dataclasses import dataclass, replace
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
from boreal_forest_expansion.analysis.regions import load_modified_cells


REPO_DIR = Path("/cluster/home/adelez/BOREAL-FOREST-EXPANSION")

POSTPROCESSED_DIR = REPO_DIR / "data" / "processed-data" / "postprocessing"

FIGURE_DIR = REPO_DIR / "results" / "figures"


# =============================================================================
# Case and plot definitions
# =============================================================================

# Total = lcc - ctrl, BVOC = lcc - fbvoc. Each period uses its own CTRL, so the FUT
# total does not contain the 2100 background (SST, GHG, emissions) change.
# fbvoc alias = LCC_<PERIOD>_fBVOC<source run>[_IM]; _IM = ISOP and MTERP only.
# LCC_FUT_fBVOCctrlPD(_IM) is fixed at CTRL_PD, so BVOC_FUT = LCC + climate change; the
# LCC-only FUT contrast needs LCC_FUT_fBVOCctrlFUT (all 19 MEGAN species).
# The processed files of the fBVOCctrlPD_IM runs keep their on-disk names LCC_{PD,FUT}_fBVOC (no rename);
# they move to 2001-2009-pre-co2-fix/ when the 2001-2014 runs (incl. 14c/24c/24d) are postprocessed;
# then switch fbvoc to the new aliases.
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
    months: tuple[int, ...] | None = None   # None = annual; e.g. (3, 4, 5) = MAM


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


SEASONS = {"DJF": (12, 1, 2), "MAM": (3, 4, 5), "JJA": (6, 7, 8), "SON": (9, 10, 11)}


def annual_mean(da: xr.DataArray, ds: xr.Dataset, months=None) -> xr.DataArray:
    """Calendar-year means weighted by record length (days); only complete years.

    `months` restricts the mean to those months of each calendar year (e.g. SEASONS["MAM"]).
    DJF = Jan + Feb + Dec of the SAME year, so every year keeps its pair in the other run.
    """
    days = record_days(ds)
    if months is not None:
        keep = ds["time"].dt.month.isin(list(months))
        da, days = da.isel(time=keep.values), days.isel(time=keep.values)
    year = days["time"].dt.year
    n = days.groupby(year).count()
    if not (n == (12 if months is None else len(months))).all():
        raise ValueError(f"Incomplete years in {ds.attrs.get('alias', '?')}: {dict(zip(n.year.values, n.values))}")
    return (da * days).groupby(year).sum("time") / days.groupby(year).sum("time")


def _require(ds: xr.Dataset, names: Iterable[str], what: str):
    missing = [v for v in names if v not in ds]
    if missing:
        raise KeyError(f"{what}: missing {missing} in {ds.attrs.get('alias', '?')} {ds.attrs.get('category', '')}")


def _incloud(ds: xr.Dataset, var: str, scale: float = 1.0, months=None) -> xr.DataArray:
    """Yearly in-cloud value: annual_mean(var) / annual_mean(FCTL), as derived.incloud(dim='time')."""
    _require(ds, [var, "FCTL"], f"{var}_incld")
    num, frac = annual_mean(ds[var], ds, months), annual_mean(ds["FCTL"], ds, months)
    return (num / frac).where(frac >= INCLOUD_MIN_FRAC) * scale


def _ratio(ds, num, den, months, min_den):
    """Yearly ratio of month-weighted means (not the mean of monthly ratios)."""
    _require(ds, [num, den], f"{num}/{den}")
    n, d = annual_mean(ds[num], ds, months), annual_mean(ds[den], ds, months)
    return (n / d).where(abs(d) >= min_den)


# Yearly (year, lat, lon) fields derived from one run: f(ds, months). Values are converted to plot units.
YEARLY_DERIVED = {
    "SW_toa": lambda ds, mo: annual_mean(ds["FSNT"], ds, mo),
    "LW_toa": lambda ds, mo: annual_mean(-ds["FLNT"], ds, mo),
    "SFISOP_mgm2d": lambda ds, mo: annual_mean(ds["SFISOP"], ds, mo) * 1e6 * 86400,
    "SFMTERP_mgm2d": lambda ds, mo: annual_mean(ds["SFMTERP"], ds, mo) * 1e6 * 86400,
    "SOA_cb_mgm2": lambda ds, mo: annual_mean(ds["SOA_cb"], ds, mo) * 1e6,
    "TGCLDLWP_gm2": lambda ds, mo: annual_mean(ds["TGCLDLWP"], ds, mo) * 1e3,
    "QFLX_mmday": lambda ds, mo: annual_mean(ds["QFLX_EVAP_TOT"], ds, mo) * 86400,
    "ACTREL_incld": lambda ds, mo: _incloud(ds, "ACTREL", months=mo),
    "ACTNL_incld": lambda ds, mo: _incloud(ds, "ACTNL", scale=1e-6, months=mo),   # m-3 -> cm-3
    # Hydrology and surface (mm/s and m/s -> mm/day; s -> days)
    "PRECT_mmday": lambda ds, mo: annual_mean(ds["PRECC"] + ds["PRECL"], ds, mo) * 1e3 * 86400,
    "QRUNOFF_mmday": lambda ds, mo: annual_mean(ds["QRUNOFF"], ds, mo) * 86400,
    "QSNOMELT_mmday": lambda ds, mo: annual_mean(ds["QSNOMELT"], ds, mo) * 86400,
    "SNOW_PERSISTENCE_days": lambda ds, mo: annual_mean(ds["SNOW_PERSISTENCE"], ds, mo) / 86400,
    "ALBEDO": lambda ds, mo: _ratio(ds, "FSR", "FSDS", mo, min_den=1.0),          # CLM surface albedo
    "BOWEN": lambda ds, mo: _ratio(ds, "SHFLX", "LHFLX", mo, min_den=5.0),
    "FSDS_cloud": lambda ds, mo: annual_mean(ds["FSDS"] - ds["FSDSC"], ds, mo),
    "FSDS_aer": lambda ds, mo: annual_mean(ds["FSDS"] - ds["FSDS_DRF"], ds, mo),
}


def yearly_field(ds: xr.Dataset, variable: str, months=None) -> xr.DataArray:
    if variable in YEARLY_DERIVED:
        return YEARLY_DERIVED[variable](ds, months)
    _require(ds, [variable], variable)
    return annual_mean(to_map(ds[variable]), ds, months)


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
    months=None,
) -> xr.DataArray:
    """Paired yearly differences case1 - case2, dims (year, lat, lon); `months` as in annual_mean."""
    ds1 = open_class(case1, variable_class, start_year, end_year, component)
    ds2 = open_class(case2, variable_class, start_year, end_year, component)
    if not np.array_equal(ds1["time"].values, ds2["time"].values):
        raise ValueError(f"{case1} and {case2} have different time axes")

    if variable == "SFC_ALBEDO_FORCING_CLEAR":
        diff = annual_mean(surface_albedo_forcing_proxy(ds1, ds2), ds2, months)
        units = "W m-2"
    else:
        diff = yearly_field(ds1, variable, months) - yearly_field(ds2, variable, months)
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


def panel_difference(panel, pairs, start_year, end_year) -> xr.DataArray:
    """Paired yearly differences (year, lat, lon) for one panel."""
    return yearly_difference(pairs[panel.case1_role], pairs[panel.case2_role], panel.variable_class,
                             panel.variable, start_year, end_year, panel.component, panel.months)


def _plot_panel(ax, panel, pairs, start_year, end_year, extent_lat, mean_lat_min,
                stipple, fdr_alpha, vmax=None, d=None, **kwargs):
    """Compute (unless `d` is given) and draw one panel; returns the yearly differences."""
    if d is None:
        d = panel_difference(panel, pairs, start_year, end_year)
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


# =============================================================================
# Ghan decomposition per contrast (total + 3 terms, shared colour scale)
# =============================================================================

GHAN_CONTRASTS = {"total": ("lcc", "ctrl", "LCC-CTRL"), "bvoc": ("lcc", "fbvoc", "LCC-fBVOC"),
                  "fbvoc_ctrl": ("fbvoc", "ctrl", "fBVOC-CTRL")}


def ghan_panels(band: str = "NET", case1_role: str = "lcc", case2_role: str = "ctrl",
                months=None) -> list[MapPanel]:
    """Total + the three Ghan (2013) terms; d(total) = d(dir) + d(cre_clean) + d(clearclean)."""
    if band not in ("NET", "SW", "LW"):
        raise ValueError("band must be 'NET', 'SW' or 'LW'")
    terms = [
        ("toa", "TOTAL", "TOA radiative effect"),
        ("dir", "AEROSOL–RADIATION (ARI)", "direct aerosol term"),
        ("cre_clean", "CLOUD (clean-sky CRE)", "clean-sky cloud term"),
        ("clearclean", "CLEAR-CLEAN (albedo, gases, T)", "clear-sky clean term"),
    ]
    return [MapPanel(key=f"{band}_{t}", title=f"{title} ({band})", variable_class="RADIATIVE",
                     variable=f"{band}_{t}", case1_role=case1_role, case2_role=case2_role,
                     long_label=f"{band} {label}", months=months)
            for t, title, label in terms]


def _shared_vmax(ds_list, extent_lat, q=0.98):
    values = np.concatenate([d.mean("year").where(d["lat"] >= extent_lat).values.ravel() for d in ds_list])
    return symmetric_vmax(xr.DataArray(values), q=q)


def _ghan_closure(ds_list, label=""):
    """Max |d(dir) + d(cre_clean) + d(clearclean) - d(total)| over all cells and years."""
    tot, *terms = ds_list
    err = float(abs(sum(terms) - tot).max())
    print(f"Ghan closure {label}: max |sum of terms - total| = {err:.1e} W m-2")
    if err > 1e-3:
        raise ValueError(f"Ghan terms do not add up to the total ({label}): {err}")
    return err


def make_ghan_figure(
    experiment: str,
    contrast: str = "total",
    band: str = "NET",
    start_year: int = 2001,
    end_year: int = 2009,
    seasonal: bool = False,
    extent_lat: float = 45.0,
    mean_lat_min: float | None = 45.0,
    save: bool = True,
    figdir: Path = FIGURE_DIR,
    dpi: int = 300,
    cmap: str = "RdBu_r",
    stipple: bool | str = True,
    fdr_alpha: float = 0.10,
):
    """
    Ghan decomposition of one contrast: total + ARI + cloud + clear-clean, one shared scale.

    contrast: "total" (LCC - CTRL) or "bvoc" (LCC - LCC_fBVOC), roles from BVOC_PAIRS.
    seasonal: False = one row of annual means; True = rows DJF/MAM/JJA/SON, one scale per row.
    """
    role1, role2, tag = GHAN_CONTRASTS[contrast]
    pairs = BVOC_PAIRS[experiment]
    rows = list(SEASONS.items()) if seasonal else [("ANN", None)]

    fig, axes = plt.subplots(len(rows), 4, figsize=(15, 4.6 * len(rows)), squeeze=False,
                             subplot_kw={"projection": ccrs.Orthographic(0, 90)},
                             constrained_layout=True)
    for i, (season, months) in enumerate(rows):
        panels = ghan_panels(band, role1, role2, months)
        diffs = [panel_difference(p, pairs, start_year, end_year) for p in panels]
        _ghan_closure(diffs, f"{experiment} {tag} {band} {season}")
        vmax = _shared_vmax(diffs, extent_lat)
        for j, (ax, panel, d) in enumerate(zip(axes[i], panels, diffs)):
            _plot_panel(ax, panel, pairs, start_year, end_year, extent_lat, mean_lat_min,
                        stipple, fdr_alpha, vmax=vmax, d=d, cmap=cmap, add_cbar=False)
            if seasonal:
                ax.set_title(f"{season}: {panel.title}", fontsize=9.5, fontweight="semibold", pad=5)
        sm = plt.cm.ScalarMappable(norm=mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax), cmap=cmap)
        cb = fig.colorbar(sm, ax=list(axes[i]), orientation="vertical" if seasonal else "horizontal",
                          shrink=0.8 if seasonal else 0.45, aspect=25, extend="both", pad=0.02 if seasonal else 0.1)
        cb.set_label(f"{band} radiative effect difference [W m$^{{-2}}$]", fontsize=8)
        cb.ax.tick_params(labelsize=7)

    c1, c2 = pairs[role1], pairs[role2]
    kind = "seasonal " if seasonal else ""
    fig.suptitle(f"{experiment}: {kind}Ghan decomposition, {band}, {c1} − {c2} ({start_year}–{end_year})",
                 fontsize=14, fontweight="bold")
    if save:
        figdir.mkdir(parents=True, exist_ok=True)
        stem = f"{experiment}_ghan_{'seasonal_' if seasonal else ''}{tag}_{band}_{start_year}_{end_year}.png"
        fig.savefig(figdir / stem, dpi=dpi, bbox_inches="tight")
        print(f"Saved {figdir / stem}")
    return fig, axes


# =============================================================================
# Contrast grids: rows = contrasts, columns = variables
# =============================================================================

def contrast_sets() -> dict[str, list[tuple[str, str]]]:
    """(case1, case2) rows of the contrast grids, built from BVOC_PAIRS."""
    pd_, fut = BVOC_PAIRS["PD"], BVOC_PAIRS["FUT"]
    return {
        # CTRL_FUT - CTRL_PD = background change alone, so row 3 ~ row 2 + row 4
        "LCC-CTRL": [(pd_["lcc"], pd_["ctrl"]), (fut["lcc"], fut["ctrl"]), (fut["lcc"], pd_["ctrl"]),
                     (fut["ctrl"], pd_["ctrl"])],
        "LCC-fBVOC": [(pd_["lcc"], pd_["fbvoc"]), (fut["lcc"], fut["fbvoc"])],
    }


def _panel(key, title, cls, var, units, label, component="atm", months=None):
    return MapPanel(key=key, title=title, variable_class=cls, variable=var, case1_role="case1",
                    case2_role="case2", units=units, long_label=label, component=component, months=months)


MMDAY = "mm day$^{-1}$"
WM2 = "W m$^{-2}$"
MAM = SEASONS["MAM"]

HYDRO_PANELS = [
    _panel("fsds", "SURFACE SHORTWAVE DOWN", "RADIATIVE", "FSDS", WM2, "FSDS (all-sky)"),
    _panel("prect", "PRECIPITATION", "METEO", "PRECT_mmday", MMDAY, "PRECC + PRECL"),
    _panel("et", "EVAPOTRANSPIRATION", "ET", "QFLX_mmday", MMDAY, "QFLX_EVAP_TOT (land)", "lnd"),
    _panel("runoff", "TOTAL RUNOFF", "HYDRO", "QRUNOFF_mmday", MMDAY, "QRUNOFF (land)", "lnd"),
    _panel("snowmelt", "SNOWMELT", "HYDRO", "QSNOMELT_mmday", MMDAY, "QSNOMELT (land)", "lnd"),
    _panel("tws", "TOTAL WATER STORAGE", "HYDRO", "TWS", "mm", "TWS (land)", "lnd"),
    _panel("soilw", "SOIL WATER 0–10 cm", "LAND", "SOILWATER_10CM", "kg m$^{-2}$", "SOILWATER_10CM", "lnd"),
    _panel("lh", "LATENT HEAT FLUX", "METEO", "LHFLX", WM2, "LHFLX (up positive)"),
    _panel("sh", "SENSIBLE HEAT FLUX", "METEO", "SHFLX", WM2, "SHFLX (up positive)"),
    _panel("cldlow", "LOW CLOUD", "CLOUDPROP", "CLDLOW", "fraction", "CLDLOW"),
]

SNOW_ALBEDO_PANELS = [
    _panel("fsno", "SNOW COVER", "SNOW", "FSNO", "fraction", "FSNO (land)", "lnd"),
    _panel("fsno_mam", "SNOW COVER (MAM)", "SNOW", "FSNO", "fraction", "FSNO, MAM (land)", "lnd", MAM),
    _panel("h2osno", "SNOW WATER EQUIVALENT", "SNOW", "H2OSNO", "mm", "H2OSNO (land)", "lnd"),
    _panel("snowpers", "SNOW PERSISTENCE", "SNOW", "SNOW_PERSISTENCE_days", "days",
           "continuous snow cover length (land)", "lnd"),
    _panel("snocan", "CANOPY SNOW", "SNOW", "SNOCAN", "mm", "SNOCAN (land)", "lnd"),
    _panel("albedo_mam", "SURFACE ALBEDO (MAM)", "ENERGY", "ALBEDO", "–", "FSR / FSDS, MAM (land)", "lnd", MAM),
    _panel("tlai", "LEAF AREA INDEX", "LAND", "TLAI", "m$^2$ m$^{-2}$", "TLAI (land)", "lnd"),
]

SURFACE_ENERGY_PANELS = [
    _panel("fsns", "NET SURFACE SHORTWAVE", "RADIATIVE", "FSNS", WM2, "FSNS"),
    _panel("flds", "SURFACE LONGWAVE DOWN", "RADIATIVE", "FLDS", WM2, "FLDS"),
    _panel("ts", "SURFACE TEMPERATURE", "METEO", "TS", "K", "TS"),
    _panel("trefht", "2 m TEMPERATURE", "METEO", "TREFHT", "K", "TREFHT"),
    _panel("lh", "LATENT HEAT FLUX", "METEO", "LHFLX", WM2, "LHFLX (up positive)"),
    _panel("sh", "SENSIBLE HEAT FLUX", "METEO", "SHFLX", WM2, "SHFLX (up positive)"),
    _panel("bowen", "BOWEN RATIO", "METEO", "BOWEN", "–", "SHFLX / LHFLX (|LHFLX| ≥ 5 W m$^{-2}$)"),
]

# The parts are diagnostic differences, not an exact additive split of FSDS.
FSDS_SPLIT_PANELS = [
    _panel("fsds", "FSDS (ALL-SKY)", "RADIATIVE", "FSDS", WM2, "FSDS"),
    _panel("fsdsc", "FSDS CLEAR-SKY", "RADIATIVE", "FSDSC", WM2, "FSDSC"),
    _panel("fsds_cloud", "FSDS CLOUD PART", "RADIATIVE", "FSDS_cloud", WM2, "FSDS − FSDSC"),
    _panel("fsds_aer", "FSDS AEROSOL PART", "RADIATIVE", "FSDS_aer", WM2, "FSDS − FSDS_DRF"),
    _panel("fsdscdrf", "FSDS CLEAR-CLEAN", "RADIATIVE", "FSDSCDRF", WM2, "FSDSCDRF (no cloud, no aerosol)"),
]


def make_contrast_grid_figure(
    contrast_set: str,
    panels: Iterable[MapPanel],
    name: str,
    start_year: int = 2001,
    end_year: int = 2009,
    extent_lat: float = 45.0,
    mean_lat_min: float | None = 45.0,
    panel_size: tuple[float, float] = (2.6, 3.3),
    save: bool = True,
    figdir: Path = FIGURE_DIR,
    dpi: int = 200,
    cmap: str = "RdBu_r",
    stipple: bool | str = True,
    fdr_alpha: float = 0.10,
):
    """
    Grid of maps: one row per contrast of `contrast_set` ("LCC-CTRL" or "LCC-fBVOC", see
    contrast_sets), one column per panel. Each panel has its own colourbar, because the
    rows differ a lot in size (LCC_FUT - CTRL_PD contains the whole 2100 background change).
    """
    rows = contrast_sets()[contrast_set]
    panels = [replace(p, case1_role="case1", case2_role="case2") for p in panels]
    fig, axes = plt.subplots(len(rows), len(panels),
                             figsize=(panel_size[0] * len(panels), panel_size[1] * len(rows)),
                             squeeze=False, subplot_kw={"projection": ccrs.Orthographic(0, 90)},
                             constrained_layout=True)
    for i, (c1, c2) in enumerate(rows):
        pairs = {"case1": c1, "case2": c2}
        for j, (ax, panel) in enumerate(zip(axes[i], panels)):
            try:
                _plot_panel(ax, panel, pairs, start_year, end_year, extent_lat, mean_lat_min,
                            stipple, fdr_alpha, cmap=cmap, add_cbar=True)
            except (FileNotFoundError, KeyError) as exc:
                ax.set_axis_off()
                ax.set_title(f"{panel.title}\nmissing", fontsize=9)
                print(f"Skipping {panel.key} ({c1} − {c2}): {exc}")
            if i > 0:
                ax.set_title("")
            if j == 0:
                ax.text(-0.12, 0.5, f"{c1}\n−\n{c2}", transform=ax.transAxes, rotation=0,
                        ha="right", va="center", fontsize=10, fontweight="bold")

    fig.suptitle(f"{name}: {contrast_set} contrasts ({start_year}–{end_year})",
                 fontsize=15, fontweight="bold")
    if save:
        figdir.mkdir(parents=True, exist_ok=True)
        path = figdir / f"contrast_grid_{name}_{contrast_set}_{start_year}_{end_year}.png"
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        print(f"Saved {path}")
    return fig, axes


# =============================================================================
# Land water budget: P - ET - R - dTWS (all from CLM, same land basis)
# =============================================================================

MODIFIED_CELLS = REPO_DIR / "diagnostics" / "check-simulation-equilibrium" / "lcc-modified-cells" / "modified_cells.nc"
SECONDS_PER_YEAR = 365 * 86400   # noleap calendar
WATER_BUDGET_TERMS = ("P", "ET", "R_liq", "R_ice", "dTWS", "residual")


def _water_budget_fields(alias, start_year, end_year):
    """Yearly (year, lat, lon) terms in mm yr-1. dTWS = TWS(Dec y) - TWS(Dec y-1), so year 1 is dropped."""
    hy = open_class(alias, "HYDRO", start_year, end_year, "lnd")
    et = open_class(alias, "ET", start_year, end_year, "lnd")
    if not np.array_equal(hy["time"].values, et["time"].values):
        raise ValueError(f"{alias}: HYDRO and ET time axes differ")
    terms = {
        "P": annual_mean(hy["RAIN"] + hy["SNOW"], hy) * SECONDS_PER_YEAR,
        "ET": annual_mean(et["QFLX_EVAP_TOT"], et) * SECONDS_PER_YEAR,
        # Runoff sent to the coupler (incl. land-use corrections): liquid and ice (snow capping on
        # glaciers). QRUNOFF alone leaves ~+28 mm/yr unclosed over unmodified land >=45N (PD).
        "R_liq": annual_mean(hy["QRUNOFF_TO_COUPLER"], hy) * SECONDS_PER_YEAR,
        "R_ice": annual_mean(hy["QRUNOFF_ICE_TO_COUPLER"], hy) * SECONDS_PER_YEAR,
    }
    dec = hy["TWS"].isel(time=(hy["time"].dt.month == 12).values)
    dec = dec.assign_coords(year=("time", dec["time"].dt.year.values)).swap_dims(time="year").drop_vars("time")
    terms["dTWS"] = dec.diff("year")                    # label = later year
    years = terms["dTWS"]["year"]
    terms = {k: v.sel(year=years) for k, v in terms.items()}
    terms["residual"] = terms["P"] - terms["ET"] - terms["R_liq"] - terms["R_ice"] - terms["dTWS"]
    weight = (hy["area"] * hy["landfrac"]).fillna(0.0)
    return terms, weight, hy


def water_budget_regions(ds: xr.Dataset, lat_min: float = 45.0) -> dict[str, xr.DataArray]:
    """LCC-modified cells and the unmodified land north of `lat_min`, on the grid of `ds`."""
    modified = load_modified_cells(MODIFIED_CELLS, ds)
    land = ds["landfrac"].fillna(0.0) > 0
    return {"modified cells": modified & land,
            f"unmodified land ≥{lat_min:g}°N": land & ~modified & (ds["lat"] >= lat_min)}


def water_budget_table(start_year: int = 2001, end_year: int = 2009, conf: float = 0.95):
    """
    Regional water budget of every contrast in contrast_sets(): yearly area x landfrac weighted
    means, case values and paired difference with a t-interval across years. mm yr-1.
    """
    import pandas as pd

    aliases = sorted({a for rows in contrast_sets().values() for pair in rows for a in pair})
    data = {a: _water_budget_fields(a, start_year, end_year) for a in aliases}
    regions = water_budget_regions(data[aliases[0]][2])

    def regional(alias, term, mask):
        terms, w, _ = data[alias]
        return terms[term].weighted(w.where(mask, 0.0)).mean(("lat", "lon"))

    rows = []
    for cset, pairs in contrast_sets().items():
        for c1, c2 in pairs:
            for rname, mask in regions.items():
                for term in WATER_BUDGET_TERMS:
                    a, b = regional(c1, term, mask), regional(c2, term, mask)
                    d = (a - b).values
                    half = stats.t.ppf(0.5 + conf / 2, d.size - 1) * d.std(ddof=1) / np.sqrt(d.size)
                    rows.append(dict(contrast_set=cset, contrast=f"{c1} − {c2}", region=rname, term=term,
                                     case1=float(a.mean()), case2=float(b.mean()),
                                     diff=float(d.mean()), ci95=float(half), n_years=d.size,
                                     years=f"{int(a.year[0])}–{int(a.year[-1])}"))
    return pd.DataFrame(rows)


def make_water_budget_figure(table, contrast_set: str, save: bool = True, figdir: Path = FIGURE_DIR,
                             dpi: int = 200, start_year: int = 2001, end_year: int = 2009):
    """Bars of the paired differences (± 95 % CI): one subplot per region, groups = contrasts."""
    t = table[table["contrast_set"] == contrast_set]
    regions, contrasts = list(dict.fromkeys(t["region"])), list(dict.fromkeys(t["contrast"]))
    terms = WATER_BUDGET_TERMS
    colors = ["#3b75af", "#4f9e5a", "#d08a2e", "#7fc6d6", "#8c6bb1", "#9a9a9a"]
    fig, axes = plt.subplots(1, len(regions), figsize=(6.5 * len(regions), 4.2), sharey=True,
                             constrained_layout=True)
    width = 0.8 / len(terms)
    for ax, region in zip(np.atleast_1d(axes), regions):
        for k, (term, color) in enumerate(zip(terms, colors)):
            sub = t[(t["region"] == region) & (t["term"] == term)].set_index("contrast").loc[contrasts]
            x = np.arange(len(contrasts)) + (k - (len(terms) - 1) / 2) * width
            ax.bar(x, sub["diff"], width, yerr=sub["ci95"], color=color, label=term,
                   capsize=2, error_kw=dict(lw=0.8))
        ax.axhline(0, color="black", lw=0.6)
        ax.set_xticks(np.arange(len(contrasts)), [c.replace(" − ", "\n− ") for c in contrasts], fontsize=8)
        ax.set_title(region, fontsize=10, fontweight="semibold")
        ax.set_ylabel("difference [mm yr$^{-1}$]")
    np.atleast_1d(axes)[0].legend(fontsize=8, ncol=len(terms), loc="best")
    fig.suptitle(f"Land water budget P − ET − R_liq − R_ice − ΔTWS, {contrast_set} ({t['years'].iloc[0]})",
                 fontsize=12, fontweight="bold")
    if save:
        path = figdir / f"water_budget_{contrast_set}_{start_year}_{end_year}.png"
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        print(f"Saved {path}")
    return fig, axes


# =============================================================================
# Regional and monthly diagnostics (PD-FUT attribution, analysis/pd-fut-attribution.ipynb)
# =============================================================================

EARTH_RADIUS = 6.371e6   # m
EARLY_YEARS, LATE_YEARS = (2001, 2004), (2006, 2009)
SOURCE_BOXES = {          # lat_min, lat_max, lon_min, lon_max (degrees east; lon_min > lon_max wraps)
    "Alaska/W Canada": (50, 72, 190, 245),
    "E Canada": (45, 65, 245, 300),
    "Europe": (45, 72, 350, 60),
    "Siberia": (50, 75, 60, 190),
}


def _static(da: xr.DataArray) -> xr.DataArray:
    return da.isel(time=0, drop=True) if "time" in da.dims else da


def cell_area(ds: xr.Dataset) -> xr.DataArray:
    """Grid-cell area [m2]. CAM: from the latitude weights gw (sum 2); CLM: `area` [km2]."""
    if "gw" in ds:
        gw = _static(ds["gw"])
        return (EARTH_RADIUS**2 * gw * 2 * np.pi / ds.sizes["lon"]).broadcast_like(ds["lon"]).transpose("lat", "lon")
    return _static(ds["area"]) * 1e6


def _landfrac(ds):
    return _static(ds["LANDFRAC"] if "LANDFRAC" in ds else ds["landfrac"]).fillna(0.0)


def region_masks(ds: xr.Dataset, lat_min: float = 45.0, boxes: bool = False) -> dict[str, xr.DataArray]:
    """Boolean (lat, lon) masks on the grid of `ds` (built per grid: CAM and CLM coords differ by ~1e-13)."""
    lat, lon = ds["lat"], ds["lon"] % 360
    north = (lat >= lat_min).broadcast_like(lon).transpose("lat", "lon")
    land = _landfrac(ds) > 0
    modified = load_modified_cells(MODIFIED_CELLS, ds) & land
    masks = {f"≥{lat_min:g}°N": north, "modified cells": modified,
             f"unmodified land ≥{lat_min:g}°N": land & ~modified & north}
    if boxes:
        for name, (la0, la1, lo0, lo1) in SOURCE_BOXES.items():
            in_lon = (lon >= lo0) & (lon <= lo1) if lo0 < lo1 else (lon >= lo0) | (lon <= lo1)
            masks[name] = ((lat >= la0) & (lat <= la1) & in_lon).transpose("lat", "lon")
    return masks


def region_weights(ds: xr.Dataset) -> xr.DataArray:
    """Area weights: CAM fields over all cells, CLM fields over land (area x landfrac)."""
    area = cell_area(ds)
    return (area * _landfrac(ds)).fillna(0.0) if "landfrac" in ds else area


def regional(da: xr.DataArray, ds: xr.Dataset, mask: xr.DataArray) -> xr.DataArray:
    """Area-weighted mean of `da` over `mask` (NaN cells skipped)."""
    return da.weighted(region_weights(ds).where(mask, 0.0)).mean(("lat", "lon"))


def _year_month(da: xr.DataArray) -> xr.DataArray:
    t = da["time"]
    da = da.assign_coords(year=("time", t.dt.year.values), month=("time", t.dt.month.values))
    return da.set_index(time=("year", "month")).unstack("time")


# Monthly fields: name -> (category, component, f(ds) in plot units, units, label).
# "_Tg" fields are regional TOTALS (Tg month-1), all others regional means.
MONTHLY_FIELDS = {
    "SFISOP_Tg": ("BVOC", "atm", lambda ds: ds["SFISOP"], "Tg month$^{-1}$", "isoprene emission"),
    "SFMTERP_Tg": ("BVOC", "atm", lambda ds: ds["SFMTERP"], "Tg month$^{-1}$", "monoterpene emission"),
    "SFISOP": ("BVOC", "atm", lambda ds: ds["SFISOP"] * 1e6 * 86400, "mg m$^{-2}$ d$^{-1}$", "isoprene emission"),
    "SFMTERP": ("BVOC", "atm", lambda ds: ds["SFMTERP"] * 1e6 * 86400, "mg m$^{-2}$ d$^{-1}$", "monoterpene emission"),
    "TLAI": ("LAND", "lnd", lambda ds: ds["TLAI"], "m$^2$ m$^{-2}$", "leaf area index"),
    "GAMMA_isoprene": ("BVOC", "lnd", lambda ds: ds["GAMMA_isoprene"], "–", "MEGAN γ isoprene (area mean)"),
    "GAMMAL": ("BVOC", "lnd", lambda ds: ds["GAMMAL"], "–", "MEGAN γ LAI (area mean)"),
    "SOA_cb": ("SOA", "atm", lambda ds: ds["SOA_cb"] * 1e6, "mg m$^{-2}$", "SOA column burden"),
    "cb_SOA_LV": ("SOA", "atm", lambda ds: ds["cb_SOA_LV"] * 1e6, "mg m$^{-2}$", "SOA_LV gas burden"),
    "cb_SOA_SV": ("SOA", "atm", lambda ds: ds["cb_SOA_SV"] * 1e6, "mg m$^{-2}$", "SOA_SV gas burden"),
    "N_AER": ("SOA", "atm", lambda ds: to_map(ds["N_AER"]), "cm$^{-3}$", "aerosol number, lowest level"),
    "NUCLRATE": ("SOA", "atm", lambda ds: to_map(ds["NUCLRATE"]), "", "nucleation rate, lowest level"),
    "ACTNL_incld": ("CLOUDPROP", "atm", lambda ds: (ds["ACTNL"] / ds["FCTL"]).where(ds["FCTL"] >= INCLOUD_MIN_FRAC) * 1e-6,
                    "cm$^{-3}$", "in-cloud cloud-top droplet number"),
    "ACTREL_incld": ("CLOUDPROP", "atm", lambda ds: (ds["ACTREL"] / ds["FCTL"]).where(ds["FCTL"] >= INCLOUD_MIN_FRAC),
                     "µm", "in-cloud cloud-top effective radius"),
    "TGCLDLWP": ("CLOUDPROP", "atm", lambda ds: ds["TGCLDLWP"] * 1e3, "g m$^{-2}$", "liquid water path (grid box)"),
    "SW_cre_clean": ("RADIATIVE", "atm", lambda ds: ds["SW_cre_clean"], WM2, "SW cloud term (clean sky)"),
    "SOLIN": ("RADIATIVE", "atm", lambda ds: ds["SOLIN"], WM2, "insolation (TOA)"),
}


def monthly_regional(alias: str, field: str, region: str, start_year: int = 2001, end_year: int = 2009,
                     boxes: bool = False) -> xr.DataArray:
    """Regional mean (or total for *_Tg) of a monthly field, dims (year, month)."""
    cls, comp, f, _, _ = MONTHLY_FIELDS[field]
    ds = open_class(alias, cls, start_year, end_year, comp)
    mask = region_masks(ds, boxes=boxes)[region]
    da = f(ds)
    if field.endswith("_Tg"):   # kg m-2 s-1 -> Tg per month
        da = (da * cell_area(ds)).where(mask).sum(("lat", "lon")) * record_days(ds) * 86400 * 1e-9
    else:
        da = regional(da, ds, mask)
    return _year_month(da).rename(f"{field} {alias} {region}")


def monthly_difference(case1, case2, field, region, **kw) -> xr.DataArray:
    """Paired monthly regional differences case1 - case2, dims (year, month)."""
    a, b = monthly_regional(case1, field, region, **kw), monthly_regional(case2, field, region, **kw)
    if not (np.array_equal(a["year"], b["year"]) and np.array_equal(a["month"], b["month"])):
        raise ValueError(f"{case1}/{case2}: different years or months")
    return a - b


def _t_half(x, axis=0, conf=0.95):
    x = np.asarray(x)
    n = np.sum(np.isfinite(x), axis=axis)
    return stats.t.ppf(0.5 + conf / 2, n - 1) * np.nanstd(x, axis=axis, ddof=1) / np.sqrt(n)


def _month_line(ax, d, label, color, ls="-", band=True, years=None):
    if years is not None:
        d = d.sel(year=slice(*years))
    m = d.mean("year")
    ax.plot(m["month"], m, color=color, ls=ls, lw=1.4, label=label)
    if band and d.sizes["year"] > 2:
        h = _t_half(d.values, axis=0)
        ax.fill_between(m["month"], m - h, m + h, color=color, alpha=0.15, lw=0)


def _month_axes(ax):
    ax.axhline(0, color="black", lw=0.5)
    ax.set_xticks(range(1, 13), list("JFMAMJJASOND"), fontsize=7)
    ax.tick_params(labelsize=7)


# ---------------------------------------------------------------- A + E: radiative budget, 3 contrasts

def budget_contrasts(period: str) -> list[tuple[str, str, str]]:
    """(label, case1, case2): LCC-CTRL = (fBVOC-CTRL) + (LCC-fBVOC) exactly, year by year."""
    p = BVOC_PAIRS[period]
    return [("LCC−CTRL", p["lcc"], p["ctrl"]), ("fBVOC−CTRL", p["fbvoc"], p["ctrl"]),
            ("LCC−fBVOC", p["lcc"], p["fbvoc"])]


GHAN_TERMS = ("toa", "dir", "cre_clean", "clearclean")


def radiative_budget_table(start_year: int = 2001, end_year: int = 2009,
                           regions=("≥45°N", "modified cells")):
    """Long table of yearly regional means: period, region, contrast, band, term, year, value [W m-2].

    term = toa / dir / cre_clean / clearclean (Ghan) or albedo_proxy (SW, surface, not a budget term).
    Checks before returning: Ghan terms sum to toa, and LCC-CTRL = (fBVOC-CTRL) + (LCC-fBVOC).
    """
    import pandas as pd

    rows = []
    for period in BVOC_PAIRS:
        ref = open_class(BVOC_PAIRS[period]["ctrl"], "RADIATIVE", start_year, end_year)
        masks = region_masks(ref)
        for label, c1, c2 in budget_contrasts(period):
            fields = {(b, t): yearly_difference(c1, c2, "RADIATIVE", f"{b}_{t}", start_year, end_year)
                      for b in ("NET", "SW", "LW") for t in GHAN_TERMS}
            fields[("SW", "albedo_proxy")] = yearly_difference(c1, c2, "RADIATIVE", "SFC_ALBEDO_FORCING_CLEAR",
                                                               start_year, end_year)
            for (band, term), d in fields.items():
                for region in regions:
                    r = regional(d, ref, masks[region])
                    rows += [dict(period=period, region=region, contrast=label, band=band, term=term,
                                  year=int(y), value=float(v)) for y, v in zip(r["year"].values, r.values)]
    t = pd.DataFrame(rows)

    key = ["period", "region", "band", "year"]
    ghan = t[t.term.isin(GHAN_TERMS)].pivot_table(index=key + ["contrast"], columns="term", values="value")
    err_g = (ghan["dir"] + ghan["cre_clean"] + ghan["clearclean"] - ghan["toa"]).abs().max()
    w = t.pivot_table(index=key + ["term"], columns="contrast", values="value")
    err_c = (w["fBVOC−CTRL"] + w["LCC−fBVOC"] - w["LCC−CTRL"]).abs().max()
    print(f"Closure before rounding: Ghan terms vs total {err_g:.1e}, contrasts {err_c:.1e} W m-2")
    if max(err_g, err_c) > 1e-3:
        raise ValueError("radiative budget does not close")
    return t


def summarize_years(t, by, conf: float = 0.95):
    """Mean and t-interval half-width across years of a long table with columns by + [year, value]."""
    g = t.groupby(list(by))["value"]
    out = g.agg(mean="mean", n="count", sd="std").reset_index()
    out["ci95"] = stats.t.ppf(0.5 + conf / 2, out["n"] - 1) * out["sd"] / np.sqrt(out["n"])
    return out.drop(columns="sd")


TERM_STYLE = {"toa": ("total", "#333333"), "dir": ("ARI", "#d08a2e"), "cre_clean": ("cloud", "#3b75af"),
              "clearclean": ("clear-clean", "#c44e52"), "albedo_proxy": ("albedo proxy (sfc)", "white")}


def make_radiative_budget_figure(t, save=True, figdir: Path = FIGURE_DIR, dpi=200,
                                 start_year=2001, end_year=2009):
    """Bars: rows = region x period, columns = NET / SW / LW; groups = the 3 contrasts; ± 95 % CI."""
    s = summarize_years(t, ["period", "region", "contrast", "band", "term"])
    rows = [(r, p) for r in dict.fromkeys(t.region) for p in BVOC_PAIRS]
    contrasts = [c for c, _, _ in budget_contrasts("PD")]
    fig, axes = plt.subplots(len(rows), 3, figsize=(15, 3.3 * len(rows)), squeeze=False, constrained_layout=True)
    for i, (region, period) in enumerate(rows):
        for j, band in enumerate(("NET", "SW", "LW")):
            ax = axes[i, j]
            terms = list(GHAN_TERMS) + (["albedo_proxy"] if band == "SW" else [])
            width = 0.8 / len(terms)
            for k, term in enumerate(terms):
                sub = s[(s.period == period) & (s.region == region) & (s.band == band) & (s.term == term)]
                sub = sub.set_index("contrast").loc[contrasts]
                label, color = TERM_STYLE[term]
                x = np.arange(len(contrasts)) + (k - (len(terms) - 1) / 2) * width
                ax.bar(x, sub["mean"], width, yerr=sub["ci95"], color=color, label=label, capsize=2,
                       edgecolor="black" if term == "albedo_proxy" else color, hatch="///" if term == "albedo_proxy" else None,
                       lw=0.6, error_kw=dict(lw=0.8))
                for xi, (m, h) in zip(x, zip(sub["mean"], sub["ci95"])):
                    if term == "toa":
                        ax.text(xi, m + np.sign(m or 1) * (h + 0.03), f"{m:+.2f}", ha="center",
                                va="bottom" if m >= 0 else "top", fontsize=6.5)
            ax.axhline(0, color="black", lw=0.6)
            ax.set_xticks(range(len(contrasts)), contrasts, fontsize=8)
            ax.set_title(f"{period}, {region}: {band}", fontsize=9.5, fontweight="semibold")
            ax.tick_params(labelsize=7)
            if j == 0:
                ax.set_ylabel("W m$^{-2}$", fontsize=8)
    axes[0, 1].legend(fontsize=7, ncol=5, loc="upper center", bbox_to_anchor=(0.5, 1.35))
    fig.suptitle(f"Radiative budget: LCC−CTRL = (fBVOC−CTRL) + (LCC−fBVOC), mean ± 95 % CI over years "
                 f"({start_year}–{end_year})", fontsize=12, fontweight="bold")
    if save:
        path = figdir / f"radiative_budget_3contrasts_{start_year}_{end_year}.png"
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        print(f"Saved {path}")
    return fig, axes


def make_paired_years_figure(t, region="≥45°N", band="NET", save=True, figdir: Path = FIGURE_DIR, dpi=200,
                             start_year=2001, end_year=2009):
    """Strip plot: each yearly regional difference (dot) + mean ± 95 % CI, per Ghan term and contrast."""
    sub = t[(t.region == region) & (t.band == band) & t.term.isin(GHAN_TERMS)]
    s = summarize_years(sub, ["period", "contrast", "term"])
    cols = [(p, c) for p in BVOC_PAIRS for c, _, _ in budget_contrasts(p)]
    fig, axes = plt.subplots(1, len(GHAN_TERMS), figsize=(16, 4), sharey=False, constrained_layout=True)
    for ax, term in zip(axes, GHAN_TERMS):
        for x, (p, c) in enumerate(cols):
            v = sub[(sub.period == p) & (sub.contrast == c) & (sub.term == term)].sort_values("year")
            color = "#3b75af" if p == "PD" else "#c44e52"
            ax.scatter(np.full(len(v), x) + np.linspace(-0.15, 0.15, len(v)), v["value"], s=10, color=color, alpha=0.7)
            m = s[(s.period == p) & (s.contrast == c) & (s.term == term)].iloc[0]
            ax.errorbar(x + 0.3, m["mean"], yerr=m["ci95"], fmt="D", color="black", ms=4, capsize=3, lw=1)
        ax.axhline(0, color="black", lw=0.5)
        ax.set_xticks(range(len(cols)), [f"{p}\n{c}" for p, c in cols], fontsize=7)
        ax.set_title(f"{TERM_STYLE[term][0]} ({band})", fontsize=10, fontweight="semibold")
        ax.tick_params(labelsize=7)
    axes[0].set_ylabel(f"{region} difference [W m$^{{-2}}$]", fontsize=8)
    fig.suptitle(f"Paired yearly regional means ({region}, {start_year}–{end_year}): dots = years "
                 f"(blue PD, red FUT), diamond = mean ± 95 % t-interval", fontsize=11, fontweight="bold")
    if save:
        path = figdir / f"paired_years_{band}_{start_year}_{end_year}.png"
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        print(f"Saved {path}")
    return fig, axes


# ---------------------------------------------------------------- B: emissions / LAI origin

def make_emission_origin_figure(fields=("SFISOP_Tg", "SFMTERP_Tg", "TLAI", "GAMMA_isoprene", "GAMMAL"),
                                save=True, figdir: Path = FIGURE_DIR, dpi=200, start_year=2001, end_year=2009):
    """Monthly differences, modified vs unmodified land >=45N, early vs late years.
    Columns = period x (LCC-CTRL, LCC-fBVOC); MEGAN factors only exist with MEGAN on (not in fBVOC)."""
    cols = [(p, lab, c1, c2) for p in BVOC_PAIRS for lab, c1, c2 in budget_contrasts(p) if lab != "fBVOC−CTRL"]
    regions = {"modified cells": "#c44e52", "unmodified land ≥45°N": "#3b75af"}
    fig, axes = plt.subplots(len(fields), len(cols), figsize=(4 * len(cols), 2.4 * len(fields)),
                             squeeze=False, constrained_layout=True, sharex=True)
    for i, field in enumerate(fields):
        _, _, _, units, label = MONTHLY_FIELDS[field]
        for j, (p, lab, c1, c2) in enumerate(cols):
            ax = axes[i, j]
            try:
                for region, color in regions.items():
                    d = monthly_difference(c1, c2, field, region, start_year=start_year, end_year=end_year)
                    _month_line(ax, d, f"{region}, {EARLY_YEARS[0]}–{EARLY_YEARS[1]}", color, "-", True, EARLY_YEARS)
                    _month_line(ax, d, f"{region}, {LATE_YEARS[0]}–{LATE_YEARS[1]}", color, "--", False, LATE_YEARS)
            except KeyError:
                ax.text(0.5, 0.5, "not available\n(MEGAN off in fBVOC)", transform=ax.transAxes,
                        ha="center", va="center", fontsize=8, color="grey")
            _month_axes(ax)
            if i == 0:
                ax.set_title(f"{p}: {c1} − {c2}", fontsize=9, fontweight="semibold")
            if j == 0:
                ax.set_ylabel(f"Δ {label}\n[{units}]", fontsize=7.5)
    axes[0, 0].legend(fontsize=6.5, loc="best")
    fig.suptitle("Origin of the emission perturbation: monthly differences, modified vs unmodified land ≥45°N; "
                 f"solid {EARLY_YEARS[0]}–{EARLY_YEARS[1]} (± 95 % CI), dashed {LATE_YEARS[0]}–{LATE_YEARS[1]}",
                 fontsize=11, fontweight="bold")
    if save:
        path = figdir / f"emission_origin_monthly_{start_year}_{end_year}.png"
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        print(f"Saved {path}")
    return fig, axes


# ---------------------------------------------------------------- C + F: monthly chains

def make_monthly_chain_figure(fields, columns, lines, name, title, context=None, save=True,
                              figdir: Path = FIGURE_DIR, dpi=200, start_year=2001, end_year=2009, boxes=False):
    """Rows = fields, columns = regions; lines = {label: (case1, case2, color, ls)} monthly differences
    (mean ± 95 % CI across years). `context` = optional field drawn as absolute climatology of `lines`' case2."""
    rows = list(fields) + ([context] if context else [])
    fig, axes = plt.subplots(len(rows), len(columns), figsize=(4.2 * len(columns), 2.2 * len(rows)),
                             squeeze=False, constrained_layout=True, sharex=True)
    for j, region in enumerate(columns):
        for i, field in enumerate(rows):
            ax = axes[i, j]
            _, _, _, units, label = MONTHLY_FIELDS[field]
            for lab, (c1, c2, color, ls) in lines.items():
                if field == context:
                    _month_line(ax, monthly_regional(c2, field, region, start_year, end_year, boxes), c2, color, ls)
                else:
                    _month_line(ax, monthly_difference(c1, c2, field, region, start_year=start_year,
                                                       end_year=end_year, boxes=boxes), lab, color, ls)
            _month_axes(ax)
            if i == 0:
                ax.set_title(region, fontsize=10, fontweight="semibold")
            if j == 0:
                ax.set_ylabel(f"{'' if field == context else 'Δ '}{label}\n[{units}]", fontsize=7.5)
    axes[0, 0].legend(fontsize=7)
    fig.suptitle(title, fontsize=11, fontweight="bold")
    if save:
        path = figdir / f"{name}_{start_year}_{end_year}.png"
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        print(f"Saved {path}")
    return fig, axes


# ---------------------------------------------------------------- D: baseline and relative change

BASELINE_FIELDS = {   # yearly field name (YEARLY_DERIVED / raw), category, units
    "SOA_cb_mgm2": ("SOA", "mg m-2"), "N_AER": ("SOA", "cm-3"), "CCN3": ("SOA", "cm-3"),
    "ACTNL_incld": ("CLOUDPROP", "cm-3"), "ACTREL_incld": ("CLOUDPROP", "µm"),
    "TGCLDLWP_gm2": ("CLOUDPROP", "g m-2"), "CLDLOW": ("CLOUDPROP", "fraction"), "FCTL": ("CLOUDPROP", "fraction"),
}


def baseline_table(region="≥45°N", start_year=2001, end_year=2009):
    """CTRL and fBVOC baselines (annual and JJA, regional mean), FUT-PD change, BVOC contrast as % of baseline."""
    import pandas as pd

    rows = []
    for var, (cls, units) in BASELINE_FIELDS.items():
        for season, months in (("ANN", None), ("JJA", SEASONS["JJA"])):
            val = {}
            for p, roles in BVOC_PAIRS.items():
                for role, alias in roles.items():
                    ds = open_class(alias, cls, start_year, end_year)
                    val[(p, role)] = float(regional(yearly_field(ds, var, months), ds, region_masks(ds)[region]).mean())
            r = dict(variable=var, units=units, season=season,
                     CTRL_PD=val[("PD", "ctrl")], CTRL_FUT=val[("FUT", "ctrl")])
            r["CTRL_FUT−PD"] = r["CTRL_FUT"] - r["CTRL_PD"]
            r["CTRL_FUT−PD_%"] = 100 * r["CTRL_FUT−PD"] / r["CTRL_PD"]
            for p in BVOC_PAIRS:
                base, lcc = val[(p, "fbvoc")], val[(p, "lcc")]
                r[f"fBVOC_{p}"] = base
                r[f"BVOC_{p}"] = lcc - base
                r[f"BVOC_{p}_%"] = 100 * (lcc - base) / base
            rows.append(r)
    return pd.DataFrame(rows)


PERCENT_PANELS = [   # (yearly field, category, title, minimum baseline for the % map)
    ("SOA_cb_mgm2", "SOA", "SOA BURDEN", 0.05),
    ("N_AER", "SOA", "AEROSOL NUMBER", 1.0),
    ("ACTNL_incld", "CLOUDPROP", "IN-CLOUD DROPLET NUMBER", 1.0),
    ("ACTREL_incld", "CLOUDPROP", "IN-CLOUD EFFECTIVE RADIUS", 1.0),
    ("TGCLDLWP_gm2", "CLOUDPROP", "LIQUID WATER PATH", 5.0),
]


def make_percent_change_figure(start_year=2001, end_year=2009, extent_lat=45.0, save=True,
                               figdir: Path = FIGURE_DIR, dpi=200, stipple=True, fdr_alpha=0.10):
    """BVOC contrast (LCC - fBVOC) as % of the fBVOC baseline mean; rows PD/FUT. Cells with a baseline
    below the panel threshold are blank. Hatching = not significant (paired t-test of the yearly % values, FDR)."""
    fig, axes = plt.subplots(2, len(PERCENT_PANELS), figsize=(3.2 * len(PERCENT_PANELS), 7.2), squeeze=False,
                             subplot_kw={"projection": ccrs.Orthographic(0, 90)}, constrained_layout=True)
    for i, (p, roles) in enumerate(BVOC_PAIRS.items()):
        for j, (var, cls, title, vmin_base) in enumerate(PERCENT_PANELS):
            d = yearly_difference(roles["lcc"], roles["fbvoc"], cls, var, start_year, end_year)
            base = yearly_field(open_class(roles["fbvoc"], cls, start_year, end_year), var).mean("year")
            pct = (100 * d / base).where(abs(base) >= vmin_base)
            panel = MapPanel(key=var, title=title if i == 0 else "", variable_class=cls, variable=var,
                             case1_role="lcc", case2_role="fbvoc", units="%",
                             long_label=f"{var}: (LCC − fBVOC) / fBVOC")
            _plot_panel(axes[i, j], panel, roles, start_year, end_year, extent_lat, extent_lat,
                        stipple, fdr_alpha, d=pct, add_cbar=True)
        axes[i, 0].text(-0.12, 0.5, f"{p}\n{roles['lcc']}\n− {roles['fbvoc']}", transform=axes[i, 0].transAxes,
                        ha="right", va="center", fontsize=9, fontweight="bold")
    fig.suptitle(f"BVOC contrast relative to the fBVOC baseline [%] ({start_year}–{end_year})",
                 fontsize=13, fontweight="bold")
    if save:
        path = figdir / f"bvoc_percent_change_maps_{start_year}_{end_year}.png"
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        print(f"Saved {path}")
    return fig, axes
