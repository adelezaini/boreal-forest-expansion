"""D1 - far-field check of the BVOC contrast (LCC - LCC_fBVOC).

Question: is the BVOC contrast contaminated by the way the fBVOC runs are built?
In LCC_fBVOC all interactive MEGAN emissions are off and only ISOP/MTERP are
prescribed (from CTRL_PD, as a 2001-2009 climatology) (a, cases-setup.sh). The other
MEGAN compounds (BCARY, methanol, acetone, CO, ...) are missing worldwide. Their effect
on oxidants, ozone and aerosol is not a land-cover effect.

Test: in regions far from the land-cover change (30S-30N, 90S-30S), the land-cover-
driven BVOC signal should be ~0. A clear non-zero difference there measures the
artifact. Its size is compared with the BVOC signal from the modified cells, both as
contributions to the global mean (regional mean x area fraction), so they are on the
same scale.

The same test applied to the Total contrast (LCC - CTRL) measures anything other than
the land cover that differs between the members, e.g. the initial land state (a: LCC
had an extra 100-yr land-only spin-up, CTRL did not).

Limits (b):
  - The artifact also exists inside the LCC region; D1 only measures it outside.
    Its size there may differ (e.g. boreal BCARY and methanol emissions are local).
  - "Far field" assumes no long-range transport of the LCC signal into the tropics or
    the southern hemisphere. Modified cells are all north of 46 N (a), so this is
    plausible for aerosol and short-lived species, less so for O3 (lifetime ~weeks).
  - Thresholds in `assess` are a convention, not a physical criterion.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import xarray as xr

from boreal_forest_expansion.analysis.ghan import BANDS, COMPONENTS, GHAN_INPUTS, ghan_terms, term_name
from boreal_forest_expansion.analysis.loading import annual_mean, open_cam_monthly
from boreal_forest_expansion.analysis.regions import area_fraction, area_weights, default_regions, load_modified_cells, regional_mean
from boreal_forest_expansion.analysis.stats import cellwise_pvalue, fdr_mask, paired_summary

log = logging.getLogger(__name__)

FAR_REGIONS = ("tropics", "SH_extratropics")
SCALE_REGION = "modified_cells"


@dataclass
class Contrast:
    """A difference between two members: `minuend - subtrahend` (file globs)."""
    name: str            # e.g. "BVOC_PD"
    period: str          # "PD" or "FUT"
    minuend: str         # glob of h0 files, e.g. LCC_PD
    subtrahend: str      # glob of h0 files, e.g. LCC_PD_fBVOC
    label: str = ""      # e.g. "LCC_PD - LCC_PD_fBVOC"


@dataclass
class D1Result:
    diffs: dict[str, xr.Dataset]            # contrast -> yearly Ghan-term differences (year, lat, lon)
    table: pd.DataFrame                     # regional statistics, one row per contrast/term/region
    verdict: pd.DataFrame                   # one row per contrast/term
    weights: xr.DataArray
    regions: dict[str, xr.DataArray]
    contrasts: list[Contrast]
    meta: dict = field(default_factory=dict)


def _same_grid(a: xr.Dataset, b: xr.Dataset) -> None:
    for c in ("lat", "lon"):
        if a.sizes[c] != b.sizes[c] or not np.allclose(a[c].values, b[c].values, atol=1e-6):
            raise ValueError(f"{a.attrs.get('case')} and {b.attrs.get('case')} differ in {c}")


def contrast_yearly(c: Contrast, spinup_months: int = 12) -> tuple[xr.Dataset, xr.Dataset]:
    """Yearly differences of all Ghan terms for one contrast; returns (diff, minuend dataset)."""
    a = open_cam_monthly(c.minuend, GHAN_INPUTS, spinup_months)
    b = open_cam_monthly(c.subtrahend, GHAN_INPUTS, spinup_months)
    _same_grid(a, b)
    ta = annual_mean(ghan_terms(a), a["days_in_interval"])
    tb = annual_mean(ghan_terms(b), b["days_in_interval"])
    years = np.intersect1d(ta["year"].values, tb["year"].values)
    dropped = sorted(set(ta["year"].values) ^ set(tb["year"].values))
    if dropped:
        log.warning("%s: years only in one member, dropped: %s", c.name, dropped)
    if years.size < 3:
        raise ValueError(f"{c.name}: only {years.size} common complete years")
    diff = (ta.sel(year=years) - tb.sel(year=years)).load()
    diff.attrs.update(contrast=c.name, period=c.period, minuend=a.attrs["case"],
                      subtrahend=b.attrs["case"], label=c.label or f"{a.attrs['case']} - {b.attrs['case']}")
    return diff, a


def regional_table(diffs: dict[str, xr.Dataset], contrasts: list[Contrast], weights: xr.DataArray,
                   regions: dict[str, xr.DataArray]) -> pd.DataFrame:
    """Paired statistics of regional means for every contrast, term and region."""
    rows = []
    period = {c.name: c.period for c in contrasts}
    for cname, diff in diffs.items():
        for comp in COMPONENTS:
            for band in BANDS:
                term = term_name(comp, band)
                for rname, mask in regions.items():
                    series = regional_mean(diff[term], weights, mask)
                    s = paired_summary(series.values)
                    frac = area_fraction(weights, mask)
                    rows.append({
                        "contrast": cname, "period": period[cname], "component": comp, "band": band,
                        "term": term, "region": rname, "area_frac": frac, **s,
                        "contrib": s["mean"] * frac, "contrib_lo": s["ci_lo"] * frac,
                        "contrib_hi": s["ci_hi"] * frac,
                        "years": ",".join(str(int(y)) for y in diff["year"].values),
                    })
    return pd.DataFrame(rows)


def assess(table: pd.DataFrame, far_region: str = "tropics", scale_region: str = SCALE_REGION,
           ratio_threshold: float = 0.2) -> pd.DataFrame:
    """One verdict per contrast and term.

    detected : the far-field 95% interval excludes zero.
    ratio    : |far-field contribution to the global mean| / |modified-cells contribution|.
    verdict  :
      'none detected'           - far field not distinguishable from zero
      'detected, small'         - detected, ratio < ratio_threshold
      'detected, MATTERS'       - detected, ratio >= ratio_threshold
      'detected, no LCC signal' - detected but the modified-cells signal itself is not
                                  significant, so the ratio is not meaningful
    The 0.2 threshold is a convention (b): the artifact would then shift the global
    BVOC term by >= 20% of the local signal.
    """
    rows = []
    for (cname, term), g in table.groupby(["contrast", "term"], sort=False):
        far = g[g.region == far_region].iloc[0]
        loc = g[g.region == scale_region].iloc[0]
        detected = bool(far.ci_lo > 0 or far.ci_hi < 0)
        loc_sig = bool(loc.ci_lo > 0 or loc.ci_hi < 0)
        ratio = abs(far.contrib) / abs(loc.contrib) if loc.contrib != 0 else np.inf
        if not detected:
            verdict = "none detected"
        elif not loc_sig:
            verdict = "detected, no LCC signal"
        elif ratio >= ratio_threshold:
            verdict = "detected, MATTERS"
        else:
            verdict = "detected, small"
        rows.append({
            "contrast": cname, "period": far.period, "component": far.component, "band": far.band,
            "term": term, f"{far_region}_mean": far["mean"], f"{far_region}_ci_lo": far.ci_lo,
            f"{far_region}_ci_hi": far.ci_hi, f"{far_region}_p": far.p,
            f"{far_region}_contrib": far.contrib, f"{scale_region}_contrib": loc.contrib,
            "ratio": ratio, "verdict": verdict,
        })
    return pd.DataFrame(rows)


def run_d1(contrasts: list[Contrast], modified_cells_path: str, spinup_months: int = 12,
           ratio_threshold: float = 0.2) -> D1Result:
    """Load, decompose, difference, and assess every contrast."""
    diffs, grid = {}, None
    for c in contrasts:
        diffs[c.name], ds = contrast_yearly(c, spinup_months)
        if grid is None:
            grid = ds
        else:
            _same_grid(grid, ds)
    weights = area_weights(grid)
    modified = load_modified_cells(modified_cells_path, grid)
    regions = default_regions(grid, modified)
    table = regional_table(diffs, contrasts, weights, regions)
    verdict = assess(table, ratio_threshold=ratio_threshold)
    meta = {"weights_source": weights.attrs["source"], "n_modified": int(modified.sum()),
            "spinup_months": spinup_months, "ratio_threshold": ratio_threshold}
    return D1Result(diffs, table, verdict, weights, regions, contrasts, meta)


def mean_maps(diff: xr.Dataset, terms: list[str], alpha: float = 0.10) -> tuple[xr.Dataset, xr.Dataset]:
    """Time-mean difference maps and global FDR significance masks for `terms`."""
    means = diff[terms].mean("year")
    sig = xr.Dataset({t: fdr_mask(cellwise_pvalue(diff[t]), alpha=alpha) for t in terms})
    return means, sig
