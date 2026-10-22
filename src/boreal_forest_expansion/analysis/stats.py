"""Cell-wise significance of paired, year-by-year differences between nudged members.

All members are nudged to the same winds and surface pressure (a), so year y of one
member is paired with year y of the other.
"""

from __future__ import annotations

import numpy as np
import xarray as xr
from scipy import stats as sps


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
