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
    EPS_*, GAMMA*: vegetated soil/crop patches, lake = 0; bare ground, urban, wetland excluded.
  So the grid-cell GAMMA_* is an AREA mean over vegetated patches, not an emission-weighted
  one, and MEG != k * EPS * GAMMA in mixed cells.

Effective (emission-weighted) gamma, exact by construction (b, derived from the above):
    gamma_eff = MEG / (k * EPS * f_valid),   k = 1e-9 / 3600  [kg s-1 per ug h-1]
    f_valid   = land fraction where EPS is defined
              = natveg * (1 - bare share) + crop + lake   (PCT_LANDUNIT, PCT_NAT_PFT)
  Check (a, CTRL_PD JJA): gamma_eff / GAMMA = 0.90-1.14 in cells with one PFT > 90 %.
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
import cartopy.feature as cfeature

from boreal_forest_expansion.plotting.common import ax_map_properties, cut_extent_Orthographic
from boreal_forest_expansion.plotting.forcing_maps import (
    BVOC_PAIRS, FIGURE_DIR, add_stippling, open_class, symmetric_vmax,
)
from boreal_forest_expansion.postprocess.averaging import record_days
from boreal_forest_expansion.analysis.stats import cellwise_pvalue, fdr_mask
from boreal_forest_expansion.analysis.regions import load_modified_cells

REPO_DIR = Path("/cluster/home/adelez/BOREAL-FOREST-EXPANSION")
MODIFIED_CELLS = REPO_DIR / "diagnostics/check-simulation-equilibrium/lcc-modified-cells/modified_cells.csv"
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
                 start_year: int = 2001, end_year: int = 2009) -> xr.Dataset:
    """Seasonal means per year (year, lat, lon) of E, EPS, gamma_eff and the partial gammas."""
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

    # land fraction where EPS/GAMMA are defined (landunits: 0 natveg, 1 crop, 4 lake)
    pl = et["PCT_LANDUNIT"].isel(time=0) / 100.0
    bare = ld["PCT_NAT_PFT"].isel(time=0, natpft=0) / 100.0
    f_valid = (pl.isel(ltype=0) * (1 - bare) + pl.isel(ltype=1) + pl.isel(ltype=4))

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
# Plotting helpers
# =============================================================================

def _modified_mask(like: xr.DataArray) -> xr.DataArray | None:
    try:
        return load_modified_cells(MODIFIED_CELLS, like.to_dataset(name="x"))
    except Exception as exc:          # outline is optional
        print(f"modified-cells outline skipped: {exc}")
        return None


def _panel(ax, da, norm, cmap, title, extent_lat=45.0, sig=None, modified=None, text=None):
    cut_extent_Orthographic(ax, lat=extent_lat)
    ax_map_properties(ax, alpha=0.25, coastlines=False, gridlines=False, ocean=False,
                      land=True, borders=False, rivers=False)
    p = da.plot.pcolormesh(ax=ax, x="lon", y="lat", transform=ccrs.PlateCarree(),
                           cmap=cmap, norm=norm, add_colorbar=False, zorder=1)
    ax.add_feature(cfeature.OCEAN, facecolor="white", edgecolor="none", alpha=0.85, zorder=2)
    ax.coastlines(linewidth=0.5, zorder=3)
    if modified is not None:
        ax.contour(modified["lon"], modified["lat"], modified.astype(float), levels=[0.5],
                   colors="0.25", linewidths=0.4, transform=ccrs.PlateCarree(), zorder=3)
    if sig is not None and bool(sig.any()):
        add_stippling(ax, sig, style="dots", zorder=4)
    ax.set_title(title, fontsize=9, fontweight="bold", pad=4)
    if text:
        ax.text(0.5, -0.06, text, transform=ax.transAxes, ha="center", va="top", fontsize=7.5)
    return p


def _cbar(fig, ax, p, label):
    cb = fig.colorbar(p, ax=ax, orientation="horizontal", pad=0.1, shrink=0.85, aspect=22, extend="both")
    cb.ax.tick_params(labelsize=7)
    cb.set_label(label, fontsize=7)
    return cb


def _weighted_mean(da, w, lat_min):
    m = (da["lat"] >= lat_min) & np.isfinite(da) & (w > 0)
    return float((da * w).where(m).sum() / w.where(m).sum())


# =============================================================================
# Figures
# =============================================================================

def make_factor_maps(group: str = "isoprene", experiment: str = "PD", season: str = "JJA",
                     start_year: int = 2001, end_year: int = 2009, extent_lat: float = 45.0,
                     fdr_alpha: float = 0.10, save: bool = True, dpi: int = 250):
    """Rows: CTRL, LCC, LCC vs CTRL (% change). Columns: EPS, gamma_eff, GAMMA and partial gammas.

    Bottom row: 100 * (exp(mean Delta ln) - 1) of paired yearly seasonal means; dots = FDR-
    significant cells (paired t-test on yearly Delta ln, alpha_FDR 0.10, cells >= extent_lat).
    """
    pairs = BVOC_PAIRS[experiment]
    a = load_factors(pairs["ctrl"], group, season, start_year, end_year)
    b = load_factors(pairs["lcc"], group, season, start_year, end_year)
    factors = [f for f in ["EPS", "gamma_eff", "GAMMA", "GAMMAL", "GAMMAT", "GAMMAP", "GAMMAA", "GAMMAC"]
               if f in a]
    modified = _modified_mask(a["MEG"].isel(year=0))
    land_w = np.cos(np.deg2rad(a["lat"])) * a["f_valid"]

    fig, axes = plt.subplots(3, len(factors), figsize=(2.55 * len(factors), 8.6),
                             subplot_kw={"projection": ccrs.Orthographic(0, 90)},
                             constrained_layout=True)
    for j, f in enumerate(factors):
        label, units = FACTOR_LABEL[f]
        ma, mb = a[f].mean("year"), b[f].mean("year")
        north = lambda x: x.where(x["lat"] >= extent_lat)
        vmax = float(np.nanquantile(np.concatenate([north(ma).values.ravel(), north(mb).values.ravel()]), 0.98))
        vmax = vmax if np.isfinite(vmax) and vmax > 0 else 1.0
        norm = mcolors.Normalize(0, vmax)
        for i, (m, who) in enumerate(((ma, pairs["ctrl"]), (mb, pairs["lcc"]))):
            p = _panel(axes[i, j], m, norm, "viridis", f"{label}\n{who}" if i == 0 else who,
                       extent_lat, modified=modified,
                       text=f"mean ≥{extent_lat:g}°N: {_weighted_mean(m, land_w, extent_lat):.3g}")
            if i == 1:
                _cbar(fig, axes[:2, j].tolist(), p, units)
        # relative change from paired yearly log ratios
        dln = np.log(b[f] / a[f]).where((a[f] > 0) & (b[f] > 0))
        rel = 100 * (np.exp(dln.mean("year")) - 1)
        sig = fdr_mask(cellwise_pvalue(dln), alpha=fdr_alpha, within=dln["lat"] >= extent_lat)
        v = symmetric_vmax(north(rel), q=0.95, fallback=10.0)
        p = _panel(axes[2, j], rel, mcolors.TwoSlopeNorm(vmin=-v, vcenter=0, vmax=v), "RdBu_r",
                   "LCC vs CTRL", extent_lat, sig=sig, modified=modified)
        _cbar(fig, axes[2, j], p, "% change")

    cov = f", coverage of MEG_MTERP ≥45°N: {a.attrs['coverage_45N']:.0%}" if "coverage_45N" in a.attrs else ""
    warn = "  [FUT: CTRL_FUT has a different land spin-up]" if experiment == "FUT" else ""
    fig.suptitle(f"{experiment}, {season} {start_year}–{end_year}: MEGAN factors, {GROUP_TITLE[group]}{cov}{warn}",
                 fontsize=12, fontweight="bold")
    if save:
        MEGAN_FIG_DIR.mkdir(parents=True, exist_ok=True)
        path = MEGAN_FIG_DIR / f"{experiment}_{group}_factors_{season}_{start_year}_{end_year}.png"
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        print(f"Saved {path}")
    return fig, axes


def make_attribution_maps(group: str = "isoprene", experiment: str = "PD", season: str = "JJA",
                          start_year: int = 2001, end_year: int = 2009, extent_lat: float = 45.0,
                          fdr_alpha: float = 0.10, min_emission_share: float = 0.01,
                          save: bool = True, dpi: int = 250):
    """100 * Delta ln of E and of its factors, LCC vs CTRL (log changes add up).

    Exact:   Delta ln E = Delta ln(f_valid * EPS) + Delta ln gamma_eff
    Approx.: Delta ln gamma_eff ~ sum of Delta ln of the area-mean partial gammas;
             'residual' = Delta ln gamma_eff - that sum (patch mixing, see module docstring).
    Cells with CTRL emission below `min_emission_share` x the 98th percentile north of
    `extent_lat` are blanked (log changes of near-zero fluxes are noise).
    Text under panels: emission-weighted mean (CTRL emission x area) north of `extent_lat`.
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

    e_ctrl = a["MEG"].mean("year")
    thr = min_emission_share * float(np.nanquantile(e_ctrl.where(e_ctrl["lat"] >= extent_lat).values, 0.98))
    keep = e_ctrl > thr
    w_em = (e_ctrl * np.cos(np.deg2rad(e_ctrl["lat"]))).where(keep, 0)
    modified = _modified_mask(e_ctrl)

    titles = {"MEG": "Δln E (total)", "EPS": "Δln(f·ε)  composition", "gamma_eff": "Δln γ$_{eff}$  activity",
              "GAMMAL": "Δln γ$_L$", "GAMMAT": "Δln γ$_T$", "GAMMAP": "Δln γ$_P$", "GAMMAA": "Δln γ$_A$",
              "GAMMAC": "Δln γ$_C$", "residual": "residual (γ$_{eff}$ − Σ partial)"}
    keys = list(d)
    ncols = 4
    nrows = int(np.ceil(len(keys) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(3.2 * ncols, 3.5 * nrows),
                             subplot_kw={"projection": ccrs.Orthographic(0, 90)},
                             constrained_layout=True)
    axes = np.asarray(axes).ravel()
    v = symmetric_vmax(100 * d["MEG"].mean("year").where(keep & (e_ctrl["lat"] >= extent_lat)), q=0.95, fallback=20.0)
    norm = mcolors.TwoSlopeNorm(vmin=-v, vcenter=0, vmax=v)
    for ax, k in zip(axes, keys):
        x = d[k].where(keep)
        sig = fdr_mask(cellwise_pvalue(x), alpha=fdr_alpha, within=x["lat"] >= extent_lat)
        m = 100 * x.mean("year")
        p = _panel(ax, m, norm, "RdBu_r", titles[k], extent_lat, sig=sig, modified=modified,
                   text=f"emission-weighted ≥{extent_lat:g}°N: {_weighted_mean(m, w_em, extent_lat):+.1f}")
    for ax in axes[len(keys):]:
        ax.set_axis_off()
    _cbar(fig, axes[:len(keys)].tolist(), p, "100 · Δln  (≈ % change), LCC vs CTRL")
    warn = "  [FUT: CTRL_FUT has a different land spin-up]" if experiment == "FUT" else ""
    fig.suptitle(f"{experiment}, {season}: attribution of the emission change, {GROUP_TITLE[group]}{warn}",
                 fontsize=12, fontweight="bold")
    if save:
        MEGAN_FIG_DIR.mkdir(parents=True, exist_ok=True)
        path = MEGAN_FIG_DIR / f"{experiment}_{group}_attribution_{season}_{start_year}_{end_year}.png"
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        print(f"Saved {path}")
    return fig, axes


# =============================================================================
# Plain maps of the CLM fields (no derived quantities)
# =============================================================================

GAMMA_COMPOUNDS = ["isoprene"] + GROUPS["MTERP"]
GAMMA_FIELDS = ["EPS", "GAMMA", "GAMMAL", "GAMMAT", "GAMMAP", "GAMMAA", "GAMMAC"]
_FIELD_TITLE = {"EPS": "EPS (ε)", "GAMMA": "GAMMA (total γ)", "GAMMAL": "GAMMAL (LAI)",
                "GAMMAT": "GAMMAT (temperature)", "GAMMAP": "GAMMAP (light)",
                "GAMMAA": "GAMMAA (leaf age)", "GAMMAC": "GAMMAC (CO$_2$)"}


def _clm_name(field: str, compound: str) -> str | None:
    """History-file name of `field` for `compound` (GAMMAL is shared, GAMMAC isoprene only)."""
    if field == "GAMMAL":
        return "GAMMAL"
    if field == "GAMMAC":
        return "GAMMAC_isoprene" if compound == "isoprene" else None
    return f"{field}_{compound}"


def gamma_fields(alias: str, season: str = "ANN", compounds=GAMMA_COMPOUNDS,
                 start_year: int = 2001, end_year: int = 2009) -> dict[tuple[str, str], xr.DataArray]:
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
                    fields=GAMMA_FIELDS, start_year: int = 2001, end_year: int = 2009,
                    extent_lat: float = 45.0, save: bool = True, dpi: int = 200):
    """One figure per member (CTRL and LCC of `experiment`): rows = compounds, columns = fields.

    Colour scale per column (0 to the 98th percentile north of `extent_lat`), shared by all
    compounds and by both members, so CTRL and LCC figures can be compared directly.
    EPS has its own scale per row (emission factors differ by orders of magnitude between
    compounds), also shared by both members.
    """
    pairs = BVOC_PAIRS[experiment]
    members = [pairs["ctrl"], pairs["lcc"]]
    data = {m: gamma_fields(m, season, compounds, start_year, end_year) for m in members}

    def p98(arrays):
        vals = np.concatenate([a.where(a["lat"] >= extent_lat).values.ravel() for a in arrays])
        v = float(np.nanquantile(vals, 0.98)) if np.isfinite(vals).any() else 1.0
        return v if v > 0 else 1.0

    vmax = {f: p98([d[k] for d in data.values() for k in d if k[1] == f]) for f in fields if f != "EPS"}
    vmax_eps = {c: p98([d[(c, "EPS")] for d in data.values() if (c, "EPS") in d]) for c in compounds}
    modified = _modified_mask(next(iter(data[members[0]].values())))

    figs = {}
    for m in members:
        fig, axes = plt.subplots(len(compounds), len(fields), figsize=(2.3 * len(fields), 2.45 * len(compounds)),
                                 subplot_kw={"projection": ccrs.Orthographic(0, 90)}, constrained_layout=True,
                                 squeeze=False)
        last = {}
        for i, c in enumerate(compounds):
            for j, f in enumerate(fields):
                ax = axes[i, j]
                if (c, f) not in data[m]:
                    ax.set_axis_off()
                    continue
                top = f if f != "EPS" else None
                norm = mcolors.Normalize(0, vmax_eps[c] if f == "EPS" else vmax[f])
                title = (_FIELD_TITLE[f] + "\n" if i == 0 else "") + c
                p = _panel(ax, data[m][(c, f)], norm, "viridis", title, extent_lat, modified=modified)
                ax.title.set_fontsize(8)
                if f == "EPS":
                    cb = fig.colorbar(p, ax=ax, orientation="horizontal", pad=0.03, shrink=0.8, aspect=18, extend="max")
                    cb.ax.tick_params(labelsize=6)
                else:
                    last[f] = (p, [axes[k, j] for k in range(len(compounds)) if (compounds[k], f) in data[m]])
        for f, (p, axs) in last.items():
            _cbar(fig, axs[-1], p, "1")
        fig.suptitle(f"{m}: CLM MEGAN fields, {season} mean {start_year}–{end_year}"
                     f"  (EPS in µg m$^{{-2}}$ h$^{{-1}}$; grey line = modified cells)",
                     fontsize=12, fontweight="bold")
        if save:
            MEGAN_FIG_DIR.mkdir(parents=True, exist_ok=True)
            path = MEGAN_FIG_DIR / f"{m}_gammas_{season}_{start_year}_{end_year}.png"
            fig.savefig(path, dpi=dpi, bbox_inches="tight")
            print(f"Saved {path}")
        figs[m] = (fig, axes)
    return figs
