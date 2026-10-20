"""Open monthly CAM (and CLM) history output for the analysis, with the time fix and spin-up drop.

Works on either
  - raw archive files      <archive>/<case>/atm/hist/<case>.cam.h0.YYYY-MM.nc
  - selected/concatenated  <case>.cam.h0.YYYY-MM_YYYY-MM.nc   (postprocess/prep)
because both match the glob  <case>.cam.h0.*.nc

Only the variables you ask for are read (plus time bounds and area weights), so
opening 10 years of monthly output is cheap.

Evidence tags used in comments: (a) verified in source/files, (b) inference, (c) unverified.
"""

from __future__ import annotations

import glob
import logging
from pathlib import Path
from typing import Iterable

import numpy as np
import xarray as xr

log = logging.getLogger(__name__)

# Variables that are kept when present, because the analysis needs them for weights.
# CAM: gw, GRIDAREA, LANDFRAC.  CLM: area (km2), landfrac.
WEIGHT_VARS = ("gw", "GRIDAREA", "LANDFRAC", "area", "landfrac")
COMPONENT_TAGS = (".cam.", ".clm2.")


def _case_of(path: str) -> str:
    """Case name = file name up to '.cam.' or '.clm2.' (e.g. NF2000..._ctrl_f19_f19-20260925)."""
    name = Path(path).name
    for tag in COMPONENT_TAGS:
        if tag in name:
            return name.split(tag)[0]
    return name


def find_files(pattern: str | Path) -> list[str]:
    """Expand a glob and refuse to mix two different cases.

    A wildcard in the case date (e.g. '...lcc_f19_f19-*') is convenient, but if two
    runs with different dates exist the files would be silently merged. That is an
    error here, not a warning.
    """
    files = sorted(glob.glob(str(pattern)))
    if not files:
        raise FileNotFoundError(f"No files match {pattern}")
    cases = sorted({_case_of(f) for f in files})
    if len(cases) > 1:
        raise ValueError(
            f"Pattern {pattern} matches files from {len(cases)} cases: {cases}. "
            "Put the full case name (with date) in the pattern."
        )
    return files


def _bounds_name(ds: xr.Dataset) -> str | None:
    for name in ("time_bnds", "time_bounds"):
        if name in ds.variables:
            return name
    return None


def fix_time(ds: xr.Dataset) -> xr.Dataset:
    """Stamp each monthly mean at the midpoint of its averaging interval.

    CAM writes monthly means with time = end of the interval, i.e. the January mean
    is stamped 1 February (a: verified in the earlier postprocessing work). Grouping
    by year/month on the raw stamp therefore shifts everything by one month.
    Also stores the interval length in days as `days_in_interval` (used as weight).
    """
    bname = _bounds_name(ds)
    if bname is None:
        raise ValueError(
            "No time bounds in the file: cannot place monthly means correctly. "
            "Open raw h0 files, or keep time_bnds when selecting variables."
        )
    bnds = ds[bname].load()
    bdim = [d for d in bnds.dims if d != "time"][0]
    start, end = bnds.isel({bdim: 0}).values, bnds.isel({bdim: 1}).values
    length = end - start                      # timedelta64 or datetime.timedelta objects
    mid = start + length / 2
    if np.issubdtype(np.asarray(length).dtype, np.timedelta64):
        days = length / np.timedelta64(1, "D")
    else:
        days = np.array([t.total_seconds() / 86400.0 for t in length])
    out = ds.assign_coords(time=("time", mid, ds.time.attrs))
    out["days_in_interval"] = ("time", np.asarray(days, dtype=float))
    return out


def drop_spinup(ds: xr.Dataset, months: int = 12) -> xr.Dataset:
    """Remove the first `months` monthly means (decision: 12 months of spin-up)."""
    if months <= 0:
        return ds
    if ds.sizes["time"] <= months:
        raise ValueError(f"Only {ds.sizes['time']} months in file, cannot drop {months} of spin-up")
    return ds.isel(time=slice(months, None))


def open_cam_monthly(
    pattern: str | Path,
    variables: Iterable[str],
    spinup_months: int = 12,
    strict: bool = True,
) -> xr.Dataset:
    """Open monthly CAM or CLM output for one case: selected variables, fixed time, no spin-up.

    Works for CLM h0 too (<case>.clm2.h0.*.nc): time bounds are found under either
    name, and `area`/`landfrac` are kept for land weights.

    Parameters
    ----------
    pattern
        Glob matching the h0 files of ONE case (see `find_files`).
    variables
        Data variables to read.
    spinup_months
        Number of leading months to drop.
    strict
        True: a missing variable raises KeyError. False: missing variables are listed in
        ds.attrs['missing'] and skipped.
    """
    files = find_files(pattern)
    variables = list(variables)
    keep = set(variables) | set(WEIGHT_VARS) | {"time_bnds", "time_bounds"}

    def _select(ds: xr.Dataset) -> xr.Dataset:
        present = [v for v in ds.data_vars if v in keep]
        return ds[present]

    try:  # xarray >= 2025.01
        time_kw = {"decode_times": xr.coders.CFDatetimeCoder(use_cftime=True)}
    except AttributeError:  # older xarray
        time_kw = {"use_cftime": True}
    ds = xr.open_mfdataset(
        files,
        combine="by_coords",
        preprocess=_select,
        data_vars="minimal",
        coords="minimal",
        compat="override",
        parallel=False,
        **time_kw,
    )
    missing = [v for v in variables if v not in ds.data_vars]
    if missing and strict:
        raise KeyError(f"{_case_of(files[0])}: missing {missing}. Present: {sorted(ds.data_vars)}")
    if missing:
        log.warning("%s: %d requested variables missing: %s", _case_of(files[0]), len(missing), missing)

    ds = drop_spinup(fix_time(ds), spinup_months)
    ds.attrs["missing"] = ",".join(missing)
    ds.attrs["case"] = _case_of(files[0])
    ds.attrs["n_files"] = len(files)
    log.info("%s: %d files, %d months after spin-up", ds.attrs["case"], len(files), ds.sizes["time"])
    return ds


def annual_mean(ds: xr.Dataset | xr.DataArray, days: xr.DataArray) -> xr.Dataset | xr.DataArray:
    """Annual means weighted by month length; incomplete years are dropped (with a log line).

    Every variable in `ds` must have a time dimension (pass only the fields to average,
    not gw or other static fields, which would otherwise be broadcast over time).
    """
    if isinstance(ds, xr.Dataset):
        static = [v for v in ds.data_vars if "time" not in ds[v].dims]
        if static:
            raise ValueError(f"annual_mean: variables without time dimension {static}; drop them first")
    year = ds["time"].dt.year
    counts = days.groupby(year).count()
    complete = counts["year"].where(counts == 12, drop=True).values
    incomplete = sorted(set(counts["year"].values) - set(complete))
    if incomplete:
        log.warning("Dropping incomplete years %s", incomplete)
    w = days.groupby(year) / days.groupby(year).sum()
    out = (ds * w).groupby(year).sum("time", skipna=False)
    return out.sel(year=complete)
