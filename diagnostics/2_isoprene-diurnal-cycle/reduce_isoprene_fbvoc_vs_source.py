"""Each production fBVOC run against its own interactive source run (isoprene, SFISOP).

The production fBVOC runs write SFISOP only on the monthly h0 tape. Their sub-daily flux is the
prescribed file (bypass_isoprene_diurnal_adjustment active, checked to 0.05 % on CTRL_PD_fBVOCctrlPD_HR),
and that file is the 2001-2014 mean, per day-of-year and 30-min step, of the source run's h1 tape.

Part D, source runs, 30-min h1 tape, every year 2001-2014 (the years the input file averages):
    -> fbvoc/diurnal_src_<SRC>_<YEAR>.nc   monthly diurnal composite (same layout as diurnal_<ALIAS>_<YEAR>.nc)
    -> timeseries/ts_src_<SRC>_<YEAR>.nc   regional totals every 30 min (Mg h-1, UTC step centre)
    Each file is read once for both outputs. LCC_FUT -20261028 has no h1: its 2001-2014 h1 comes from the
    output-only rerun LCC_FUT_HRBVOC (s1 2000-04, s2 2005-09, s3 2010-14), which the input file was built from.
Part E, monthly h0 SFISOP, regional totals (Mg h-1, monthly-mean rate), 2001-2025:
    the 8 production fBVOC runs, their 4 sources and LCC_FUT_HRBVOC (2001-2014)
    -> timeseries/monthly_h0_SFISOP_fbvoc_vs_source.csv (alias, role, source, case, region, year, month, Mg_per_h)

Time convention, regions and weights as reduce_isoprene_fbvoc_and_timeseries.py.
Raw files on /cluster/work are purged ~Dec 2026; outputs live on NIRD (data/processed-data).

Usage: $PY diagnostics/2_isoprene-diurnal-cycle/reduce_isoprene_fbvoc_vs_source.py [--nproc 12] [--parts D E]
Skips existing outputs (part E: rewrites the CSV).
"""
import argparse
import csv
import glob
import os
import re
import sys
import time
from multiprocessing import Pool

import netCDF4
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reduce_isoprene_diurnal as R  # noqa: E402
import reduce_isoprene_fbvoc_and_timeseries as F  # noqa: E402

R.VARS = ("SFISOP",)          # read only isoprene (set before the pools fork)
ARCH = R.ARCHIVE
STEPS, NREC = F.STEPS, F.NREC
YEARS_SRC = range(2001, 2015)
YEARS_H0 = range(2001, 2026)

SOURCES = {   # alias -> h0 case (the run the input file names)
    "CTRL_PD": "NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20261029",
    "LCC_PD": "NF2000norbc_tropstratchem_nudg_lcc_f19_f19-20261028",
    "CTRL_FUT": "NF2100ssp585norbc_tropstratchem_nudg_ctrl_f19_f19-20261028",
    "LCC_FUT": "NF2100ssp585norbc_tropstratchem_nudg_lcc_f19_f19-20261028",
}
HRBVOC = "NF2100ssp585norbc_tropstratchem_nudg_lcc_HRBVOC_f19_f19-20261104-s{}"
FBVOC = {     # production fBVOC run -> (case, source alias)
    "CTRL_PD_fBVOCctrlPD": ("NF2000norbc_tropstratchem_nudg_ctrl_fBVOCctrlPD_f19_f19-20261031", "CTRL_PD"),
    "LCC_PD_fBVOCctrlPD": ("NF2000norbc_tropstratchem_nudg_lcc_fBVOCctrlPD_f19_f19-20261031", "CTRL_PD"),
    "LCC_PD_fBVOClccPD": ("NF2000norbc_tropstratchem_nudg_lcc_fBVOClccPD_f19_f19-20261031", "LCC_PD"),
    "LCC_FUT_fBVOCctrlPD": ("NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOCctrlPD_f19_f19-20261031", "CTRL_PD"),
    "LCC_FUT_fBVOClccPD": ("NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOClccPD_f19_f19-20261031", "LCC_PD"),
    "CTRL_FUT_fBVOCctrlFUT": ("NF2100ssp585norbc_tropstratchem_nudg_ctrl_fBVOCctrlFUT_f19_f19-20261031", "CTRL_FUT"),
    "LCC_FUT_fBVOCctrlFUT": ("NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOCctrlFUT_f19_f19-20261031", "CTRL_FUT"),
    "LCC_FUT_fBVOClccFUT": ("NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOClccFUT_f19_f19-20261106", "LCC_FUT"),
}


def h1_case(src, year):
    if src == "LCC_FUT":
        return HRBVOC.format(1 if year < 2005 else 2 if year < 2010 else 3)
    return SOURCES[src]


def h1_files(case_dir, year):
    files = sorted(glob.glob(f"{case_dir}/atm/hist/*.cam.h1.{year}-*.nc"))
    files += sorted(glob.glob(f"{case_dir}/atm/hist/*.cam.h1.{year + 1}-01-01-*.nc"))[:1]
    return [f for f in files if re.search(r"\.cam\.h1\.\d{4}-\d{2}-\d{2}-\d{5}\.nc$", f)]


def reduce_src_year(case_dir, year, nproc, w):
    """One pass over the h1 files of `year`: monthly diurnal composite + 30-min regional totals."""
    files = h1_files(case_dir, year)
    if not files:
        return None, "no cam.h1 files"
    with netCDF4.Dataset(files[0]) as ds:
        lat, lon = ds.variables["lat"][:].data, ds.variables["lon"][:].data
    sums = np.zeros((12, STEPS, lat.size, lon.size), "f8")
    tot = np.full((len(F.REGIONS), NREC), np.nan)
    seen = np.zeros((365, STEPS), bool)
    with Pool(nproc) as pool:
        for yr, doy, step, data in pool.imap(R.read_file, files, chunksize=4):
            x = data["SFISOP"]
            for i in np.flatnonzero(yr == year):
                if seen[doy[i], step[i]]:
                    raise RuntimeError(f"duplicate record {year} doy {doy[i]} step {step[i]}")
                seen[doy[i], step[i]] = True
                m = np.searchsorted(R.CUM_DAYS, doy[i], side="right") - 1
                sums[m, step[i]] += x[i]
                tot[:, doy[i] * STEPS + step[i]] = np.tensordot(x[i].astype("f8"), w, axes=([0, 1], [1, 2]))
    if not seen.all():
        return None, f"incomplete: {(~seen).sum()} of {seen.size} (day, step) records missing"
    means = (sums / R.DAYS_PER_MONTH[:, None, None, None]).astype("f4")
    return (lat, lon, means, tot * F.KG_S_TO_MG_H, files), "ok"


def readable(path):
    try:
        with netCDF4.Dataset(path) as ds:
            for v in ds.variables:
                ds.variables[v][:]
        return True
    except Exception:
        return False


def written_ok(write, path, tries=3):
    """Write, then read everything back (NIRD, 16 Nov 2026: ~5 % of reads failed with 'NetCDF: HDF error' on
    intact files, same md5; 0 % from a /cluster/work copy). A failed read-back rewrites the file."""
    for _ in range(tries):
        write()
        if readable(path):
            return
        print(f"  ! {os.path.basename(path)} unreadable after writing, retrying", flush=True)
        os.remove(path)
    raise RuntimeError(f"{path}: unreadable after {tries} writes")


def part_d(nproc):
    w = None
    for src in SOURCES:
        for y in YEARS_SRC:
            pc, pt = f"{F.OUT_FB}/diurnal_src_{src}_{y}.nc", f"{F.OUT_TS}/ts_src_{src}_{y}.nc"
            if os.path.exists(pc) and os.path.exists(pt):
                print(f"D {src} {y}: exists, skipped", flush=True)
                continue
            d = f"{ARCH}/{h1_case(src, y)}"
            if w is None:
                with netCDF4.Dataset(h1_files(d, y)[0]) as ds:
                    w = F.weights(ds.variables["lat"][:].data, ds.variables["lon"][:].data)
            t0 = time.time()
            res, msg = reduce_src_year(d, y, nproc, w)
            if res is None:
                print(f"D {src} {y}: {msg}, not written", flush=True)
                continue
            lat, lon, means, tot, files = res
            attrs = dict(case=os.path.basename(d), source_alias=src, year=y,
                         source_files=f"{len(files)} cam.h1 files: {os.path.basename(files[0])} .. "
                                      f"{os.path.basename(files[-1])}",
                         time_convention="record stamped t assigned to step centre t - 15 min")
            written_ok(lambda: F.write_composite(pc, lat, lon, {"SFISOP": means}, attrs), pc)
            written_ok(lambda: F.write_ts(pt, tot, y, attrs), pt)
            print(f"D {src} {y}: written ({time.time() - t0:.0f} s)", flush=True)


def _h0(args):
    path, w = args
    with netCDF4.Dataset(path) as ds:
        x = np.asarray(ds.variables["SFISOP"][0], dtype="f8")
    return np.tensordot(x, w, axes=([0, 1], [1, 2])) * F.KG_S_TO_MG_H


def part_e(nproc):
    runs = [(a, "fBVOC", s, c) for a, (c, s) in FBVOC.items()]
    runs += [(s, "source", s, c) for s, c in SOURCES.items()]
    runs += [(f"LCC_FUT_HRBVOC_s{k}", "source h1 rerun", "LCC_FUT", HRBVOC.format(k)) for k in (1, 2, 3)]
    w, rows = None, []
    for alias, role, src, case in runs:
        jobs = []
        for y in YEARS_H0:
            for m in range(1, 13):
                f = f"{ARCH}/{case}/atm/hist/{case}.cam.h0.{y}-{m:02d}.nc"
                if os.path.exists(f):
                    jobs.append((y, m, f))
        if not jobs:
            print(f"E {alias}: no h0 files", flush=True)
            continue
        if w is None:
            with netCDF4.Dataset(jobs[0][2]) as ds:
                w = F.weights(ds.variables["lat"][:].data, ds.variables["lon"][:].data)
        with Pool(nproc) as pool:
            tots = pool.map(_h0, [(f, w) for _, _, f in jobs])
        for (y, m, _), t in zip(jobs, tots):
            for r, v in zip(F.REGIONS, t):
                rows.append((alias, role, src, case, r, y, m, f"{v:.6g}"))
        print(f"E {alias}: {len(jobs)} months ({jobs[0][0]}-{jobs[-1][0]})", flush=True)
    out = f"{F.OUT_TS}/monthly_h0_SFISOP_fbvoc_vs_source.csv"
    with open(out + ".part", "w", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(("alias", "role", "source", "case", "region", "year", "month", "Mg_per_h"))
        wr.writerows(rows)
    os.replace(out + ".part", out)
    print(f"E written {out} ({len(rows)} rows)", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nproc", type=int, default=12)
    ap.add_argument("--parts", nargs="+", default=["D", "E"])
    args = ap.parse_args()
    os.makedirs(F.OUT_FB, exist_ok=True)
    os.makedirs(F.OUT_TS, exist_ok=True)
    if "E" in args.parts:
        part_e(args.nproc)
    if "D" in args.parts:
        part_d(args.nproc)


if __name__ == "__main__":
    sys.exit(main())
