#!/usr/bin/env python3
"""Check 1-day tests of the all-species fBVOC cases (tests/{14c,24c,24d}-…-1day.sh).

Usage (after the test jobs have finished):
    PY=/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python
    $PY tests/check_fbvoc_all_1day.py CASE [CASE ...]

Per case:
  namelist  CaseDocs/drv_flds_in has no MEGAN compounds (megan_specifier = '');
            CaseDocs/atm_in srf_emis_specifier: 19 prescribed ems_* entries (one per species),
            no biomass-burning ISOP/MTERP file, the 17 other species keep their anthro/BB files
  atm.log   all 19 prescribed files are opened; no ERROR/endrun lines
  h0        SFISOP, SFMTERP, SFBCARY > 0 (BCARY has no file source besides the prescribed one,
            so SFBCARY > 0 shows that an added species is emitted); no MEG_* fields.
            (MEG_* in fincl1 give expected 'FLDLST ... not found' lines; reported as INFO.)
Exit status 1 if any check fails.
"""
import glob, gzip, os, re, sys
import numpy as np
from netCDF4 import Dataset

SPECIES = ["ISOP", "MTERP", "BCARY", "C3H6", "BIGENE", "CH3CHO", "CH2O", "C2H4", "CH3OH", "C2H5OH", "CH3COOH",
           "CH3COCH3", "HCOOH", "HCN", "CO", "C2H6", "C3H8", "BIGALK", "TOLUENE"]
ARCHIVE, WORK, CASES = "/cluster/work/users/adelez/archive", "/cluster/work/users/adelez/noresm", os.path.expanduser("~/cases/BRL_FRST_XPSN")
failed = False


def report(ok, msg):
    global failed
    failed |= not ok
    print(f"  {'PASS' if ok else 'FAIL'}  {msg}")


for case in sys.argv[1:]:
    print(f"\n== {case}")
    docs = f"{CASES}/{case}/CaseDocs"
    drv = open(f"{docs}/drv_flds_in").read()
    report("megan_specifier" not in drv or not re.search(r"megan_specifier\s*=\s*'[^']+", drv),
           "drv_flds_in: no MEGAN compounds")
    entries = re.findall(r"'\s*([A-Z0-9_]+)\s*->\s*([^']+)'", open(f"{docs}/atm_in").read())
    ems = {sp: p.strip() for sp, p in entries if "/ems_" in p}
    report(sorted(ems) == sorted(SPECIES), f"atm_in: {len(entries)} srf entries, prescribed ems_* for {len(ems)}/19 species"
           + (f"; missing {sorted(set(SPECIES) - set(ems))}" if sorted(ems) != sorted(SPECIES) else ""))
    bb = [sp for sp, p in entries if sp in ("ISOP", "MTERP") and "bbsurf" in p]
    report(not bb, f"atm_in: biomass-burning ISOP/MTERP files absent ({bb or 'none'})")
    others = {sp for sp, p in entries if "anthro" in p or "bbsurf" in p}
    kept = sorted(set(SPECIES[2:]) & others)
    print(f"  INFO  species with anthro/BB files kept: {kept}")
    missing_files = [p for p in ems.values() if not os.path.exists(p)]
    report(not missing_files, f"prescribed files exist ({missing_files or 'all'})")

    logs = sorted(glob.glob(f"{ARCHIVE}/{case}/logs/atm.log.*") + glob.glob(f"{WORK}/{case}/run/atm.log.*"))
    if logs:
        opener = gzip.open if logs[-1].endswith(".gz") else open
        with opener(logs[-1], "rt", errors="replace") as f:
            text = f.read()
        flat = re.sub(r"\s+", "", text)   # atm.log wraps long file names at 80 characters
        opened = [sp for sp, p in ems.items() if os.path.basename(p) in flat]
        report(len(opened) == 19, f"{os.path.basename(logs[-1])}: {len(opened)}/19 prescribed files opened")
        bad = [l.strip() for l in text.splitlines() if re.search(r"\bERROR\b|ENDRUN", l)]
        report(not bad, f"atm.log ERROR/ENDRUN lines: {bad[:3] or 'none'}")
        print(f"  INFO  'FLDLST ... not found' lines: {sum('FLDLST' in l and 'not found' in l for l in text.splitlines())} (MEG_* expected)")
    else:
        report(False, "no atm.log found")

    h0 = sorted(glob.glob(f"{ARCHIVE}/{case}/atm/hist/{case}.cam.h0.*.nc") or glob.glob(f"{WORK}/{case}/run/{case}.cam.h0.*.nc"))
    if h0:
        with Dataset(h0[0]) as d:
            meg = [v for v in d.variables if v.startswith("MEG_")]
            report(not meg, f"h0 {os.path.basename(h0[0])}: MEG_* fields {meg or 'none'}")
            for v in ("SFISOP", "SFMTERP", "SFBCARY"):
                x = d[v][:].astype("f8")
                report(np.isfinite(x).all() and x.max() > 0, f"h0 {v} max {x.max():.3e}, cells>0 {np.mean(x[0] > 0):.0%}")
    else:
        report(False, "no h0 file found")

sys.exit(1 if failed else 0)
