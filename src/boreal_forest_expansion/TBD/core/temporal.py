from __future__ import annotations

import numpy as np
import pandas as pd
import xarray as xr


def annual_mean(series: xr.DataArray) -> xr.DataArray:
    """
    Compute annual means from a time series using year-start bins.
    """
    return series.resample(time="YS").mean(skipna=True)


def rolling_mean(values: np.ndarray, window: int) -> np.ndarray:
    """
    Compute a centered rolling mean for a 1D array.
    """
    return (
        pd.Series(values)
        .rolling(window=window, center=True, min_periods=1)
        .mean()
        .to_numpy()
    )
