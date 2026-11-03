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
    start = dt.date.fromisoformat(a.start)
    # 10 full days + record 0 of the day after (written at the stop time)
    dates = [start + dt.timedelta(days=i) for i in range(a.days + 1)]
    ok = True
    n_values = 0
    for d in dates:
        tag = f"{d:%Y-%m-%d}-00000"
        f_test = hist / f"{a.testcase}.cam.h1.{tag}.nc"
        f_ref = NUDGDIR / f"{MET}.cam.h1.{tag}.nc"
        if not f_test.exists() or not f_ref.exists():
            print(f"MISSING {tag}: test={f_test.exists()} ref={f_ref.exists()}")
            ok = False
            continue
        with xr.open_dataset(f_test, decode_times=False, mask_and_scale=False) as t, \
             xr.open_dataset(f_ref, decode_times=False, mask_and_scale=False) as r:
            nrec = t.sizes["time"]
            if d == dates[-1]:
                r = r.isel(time=slice(0, nrec))   # last day: test has only record 0
            elif nrec != r.sizes["time"]:
                print(f"DIFF {tag}: {nrec} records in test, {r.sizes['time']} in MET")
                ok = False
                continue
            bad = []
            for v in COORDS + VARS:
                same = np.array_equal(t[v].values, r[v].values)
                if not same:
                    diff = np.abs(t[v].values.astype("f8") - r[v].values.astype("f8")).max()
                    bad.append(f"{v} (max |diff| {diff:.3e})")
                n_values += t[v].size
            status = "identical" if not bad else "DIFFERENT: " + ", ".join(bad)
            print(f"{tag}: {nrec} rec, {status}")
            ok &= not bad
    print(f"\n{'PASS' if ok else 'FAIL'}: {len(dates)} files, {n_values:,} values compared "
          f"({', '.join(VARS)}; time/date/datesec)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
