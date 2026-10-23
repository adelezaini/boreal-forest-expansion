#!/usr/bin/env python3
"""Append 06/12/18 h records to the last (single-record) nudging met file.

Why
---
The met run writes its last 6-hourly h1 file at the stop date with ONE record
(e.g. 2015-01-01 00:00). On the final step of a nudged run that stops at that
date, CAM's met reader asks for a time just after it and aborts with
``FIND_TIMES: Failed to find dates bracketing desired time``.
Jobs 1775779 / 1775781 (LCC_PD / LCC_FUT 2010-2014 extensions) crashed on
2014-12-31 this way.

What
----
1. Back up the original file to ``--backup-dir`` (refuse if a backup exists).
2. Copy it to a hidden temp file in the met folder and append records 1-3
   (06, 12, 18 h) copied from the previous day's file, with the time
   coordinates (time, time_bnds, date, datesec, ndcur, nscur, nsteph) rebuilt
   for the last day.
3. Atomically replace the original.

The added records only drive the model past its stop date, so no output
up to the stop date depends on them.
Refuses to run if the last file already has more than one record.

Usage
-----
HDF5_USE_FILE_LOCKING=FALSE python extend_last_met_file.py \
    --met-dir /cluster/shared/noresm/inputdata/noresm-only/inputForNudging/AZ/NF2000norbc_tropstratchem_met_f19_f19_20260422_6h_2000-2015 \
    --casename NF2000norbc_tropstratchem_met_f19_f19_20260422 \
    --last-date 2015-01-01 --prev-date 2014-12-31 \
    --backup-dir /cluster/home/adelez/BOREAL-FOREST-EXPANSION/data/nudging-met-backup
"""
import argparse
import os
import shutil
from datetime import datetime
from pathlib import Path

import netCDF4 as nc
import numpy as np

# Time coordinates rebuilt for the new records, not copied from the previous day
TIME_VARS = {"time", "time_bnds", "date", "datesec", "ndcur", "nscur", "nsteph"}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--met-dir", required=True, type=Path)
    p.add_argument("--casename", required=True)
    p.add_argument("--last-date", required=True, help="YYYY-MM-DD of the single-record file")
    p.add_argument("--prev-date", required=True, help="YYYY-MM-DD of the 4-record file before it")
    p.add_argument("--backup-dir", required=True, type=Path)
    a = p.parse_args()

    last = a.met_dir / f"{a.casename}.cam.h1.{a.last_date}-00000.nc"
    prev = a.met_dir / f"{a.casename}.cam.h1.{a.prev_date}-00000.nc"
    tmp = a.met_dir / f".tmp_{last.name}"
    backup = a.backup_dir / f"{last.name}.orig"

    with nc.Dataset(last) as d:
        nrec = len(d.dimensions["time"])
    if nrec != 1:
        raise SystemExit(f"{last.name} has {nrec} records, expected 1: already patched?")
    if backup.exists():
        raise SystemExit(f"Backup already exists: {backup}")

    a.backup_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(last, backup)
    shutil.copy2(last, tmp)

    with nc.Dataset(prev) as src, nc.Dataset(tmp, "a") as dst:
        nprev = len(src.dimensions["time"])
        assert nprev == 4, f"{prev.name} has {nprev} records, expected 4"
        t0 = float(dst["time"][0])
        dt = float(src["time"][1] - src["time"][0])  # 0.25 day
        nsteps_per_rec = int(src["nsteph"][1] - src["nsteph"][0])
        for k in range(1, nprev):
            for name, var in src.variables.items():
                if "time" in var.dimensions and name not in TIME_VARS:
                    dst[name][k] = var[k]
            dst["time"][k] = t0 + k * dt
            dst["time_bnds"][k] = [t0 + (k - 1) * dt, t0 + k * dt]
            dst["date"][k] = dst["date"][0]
            dst["datesec"][k] = int(round(k * dt * 86400))
            dst["ndcur"][k] = dst["ndcur"][0]
            dst["nscur"][k] = int(round(k * dt * 86400))
            dst["nsteph"][k] = int(dst["nsteph"][0]) + k * nsteps_per_rec
        dst.setncattr(
            "history_patch",
            f"{datetime.now():%Y-%m-%d %H:%M}: records 1-{nprev - 1} copied from {prev.name} "
            f"(same hours) by preprocess/nudging/extend_last_met_file.py, so nudged runs can "
            f"finish their last step. Original: {backup}",
        )

    os.replace(tmp, last)

    # Check: record 0 unchanged, records 1-3 equal the previous day's records 1-3
    with nc.Dataset(backup) as o, nc.Dataset(prev) as src, nc.Dataset(last) as new:
        for name in ("PS", "U", "V", "T", "Q"):
            assert np.array_equal(new[name][0], o[name][0]), f"{name} record 0 changed"
            assert np.array_equal(new[name][1:], src[name][1:]), f"{name} records 1-3 differ"
        print(f"Patched {last}")
        print("time   ", new["time"][:])
        print("date   ", new["date"][:], "datesec", new["datesec"][:])
        print("Backup ", backup)


if __name__ == "__main__":
    main()
