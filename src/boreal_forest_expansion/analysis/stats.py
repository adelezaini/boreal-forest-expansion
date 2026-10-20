"""Statistics for paired, year-by-year differences between nudged members.

All members are nudged to the same winds and surface pressure (a), so year y of one
member is paired with year y of the other. The difference d_y removes most of the
shared weather noise; the uncertainty of the mean difference is s_d / sqrt(n).

Assumption (b): annual differences are roughly independent between years. The lag-1
autocorrelation r1 is reported; with r1 > 0 the effective sample size
n_eff = n (1 - r1) / (1 + r1) is smaller and the interval is widened accordingly.
"""

from __future__ import annotations

import numpy as np
import xarray as xr
from scipy import stats as sps


def lag1_autocorr(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if x.size < 3 or np.allclose(x, x.mean()):
        return np.nan
    a = x - x.mean()
    return float(np.sum(a[1:] * a[:-1]) / np.sum(a * a))


def paired_summary(d: xr.DataArray | np.ndarray, conf: float = 0.95, n_boot: int = 10000,
                   seed: int = 0) -> dict:
    """Mean of yearly differences with t-based and bootstrap intervals.

    Returns mean, sd, n, r1, n_eff, se (with n_eff), ci_lo/ci_hi (t, n_eff - 1 dof),
    p (two-sided, H0: mean = 0), boot_lo/boot_hi (percentile bootstrap over years;
    with only ~9 years it is narrower than the t interval and is shown for reference).
    """
    x = np.asarray(d, dtype=float).ravel()
    x = x[np.isfinite(x)]
    n = x.size
    out = {"mean": np.nan, "sd": np.nan, "n": n, "r1": np.nan, "n_eff": np.nan, "se": np.nan,
           "ci_lo": np.nan, "ci_hi": np.nan, "p": np.nan, "boot_lo": np.nan, "boot_hi": np.nan}
    if n < 3:
        return out
    mean, sd = x.mean(), x.std(ddof=1)
    r1 = lag1_autocorr(x)
    r1_pos = max(r1, 0.0) if np.isfinite(r1) else 0.0
    n_eff = max(n * (1 - r1_pos) / (1 + r1_pos), 2.0)
    se = sd / np.sqrt(n_eff)
    tcrit = sps.t.ppf(0.5 + conf / 2, df=n_eff - 1)
    p = 2 * sps.t.sf(abs(mean) / se, df=n_eff - 1) if se > 0 else (0.0 if mean != 0 else 1.0)
    rng = np.random.default_rng(seed)
    boot = x[rng.integers(0, n, size=(n_boot, n))].mean(axis=1)
    lo, hi = np.percentile(boot, [50 * (1 - conf), 50 * (1 + conf)])
    out.update(mean=mean, sd=sd, r1=r1, n_eff=n_eff, se=se, ci_lo=mean - tcrit * se,
               ci_hi=mean + tcrit * se, p=p, boot_lo=lo, boot_hi=hi)
    return out


def cellwise_pvalue(d: xr.DataArray, dim: str = "year") -> xr.DataArray:
    """Two-sided one-sample t-test of the yearly differences in every grid cell."""
    def _p(x):
        with np.errstate(invalid="ignore", divide="ignore"):
            return sps.ttest_1samp(x, 0.0, axis=-1, nan_policy="omit").pvalue
    p = xr.apply_ufunc(_p, d, input_core_dims=[[dim]], dask="allowed")
    return p.rename("p")


def fdr_mask(p: xr.DataArray, alpha: float = 0.10, within: xr.DataArray | None = None) -> xr.DataArray:
    """Benjamini-Hochberg false discovery rate control (Wilks 2016 suggests alpha_FDR = 0.10).

    Cells with p_(i) <= (i / N) * alpha are significant, where N counts the cells
    tested. `within` restricts the test to a region (e.g. 45-90 N for the maps), so N
    is the number of cells in that region.
    """
    pv = p.values.copy()
    valid = np.isfinite(pv)
    if within is not None:
        valid &= within.broadcast_like(p).transpose(*p.dims).values.astype(bool)
    flat = pv[valid]
    sig = np.zeros_like(pv, dtype=bool)
    if flat.size:
        order = np.argsort(flat)
        ranked = flat[order]
        thresh = alpha * np.arange(1, flat.size + 1) / flat.size
        below = np.nonzero(ranked <= thresh)[0]
        if below.size:
            cutoff = ranked[below.max()]
            sig[valid] = flat <= cutoff
    return xr.DataArray(sig, coords=p.coords, dims=p.dims, name="fdr_significant")
