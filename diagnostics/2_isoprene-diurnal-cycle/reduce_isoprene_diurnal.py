"""Reduce the 30-min CAM tape of the MEGAN exact-split branch runs to monthly diurnal composites.

Input : <archive>/<case>/atm/hist/<case>.cam.h1.YYYY-MM-DD-SSSSS.nc
        SFISOP, SFMTERP (kg m-2 s-1), 48 records per file, avgflag 'I' (instantaneous,
        user_nl_cam: nhtfrq = 0, 1; avgflag_pertape = 'A', 'I').
Output: data/processed-data/isoprene-diurnal/diurnal_<ALIAS>_<YEAR>.nc
        <VAR>(month, step, lat, lon) = mean over the days of that month of the value at
        UTC half-hour step `step` (0..47); float32, plus n_days(month, step).

Time convention: a record stamped t is the flux of the model step that ends at t
(instantaneous output written at the end of the step). It is assigned to the step centre
t - 15 min, so a 00:00 stamp belongs to 23:30-24:00 of the previous day (and year).
This handles the 2000-chain (hybrid) files that start at 00:00 and the branch files
that start at 00:30 the same way (cf. the MEGAN month-offset fix of 2026-11-16).

The raw files on /cluster/work are purged (~Dec 2026); the outputs live on NIRD.

Usage:
    $PY diagnostics/2_isoprene-diurnal-cycle/reduce_isoprene_diurnal.py [--nproc 12] [--periods PD FUT]
Skips existing outputs; a year is written only if every (day, step) is present.
"""
import argparse
import glob
import os
import re
import sys
import time
from multiprocessing import Pool

import netCDF4
import numpy as np

ARCHIVE = "/cluster/work/users/adelez/archive"
OUTDIR = "/cluster/home/adelez/BOREAL-FOREST-EXPANSION/data/processed-data/isoprene-diurnal"
VARS = ("SFISOP", "SFMTERP")
STEPS = 48
DAYS_PER_MONTH = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
CUM_DAYS = np.concatenate([[0], np.cumsum(DAYS_PER_MONTH)])

# alias -> {first year of chain: case}; years used = the chain years except the hybrid year 2000
PERIOD_PREFIX = {"PD": "NF2000norbc_tropstratchem_nudg", "FUT": "NF2100ssp585norbc_tropstratchem_nudg"}
YEARS = {2000: (2001, 2002), 2005: (2005, 2006), 2010: (2010, 2011)}


def find_cases():
    """Return {(alias, year): [case dirs]} for the meganpatch branch chains present in the archive."""
    out = {}
    for period, prefix in PERIOD_PREFIX.items():
        for veg in ("ctrl", "lcc"):
            for chain, years in YEARS.items():
                hits = sorted(glob.glob(f"{ARCHIVE}/{prefix}_{veg}_meganpatch_f19_f19-*-from{chain}"))
                if len(hits) != 1:
                    print(f"  ! {period} {veg} from{chain}: {len(hits)} archive dirs, skipped", flush=True)
                    continue
                for y in years:
                    out[(f"{veg.upper()}_{period}", y)] = hits[0]
    return out


def read_file(path):
    """Return (year, day-of-year index 0..364, step 0..47) arrays and the fields of one file."""
    with netCDF4.Dataset(path) as ds:
        t = np.asarray(ds.variables["time"][:], dtype="f8")  # days since 2000-01-01, noleap
        centre = t - 0.5 / STEPS                              # step centre = stamp - 15 min
        days = np.floor(centre + 1e-9)
        year = 2000 + (days // 365).astype(int)
        doy = (days % 365).astype(int)
        step = np.floor((centre - days) * STEPS + 1e-6).astype(int)
        data = {v: np.asarray(ds.variables[v][:], dtype="f4") for v in VARS}
    return year, doy, step, data


def reduce_year(case_dir, year, nproc):
    files = sorted(glob.glob(f"{case_dir}/atm/hist/*.cam.h1.{year}-*.nc"))
    nxt = sorted(glob.glob(f"{case_dir}/atm/hist/*.cam.h1.{year + 1}-01-01-*.nc"))
    files += nxt[:1]                                         # its 00:00 stamp belongs to 31 Dec
    files = [f for f in files if re.search(r"\.cam\.h1\.\d{4}-\d{2}-\d{2}-\d{5}\.nc$", f)]
    if not files:
        return None, "no cam.h1 files"
    with netCDF4.Dataset(files[0]) as ds:
        lat = ds.variables["lat"][:]
        lon = ds.variables["lon"][:]
        nlat, nlon = lat.size, lon.size
    sums = {v: np.zeros((12, STEPS, nlat, nlon), "f8") for v in VARS}
    seen = np.zeros((365, STEPS), bool)
    with Pool(nproc) as pool:
        for yr, doy, step, data in pool.imap(read_file, files, chunksize=4):
            for i in range(yr.size):
                if yr[i] != year:
                    continue
                if seen[doy[i], step[i]]:
                    raise RuntimeError(f"duplicate record {year} doy {doy[i]} step {step[i]}")
                seen[doy[i], step[i]] = True
                m = np.searchsorted(CUM_DAYS, doy[i], side="right") - 1
                for v in VARS:
                    sums[v][m, step[i]] += data[v][i]
    if not seen.all():
        return None, f"incomplete: {(~seen).sum()} of {seen.size} (day, step) records missing"
    n_days = DAYS_PER_MONTH[:, None] * np.ones(STEPS, int)
    means = {v: (sums[v] / n_days[:, :, None, None]).astype("f4") for v in VARS}
    return (lat, lon, means, n_days, files), "ok"


def write(path, case_dir, year, lat, lon, means, n_days, files):
    tmp = path + ".part"
    with netCDF4.Dataset(tmp, "w") as ds:
        ds.createDimension("month", 12)
        ds.createDimension("step", STEPS)
        ds.createDimension("lat", lat.size)
        ds.createDimension("lon", lon.size)
        ds.createVariable("month", "i4", ("month",))[:] = np.arange(1, 13)
        st = ds.createVariable("step", "f8", ("step",))
        st[:] = (np.arange(STEPS) + 0.5) * 24 / STEPS
        st.long_name = "UTC hour of the step centre"
        st.units = "hours"
        ds.createVariable("lat", "f8", ("lat",))[:] = lat
        ds.createVariable("lon", "f8", ("lon",))[:] = lon
        nd = ds.createVariable("n_days", "i4", ("month", "step"))
        nd[:] = n_days
        for v, arr in means.items():
            var = ds.createVariable(v, "f4", ("month", "step", "lat", "lon"), zlib=True, complevel=4)
            var[:] = arr
            var.units = "kg/m2/s"
            var.long_name = f"monthly-mean diurnal composite of {v} (instantaneous 30-min output, UTC step)"
        ds.case = os.path.basename(case_dir)
        ds.year = year
        ds.source_files = f"{len(files)} cam.h1 files: {os.path.basename(files[0])} .. {os.path.basename(files[-1])}"
        ds.time_convention = "record stamped t assigned to step centre t - 15 min (end-of-step instantaneous output)"
        ds.created_by = "diagnostics/2_isoprene-diurnal-cycle/reduce_isoprene_diurnal.py"
        ds.created = time.strftime("%Y-%m-%d %H:%M")
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nproc", type=int, default=12)
    ap.add_argument("--periods", nargs="+", default=["PD", "FUT"])
    args = ap.parse_args()
    os.makedirs(OUTDIR, exist_ok=True)
    for (alias, year), case_dir in sorted(find_cases().items()):
        if alias.split("_")[1] not in args.periods:
            continue
        path = f"{OUTDIR}/diurnal_{alias}_{year}.nc"
        if os.path.exists(path):
            print(f"{time.strftime('%H:%M:%S')} {alias} {year}: exists, skipped", flush=True)
            continue
        t0 = time.time()
        res, msg = reduce_year(case_dir, year, args.nproc)
        if res is None:
            print(f"{time.strftime('%H:%M:%S')} {alias} {year}: {msg}, not written", flush=True)
            continue
        write(path, case_dir, year, *res)
        print(f"{time.strftime('%H:%M:%S')} {alias} {year}: written ({time.time() - t0:.0f} s)", flush=True)


if __name__ == "__main__":
    sys.exit(main())
