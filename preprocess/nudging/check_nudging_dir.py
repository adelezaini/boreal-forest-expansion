"""Check a CAM nudging folder: one h1 file per day, 4 six-hourly records, continuous time.

Checks (noleap calendar):
  - one <case>.cam.h1.YYYY-MM-DD-00000.nc per day from --start to --end, nothing else;
  - 4 records per file (00, 06, 12, 18 h); the --end file may have fewer;
  - `time` steps exactly 0.25 days across all files, and date/datesec match the file name;
  - the file list (if present) lists every file, in order, with absolute paths;
  - --compare-rec0 FILE: record 0 of the same-date file in the folder equals record 0 of FILE
    (used for 2015-01-01: the real file vs the old patched one, whose record 0 is original).

Usage:
    $PY preprocess/nudging/check_nudging_dir.py <folder> --start 2000-01-01 --end 2026-01-02 [--compare-rec0 FILE]
Exit code 0 = all checks pass.
"""
import argparse
import datetime as dt
import re
import sys
from pathlib import Path

import numpy as np
import netCDF4

NOLEAP_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
VARS = ["PS", "U", "V", "T", "Q"]


def noleap_days(start, end):
    d = start
    while d <= end:
        yield d
        if d.month == 2 and d.day == 28:
            d = d.replace(month=3, day=1)
        else:
            d += dt.timedelta(days=1)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("folder", type=Path)
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--compare-rec0", type=Path)
    a = p.parse_args()

    files = sorted(a.folder.glob("*.cam.h1.*-00000.nc"))
    errors = []
    by_tag = {re.search(r"\.h1\.(\d{4}-\d{2}-\d{2})-00000\.nc$", f.name).group(1): f for f in files}
    expected = [f"{d:%Y-%m-%d}" for d in noleap_days(dt.date.fromisoformat(a.start), dt.date.fromisoformat(a.end))]
    missing = sorted(set(expected) - set(by_tag))
    extra = sorted(set(by_tag) - set(expected))
    if missing:
        errors.append(f"{len(missing)} missing days, e.g. {missing[:5]}")
    if extra:
        errors.append(f"{len(extra)} unexpected files, e.g. {extra[:5]}")

    prev_time = None
    for i, tag in enumerate(t for t in expected if t in by_tag):
        with netCDF4.Dataset(by_tag[tag]) as nc:
            time = nc["time"][:].data
            date = nc["date"][:].data
            datesec = nc["datesec"][:].data
        last = tag == expected[-1]
        if len(time) != 4 and not last:
            errors.append(f"{tag}: {len(time)} records")
        ymd = int(tag.replace("-", ""))
        if not (np.all(date == ymd) and np.array_equal(datesec, [0, 21600, 43200, 64800][:len(time)])):
            errors.append(f"{tag}: date/datesec {date.tolist()} {datesec.tolist()}")
        steps = np.diff(np.concatenate([[prev_time], time]) if prev_time is not None else time)
        if not np.allclose(steps, 0.25, atol=1e-9):
            errors.append(f"{tag}: time steps {steps.tolist()}")
        prev_time = time[-1]
        if i % 1000 == 0:
            print(f"  ... {tag}", flush=True)

    flist = next(a.folder.glob("*filelist*.txt"), None)
    if flist is not None:
        listed = flist.read_text().split()
        if listed != [str(by_tag[t]) for t in expected if t in by_tag]:
            errors.append(f"{flist.name}: does not list exactly the files in date order")
    else:
        print("  (no file list found)")

    if a.compare_rec0:
        tag = re.search(r"\.h1\.(\d{4}-\d{2}-\d{2})-00000\.nc", a.compare_rec0.name).group(1)
        with netCDF4.Dataset(by_tag[tag]) as n, netCDF4.Dataset(a.compare_rec0) as o:
            for v in ["time", "date", "datesec"] + VARS:
                if not np.array_equal(n[v][0].data, o[v][0].data):
                    errors.append(f"rec0 of {tag}: {v} differs from {a.compare_rec0.name}")
        print(f"  record 0 of {tag} compared with {a.compare_rec0}")

    print(f"{len(files)} files, {len(expected)} expected days ({a.start} ... {a.end})")
    for e in errors:
        print("ERROR:", e)
    print("PASS" if not errors else f"FAIL ({len(errors)} problems)")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
