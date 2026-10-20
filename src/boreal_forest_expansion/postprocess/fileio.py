"""Reading NorESM history files, fixing time, dropping spin-up, saving and loading.

Time convention (verified in the source code and on a CAM h0 file):
CAM (cam_history.F90) and CLM (histFileMod.F90) write `time` = END of the averaging
interval, e.g. the January 2009 mean is stamped 2009-02-01. `fix_time` moves it to the
midpoint of the bounds (2009-01-16 12:00). Works for any calendar (NorESM uses noleap).

Changes vs the old code (old: postprocess.create_dataset, fix_cam_time, save_postprocessed;
functions.load_dataset_dict)
--------------------------------------------------------------------------------------
- FIXED   fix_cam_time built the renamed copy `ds_` but assigned the new time to the
          original `ds`, so the CLM renames were lost.
- FIXED   the default 'datetime64' option crashed: xarray decodes noleap times as cftime
          objects, and cftime + np.timedelta64 raises UFuncTypeError (tested).
- CHANGED time = midpoint of the bounds instead of "start + 14 days": same meaning,
          no calendar arithmetic, works for CAM (time_bnds) and CLM (time_bounds).
- FIXED   empty glob: now a clear FileNotFoundError instead of an obscure xarray error.
- CHANGED variables are selected per file while opening (preprocess) instead of opening
          every field of every file first: faster and far less memory, esp. for CLM.
- CHANGED a requested variable that is missing is logged and skipped (and recorded in the
          output attribute `missing_variables`) instead of raising KeyError.
- FIXED   save_postprocessed used an undefined `casename` (NameError for lnd), looped over
          all categories even if only one was loaded (KeyError), and always appended the
          Ghan variables even when they had not been computed.
- CHANGED output name <alias>_<component>_<category>_<y0>-<y1>.nc (component added) and
          global attributes record case, tape, spin-up, missing variables, creation date.
- CHANGED load_processed finds the year span from the file name (old: hard-coded
          '20082012') and takes the case aliases as an argument (old: module-level list).
- ADDED   (review round 2) scan_files(): availability is checked in EVERY file, not only
          the first. A variable present in only some files raises ValueError (xarray would
          otherwise fill the gaps with NaN silently; tested).
- ADDED   (review round 2) validate_monthly_means(): before fix_time and drop_spinup,
          checks that records are 28-31 days long, contiguous (no gaps, duplicates,
          unsorted files) and time-averaged (no cell_methods 'time: point'), so an
          instantaneous or daily tape passed with --tape is rejected, not mislabelled.
"""
import glob
import logging
import os
from datetime import datetime

import numpy as np
import xarray as xr

log = logging.getLogger(__name__)

MODEL_NAME = {"atm": "cam", "lnd": "clm2"}
BOUNDS_NAMES = ("time_bnds", "time_bounds")   # CAM, CLM


# ---------------------------------------------------------------------------- reading
def find_history_files(raw_path, casename, component, tape="h0"):
    """Sorted list of history files, e.g. <raw>/<case>/atm/hist/<case>.cam.h0.*.nc"""
    pattern = os.path.join(raw_path, casename, component, "hist",
                           f"{casename}.{MODEL_NAME[component]}.{tape}.*.nc")
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No history files match {pattern}")
    log.info("Found %d files for %s %s %s", len(files), casename, component, tape)
    return files


def scan_files(files, variables):
    """Check which requested variables are in ALL, SOME or NONE of the files.

    Reads only the file headers. Returns (present, missing, partial) where
    partial = {variable: [files that lack it]}.
    """
    lacking = {v: [] for v in variables}
    for f in files:
        with xr.open_dataset(f, decode_cf=False) as d:
            names = set(d.variables)
        for v in variables:
            if v not in names:
                lacking[v].append(f)
    n = len(files)
    present = [v for v in variables if not lacking[v]]
    missing = [v for v in variables if len(lacking[v]) == n]
    partial = {v: lacking[v] for v in variables if 0 < len(lacking[v]) < n}
    return present, missing, partial


def open_history(files, variables):
    """Open history files, keeping only `variables` (+ time bounds).

    Returns (dataset, missing), where `missing` lists requested variables that are in
    none of the files (logged and skipped). A variable present in only SOME files raises
    ValueError: xarray would otherwise fill the gaps with NaN silently (tested), e.g.
    after a change of fincl between run segments.
    Variables are selected per file before concatenation (fast, low memory).
    """
    present, missing, partial = scan_files(files, list(variables) + list(BOUNDS_NAMES))
    bounds = [b for b in BOUNDS_NAMES if b in present]
    partial = {v: f for v, f in partial.items() if v not in BOUNDS_NAMES}
    missing = [v for v in missing if v not in BOUNDS_NAMES]
    if partial:
        lines = [f"  {v}: missing in {len(f)} of {len(files)} files, e.g. {os.path.basename(f[0])}"
                 for v, f in partial.items()]
        raise ValueError("Variables present in only some history files "
                         "(did fincl change between run segments?):\n" + "\n".join(lines))
    if missing:
        log.warning("Not in history files, skipped: %s", ", ".join(missing))
    if not bounds:
        raise KeyError(f"No time bounds variable ({' or '.join(BOUNDS_NAMES)}) in the files")
    keep = [v for v in present if v not in BOUNDS_NAMES] + bounds

    ds = xr.open_mfdataset(
        files,
        preprocess=lambda d: d[[v for v in keep if v in d]],
        combine="by_coords",
        data_vars="minimal",    # only concatenate variables that have a time dimension
        coords="minimal",
        compat="override",      # time-invariant variables (gw, hyai, area, ...) taken from first file
    )
    return ds, missing


def bounds_name(ds):
    """Name of the time-bounds variable (CAM: time_bnds, CLM: time_bounds)."""
    name = next((b for b in BOUNDS_NAMES if b in ds), None)
    if name is None:
        raise KeyError(f"No time bounds variable ({' or '.join(BOUNDS_NAMES)}) in dataset")
    return name


def validate_monthly_means(ds, min_days=28, max_days=31):
    """Raise ValueError unless every record is a monthly MEAN and the records are contiguous.

    Checks (on the time bounds and the cell_methods attributes):
      1. each record spans min_days..max_days days        (rejects daily/6-hourly tapes,
                                                            partial first intervals)
      2. each record starts where the previous one ended  (rejects gaps, duplicates,
                                                            unsorted files)
      3. no time-varying field has cell_methods "time: point" (rejects instantaneous
         tapes, e.g. avgflag 'I'; CAM writes time bounds for those too), and at least
         one field has "time: mean".
    fix_time() and drop_spinup() rely on these properties.
    """
    name = bounds_name(ds)
    bnds = ds[name].compute()
    bnd_dim = bnds.dims[-1]
    start, end = bnds.isel({bnd_dim: 0}), bnds.isel({bnd_dim: 1})
    days = ((end - start) / np.timedelta64(1, "D")).values

    bad = np.flatnonzero((days < min_days) | (days > max_days))
    if bad.size:
        examples = ", ".join(f"{start.values[i]} ({days[i]:g} days)" for i in bad[:3])
        raise ValueError(f"{bad.size} records are not monthly ({min_days}-{max_days} days), "
                         f"e.g. {examples}. This pipeline needs monthly-mean history files.")

    s, e = start.values, end.values
    breaks = np.flatnonzero(s[1:] != e[:-1])
    if breaks.size:
        examples = ", ".join(f"{e[i]} -> {s[i + 1]}" for i in breaks[:3])
        raise ValueError(f"{breaks.size} gaps/duplicates/out-of-order records in the time axis, "
                         f"e.g. previous end -> next start: {examples}")

    methods = {v: ds[v].attrs.get("cell_methods", "") for v in ds.data_vars
               if "time" in ds[v].dims and v != name}
    point = [v for v, m in methods.items() if "time: point" in m]
    if point:
        raise ValueError(f"Instantaneous fields (cell_methods 'time: point'): {', '.join(point[:5])}. "
                         "This pipeline needs time-averaged (monthly-mean) history files.")
    if methods and not any("time: mean" in m for m in methods.values()):
        raise ValueError("No field has cell_methods 'time: mean'; cannot confirm monthly means.")
    log.info("Time axis OK: %d contiguous monthly-mean records", len(days))
    return ds


def fix_time(ds):
    """Set `time` to the midpoint of the averaging interval (calendar-agnostic).

    Assumes time-averaged records; call validate_monthly_means() first.
    """
    bounds = bounds_name(ds)
    bnd_dim = ds[bounds].dims[-1]
    mid = ds[bounds].mean(bnd_dim).compute()
    attrs = dict(ds.time.attrs, comment="midpoint of time bounds (model writes interval end)")
    encoding = {k: v for k, v in ds.time.encoding.items() if k in ("units", "calendar")}
    out = ds.assign_coords(time=("time", mid.values, attrs))
    out.time.encoding.update(encoding)      # keep 'days since ...' + noleap when writing
    return out


def drop_spinup(ds, months):
    """Remove the first `months` records (one record = one month after validate_monthly_means)."""
    if months <= 0:
        return ds
    if months >= ds.sizes["time"]:
        raise ValueError(f"Cannot drop {months} spin-up months from {ds.sizes['time']} time steps")
    log.info("Dropping %d spin-up months", months)
    return ds.isel(time=slice(months, None))


def fix_unit_labels(ds, fixes):
    """Correct `units` attributes that the model writes wrongly (no numeric change)."""
    for var, units in fixes.items():
        if var in ds:
            ds[var].attrs.update(units=units, units_comment="corrected after source check")
    return ds


# ---------------------------------------------------------------------------- saving
def year_span(ds):
    years = ds.time.dt.year.values
    return f"{years[0]:04d}-{years[-1]:04d}"


def processed_filename(alias, component, category, span):
    """e.g. CTRL_PD_atm_BVOC_2009-2018.nc"""
    return f"{alias}_{component}_{category}_{span}.nc"


def save_category(ds, variables, out_path, alias, component, category, provenance):
    """Write the present `variables` of `ds` (+ time bounds) to one netCDF file."""
    keep = [v for v in variables if v in ds] + [b for b in BOUNDS_NAMES if b in ds]
    out = ds[keep]
    out.attrs = dict(provenance, category=category,
                     created=datetime.now().isoformat(timespec="seconds"))
    os.makedirs(out_path, exist_ok=True)
    fname = os.path.join(out_path, processed_filename(alias, component, category, year_span(ds)))
    out.to_netcdf(fname)
    log.info("Saved %s", fname)
    return fname


# ---------------------------------------------------------------------------- loading
def load_processed(processed_path, aliases, component, category, lat_min=None, lon_180=False):
    """Load one category for several cases into {alias: Dataset}.

    lat_min : keep only latitudes > lat_min (e.g. 45 for the boreal domain).
    lon_180 : convert longitudes from 0..360 to -180..180.
    """
    out = {}
    for alias in aliases:
        pattern = os.path.join(processed_path, processed_filename(alias, component, category, "*"))
        matches = sorted(glob.glob(pattern))
        if len(matches) != 1:
            raise FileNotFoundError(f"Expected one file for {pattern}, found {len(matches)}: {matches}")
        ds = xr.open_dataset(matches[0])
        if lon_180:
            ds = ds.assign_coords(lon=((ds.lon + 180) % 360) - 180).sortby("lon")
        if lat_min is not None:
            ds = ds.sel(lat=ds.lat[ds.lat > lat_min])
        out[alias] = ds
    return out
