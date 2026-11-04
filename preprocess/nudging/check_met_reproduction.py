"""Check that the MET reproduction test (12d test mode) is bit-identical to MET.

The test branches from MET's 2010-01-01 restart and runs 10 days. Its 6-hourly h1
files (PS, U, V, T, Q) must equal, value for value, the MET files of the same dates in
the nudging folder. File metadata (case name, history attribute) is not compared.

Usage:
    $PY preprocess/nudging/check_met_reproduction.py <test case name> [--start 2010-01-01 --days 10]
Exit code 0 = all identical, 1 = a difference or a missing file.
"""
import argparse
import datetime as dt
import sys
from pathlib import Path

import numpy as np
import xarray as xr

MET = "NF2000norbc_tropstratchem_met_f19_f19_20260422"
NUDGDIR = Path(f"/cluster/shared/noresm/inputdata/noresm-only/inputForNudging/AZ/{MET}_6h_2000-2015")
WORK_ARCHIVE = Path("/cluster/work/users/adelez/archive")
VARS = ["PS", "U", "V", "T", "Q"]
COORDS = ["time", "date", "datesec"]


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("testcase")
    p.add_argument("--start", default="2010-01-01")
    p.add_argument("--days", type=int, default=10)
    p.add_argument("--hist-dir", type=Path, help="override the test's atm/hist folder (for checking this script)")
    a = p.parse_args()

    hist = a.hist_dir or WORK_ARCHIVE / a.testcase / "atm" / "hist"
    # A branch run writes no record at the branch time: its files are <date>-21600.nc with
    # 06, 12, 18 h + next day 00 h. Match every test record to the MET record of the same
    # (date, datesec) instead of matching files by name (fixed 2026-11-04).
    start = dt.date.fromisoformat(a.start)
    end = start + dt.timedelta(days=a.days)          # last record: end 00 h
    ok, n_values, n_rec = True, 0, 0
    files = sorted(hist.glob(f"{a.testcase}.cam.h1.*.nc"))
    if not files:
        print(f"MISSING: no h1 files in {hist}")
        return 1
    for f_test in files:
        with xr.open_dataset(f_test, decode_times=False, mask_and_scale=False) as t:
            for i in range(t.sizes["time"]):
                d, s = int(t["date"][i]), int(t["datesec"][i])
                day = dt.date(d // 10000, d // 100 % 100, d % 100)
                if not (start <= day <= end):
                    continue
                f_ref = NUDGDIR / f"{MET}.cam.h1.{day:%Y-%m-%d}-00000.nc"
                if not f_ref.exists():
                    print(f"MISSING {f_ref.name}"); ok = False; continue
                with xr.open_dataset(f_ref, decode_times=False, mask_and_scale=False) as r:
                    j = np.flatnonzero((r["date"].values == d) & (r["datesec"].values == s))
                    if j.size != 1:
                        print(f"NO MATCH {d} {s}"); ok = False; continue
                    bad = []
                    for v in ["time"] + VARS:
                        x, y = t[v].values[i], r[v].values[j[0]]
                        if not np.array_equal(x, y):
                            bad.append(f"{v} (max |diff| {np.abs(x.astype('f8') - y.astype('f8')).max():.3e})")
                        n_values += np.size(x)
                n_rec += 1
                print(f"{d} {s:5d}: {'identical' if not bad else 'DIFFERENT: ' + ', '.join(bad)}")
                ok &= not bad
    expected = a.days * 4   # branch: no record at start 00 h; 06 h of day 1 ... 00 h of day days+1
    if n_rec != expected:
        print(f"expected {expected} records, compared {n_rec}"); ok = False
    print(f"\n{'PASS' if ok else 'FAIL'}: {n_rec} records, {n_values:,} values compared "
          f"({', '.join(VARS)}; time; matched by date/datesec)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
