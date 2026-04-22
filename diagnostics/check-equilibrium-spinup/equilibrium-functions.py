@dataclass
class EquilibriumSummary:
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


def open_mfdataset_sorted(file_glob: str) -> xr.Dataset:
    files = sorted(glob.glob(file_glob))
    if not files:
        raise FileNotFoundError(f"No files found for pattern: {file_glob}")
    ds = xr.open_mfdataset(
        files,
        combine="by_coords",
        decode_times=True,
        parallel=False,
        use_cftime=False,
    )
    if "time" in ds.coords:
        ds = ds.sortby("time")
    return ds


def infer_lat_lon_names(da: xr.DataArray) -> Tuple[Optional[str], Optional[str]]:
    lat_candidates = ["lat", "latitude", "LAT", "nav_lat"]
    lon_candidates = ["lon", "longitude", "LON", "nav_lon"]
    lat_name = next((d for d in da.dims if d in lat_candidates), None)
    lon_name = next((d for d in da.dims if d in lon_candidates), None)
    if lat_name is None:
        lat_name = next((c for c in da.coords if c in lat_candidates and c in da.dims), None)
    if lon_name is None:
        lon_name = next((c for c in da.coords if c in lon_candidates and c in da.dims), None)
    return lat_name, lon_name


def get_units(da: xr.DataArray) -> str:
    return str(da.attrs.get("units", "")).strip()


def annual_mean(series: xr.DataArray) -> xr.DataArray:
    return series.resample(time="YS").mean(skipna=True)


def rolling_mean(values: np.ndarray, window: int) -> np.ndarray:
    return pd.Series(values).rolling(window=window, center=True, min_periods=1).mean().to_numpy()


def region_to_dataset_lon_bounds(lon_min: float, lon_max: float, ds_lon: xr.DataArray):
    lon_values = np.asarray(ds_lon.values)
    if np.nanmax(lon_values) > 180.0:
        a = lon_min % 360.0
        b = lon_max % 360.0
    else:
        a = lon_min
        b = lon_max
    crosses = a > b
    return a, b, crosses


def subset_region(da: xr.DataArray, region_bounds):
    if region_bounds is None:
        return da
    lat_name, lon_name = infer_lat_lon_names(da)
    if lat_name is None or lon_name is None:
        raise ValueError(f"Cannot subset region for {da.name}: lat/lon dims not found")
    lat_min, lat_max, lon_min, lon_max = region_bounds
    da_sub = da.where((da[lat_name] >= lat_min) & (da[lat_name] <= lat_max), drop=True)
    a, b, crosses = region_to_dataset_lon_bounds(lon_min, lon_max, da_sub[lon_name])
    if crosses:
        da_sub = da_sub.where((da_sub[lon_name] >= a) | (da_sub[lon_name] <= b), drop=True)
    else:
        da_sub = da_sub.where((da_sub[lon_name] >= a) & (da_sub[lon_name] <= b), drop=True)
    return da_sub


def collapse_extra_dims(da: xr.DataArray) -> xr.DataArray:
    lat_name, lon_name = infer_lat_lon_names(da)
    keep = {"time"}
    if lat_name is not None:
        keep.add(lat_name)
    if lon_name is not None:
        keep.add(lon_name)
    extra_dims = [d for d in da.dims if d not in keep]
    if extra_dims:
        da = da.mean(dim=extra_dims, skipna=True)
    return da


def weighted_mean_latlon(da: xr.DataArray) -> xr.DataArray:
    lat_name, lon_name = infer_lat_lon_names(da)
    if lat_name is None or lon_name is None:
        other_dims = [d for d in da.dims if d != "time"]
        return da.mean(dim=other_dims, skipna=True) if other_dims else da
    weights = np.cos(np.deg2rad(da[lat_name]))
    return da.weighted(weights).mean(dim=[lat_name, lon_name], skipna=True)


def reduce_series(da: xr.DataArray, region_bounds):
    da = collapse_extra_dims(da)
    da = subset_region(da, region_bounds)
    da = weighted_mean_latlon(da)
    return da


def equilibrium_test(annual_series: xr.DataArray, last_n_years: int, rel_drift_threshold: float, pval_threshold: float):
    years = pd.to_datetime(annual_series["time"].values).year.astype(float)
    vals = annual_series.values.astype(float)
    mask = np.isfinite(vals)
    years = years[mask]
    vals = vals[mask]
    if len(vals) < max(5, last_n_years):
        raise ValueError(f"Not enough annual points ({len(vals)}) for last_n_years={last_n_years}")
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
            np.isnan(reg.pvalue) or reg.pvalue >= pval_threshold or abs(reg.slope) < 1e-15
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
    years = pd.to_datetime(annual_series["time"].values).year.astype(float)
    vals = annual_series.values.astype(float)
    mask = np.isfinite(vals)
    years = years[mask]
    vals = vals[mask]
    rows = []
    if len(vals) < window:
        return pd.DataFrame(columns=["year_end", "slope_per_year", "slope_per_decade", "p_value", "r_value"])
    for i in range(window - 1, len(vals)):
        y = years[i - window + 1 : i + 1]
        v = vals[i - window + 1 : i + 1]
        reg = linregress(y, v)
        rows.append({
            "year_end": y[-1],
            "slope_per_year": reg.slope,
            "slope_per_decade": reg.slope * 10.0,
            "p_value": reg.pvalue,
            "r_value": reg.rvalue,
        })
    return pd.DataFrame(rows)


def maybe_convert_units(da: xr.DataArray, varname: str) -> xr.DataArray:
    units = get_units(da).lower()
    if varname.upper() == "PRECT":
        if units in {"m/s", "m s-1"}:
            out = da * 1000.0 * 86400.0
            out.attrs["units"] = "mm/day"
            return out
        if units in {"kg/m2/s", "kg m-2 s-1"}:
            out = da * 86400.0
            out.attrs["units"] = "mm/day"
            return out
    if varname.upper() in {"PSL", "PS"} and units == "pa":
        out = da / 100.0
        out.attrs["units"] = "hPa"
        return out
    return da


def add_derived_cam_fields(ds: xr.Dataset) -> xr.Dataset:
    if "RESTOM" not in ds and "FSNT" in ds and "FLNT" in ds:
        ds["RESTOM"] = ds["FSNT"] - ds["FLNT"]
        ds["RESTOM"].attrs["units"] = get_units(ds["FSNT"])
        ds["RESTOM"].attrs["long_name"] = "Top-of-atmosphere net downward radiation (FSNT - FLNT)"
    return ds