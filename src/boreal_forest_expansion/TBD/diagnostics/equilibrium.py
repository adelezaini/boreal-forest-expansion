from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import xarray as xr
from scipy.stats import linregress

from boreal_forest_expansion.core.metadata import get_units


@dataclass
class EquilibriumSummary:
    """
    Summary diagnostics describing whether a series appears close to equilibrium.
    """
    variable: str
    region: str
    n_years_total: int
    last_n_years: int
    mean_last_period: float
    slope_per_year: float
    slope_per_decade: float
    p_value: float
    r_value: float
    start_last_period: float
    end_last_period: float
    abs_change_last_period: float
    rel_change_last_period: float
    equilibrium_flag: bool
    units: str
    note: str


def _extract_years(time_values) -> np.ndarray:
    """
    Extract years as float from time coordinate values.

    Notes
    -----
    This helper avoids assuming standard pandas-compatible datetimes only.
    It works for both numpy/pandas timestamps and cftime objects.
    """
    try:
        return pd.to_datetime(time_values).year.astype(float)
    except Exception:
        return np.array([t.year for t in time_values], dtype=float)


def equilibrium_test(
    annual_series: xr.DataArray,
    last_n_years: int,
    rel_drift_threshold: float,
    pval_threshold: float,
):
    """
    Test whether the final segment of an annual series appears close to equilibrium.
    """
    years = _extract_years(annual_series["time"].values)
    vals = annual_series.values.astype(float)

    mask = np.isfinite(vals)
    years = years[mask]
    vals = vals[mask]

    if len(vals) < max(5, last_n_years):
        raise ValueError(
            f"Not enough annual points ({len(vals)}) for last_n_years={last_n_years}"
        )

    y_last = years[-last_n_years:]
    v_last = vals[-last_n_years:]

    reg = linregress(y_last, v_last)
    fitted_last = reg.intercept + reg.slope * y_last

    start = v_last[0]
    end = v_last[-1]
    abs_change = end - start
    mean_last = np.nanmean(v_last)

    if np.isclose(mean_last, 0.0, atol=1e-20):
        rel_change = np.nan
        eq_flag = False
        note = "Mean over final period is ~0; relative change unstable."
    else:
        rel_change = abs_change / abs(mean_last)
        eq_flag = (abs(rel_change) < rel_drift_threshold) and (
            np.isnan(reg.pvalue)
            or reg.pvalue >= pval_threshold
            or abs(reg.slope) < 1e-15
        )
        note = "Flag combines small relative drift with weak/insignificant late-run trend."

    summary = EquilibriumSummary(
        variable="",
        region="",
        n_years_total=len(vals),
        last_n_years=last_n_years,
        mean_last_period=float(mean_last),
        slope_per_year=float(reg.slope),
        slope_per_decade=float(reg.slope * 10.0),
        p_value=float(reg.pvalue),
        r_value=float(reg.rvalue),
        start_last_period=float(start),
        end_last_period=float(end),
        abs_change_last_period=float(abs_change),
        rel_change_last_period=float(rel_change),
        equilibrium_flag=bool(eq_flag),
        units=get_units(annual_series),
        note=note,
    )

    return summary, y_last, fitted_last


def moving_window_trends(annual_series: xr.DataArray, window: int) -> pd.DataFrame:
    """
    Compute linear trends over a sliding window of annual values.
    """
    years = _extract_years(annual_series["time"].values)
    vals = annual_series.values.astype(float)

    mask = np.isfinite(vals)
    years = years[mask]
    vals = vals[mask]

    rows = []
    if len(vals) < window:
        return pd.DataFrame(
            columns=["year_end", "slope_per_year", "slope_per_decade", "p_value", "r_value"]
        )

    for i in range(window - 1, len(vals)):
        y = years[i - window + 1 : i + 1]
        v = vals[i - window + 1 : i + 1]
        reg = linregress(y, v)

        rows.append(
            {
                "year_end": y[-1],
                "slope_per_year": reg.slope,
                "slope_per_decade": reg.slope * 10.0,
                "p_value": reg.pvalue,
                "r_value": reg.rvalue,
            }
        )

    return pd.DataFrame(rows)
