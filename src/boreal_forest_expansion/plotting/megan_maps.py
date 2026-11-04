"""
Maps of the CLM MEGAN emission factors (EPS_*) and activity factors (GAMMA*), north of 45N.

Inputs: lnd_BVOC (MEG_*, EPS_*, GAMMA*), lnd_ET (PCT_LANDUNIT), lnd_LAND (PCT_NAT_PFT) in
data/processed-data/postprocessing. The fBVOC members have no MEGAN output, so only CTRL and LCC.

How CLM writes these fields (a, model/SourceMods/src.clm/VOCEmissionMod.F90):
  - For every vegetated soil/crop patch:  E_p = eps_p * gamma_p,
    gamma_p = gammaL * gammaS(=1) * gammaA * gammaP * gammaT * gammaC(isoprene only).
  - Gammas are computed for all vegetated patches, also where eps = 0 for that compound.
  - Patch -> grid cell: area mean over valid patches (spval excluded, subgridAveMod).
    MEG_*:   all land, lake/urban = 0, bare ground = 0.
    EPS_*, GAMMA*: vegetated soil/crop patches only; lake, bare ground, urban, wetland excluded
                   (spval). Lake is NOT 0: the h0 grid EPS rebuilt from the patch tape over
                   veg + crop patches matches to ~1e-14 (a,
                   diagnostics/megan-exact-split-test/gamma_eff_vs_GAMMA_check.ipynb).
  So the grid-cell GAMMA_* is an AREA mean over vegetated patches, not an emission-weighted
  one, and MEG != k * EPS * GAMMA in mixed cells.

Effective (emission-weighted) gamma, exact by construction (b, derived from the above):
    gamma_eff = MEG / (k * EPS * f_valid),   k = 1e-9 / 3600  [kg s-1 per ug h-1]
    f_valid   = land fraction where EPS is defined
              = natveg * (1 - bare share) + crop          (PCT_LANDUNIT, PCT_NAT_PFT)
  Until 2026-11-03 lake was wrongly added to f_valid (gamma_eff too low by up to 6x in lake-rich
  cells); `load_factors(..., lake_in_f_valid=True)` reproduces that, for
  diagnostics/megan-exact-split-test/lake_fix_effect.ipynb only.
  Check (a, 5-day patch tape): gamma_eff / GAMMA = 1 in cells with one valid patch; elsewhere it
  differs because GAMMA is area- and gamma_eff emission-weighted.
  It satisfies E = k * f_valid * EPS * gamma_eff, so Delta ln E splits exactly into
  Delta ln(f_valid * EPS) (composition) + Delta ln gamma_eff (activity).
  The partial factors gammaL, T, P, A, C are only available as area means; their product
  differs from gamma_eff. The attribution figure shows that difference as a residual.

Monoterpenes: EPS/GAMMA output exists for 7 of the 21 MTERP compounds (pinene_a, carene_3,
pinene_b, myrcene, limonene, ocimene_t_b, sabinene) (a, cases-setup.sh). The group uses the
sum of their EPS and MEG; partial gammas are EPS-weighted over the 7. Their share of MEG_MTERP
(all 21) is printed as `coverage`.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import xarray as xr

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs

from boreal_forest_expansion.plotting.common import ax_map_properties, cut_extent_Orthographic
from cartopy.util import add_cyclic_point
from scipy import stats

from boreal_forest_expansion.plotting import forcing_maps as fm
from boreal_forest_expansion.plotting.forcing_maps import (
    BVOC_PAIRS, FIGURE_DIR, add_stippling, open_class, symmetric_vmax,
)
from boreal_forest_expansion.postprocess.averaging import record_days
from boreal_forest_expansion.analysis.stats import cellwise_pvalue, fdr_mask
from boreal_forest_expansion.analysis.regions import load_modified_cells

REPO_DIR = Path("/cluster/home/adelez/BOREAL-FOREST-EXPANSION")
MODIFIED_CELLS = REPO_DIR / "diagnostics/lcc-modified-cells/modified_cells.csv"
MEGAN_FIG_DIR = FIGURE_DIR / "megan_factors"

K_UNITS = 1e-9 / 3600.0        # ug m-2 h-1 -> kg m-2 s-1 (megemis_units_factor * 1e-3)

MTERP_ALL = [
    "pinene_a", "carene_3", "thujene_a", "2met_styrene", "cymene_p", "cymene_o", "terpinolene",
    "bornene", "fenchene_a", "ocimene_al", "pinene_b", "sabinene", "camphene", "limonene",
    "phellandrene_a", "terpinene_g", "terpinene_a", "phellandrene_b", "myrcene", "ocimene_t_b",
    "ocimene_c_b",
]
GROUPS = {
    "isoprene": ["isoprene"],
    "MTERP": ["pinene_a", "carene_3", "pinene_b", "myrcene", "limonene", "ocimene_t_b", "sabinene"],
}
GROUP_TITLE = {"isoprene": "isoprene", "MTERP": "monoterpenes (7 of 21 compounds)"}

SEASONS = {"JJA": [6, 7, 8], "MAM": [3, 4, 5], "SON": [9, 10, 11], "DJF": [12, 1, 2],
           "ANN": list(range(1, 13))}

FACTOR_LABEL = {
    "EPS": ("ε (emission factor)", "µg m$^{-2}$ h$^{-1}$"),
    "gamma_eff": ("γ$_{eff}$ = E / (k·f·ε)", "1"),
    "GAMMA": ("γ (area-mean)", "1"),
    "GAMMAL": ("γ$_L$ (LAI)", "1"),
    "GAMMAT": ("γ$_T$ (temperature)", "1"),
    "GAMMAP": ("γ$_P$ (light)", "1"),
    "GAMMAA": ("γ$_A$ (leaf age)", "1"),
    "GAMMAC": ("γ$_C$ (CO$_2$)", "1"),
    "MEG": ("E (MEGAN flux)", "mg m$^{-2}$ d$^{-1}$"),
}


# =============================================================================
# Loading
# =============================================================================

def _season_mean_by_year(da: xr.DataArray, days: xr.DataArray, months: list[int]) -> xr.DataArray:
    """Record-length weighted mean over `months`, per season-year (DJF: December counts with
    the following year). Only complete seasons are kept."""
    month = da["time"].dt.month
    year = da["time"].dt.year
    if 12 in months and 1 in months:                  # DJF: December belongs to the next year
        year = year + (month == 12)
    year = year.rename("year")
    sel = month.isin(months)
    w = days.where(sel, 0.0)
    num = (da * w).groupby(year).sum("time")
    den = w.groupby(year).sum("time")
    n = sel.groupby(year).sum("time")
    return (num / den).where(n == len(months), drop=True)


def load_factors(alias: str, group: str, season: str = "JJA",
                 start_year: int = 2001, end_year: int = 2014,
                 lake_in_f_valid: bool = False) -> xr.Dataset:
    """Seasonal means per year (year, lat, lon) of E, EPS, gamma_eff and the partial gammas.

    lake_in_f_valid=True reproduces the pre-2026-11-03 bug (lake counted in f_valid); diagnostics only.
    """
    if group not in GROUPS:
        raise ValueError(f"group must be one of {list(GROUPS)}")
    months = SEASONS[season]
    bv = open_class(alias, "BVOC", start_year, end_year, "lnd")
    if f"EPS_{GROUPS[group][0]}" not in bv:
        raise KeyError(f"{alias}: no EPS_/GAMMA output (fBVOC members have MEGAN off)")
    et = open_class(alias, "ET", start_year, end_year, "lnd")
    ld = open_class(alias, "LAND", start_year, end_year, "lnd")
    days = record_days(bv)

    def smean(da):
        return _season_mean_by_year(da, days, months)

    # land fraction where EPS/GAMMA are defined (landunits: 0 natveg, 1 crop; lake excluded)
    pl = et["PCT_LANDUNIT"].isel(time=0) / 100.0
    bare = ld["PCT_NAT_PFT"].isel(time=0, natpft=0) / 100.0
    f_valid = pl.isel(ltype=0) * (1 - bare) + pl.isel(ltype=1)
    if lake_in_f_valid:
        f_valid = f_valid + pl.isel(ltype=4)

    comps = GROUPS[group]
    eps = {c: bv[f"EPS_{c}"].isel(time=0) for c in comps}            # time-constant
    eps_sum = sum(eps.values())
    meg = smean(sum(bv[f"MEG_{c}"] for c in comps))

    out = xr.Dataset()
    out["MEG"] = meg * 1e6 * 86400                                    # mg m-2 d-1
    out["EPS"] = eps_sum.expand_dims(year=meg["year"])
    out["gamma_eff"] = (meg / (K_UNITS * eps_sum * f_valid)).where((eps_sum > 0) & (f_valid > 0))

    def eps_weighted(name):
        tot = sum(eps[c] * smean(bv[f"{name}_{c}"]) for c in comps)
        return (tot / eps_sum).where(eps_sum > 0)

    out["GAMMA"] = eps_weighted("GAMMA")
    out["GAMMAL"] = smean(bv["GAMMAL"])
    out["GAMMAT"] = eps_weighted("GAMMAT")
    out["GAMMAP"] = eps_weighted("GAMMAP")
    out["GAMMAA"] = eps_weighted("GAMMAA")
    if group == "isoprene":
        out["GAMMAC"] = smean(bv["GAMMAC_isoprene"])
    out["f_valid"] = f_valid

    if group == "MTERP":
        all21 = sum(bv[f"MEG_{c}"] for c in MTERP_ALL if f"MEG_{c}" in bv)
        w = (bv["area"] * bv["landfrac"]).fillna(0).where(bv["lat"] >= 45, 0)
        out.attrs["coverage_45N"] = float((smean(sum(bv[f"MEG_{c}"] for c in comps)) * w).sum()
                                          / (smean(all21) * w).sum())
    out.attrs.update(alias=alias, group=group, season=season)
    return out


# =============================================================================
# Plotting helpers (same look as the forcing maps: forcing_maps.map_grid, _cbar_below, ...)
# =============================================================================

TITLE = {
    "MEG": "EMISSION\nΔln E", "EPS": "COMPOSITION\nΔln(f·ε)", "gamma_eff": "ACTIVITY\nΔln γ$_{eff}$",
    "GAMMA": "AREA-MEAN γ", "GAMMAL": "LAI\nΔln γ$_L$", "GAMMAT": "TEMPERATURE\nΔln γ$_T$",
    "GAMMAP": "LIGHT\nΔln γ$_P$", "GAMMAA": "LEAF AGE\nΔln γ$_A$", "GAMMAC": "CO$_2$\nΔln γ$_C$",
    "residual": "RESIDUAL\nΔln γ$_{eff}$ − Σ Δln γ$_i$",
    "weighting": "WEIGHTING\nΔln γ$_{eff}$ − Δln γ$_{CLM}$",
    "covariation": "CO-VARIATION\nΔln γ$_{CLM}$ − Σ Δln γ$_i$",
}


def _modified_mask(like: xr.DataArray) -> xr.DataArray | None:
    try:
        return load_modified_cells(MODIFIED_CELLS, like.to_dataset(name="x"))
    except Exception as exc:          # outline is optional
        print(f"modified-cells outline skipped: {exc}")
        return None


def _panel(ax, da, norm, cmap, title, extent_lat=45.0, not_sig=None, modified=None, text=None):
    """One polar map as in forcing_maps.plot_single_boreal_panel, plus the modified-cells outline.
    not_sig: cells hatched as not significant (IPCC look, as the forcing maps)."""
    cut_extent_Orthographic(ax, lat=extent_lat)
    ax_map_properties(ax, alpha=0.25, coastlines=False, gridlines=False, ocean=False,
                      land=True, borders=False, rivers=False)
    p = da.plot.pcolormesh(ax=ax, x="lon", y="lat", transform=ccrs.PlateCarree(),
                           cmap=cmap, norm=norm, add_colorbar=False, zorder=1)
    ax.coastlines(linewidth=0.6, zorder=3)
    if modified is not None:
        data, lon_c = add_cyclic_point(modified.astype(float).values, coord=modified["lon"].values)
        ax.contour(lon_c, modified["lat"], data, levels=[0.5], colors="0.15", linewidths=0.9,
                   linestyles="--", transform=ccrs.PlateCarree(), zorder=3)
    if not_sig is not None and bool(not_sig.any()):
        add_stippling(ax, not_sig, style="lines", zorder=4)
    ax.set_title(title or "", fontsize=9.5, fontweight="semibold", pad=fm.TITLE_PAD)   # "" replaces xarray's "time = ..."
    if text:   # centred between the map and its colourbar, as in the forcing maps
        h = ax.get_position().height * ax.figure.get_figheight()
        ax.text(0.5, -0.5 * fm.CBAR_OFFSET / h, text, transform=ax.transAxes, ha="center", va="center",
                fontsize=fm.MEAN_FONTSIZE)
    return p


def _not_significant(d, extent_lat, fdr_alpha):
    """Cells >= extent_lat that are not FDR-significant (paired t-test over years)."""
    p = cellwise_pvalue(d)
    region = d["lat"] >= extent_lat
    return (~fdr_mask(p, alpha=fdr_alpha, within=region)) & np.isfinite(p) & region


def _interval(d, w, lat_min, conf=0.95):
    """Mean and t-interval half-width of the yearly `w`-weighted means of `d` (year, lat, lon) >= lat_min."""
    m = (d["lat"] >= lat_min) & np.isfinite(d) & (w > 0)
    r = ((d * w).where(m).sum(("lat", "lon")) / w.where(m).sum(("lat", "lon"))).values
    half = stats.t.ppf(0.5 + conf / 2, r.size - 1) * r.std(ddof=1) / np.sqrt(r.size)
    return float(r.mean()), float(half)


def _ratio_interval(a, b, w, lat_min, conf=0.95):
    """% change of the `w`-weighted regional mean (b vs a), mean and t half-width over years.
    Ratio of means, not mean of cell ratios: cells with near-zero CTRL values would dominate that."""
    m = (a["lat"] >= lat_min) & np.isfinite(a) & np.isfinite(b) & (w > 0)
    ra, rb = ((x * w).where(m).sum(("lat", "lon")) for x in (a, b))
    r = (100 * (rb / ra - 1)).values
    half = stats.t.ppf(0.5 + conf / 2, r.size - 1) * r.std(ddof=1) / np.sqrt(r.size)
    return float(r.mean()), float(half)


def _row_label(ax, text):
    ax.text(-0.08, 0.5, text, transform=ax.transAxes, ha="right", va="center", fontsize=9, fontweight="bold")


def _p98(arrays, lat_min):
    vals = np.concatenate([a.where(a["lat"] >= lat_min).values.ravel() for a in arrays])
    v = float(np.nanquantile(vals, 0.98)) if np.isfinite(vals).any() else 1.0
    return v if v > 0 else 1.0


def _title(fig, title, subtitle):
    fm.add_suptitle(fig, title, None, fontsize=13, y=fm._suptitle_y(fig), subtitle=subtitle)


def _save(fig, name, dpi):
    MEGAN_FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = MEGAN_FIG_DIR / name
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    print(f"Saved {path}")


FACTOR_TITLE = {
    "EPS": "EMISSION FACTOR\nε", "gamma_eff": "EFFECTIVE ACTIVITY\nγ$_{eff}$ = E / (k·f·ε)",
    "GAMMA": "AREA-MEAN ACTIVITY\nγ", "GAMMAL": "LAI\nγ$_L$", "GAMMAT": "TEMPERATURE\nγ$_T$",
    "GAMMAP": "LIGHT\nγ$_P$", "GAMMAA": "LEAF AGE\nγ$_A$", "GAMMAC": "CO$_2$\nγ$_C$",
}


# =============================================================================
# Figures
# =============================================================================

def make_factor_maps(group: str = "isoprene", experiment: str = "PD", season: str = "JJA",
                     start_year: int = 2001, end_year: int = 2014, extent_lat: float = 45.0,
                     fdr_alpha: float = 0.10, save: bool = True, dpi: int = 200):
    """Rows: CTRL, LCC, LCC vs CTRL (% change). Columns: EPS, gamma_eff, GAMMA and partial gammas.

    Rows 1-2 share one colour scale per column (colourbar under row 2). Row 3: 100 * (exp(mean
    Delta ln) - 1) of paired yearly seasonal means; hatched = not FDR-significant (paired t-test on
    yearly Delta ln, alpha_FDR 0.10, cells >= extent_lat). Under the maps: mean over vegetated land
    (cos lat x f_valid) >= extent_lat +- 95 % CI of the yearly means (row 3: of the yearly % changes).
    """
    pairs = BVOC_PAIRS[experiment]
    a = load_factors(pairs["ctrl"], group, season, start_year, end_year)
    b = load_factors(pairs["lcc"], group, season, start_year, end_year)
    factors = [f for f in ["EPS", "gamma_eff", "GAMMA", "GAMMAL", "GAMMAT", "GAMMAP", "GAMMAA", "GAMMAC"]
               if f in a]
    modified = _modified_mask(a["MEG"].isel(year=0))
    land_w = np.cos(np.deg2rad(a["lat"])) * a["f_valid"]

    fig, axes = fm.map_grid(3, len(factors), left=1.6)
    for j, f in enumerate(factors):
        units = FACTOR_LABEL[f][1]
        vmax = _p98([a[f].mean("year"), b[f].mean("year")], extent_lat)
        norm = mcolors.Normalize(0, vmax)
        for i, x in enumerate((a, b)):
            m, half = _interval(x[f], land_w, extent_lat)
            p = _panel(axes[i, j], x[f].mean("year"), norm, "viridis", FACTOR_TITLE[f] if i == 0 else "",
                       extent_lat, modified=modified, text=fm._format_interval(m, half).replace("+", "", 1))
        fm._cbar_below(fig, axes[1, j], p, f"{f}\n[{units}]", fm.CBAR_LABELSIZE, shrink=fm.CBAR_SHRINK,
                       height=fm.CBAR_HEIGHT, extend="max")
        # relative change from paired yearly log ratios
        dln = np.log(b[f] / a[f]).where((a[f] > 0) & (b[f] > 0))
        rel = 100 * (np.exp(dln.mean("year")) - 1)
        v = symmetric_vmax(rel.where(rel["lat"] >= extent_lat), q=0.95, fallback=10.0)
        m, half = _ratio_interval(a[f], b[f], land_w, extent_lat)
        p = _panel(axes[2, j], rel, mcolors.TwoSlopeNorm(vmin=-v, vcenter=0, vmax=v), "RdBu_r", "",
                   extent_lat, not_sig=_not_significant(dln, extent_lat, fdr_alpha), modified=modified,
                   text=f"{fm._format_interval(m, half)} %")
        fm._cbar_below(fig, axes[2, j], p, f"{f}: LCC vs CTRL\n[%]", fm.CBAR_LABELSIZE, shrink=fm.CBAR_SHRINK,
                       height=fm.CBAR_HEIGHT, five_ticks=True)
    for i, txt in enumerate((pairs["ctrl"], pairs["lcc"], f"{pairs['lcc']}\nvs {pairs['ctrl']}\n(% change)")):
        _row_label(axes[i, 0], txt)

    cov = f" (coverage of MEG_MTERP ≥{extent_lat:g}°N: {a.attrs['coverage_45N']:.0%})" if "coverage_45N" in a.attrs else ""
    _title(fig, f"MEGAN factors, {GROUP_TITLE[group]}{cov}: {experiment}, {season} ({start_year}–{end_year})",
           rf"$\mathit{{Under\ the\ maps}}$: mean over vegetated land {extent_lat:g}–90°N ± 95 % CI of the yearly means"
           " (row 3: % change of that mean)"
           f" · hatched: not significant · dashed line: modified cells")
    if save:
        _save(fig, f"{experiment}_{group}_factors_{season}_{start_year}_{end_year}.png", dpi)
    return fig, axes


# Fixed colour scale (+-vmax) and tick step of the attribution maps, per experiment (user 2026-10-29)
ATTRIBUTION_VMAX = {"PD": (60.0, 15.0), "FUT": (100.0, 25.0)}


def make_attribution_maps(group: str = "isoprene", experiment: str = "PD", season: str = "JJA",
                          start_year: int = 2001, end_year: int = 2014, extent_lat: float = 45.0,
                          fdr_alpha: float = 0.10, min_emission_share: float = 0.01,
                          fixed_scale: bool = True, save: bool = True, dpi: int = 200):
    """100 * Delta ln of E and of its factors, LCC vs CTRL (log changes add up).

    Row 1, exact:   Delta ln E = Delta ln(f_valid * EPS) + Delta ln gamma_eff
    Row 2, approx.: Delta ln gamma_eff ~ sum of Delta ln of the area-mean partial gammas.
    Row 3, exact:   residual = Delta ln gamma_eff - that sum = weighting + co-variation, using CLM's
                    GAMMA (product per patch and timestep, then area/time mean):
                    weighting    = Delta ln gamma_eff - Delta ln GAMMA   (emission- vs area-weighted patches)
                    co-variation = Delta ln GAMMA - sum Delta ln gamma_i (mean of product vs product of means)
    One colour scale for all panels, so they can be added by eye: +-ATTRIBUTION_VMAX[experiment]
    (PD +-60, FUT +-100); fixed_scale=False picks it from the data (95th percentile of |Delta ln E|).
    Cells with CTRL emission below `min_emission_share` x the 98th percentile north of
    `extent_lat` are blanked (log changes of near-zero fluxes are noise).
    Under the maps: emission-weighted mean (CTRL emission x area) north of `extent_lat`
    +- 95 % CI of the yearly means; with these weights the row sums hold for the means too.
    """
    pairs = BVOC_PAIRS[experiment]
    a = load_factors(pairs["ctrl"], group, season, start_year, end_year)
    b = load_factors(pairs["lcc"], group, season, start_year, end_year)
    partial = [f for f in ["GAMMAL", "GAMMAT", "GAMMAP", "GAMMAA", "GAMMAC"] if f in a]

    def dln(x, y):
        return np.log(y / x).where((x > 0) & (y > 0))

    d = {
        "MEG": dln(a["MEG"], b["MEG"]),
        "EPS": dln(a["EPS"] * a["f_valid"], b["EPS"] * b["f_valid"]),
        "gamma_eff": dln(a["gamma_eff"], b["gamma_eff"]),
    }
    for f in partial:
        d[f] = dln(a[f], b[f])
    d["residual"] = d["gamma_eff"] - sum(d[f] for f in partial)
    d["weighting"] = d["gamma_eff"] - dln(a["GAMMA"], b["GAMMA"])
    d["covariation"] = dln(a["GAMMA"], b["GAMMA"]) - sum(d[f] for f in partial)

    e_ctrl = a["MEG"].mean("year")
    thr = min_emission_share * float(np.nanquantile(e_ctrl.where(e_ctrl["lat"] >= extent_lat).values, 0.98))
    keep = e_ctrl > thr
    w_em = (e_ctrl * np.cos(np.deg2rad(e_ctrl["lat"]))).where(keep, 0)
    modified = _modified_mask(e_ctrl)

    rows = [["MEG", "EPS", "gamma_eff"], partial, ["residual", "weighting", "covariation"]]
    ncols = max(len(r) for r in rows)
    fig, axes = fm.map_grid(len(rows), ncols, left=2.2, titles_every_row=True)
    if fixed_scale:
        v, step = ATTRIBUTION_VMAX[experiment]
    else:
        v = symmetric_vmax(100 * d["MEG"].mean("year").where(keep & (e_ctrl["lat"] >= extent_lat)), q=0.95, fallback=20.0)
    norm = mcolors.TwoSlopeNorm(vmin=-v, vcenter=0, vmax=v)
    for i, keys in enumerate(rows):
        for j in range(ncols):
            if j >= len(keys):
                axes[i, j].set_visible(False)
                continue
            x = 100 * d[keys[j]].where(keep)
            m, half = _interval(x, w_em, extent_lat)
            p = _panel(axes[i, j], x.mean("year"), norm, "RdBu_r", TITLE[keys[j]], extent_lat,
                       not_sig=_not_significant(x, extent_lat, fdr_alpha), modified=modified,
                       text=fm._format_interval(m, half))
    _row_label(axes[0, 0], "Δln E\n= Δln(f·ε)\n+ Δln γ$_{eff}$")
    _row_label(axes[1, 0], "Δln γ$_{eff}$\n= Σ Δln γ$_i$\n+ residual")
    _row_label(axes[2, 0], "residual\n= weighting\n+ co-variation")
    cb = fm._cbar_below(fig, axes[-1, :], p, "100 · Δln (≈ % change), LCC vs CTRL", fm.CBAR_LABELSIZE_SHARED, shrink=0.6)
    if fixed_scale:
        cb.set_ticks(np.arange(-v, v + step / 2, step))

    _title(fig, f"Attribution of the emission change, {GROUP_TITLE[group]}: {experiment} "
                f"{pairs['lcc']} vs {pairs['ctrl']}, {season} ({start_year}–{end_year})",
           rf"$\mathit{{Under\ the\ maps}}$: CTRL-emission-weighted mean {extent_lat:g}–90°N ± 95 % CI of the yearly means"
           f" · hatched: not significant · dashed line: modified cells")
    if save:
        _save(fig, f"{experiment}_{group}_attribution_{season}_{start_year}_{end_year}.png", dpi)
    return fig, axes


# =============================================================================
# Plain maps of the CLM fields (no derived quantities)
# =============================================================================

GAMMA_COMPOUNDS = ["isoprene"] + GROUPS["MTERP"]
GAMMA_FIELDS = ["EPS", "GAMMA", "GAMMAL", "GAMMAT", "GAMMAP", "GAMMAA", "GAMMAC"]
_FIELD_TITLE = {"EPS": "EPS (ε)", "GAMMA": "GAMMA (TOTAL γ)", "GAMMAL": "GAMMAL (LAI)",
                "GAMMAT": "GAMMAT (TEMPERATURE)", "GAMMAP": "GAMMAP (LIGHT)",
                "GAMMAA": "GAMMAA (LEAF AGE)", "GAMMAC": "GAMMAC (CO$_2$)"}


def _clm_name(field: str, compound: str) -> str | None:
    """History-file name of `field` for `compound` (GAMMAL is shared, GAMMAC isoprene only)."""
    if field == "GAMMAL":
        return "GAMMAL"
    if field == "GAMMAC":
        return "GAMMAC_isoprene" if compound == "isoprene" else None
    return f"{field}_{compound}"


def gamma_fields(alias: str, season: str = "ANN", compounds=GAMMA_COMPOUNDS,
                 start_year: int = 2001, end_year: int = 2014) -> dict[tuple[str, str], xr.DataArray]:
    """Time mean (record-length weighted, months of `season`, all years) of the raw CLM fields.

    Values are the grid-cell values CLM writes: area means over vegetated patches,
    including patches that do not emit the compound (see module docstring).
    """
    bv = open_class(alias, "BVOC", start_year, end_year, "lnd")
    if "GAMMAL" not in bv:
        raise KeyError(f"{alias}: no GAMMA output (fBVOC members have MEGAN off)")
    days = record_days(bv)
    sel = bv["time"].dt.month.isin(SEASONS[season])
    w = days.where(sel, 0.0)
    out = {}
    for c in compounds:
        for f in GAMMA_FIELDS:
            name = _clm_name(f, c)
            if name is None or name not in bv:
                continue
            out[(c, f)] = ((bv[name] * w).sum("time") / w.sum()).where(bv[name].notnull().any("time"))
    return out


def make_gamma_maps(experiment: str = "PD", season: str = "ANN", compounds=GAMMA_COMPOUNDS,
                    fields=GAMMA_FIELDS, start_year: int = 2001, end_year: int = 2014,
                    extent_lat: float = 45.0, save: bool = True, dpi: int = 200):
    """One figure per member (CTRL and LCC of `experiment`): rows = compounds, columns = fields.

    Colour scale per column (0 to the 98th percentile north of `extent_lat`), shared by all
    compounds and by both members, so CTRL and LCC figures can be compared directly
    (colourbar under the last row). EPS has its own scale per row (emission factors differ by
    orders of magnitude between compounds), also shared by both members (colourbar under each map).
    """
    pairs = BVOC_PAIRS[experiment]
    members = [pairs["ctrl"], pairs["lcc"]]
    data = {m: gamma_fields(m, season, compounds, start_year, end_year) for m in members}

    vmax = {f: _p98([d[k] for d in data.values() for k in d if k[1] == f], extent_lat) for f in fields if f != "EPS"}
    vmax_eps = {c: _p98([d[(c, "EPS")] for d in data.values() if (c, "EPS") in d], extent_lat) for c in compounds}
    modified = _modified_mask(next(iter(data[members[0]].values())))

    figs = {}
    for m in members:
        fig, axes = fm.map_grid(len(compounds), len(fields), under=1.0, left=1.3, map_size=2.0)
        last = {}
        for i, c in enumerate(compounds):
            _row_label(axes[i, 0], c)
            for j, f in enumerate(fields):
                ax = axes[i, j]
                if (c, f) not in data[m]:
                    ax.set_visible(False)
                    continue
                norm = mcolors.Normalize(0, vmax_eps[c] if f == "EPS" else vmax[f])
                p = _panel(ax, data[m][(c, f)], norm, "viridis", _FIELD_TITLE[f] if i == 0 else "",
                           extent_lat, modified=modified)
                if f == "EPS":
                    fm._cbar_below(fig, ax, p, "[µg m$^{-2}$ h$^{-1}$]", fm.CBAR_LABELSIZE, shrink=fm.CBAR_SHRINK,
                                   height=fm.CBAR_HEIGHT, extend="max")
                else:
                    last[f] = (p, ax)
        for f, (p, ax) in last.items():
            fm._cbar_below(fig, ax, p, f"{f}\n[1]", fm.CBAR_LABELSIZE, shrink=fm.CBAR_SHRINK,
                           height=fm.CBAR_HEIGHT, extend="max")
        _title(fig, f"{m}: CLM MEGAN fields, {season} mean ({start_year}–{end_year})",
               "Grid-cell values = area means over vegetated patches · dashed line: modified cells")
        if save:
            _save(fig, f"{m}_gammas_{season}_{start_year}_{end_year}.png", dpi)
        figs[m] = (fig, axes)
    return figs
