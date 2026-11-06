#!/usr/bin/env python3
"""Bit-identity check of a MEGAN patch-output branch run against its parent (analysis/MEGAN_ATTRIBUTION.md, step 3).

A branch only adds history output, so everything it shares with the parent must be bit-identical:
  1. CAM h1, 30-min instantaneous SFISOP/SFMTERP, every common step, matched by time value (only where the
     parent wrote them: CTRL_PD, LCC_PD, CTRL_FUT; LCC_FUT has no 30-min output -> SKIP);
  2. CAM h0, monthly mean SFISOP/SFMTERP, every complete month of the branch;
  3. CLM h0, monthly mean MEG_*/GAMMA*/EPS_* fields present in both, every complete month of the branch.
Branch files are read from the archive (/cluster/work/users/adelez/archive/<case>), the parent's from its archive.

Usage:
    python check_identity.py --branch <branch case> --parent <parent case> [--year 2005]
Exit 1 if any value differs, or if a category the parent has data for compared nothing.
"""
import argparse, glob, os, sys
import numpy as np
from netCDF4 import Dataset

ARCHIVE = "/cluster/work/users/adelez/archive"
CAM_VARS = ["SFISOP", "SFMTERP"]
CLM_PREFIXES = ("MEG_", "GAMMA", "EPS_")


def files(case, comp, tape, year):
    """{date stamp: path} of the archived history files of one tape (year=None: all)."""
    sub = "atm" if comp == "cam" else "lnd"
    y = f"{year:04d}-" if year else ""
    out = {}
    for f in sorted(glob.glob(f"{ARCHIVE}/{case}/{sub}/hist/{case}.{comp}.{tape}.{y}*.nc")):
        out[f.split(f".{comp}.{tape}.")[1][:-3]] = f
    return out


def compare(fb, fp, names):
    """Per variable: (n values compared, n differing). Raw values, no masking (fill values compare too)."""
    res = {}
    with Dataset(fb) as b, Dataset(fp) as p:
        b.set_auto_mask(False); p.set_auto_mask(False)
        tb, tp = b["time"][:], p["time"][:]
        for v in names:
            if v not in b.variables or v not in p.variables:
                continue
            xb, xp = b[v][:], p[v][:]
            if not np.array_equal(tb, tp):
                res[v] = (xb.size, xb.size)
                continue
            if xb.shape != xp.shape:
                res[v] = (xb.size, xb.size)
                continue
            if xb.dtype != xp.dtype:
                res[v] = (xb.size, xb.size)
                continue
            u = np.dtype(f"u{xb.dtype.itemsize}")          # compare the bits (NaN == NaN, -0 != +0)
            res[v] = (xb.size, int(np.count_nonzero(np.ascontiguousarray(xb).view(u) != np.ascontiguousarray(xp).view(u))))
    return res


def compare_h1(fb, fp):
    """30-min tape: file stamps differ (a branch's daily files start at 00:30, a continued run's at 00:00),
    so match the steps by time value. Returns (n files, n values, n differing, {var: [first bad time]})."""
    where = {}                                         # parent time -> (file, index)
    for f in fp.values():
        with Dataset(f) as p:
            if not all(v in p.variables for v in CAM_VARS):
                return None
            for i, t in enumerate(p["time"][:]):
                where[float(t)] = (f, i)
    n_val = n_diff = n_files = 0
    bad = {}
    for f in fb.values():
        with Dataset(f) as b:
            b.set_auto_mask(False)
            tb = b["time"][:]
            hits = [(i, where[float(t)]) for i, t in enumerate(tb) if float(t) in where]
            if not hits:
                continue
            n_files += 1
            for pf in sorted({h[1][0] for h in hits}):
                ib = [i for i, (g, _) in hits if g == pf]
                ip = [j for _, (g, j) in hits if g == pf]
                with Dataset(pf) as p:
                    p.set_auto_mask(False)
                    for v in CAM_VARS:
                        xb, xp = b[v][ib], p[v][ip]
                        u = np.dtype(f"u{xb.dtype.itemsize}")
                        nd = int(np.count_nonzero(np.ascontiguousarray(xb).view(u) != np.ascontiguousarray(xp).view(u))) \
                            if xb.dtype == xp.dtype else xb.size
                        n_val += xb.size; n_diff += nd
                        if nd:
                            bad.setdefault(v, float(tb[ib[0]]))
    return n_files, n_val, n_diff, bad


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--branch", required=True)
    ap.add_argument("--parent", required=True)
    ap.add_argument("--year", type=int)
    a = ap.parse_args()

    ok = True
    # 1. 30-min CAM: the parent's files of the same year (+ the next year's first file for the last step)
    fb = files(a.branch, "cam", "h1", a.year)
    fp = files(a.parent, "cam", "h1", a.year)
    if a.year:
        fp.update(dict(list(files(a.parent, "cam", "h1", a.year + 1).items())[:1]))
    r = compare_h1(fb, fp) if fb and fp else None
    if r is None or r[0] == 0:
        # only CTRL_PD, LCC_PD, CTRL_FUT wrote 30-min SFISOP/SFMTERP (LCC_FUT has none): skip, not fail
        print(f"SKIP  CAM h1 30-min: no common steps with SFISOP/SFMTERP (branch {len(fb)} files, parent {len(fp)})")
    else:
        n_files, n_val, n_diff, bad = r
        ok &= n_diff == 0
        print(f"{'PASS' if n_diff == 0 else 'FAIL'}  CAM h1 30-min: {n_files} branch files, "
              f"{n_val:,} values compared, {n_diff:,} differ")
        for v, t in bad.items():
            print(f"      {v} differs, first at time {t}")
    # 2.-3. monthly means: same file stamps (YYYY-MM)
    for label, comp, tape, pick in (("CAM h0 monthly", "cam", "h0", lambda vs: CAM_VARS),
                                    ("CLM h0 monthly", "clm2", "h0", lambda vs: [v for v in vs if v.startswith(CLM_PREFIXES)])):
        fb, fp = files(a.branch, comp, tape, a.year), files(a.parent, comp, tape, a.year)
        common = sorted(set(fb) & set(fp))
        if not common:                                 # the branch must have at least one complete month
            print(f"FAIL  {label}: no common files (branch {len(fb)}, parent {len(fp)})")
            ok = False
            continue
        n_val = n_diff = 0
        bad = {}
        for d in common:
            with Dataset(fb[d]) as b:
                names = pick(list(b.variables))
            for v, (n, nd) in compare(fb[d], fp[d], names).items():
                n_val += n; n_diff += nd
                if nd:
                    bad.setdefault(v, []).append(d)
        status = "PASS" if n_diff == 0 and n_val > 0 else "FAIL"
        ok &= status == "PASS"
        print(f"{status}  {label}: {len(common)} files ({common[0]} ... {common[-1]}), "
              f"{n_val:,} values compared, {n_diff:,} differ")
        for v, ds in bad.items():
            print(f"      {v} differs in {len(ds)} files, first {ds[0]}")
    print(f"identity {a.branch} vs {a.parent}{f' ({a.year})' if a.year else ''}: {'PASS' if ok else 'FAIL'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
