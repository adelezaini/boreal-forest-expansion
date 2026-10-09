"""CAM/CLM monthly equilibrium diagnostics on rectilinear lat/lon grids.

No automatic equilibrium verdict. Monthly history is reduced one file at a time.
Years are integers (including 0001); time bounds are authoritative.
"""
from pathlib import Path
from datetime import timedelta
import json
import warnings
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt

CLM_VARS = ('GPP', 'TOTVEGC', 'TOTVEGN', 'TWS', 'H2OSOI', 'TSOI')
CAM_VARS = ('RESTOM', 'TREFHT', 'FSNT', 'FLNT', 'TS')
GASES = ('SF6', 'CFC115', 'N2O', 'CH4', 'CO2')
MOLAR_MASS = dict(SF6=146.055, CFC115=154.466, N2O=44.013, CH4=16.043, CO2=44.010)
R_EARTH, GRAVITY, M_AIR = 6371000.0, 9.80665, 28.9647


def history_files(path, component):
    """Accept a case directory or its hist directory; no recursive archive scan."""
    path = Path(path).expanduser()
    sub, pattern = ('lnd/hist', '*.clm2.h0.*.nc') if component == 'CLM' else ('atm/hist', '*.cam.h0.*.nc')
    files = sorted(set(path.glob(pattern)) | set((path / sub).glob(pattern)))
    if not files:
        raise FileNotFoundError(f'No {pattern} in {path} or {path / sub}')
    return files


def grid(ds):
    if 'lat' not in ds or 'lon' not in ds or ds.lat.ndim != 1 or ds.lon.ndim != 1:
        raise ValueError('Only rectilinear lat/lon history grids supported; regrid explicitly first.')
    if len(np.unique(ds.lon.values % 360)) != ds.sizes['lon']:
        raise ValueError('Duplicate cyclic longitude endpoint')
    return ds.lat.values, ds.lon.values % 360


def build_modified_cells(baseline, modified, output='modified_cells.nc', tolerance_pp=1e-6):
    """One-time PCT_NAT_PFT comparison; writes reusable NetCDF and readable CSV.

    Use the exact original surface file from which the modified file was made.
    Indices in CSV are zero-based source surfdata indices. Only PFT changes count.
    """
    output = Path(output)
    if output.exists() or output.with_suffix('.csv').exists():
        raise FileExistsError(f'{output}: choose a new name or deliberately delete the old cache')
    with xr.open_dataset(baseline) as a, xr.open_dataset(modified) as b:
        x, y = xr.align(a.PCT_NAT_PFT, b.PCT_NAT_PFT, join='exact')
        if x.dims != y.dims or x.shape != y.shape or 'natpft' not in x.dims:
            raise ValueError('PFT dimensions differ')
        lat, lon = b.LATIXY.values, b.LONGXY.values % 360
        if not np.allclose(a.LATIXY, lat, rtol=0, atol=1e-5) or not np.allclose(a.LONGXY.values % 360, lon, rtol=0, atol=1e-5):
            raise ValueError('Surface coordinates differ')
        if not np.array_equal(np.isfinite(x), np.isfinite(y)):
            raise ValueError('Surface missing-value patterns differ')
        delta = abs(y - x).max('natpft', skipna=True).values
        if delta.shape != lat.shape or not np.allclose(lat, lat[:, :1]) or not np.allclose(lon, lon[:1, :]):
            raise ValueError('Expected matching rectilinear surface grid')
        changed = np.isfinite(delta) & (delta > tolerance_pp)
        if not changed.any():
            raise ValueError('No changed cells: check surface files and tolerance')
        cache = xr.Dataset({'modified': (('lat', 'lon'), changed.astype('int8')),
                            'max_pft_change_pp': (('lat', 'lon'), delta)},
                           coords={'lat': lat[:, 0], 'lon': lon[0]},
                           attrs={'baseline': str(Path(baseline).resolve()), 'modified_source': str(Path(modified).resolve()),
                                  'tolerance_pp': tolerance_pp, 'definition': 'any natural PFT absolute change > tolerance_pp'})
    output.parent.mkdir(parents=True, exist_ok=True)
    cache.to_netcdf(output)
    i, j = np.where(changed)
    table = pd.DataFrame(dict(lat_index=i, lon_index=j, lat=lat[changed], lon_360=lon[changed],
                              lon_180=(lon[changed] + 180) % 360 - 180, max_pft_change_pp=delta[changed]))
    table.to_csv(output.with_suffix('.csv'), index=False)
    print(f'Saved {len(table)} modified cells: {output}, {output.with_suffix(".csv")}')
    return cache


def load_modified_cells(path):
    with xr.open_dataset(path) as ds:
        cache = ds.load()
    if not np.isin(cache.modified, [0, 1]).all() or not cache.modified.any():
        raise ValueError('Invalid/empty modified-cell mask')
    print(f'Modified cells: {int(cache.modified.sum())}; source: {cache.attrs.get("modified_source", "unspecified")}')
    return cache


def modified_mask(ds, cache):
    """Coordinate match with longitude wrapping/reordering; never nearest regrid."""
    lat, lon = grid(ds)
    def match(source, target, cyclic=False):
        distance = abs(np.asarray(target)[:, None] - np.asarray(source)[None, :])
        if cyclic:
            distance = np.minimum(distance, 360 - distance)
        index = distance.argmin(axis=1)
        if len(source) != len(target) or len(set(index)) != len(index) or np.any(distance[np.arange(len(target)), index] > 1e-4):
            raise ValueError('Mask and history grids differ; conservative remapping needs an explicit decision.')
        return index
    i, j = match(cache.lat.values, lat), match(cache.lon.values % 360, lon, True)
    return xr.DataArray(cache.modified.values[np.ix_(i, j)].astype(bool), dims=('lat', 'lon'), coords={'lat': ds.lat, 'lon': ds.lon})


def _surface(field):
    if 'time' in field.dims:
        first = field.isel(time=0, drop=True)
        if not bool((field == first).all()):
            raise ValueError(f'{field.name} changes with time inside a file')
        field = first
    if set(field.dims) != {'lat', 'lon'}:
        raise ValueError(f'{field.name}: expected lat/lon, got {field.dims}')
    return field.transpose('lat', 'lon')


def cell_area(ds):
    """Physical area (m2): prefer metadata, then exact spherical regular-grid bands."""
    lat, lon = grid(ds)
    if 'area' in ds:
        area = _surface(ds.area)
        unit = area.attrs.get('units', '').lower().replace(' ', '').replace('^', '')
        scale = {'m2': 1, 'km2': 1e6, 'steradians': R_EARTH**2, 'sr': R_EARTH**2, 'radians2': R_EARTH**2}.get(unit)
        if scale is None:
            raise ValueError(f'Unknown area units {unit!r}; supply verified area metadata')
        area = area * scale
    else:
        if not np.all(np.diff(lat) > 0) or len(lat) < 2 or len(lon) < 2:
            raise ValueError('Area fallback requires increasing global latitude and regular longitude')
        spacing = np.diff(np.r_[np.sort(lon), np.sort(lon)[0] + 360])
        if not np.allclose(spacing, 360 / len(lon), atol=1e-5):
            raise ValueError('Irregular longitude requires explicit cell area')
        if 'gw' in ds:
            band = ds.gw.values
            if band.shape != lat.shape or not np.isclose(band.sum(), 2, rtol=1e-4):
                raise ValueError('Invalid Gaussian quadrature weights')
        else:
            edges = np.r_[-90, (lat[:-1] + lat[1:]) / 2, 90]
            if lat.min() > -80 or lat.max() < 80:
                raise ValueError('Cannot infer global area from a regional grid')
            band = np.diff(np.sin(np.deg2rad(edges)))
        area = xr.DataArray(np.broadcast_to((R_EARTH**2 * 2 * np.pi / len(lon) * band)[:, None], (len(lat), len(lon))),
                            dims=('lat', 'lon'), coords={'lat': ds.lat, 'lon': ds.lon})
    if not bool((np.isfinite(area) & (area > 0)).all()):
        raise ValueError('Invalid cell area')
    return area


def spatial_weights(ds, component, region, cache=None):
    area = cell_area(ds)
    w = area.copy()
    if component == 'CLM':
        if 'landfrac' not in ds:
            raise ValueError('CLM requires landfrac')
        f = _surface(ds.landfrac)
        if not bool((np.isfinite(f) & (f >= 0) & (f <= 1)).all()):
            raise ValueError('landfrac must be a finite fraction in [0,1]')
        w = w * f
    if region == 'modified':
        if cache is None:
            raise ValueError('modified region requires saved mask')
        w = w.where(modified_mask(ds, cache), 0)
    elif region == 'north45':
        w = w.where(ds.lat >= 45, 0)
    elif region != 'global':
        raise ValueError(f'Unknown region {region}')
    if float(w.sum()) <= 0:
        raise ValueError('Empty regional weights')
    return w


def weighted_mean(field, weights, min_coverage=0.99):
    """NaN below required area coverage; no changing-denominator silent averages."""
    valid = weights.where(np.isfinite(field), 0)
    coverage = valid.sum(('lat', 'lon')) / weights.sum()
    mean = (field.fillna(0) * valid).sum(('lat', 'lon')) / valid.sum(('lat', 'lon'))
    return mean.where(coverage >= min_coverage), coverage


def at_soil_depth(ds, field, target=1.0, depth_overrides=None):
    dim = next((d for d in ('levsoi', 'levgrnd') if d in field.dims), None)
    if dim is None:
        raise ValueError(f'{field.name} has no soil dimension')
    if depth_overrides and dim in depth_overrides:
        depths = np.asarray(depth_overrides[dim], dtype=float)
    else:
        coord = ds.get(dim)
        units = '' if coord is None else coord.attrs.get('units', '').lower()
        factors = {'m': 1, 'meter': 1, 'meters': 1, 'metres': 1, 'cm': .01, 'centimeters': .01}
        if coord is None or coord.ndim != 1 or units not in factors:
            raise ValueError(f'{field.name}: {dim} lacks verified physical depths. Set depth_overrides["{dim}"] to model depths in metres.')
        depths = np.asarray(coord.values, dtype=float) * factors[units]
    if len(depths) != field.sizes[dim] or not np.isfinite(depths).all() or not np.all(np.diff(depths) > 0) or depths.min() < 0:
        raise ValueError(f'Invalid depth vector for {dim}')
    if target < depths.min() or target > depths.max():
        raise ValueError('Target soil depth outside saved levels')
    index = int(np.argmin(abs(depths - target)))
    return field.isel({dim: index}, drop=True), float(depths[index])


def monthly_dates(ds, timestamp='bounds'):
    """Return (year, month, duration_days); require complete calendar months.

    No-bounds fallback must be explicit: 'start', 'end', or 'mid'.
    """
    def native(t):
        return pd.Timestamp(t) if isinstance(t, np.datetime64) else t
    bounds = next((x for x in (ds.time.attrs.get('bounds'), 'time_bnds', 'time_bounds') if x and x in ds), None)
    result = []
    for i, t in enumerate(ds.time.values):
        if bounds:
            b = ds[bounds].isel(time=i).values.ravel()
            start, end = map(native, b)
            days = (end - start).total_seconds() / 86400
            next_y, next_m = (start.year + 1, 1) if start.month == 12 else (start.year, start.month + 1)
            if start.day != 1 or end.day != 1 or (end.year, end.month) != (next_y, next_m) or any(getattr(d, a, 0) for d in (start, end) for a in ('hour', 'minute', 'second')):
                raise ValueError('Expected complete monthly means; annual/daily/incomplete bounds detected')
        else:
            if timestamp not in ('start', 'end', 'mid'):
                raise ValueError('No time bounds: set timestamp explicitly after checking file conventions')
            start = native(t) - timedelta(days=1) if timestamp == 'end' else native(t)
            days = getattr(start, 'daysinmonth', None) or getattr(start, 'days_in_month', None)
            if days is None:
                raise ValueError('Cannot determine calendar month length')
        result.append((int(start.year), int(start.month), float(days)))
    return result


def _pressure(field):
    u = field.attrs.get('units', '').lower()
    if u not in ('pa', 'hpa', 'mb', 'mbar'):
        raise ValueError(f'{field.name}: pressure units {u!r}')
    return field * (1 if u == 'pa' else 100)


def gas_diagnostics(ds, name, weights, plev_hpa, basis=None):
    """Pressure profiles and column mass from monthly means (covariance omitted).

    basis explicitly 'dry' or 'moist' for mol/mol or kg/kg fields. Dry basis uses
    Q (specific humidity) to estimate dry layer mass. Full saved model column.
    """
    f = ds[name]
    if set(f.dims) != {'lev', 'lat', 'lon'}:
        raise ValueError(f'{name}: need prognostic 3D lev/lat/lon field, got {f.dims}')
    p = ds.hyam * _pressure(ds.P0) + ds.hybm * _pressure(ds.PS)
    pi = ds.hyai * _pressure(ds.P0) + ds.hybi * _pressure(ds.PS)
    if pi.sizes['ilev'] != f.sizes['lev'] + 1:
        raise ValueError('Pressure interfaces do not bracket all tracer levels')
    dp = pi.diff('ilev').rename(ilev='lev').assign_coords(lev=f.lev)
    if not bool((dp > 0).all()):
        raise ValueError('Expected top-to-bottom positive layer pressure thickness')
    if not bool((p > 0).all()):
        raise ValueError('Nonpositive midpoint pressure')
    def interpolate(v, pressure):
        if not np.isfinite(v).all() or not np.isfinite(pressure).all() or not np.all(np.diff(pressure) > 0):
            return np.full(len(plev_hpa), np.nan)
        return np.interp(np.log(np.asarray(plev_hpa) * 100), np.log(pressure), v, left=np.nan, right=np.nan)
    vertical = xr.apply_ufunc(interpolate, f, p, input_core_dims=[['lev'], ['lev']], output_core_dims=[['pressure']], vectorize=True)
    vertical = vertical.assign_coords(pressure=np.asarray(plev_hpa))
    profile, coverage = weighted_mean(vertical, weights, min_coverage=0)
    # Report pressure-dependent coverage: never extrapolate below ground/model top.
    profile = profile.where(coverage > 0)
    if basis not in ('dry', 'moist'):
        return profile, coverage, None, 'Set gas_basis to dry or moist after checking tracer definition'
    units = f.attrs.get('units', '').lower().replace(' ', '')
    molar = {'mol/mol': 1, 'molmol-1': 1, 'molmol^-1': 1, 'ppmv': 1e-6, 'ppm': 1e-6, 'ppbv': 1e-9, 'ppb': 1e-9, 'pptv': 1e-12, 'ppt': 1e-12}
    if units in molar:
        q = f * molar[units] * MOLAR_MASS[name] / M_AIR
        if basis == 'moist':
            if 'Q' not in ds:
                return profile, coverage, None, 'Moist molar conversion requires Q for mean molecular mass'
            q = f * molar[units] * MOLAR_MASS[name] * ((1 - ds.Q) / M_AIR + ds.Q / 18.01528)
    elif units in ('kg/kg', 'kgkg-1', 'kgkg^-1'):
        q = f
    else:
        return profile, coverage, None, f'Unsupported tracer units {units!r}; no guessed conversion'
    mass = dp / GRAVITY
    if basis == 'dry' or (basis == 'moist' and units in molar):
        if 'Q' not in ds:
            return profile, coverage, None, 'Dry-air burden requires Q'
        if ds.Q.attrs.get('units', '').lower().replace(' ', '') not in ('kg/kg', 'kgkg-1', 'kgkg^-1'):
            raise ValueError('Q must be specific humidity in kg/kg')
        if not bool(((ds.Q >= 0) & (ds.Q < 1)).all()):
            raise ValueError('Invalid Q')
        if basis == 'dry':
            mass = mass * (1 - ds.Q)
    column = (q * mass).sum('lev', skipna=False)
    mean, cov = weighted_mean(column, weights)
    # Total is not rescaled from incomplete columns.
    total = float((column.where(weights > 0, 0) * weights).sum(skipna=False)) / 1e9
    return profile, coverage, (float(mean), total, float(cov)), 'monthly-mean product approximation'


def read_case(files, component, regions=('global',), cache=None, variables=None, gases=GASES,
              years=None, soil_depth=1.0, depth_overrides=None, timestamp='bounds', gas_basis=None,
              plev_hpa=(1000, 850, 700, 500, 300, 200, 100, 70, 50, 30, 10, 5, 1)):
    """Stream monthly files; return scalar and pressure-profile tables plus audit."""
    variables = variables or (CLM_VARS if component == 'CLM' else CAM_VARS)
    rows, profiles, audit, seen, units, depths = [], [], [], set(), {}, {}
    for file in files:
        with xr.open_dataset(file, decode_times=True) as ds:
            dates = monthly_dates(ds, timestamp)
            for it, (year, month, days) in enumerate(dates):
                if years is not None and not years[0] <= year <= years[1]:
                    continue
                if (year, month) in seen:
                    raise ValueError(f'Duplicate month {year:04}-{month:02}: {file}')
                seen.add((year, month))
                s = ds.isel(time=it, drop=True)
                if component == 'CAM' and 'RESTOM' not in s and {'FSNT', 'FLNT'} <= set(s):
                    s['RESTOM'] = s.FSNT - s.FLNT
                    s.RESTOM.attrs = {'units': 'W/m2', 'long_name': 'Derived FSNT - FLNT; top of model'}
                for region in regions:
                    weights = spatial_weights(s, component, region, cache)
                    row = dict(year=year, month=month, days=days, region=region)
                    for var in variables:
                        if var not in s:
                            audit.append((var, 'missing'))
                            continue
                        field = s[var]
                        if component == 'CLM' and var in ('TSOI', 'H2OSOI'):
                            field, depth = at_soil_depth(s, field, soil_depth, depth_overrides)
                            if var in depths and depths[var] != depth:
                                raise ValueError(f'{var}: selected depth changes between files')
                            depths[var] = depth
                        if set(field.dims) != {'lat', 'lon'}:
                            audit.append((var, f'unsupported scalar dimensions {field.dims}'))
                            continue
                        u = field.attrs.get('units', 'unknown')
                        if var in units and units[var] != u:
                            raise ValueError(f'{var}: units changed')
                        units[var] = u
                        value, cov = weighted_mean(field, weights)
                        row[var], row[var + '__coverage'] = float(value), float(cov)
                    if component == 'CAM':
                        for gas in gases:
                            if gas not in s:
                                audit.append((gas, 'missing'))
                                continue
                            if set(s[gas].dims) != {'lev', 'lat', 'lon'}:
                                audit.append((gas, 'not a 3D tracer; prescribed scalar is not an equilibrium diagnostic'))
                                continue
                            required = {'PS', 'P0', 'hyam', 'hybm', 'hyai', 'hybi'}
                            if not required <= set(s.variables):
                                audit.append((gas, 'missing pressure auxiliaries: ' + str(sorted(required - set(s.variables)))))
                                continue
                            u = s[gas].attrs.get('units', 'unknown')
                            if gas in units and units[gas] != u:
                                raise ValueError(f'{gas}: units changed')
                            units[gas] = u
                            profile, cov, burden, note = gas_diagnostics(s, gas, weights, plev_hpa, (gas_basis or {}).get(gas))
                            audit.append((gas, note))
                            for pressure in plev_hpa:
                                profiles.append(dict(year=year, month=month, days=days, region=region, gas=gas, pressure_hpa=pressure,
                                                     value=float(profile.sel(pressure=pressure)), coverage=float(cov.sel(pressure=pressure))))
                            if burden:
                                row[gas + '_column_kg_m2'], row[gas + '_burden_Tg'], row[gas + '_column__coverage'] = burden
                                units[gas + '_column_kg_m2'], units[gas + '_burden_Tg'] = 'kg m-2', 'Tg'
                    rows.append(row)
    if not rows:
        raise ValueError('No monthly records in requested year range')
    table = pd.DataFrame(rows).sort_values(['region', 'year', 'month']).reset_index(drop=True)
    audit = pd.DataFrame(sorted(set(audit)), columns=['variable', 'note'])
    return dict(monthly=table, profiles=pd.DataFrame(profiles), units=units, depths=depths, audit=audit, files=[str(p) for p in files],
                config=dict(component=component, regions=regions, years=years, timestamp=timestamp, soil_depth_m=soil_depth,
                            gas_basis=gas_basis, pressure_hpa=list(plev_hpa), mask_sources=dict(cache.attrs) if cache is not None else None))


def annual_means(table, group=('region',), values=None):
    """Day-weighted means; require all twelve months and finite values per field."""
    values = values or [c for c in table if c not in {*group, 'year', 'month', 'days'} and pd.api.types.is_numeric_dtype(table[c])]
    rows = []
    for keys, block in table.groupby([*group, 'year'], dropna=False):
        row = dict(zip([*group, 'year'], keys))
        complete = len(block) == 12 and set(block.month) == set(range(1, 13))
        for var in values:
            row[var] = np.average(block[var], weights=block.days) if complete and np.isfinite(block[var]).all() else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def rolling_diagnostics(annual, var, region, window=20, late_years=10, block=5):
    """Trailing equal-year mean; derivative is one-year difference, not gradient."""
    s = annual[annual.region == region].set_index('year')[var].sort_index()
    s = s.reindex(range(int(s.index.min()), int(s.index.max()) + 1))
    rolling = s.rolling(window, min_periods=window).mean()
    derivative = rolling.diff()
    late = s.iloc[-late_years:]
    slope = np.polyfit(late.index, late.values, 1)[0] if len(late) == late_years and late.notna().all() else np.nan
    last, previous = s.iloc[-block:], s.iloc[-2*block:-block]
    delta = last.mean() - previous.mean() if len(previous) == block and last.notna().all() and previous.notna().all() else np.nan
    summary = dict(variable=var, region=region, valid_annual_years=int(s.notna().sum()), last_year=int(s.index[-1]),
                   late_slope_per_year=slope, block_change=delta, final_rolling_derivative=derivative.iloc[-1],
                   rolling_status='available' if np.isfinite(derivative.iloc[-1]) else f'needs {window + 1} consecutive complete years ending at final year')
    return pd.DataFrame({'annual': s, 'rolling': rolling, 'derivative': derivative}), summary


def plot_timeseries(result, variables, region, title='', window=20):
    table = result['monthly']; table = table[table.region == region]
    annual = annual_means(table)
    fig, axes = plt.subplots(len(variables), 2, figsize=(13, 2.8 * len(variables)), squeeze=False, layout='constrained')
    summaries = []
    for (left, right), var in zip(axes, variables):
        if var not in table:
            left.set_title(f'{var}: unavailable'); right.axis('off'); continue
        d, summary = rolling_diagnostics(annual, var, region, window)
        summaries.append(summary)
        left.plot(table.year + (table.month - .5) / 12, table[var], color='0.75', lw=.7, label='Monthly')
        left.plot(d.index + .5, d.annual, color='#245B78', lw=1.2, label='Annual (day-weighted)')
        if d['rolling'].notna().any():
            left.plot(d.index + .5, d['rolling'], color='#D35400', lw=2, label=f'{window}-year mean (trailing)')
        right.plot(d.index + .5, d.derivative, color='#D35400')
        right.axhline(0, color='0.4', lw=.7)
        right.set_xlim(float(d.index.min()), float(d.index.max()) + 1)
        if not d.derivative.notna().any():
            right.text(.5, .5, f'Needs at least {window + 1} complete consecutive years', transform=right.transAxes, ha='center', wrap=True, bbox=dict(facecolor='white', edgecolor='none'))
        unit = result['units'].get(var, 'unknown')
        depth = f" at {result['depths'][var]:.3f} m" if var in result['depths'] else ''
        left.set(title=var + depth, ylabel=unit, xlabel='Model year')
        right.set(title=f'Change in {window}-year rolling mean', ylabel=f'{unit} / year', xlabel='Model year')
        left.legend(fontsize=8); left.grid(alpha=.15); right.grid(alpha=.15)
    fig.suptitle(f'{title} | {region}')
    return fig, pd.DataFrame(summaries)


def plot_gas_profiles(result, gas, region='global', block=5, min_coverage=.95, title=''):
    table = result['profiles']
    if table.empty or gas not in set(table.gas):
        print(f'{gas}: no usable profile'); return None
    table = table[(table.gas == gas) & (table.region == region)].copy()
    table.loc[table.coverage < min_coverage, 'value'] = np.nan
    annual = annual_means(table, group=('region', 'gas', 'pressure_hpa'), values=['value', 'coverage'])
    data = annual.pivot(index='year', columns='pressure_hpa', values='value').sort_index().sort_index(axis=1)
    data = data.reindex(range(int(data.index.min()), int(data.index.max()) + 1))
    fig, axes = plt.subplots(1, 3, figsize=(14, 5), layout='constrained')
    image = axes[0].pcolormesh(data.index + .5, data.columns, data.values.T, shading='nearest', cmap='viridis')
    fig.colorbar(image, ax=axes[0], label=result['units'][gas])
    axes[0].set(xlabel='Model year', title='Annual global/region mean')
    if len(data) >= 2 * block:
        previous, last = data.iloc[-2*block:-block], data.iloc[-block:]
        # Require all years at each pressure; prevent unequal block denominators.
        a, b = previous.mean().where(previous.notna().all()), last.mean().where(last.notna().all())
        axes[1].plot(a, data.columns, label=f'{previous.index[0]}–{previous.index[-1]}', color='#245B78')
        axes[1].plot(b, data.columns, label=f'{last.index[0]}–{last.index[-1]}', color='#D35400')
        axes[1].legend(); axes[2].plot(b - a, data.columns, color='#D35400')
    else:
        axes[1].text(.1, .5, f'Needs {2*block} years', transform=axes[1].transAxes)
    axes[1].set(xlabel=result['units'][gas], title='Last two blocks')
    axes[2].set(xlabel=result['units'][gas], title='Last minus previous block'); axes[2].axvline(0, color='0.5', lw=.7)
    for ax in axes:
        ax.set_yscale('log'); ax.set_ylim(float(data.columns.max()), float(data.columns.min())); ax.set_ylabel('Pressure (hPa)')
    fig.suptitle(f'{title}: {gas} | {region} | area coverage ≥ {min_coverage:.0%}')
    return fig


def save_result(result, directory):
    directory = Path(directory); directory.mkdir(parents=True, exist_ok=True)
    for key in ('monthly', 'profiles', 'audit'):
        result[key].to_csv(directory / f'{key}.csv', index=False)
    annual_means(result['monthly']).to_csv(directory / 'annual.csv', index=False)
    (directory / 'metadata.json').write_text(json.dumps({k: result[k] for k in ('units', 'depths', 'files', 'config')}, indent=2))
