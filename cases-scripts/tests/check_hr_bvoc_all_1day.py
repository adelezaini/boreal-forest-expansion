#!/usr/bin/env python3
"""Check the 1-day HR_BVOC_ALL test cases (tests/*-hrbvocall-1day.sh) before trusting the CTRL reruns.

Usage (after the test jobs have finished):
    PY=/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python
    $PY tests/check_hr_bvoc_all_1day.py \
        NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-test-hrbvocall-20261023 \
        NF2100ssp585norbc_tropstratchem_nudg_ctrl_f19_f19-test-hrbvocall-20261023

Per case it checks (files from the archive, else the run directory):
  h0  all 19 MEG_* fields (16 added by HR_BVOC_ALL + MEG_ISOP/MTERP/BCARY), SFISOP, SFMTERP
  h1  SFISOP, SFMTERP + MEG_{BCARY,C3H6,BIGENE,CH3CHO,CH2O,C2H4}; 48 records (30 min);
      units kg/m2/s(ec); finite, >= 0, nonzero somewhere
  atm.log  no "FLDLST: ... not found" lines (CAM drops unknown fincl fields silently)
  size  h1 bytes for one day, projected to 15 model years
Exit status 1 if any check fails. Production runs: CTRL_FUT job 1775814 (queued with the tests);
cancel it (scancel) only with the user's OK if a check fails.
"""
import glob, gzip, os, sys
import numpy as np
from netCDF4 import Dataset

MEG_ALL = ["ISOP", "MTERP", "BCARY", "CH3OH", "C2H5OH", "CH2O", "CH3CHO", "CH3COOH", "CH3COCH3",
           "HCOOH", "HCN", "CO", "C2H6", "C2H4", "C3H8", "C3H6", "BIGALK", "BIGENE", "TOLUENE"]
H0_FIELDS = ["MEG_" + s for s in MEG_ALL] + ["SFISOP", "SFMTERP"]
H1_FIELDS = ["SFISOP", "SFMTERP"] + ["MEG_" + s for s in ["BCARY", "C3H6", "BIGENE", "CH3CHO", "CH2O", "C2H4"]]
ARCHIVE, WORK = "/cluster/work/users/adelez/archive", "/cluster/work/users/adelez/noresm"
failed = False


def report(ok, msg):
    global failed
    failed |= not ok
    print(f"  {'PASS' if ok else 'FAIL'}  {msg}")


def find(case, pattern):
    """Return files from the archive, or from the run directory if not archived yet."""
    for d in (f"{ARCHIVE}/{case}/atm/hist", f"{WORK}/{case}/run"):
        files = sorted(glob.glob(f"{d}/{case}.cam.{pattern}.*.nc"))
        if files:
            return files
    return []


def atm_logs(case):
    return sorted(glob.glob(f"{ARCHIVE}/{case}/logs/atm.log.*") + glob.glob(f"{WORK}/{case}/run/atm.log.*"))


for case in sys.argv[1:]:
    print(f"\n== {case}")
    h0, h1 = find(case, "h0"), find(case, "h1")
    report(bool(h0) and bool(h1), f"history files found: h0 {len(h0)}, h1 {len(h1)}"
           + ("" if h0 and h1 else "  (job finished? check squeue / CaseStatus)"))
    if h0:
        with Dataset(h0[0]) as ds:
            missing = [v for v in H0_FIELDS if v not in ds.variables]
            n_meg = sum(v.startswith("MEG_") for v in ds.variables)
        report(not missing, f"h0 {os.path.basename(h0[0])}: {n_meg} MEG_* fields; missing {missing or 'none'}")
    if h1:
        with Dataset(h1[0]) as ds:
            nt = len(ds.dimensions["time"])
            report(nt == 48, f"h1 {os.path.basename(h1[0])}: {nt} records (expect 48)")
            for v in H1_FIELDS:
                if v not in ds.variables:
                    report(False, f"h1 {v} missing")
                    continue
                x = np.ma.filled(ds.variables[v][:].astype("f8"), np.nan)
                units = getattr(ds.variables[v], "units", "")
                ok = (np.isfinite(x).all() and (x >= 0).all() and x.max() > 0
                      and units.replace("sec", "s") == "kg/m2/s")
                report(ok, f"h1 {v:12s} units {units!r}, max {np.nanmax(x):.3e}, "
                           f"cells>0 {np.mean(x.max(axis=0) > 0):.0%}, cell_methods {getattr(ds.variables[v], 'cell_methods', '')!r}")
        gb_day = os.path.getsize(h1[0]) / 1e9   # one h1 file = 48 records = 1 day (mfilt 48)
        print(f"  INFO  h1 size {gb_day:.3f} GB/day -> {gb_day*365:.1f} GB/yr -> {gb_day*365*15:.0f} GB for 15 yr")
    logs = atm_logs(case)
    if logs:
        opener = gzip.open if logs[-1].endswith(".gz") else open
        with opener(logs[-1], "rt", errors="replace") as f:
            bad = [l.strip() for l in f if "FLDLST" in l and "not found" in l]
        report(not bad, f"{os.path.basename(logs[-1])}: 'FLDLST ... not found' lines: {bad or 'none'}")
    else:
        report(False, "no atm.log found")

sys.exit(1 if failed else 0)
