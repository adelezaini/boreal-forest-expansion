"""Regroup the MET extension's 6-hourly h1 files into calendar-day nudging files.

Why
---
The MET extension (12d) is a BRANCH run: CAM writes no record at the branch time, so
each h1 file `<MET>.cam.h1.YYYY-MM-DD-21600.nc` holds 06, 12, 18 h of day D and 00 h of
day D+1. The nudging folder (and the old MET 2000-2014 files) use calendar days:
`<MET>.cam.h1.YYYY-MM-DD-00000.nc` with 00, 06, 12, 18 h of day D.

What
----
For each day D from 2015-01-01:
    record 0 (D 00 h)       = last record of the D-1 file of the extension,
                              for D = 2015-01-01: record 0 of the OLD folder's 2015-01-01
                              file (original MET output; records 1-3 of that file are the
                              patched copies and are not used)
    records 1-3 (06-18 h)   = records 0-2 of the D file of the extension
Variables without a time dimension come from the D file. Global attributes too.
A day is built only when both sources exist. `--final` also builds the last day
(2026-01-02, record 0 only: the run stops at 2026-01-02 00 h).
Output: NetCDF4, zlib 5 + shuffle (as the old 2000-2015 folder), lossless.

Safety
------
- never overwrites: an existing output file is skipped (and re-verified with --verify-existing);
- writes `.<name>.tmp` in the output folder, verifies, then renames;
- verification: every variable of every record bit-identical to its source record,
  date/datesec = D / 0, 21600, 43200, 64800; time steps 0.25 d.

Usage
-----
python3 regroup_met_ext_days.py --src <archive>/atm/hist --old-dir <..._6h_2000-2015> \
    --out-dir <..._6h_2000-2025> [--run] [--final] [--verify-existing]
Without --run: dry run, prints which days would be built. Exit 0 = ok.
"""
import argparse
import datetime as dt
import os
import sys
from pathlib import Path

import netCDF4
import numpy as np

MET = "NF2000norbc_tropstratchem_met_f19_f19_20260422"
FIRST = dt.date(2015, 1, 1)
FINAL = dt.date(2026, 1, 2)
SECS = [0, 21600, 43200, 64800]


def noleap_next(d):
    if d.month == 2 and d.day == 28:
        return d.replace(month=3, day=1)
    return d + dt.timedelta(days=1)


def noleap_prev(d):
    if d.month == 3 and d.day == 1:
        return d.replace(month=2, day=28)
    return d - dt.timedelta(days=1)


def ymd(d):
    return int(f"{d:%Y%m%d}")


def ext_file(src, d):
    return src / f"{MET}.cam.h1.{d:%Y-%m-%d}-21600.nc"


def out_file(out, d):
    return out / f"{MET}.cam.h1.{d:%Y-%m-%d}-00000.nc"


def sources(d, src, old_dir):
    """[(file, record index), ...] for records 0..3 of day d (shorter for the final day)."""
    if d == FIRST:
        rec0 = (old_dir / f"{MET}.cam.h1.{d:%Y-%m-%d}-00000.nc", 0)
    else:
        rec0 = (ext_file(src, noleap_prev(d)), 3)
    if d == FINAL:
        return [rec0]
    cur = ext_file(src, d)
    return [rec0, (cur, 0), (cur, 1), (cur, 2)]


def open_raw(path):
    ds = netCDF4.Dataset(path)
    ds.set_auto_maskandscale(False)
    ds.set_auto_chartostring(False)
    return ds


def write_day(d, srcs, tmp):
    # template for dims, non-record variables and attributes = the file of record 1
    # (the D file of the extension), or of record 0 for the final day
    tmpl_path = srcs[1][0] if len(srcs) > 1 else srcs[0][0]
    opened = {p: open_raw(p) for p in {s[0] for s in srcs} | {tmpl_path}}
    try:
        t = opened[tmpl_path]
        o = netCDF4.Dataset(tmp, "w", format="NETCDF4")
        o.set_auto_maskandscale(False)
        o.set_auto_chartostring(False)
        o.setncatts({k: t.getncattr(k) for k in t.ncattrs()})
        for name, dim in t.dimensions.items():
            o.createDimension(name, None if dim.isunlimited() else len(dim))
        for name, v in t.variables.items():
            attrs = {k: v.getncattr(k) for k in v.ncattrs()}
            fill = attrs.pop("_FillValue", None)
            comp = dict(zlib=True, complevel=5, shuffle=True) if v.ndim > 0 else {}
            ov = o.createVariable(name, v.datatype, v.dimensions, fill_value=fill, **comp)
            ov.setncatts(attrs)
            if v.dimensions[:1] == ("time",):
                for i, (p, j) in enumerate(srcs):
                    ov[i] = opened[p][name][j]
            else:
                ov[...] = v[...]
        o.close()
    finally:
        for ds in opened.values():
            ds.close()


def verify_day(d, srcs, path):
    """List of problems (empty = ok)."""
    errs = []
    tmpl_path = srcs[1][0] if len(srcs) > 1 else srcs[0][0]
    o = open_raw(path)
    opened = {p: open_raw(p) for p in {s[0] for s in srcs} | {tmpl_path}}
    try:
        n = o.dimensions["time"].size
        if n != len(srcs):
            errs.append(f"{n} records, expected {len(srcs)}")
        if not (np.all(o["date"][:] == ymd(d)) and np.array_equal(o["datesec"][:], SECS[:n])):
            errs.append(f"date/datesec {o['date'][:].tolist()} {o['datesec'][:].tolist()}")
        if n > 1 and not np.allclose(np.diff(o["time"][:]), 0.25, atol=1e-9):
            errs.append(f"time steps {np.diff(o['time'][:]).tolist()}")
        t = opened[tmpl_path]
        if set(o.variables) != set(t.variables):
            errs.append("variable set differs from source")
        for name in t.variables:
            if name not in o.variables:
                continue
            if t[name].dimensions[:1] == ("time",):
                for i, (p, j) in enumerate(srcs):
                    if not np.array_equal(o[name][i], opened[p][name][j]):
                        errs.append(f"{name} record {i} differs from {p.name}[{j}]")
            elif not np.array_equal(o[name][...], t[name][...]):
                errs.append(f"{name} differs from {tmpl_path.name}")
            # non-record variables must also agree between all sources (same grid)
            if t[name].dimensions[:1] != ("time",):
                for p in opened:
                    if name in opened[p].variables and not np.array_equal(opened[p][name][...], t[name][...]):
                        errs.append(f"{name} differs between {p.name} and {tmpl_path.name}")
    finally:
        o.close()
        for ds in opened.values():
            ds.close()
    return errs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", type=Path, required=True, help="extension h1 files (work archive atm/hist)")
    ap.add_argument("--old-dir", type=Path, required=True, help="old _6h_2000-2015 folder (for 2015-01-01 rec 0)")
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--final", action="store_true", help="also build 2026-01-02 (record 0 only)")
    ap.add_argument("--verify-existing", action="store_true")
    a = ap.parse_args()

    days, d = [], FIRST
    while d <= FINAL:
        days.append(d)
        d = noleap_next(d)

    built = skipped = 0
    last_ok = None
    for d in days:
        if d == FINAL and not a.final:
            break
        srcs = sources(d, a.src, a.old_dir)
        out = out_file(a.out_dir, d)
        if out.exists():
            if a.verify_existing:
                errs = verify_day(d, srcs, out)
                if errs:
                    print(f"ERROR existing {out.name}: {'; '.join(errs)}")
                    return 1
            skipped += 1
            last_ok = d
            continue
        if not all(p.exists() for p, _ in srcs):
            print(f"stop at {d}: source missing ({', '.join(sorted({p.name for p, _ in srcs if not p.exists()}))})")
            break
        if not a.run:
            built += 1
            last_ok = d
            continue
        tmp = a.out_dir / f".{out.name}.tmp"
        if tmp.exists():
            tmp.unlink()   # own leftover from an interrupted run (hidden name, never a real file)
        write_day(d, srcs, tmp)
        errs = verify_day(d, srcs, tmp)
        if errs:
            print(f"ERROR {out.name}: {'; '.join(errs)} (left as {tmp})")
            return 1
        os.rename(tmp, out)   # out did not exist (checked above)
        built += 1
        last_ok = d
        if built % 200 == 0:
            print(f"  ... {d}", flush=True)
    verb = "built" if a.run else "would build"
    print(f"{verb} {built} days, {skipped} already there; last complete day: {last_ok}")
    if last_ok is not None:
        print(f"LAST_DAY={last_ok:%Y-%m-%d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
