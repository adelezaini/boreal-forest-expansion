#!/usr/bin/env python3
"""Independent check of a reduced MEGAN-LMDI file against the raw tape-2 files it was made from (user 2026-11-15:
"check with raw files" before the raw files are deleted). Does NOT use reduce_megan_lmdi.py: it recomputes from
the raw daily files, for the months asked,
  1. nsteps per month;
  2. grid-cell monthly mean emission E = mean_t sum_p w_p MEG_p (vegetated patches >= lat_min) vs E_ctrl / E_lcc;
  3. per patch pair, the monthly integral sum_t w MEG * dt vs Ep_ctrl / Ep_lcc (pair_ixy, pair_jxy, pair_pft);
  4. patch weights pfts1d_wtgcell constant over all days read (the reduction reads them from the first day);
  5. internal closures of the reduced file: sum of contributions = E_lcc - E_ctrl; sum of swap4/swap3 terms
     = Ep_lcc - Ep_ctrl; grid-cell sum of Ep / (month length) = E (consistency of the two parts).
Prints PASS/FAIL per check; exit 1 on any FAIL.

    $PY postprocess/megan_lmdi/check_reduced_vs_raw.py --ctrl <CTRL branch> --lcc <LCC branch> \
        --reduced data/processed-data/megan-lmdi/megan_lmdi_PD_2005.nc --year 2005 --months 1 7
"""
import argparse, glob, sys
import numpy as np
from netCDF4 import Dataset

ARCHIVE = "/cluster/work/users/adelez/archive"
TOL = 1e-10


def rel(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.max(np.abs(a - b)) / max(np.max(np.abs(b)), 1e-300))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ctrl", required=True); ap.add_argument("--lcc", required=True)
    ap.add_argument("--reduced", required=True); ap.add_argument("--year", type=int, required=True)
    ap.add_argument("--months", type=int, nargs="+", default=[1, 7])
    a = ap.parse_args()

    R = Dataset(a.reduced)
    comps = [s.strip() for s in R.getncattr("compounds").split(",")]
    lat_min = float(R.lat_min)
    months_red = [int(m) for m in R["month"][:]]
    pix, pjx, ppft = R["pair_ixy"][:], R["pair_jxy"][:], R["pair_pft"][:]
    ny, nx = R["lat"].size, R["lon"].size
    fails = []

    def report(name, value, tol=TOL):
        ok = value < tol
        print(f"{'PASS' if ok else 'FAIL'}  {name}: {value:.2e}")
        if not ok:
            fails.append(name)

    # 5. internal closures (all months)
    E0, E1, C = R["E_ctrl"][:], R["E_lcc"][:], R["contribution"][:]
    report("reduced: sum(contribution) = E_lcc - E_ctrl", rel(C.sum(axis=1), E1 - E0))
    Ep0, Ep1 = R["Ep_ctrl"][:], R["Ep_lcc"][:]
    for v in ("swap4", "swap3"):
        S = R[v][:]
        report(f"reduced: sum({v}) = Ep_lcc - Ep_ctrl", rel(S.sum(axis=1), Ep1 - Ep0))

    for m in a.months:
        im = months_red.index(int(f"{a.year}{m:02d}")) if int(f"{a.year}{m:02d}") in months_red else months_red.index(m)
        acc = {}
        for r, case in enumerate((a.ctrl, a.lcc)):
            files = sorted(glob.glob(f"{ARCHIVE}/{case}/lnd/hist/{case}.clm2.h1.{a.year:04d}-{m:02d}-*.nc"))
            if not files:
                raise SystemExit(f"no raw files for {case} {a.year}-{m:02d}")
            E = np.zeros((len(comps), ny, nx)); Ep = np.zeros((len(comps), len(pix))); n = 0; w_ref = None; wdiff = 0.0
            for f in files:
                with Dataset(f) as d:
                    if int(str(int(d["mcdate"][0]))[4:6]) != m:      # first file of a month may start at 00:30 of day 1
                        pass
                    itype, lat = d["pfts1d_itype_veg"][:], d["pfts1d_lat"][:]
                    sel = np.where((itype > 0) & (lat >= lat_min))[0]
                    w = np.asarray(d["pfts1d_wtgcell"][:])[sel]
                    if w_ref is None:
                        w_ref = w
                        ix, jy, pf = d["pfts1d_ixy"][:][sel], d["pfts1d_jxy"][:][sel], itype[sel]
                        key = {(int(i), int(j), int(p)): k for k, (i, j, p) in enumerate(zip(ix, jy, pf))}
                        pair_of = np.array([key.get((int(i), int(j), int(p)), -1) for i, j, p in zip(pix, pjx, ppft)])
                        cell = (jy - 1) * nx + (ix - 1)
                    else:
                        wdiff = max(wdiff, float(np.max(np.abs(w - w_ref))))
                    dt = float(np.round((d["time"][1] - d["time"][0]) * 86400)) if d["time"].size > 1 else 1800.0
                    months_steps = np.array([int(str(int(x))[4:6]) for x in d["mcdate"][:]])
                    for ic, c in enumerate(comps):
                        meg = np.asarray(d[f"MEG_{c}"][:][:, sel], float)
                        meg = np.where(np.isfinite(meg), meg, 0.0)
                        e = meg * w[None, :]                          # (time, patch)
                        E[ic] += np.bincount(cell, weights=e.sum(axis=0), minlength=ny * nx).reshape(ny, nx)
                        ok = pair_of >= 0
                        Ep[ic, ok] += e[:, pair_of[ok]].sum(axis=0) * dt
                    n += d["time"].size
            acc[r] = (E / n, Ep, n, wdiff)
            print(f"{case} {a.year}-{m:02d}: {len(files)} files, {n} steps, max |dw| over days {wdiff:.1e}")
        report(f"{m:02d}: nsteps", abs(acc[0][2] - int(R["nsteps"][im])) + abs(acc[1][2] - int(R["nsteps"][im])), 0.5)
        report(f"{m:02d}: weights constant over days", max(acc[0][3], acc[1][3]))
        report(f"{m:02d}: E_ctrl raw vs reduced", rel(acc[0][0], E0[:, im]))
        report(f"{m:02d}: E_lcc raw vs reduced", rel(acc[1][0], E1[:, im]))
        report(f"{m:02d}: Ep_ctrl raw vs reduced (pairs present in CTRL)", rel(acc[0][1], Ep0[:, im]))
        report(f"{m:02d}: Ep_lcc raw vs reduced (pairs present in LCC)", rel(acc[1][1], Ep1[:, im]))
        # consistency of the two parts: grid-cell sum of Ep / (n * dt) = E
        cellp = (pjx - 1) * nx + (pix - 1)
        for r, (Ered, Epred) in enumerate(((E0, Ep0), (E1, Ep1))):
            Eg = np.stack([np.bincount(cellp, weights=Epred[ic, im], minlength=ny * nx).reshape(ny, nx)
                           for ic in range(len(comps))]) / (acc[r][2] * 1800.0)
            report(f"{m:02d}: {'CTRL' if r == 0 else 'LCC'} sum_pairs(Ep)/(n dt) = E (reduced)", rel(Eg, Ered[:, im]))
    print("ALL PASS" if not fails else f"FAILED: {fails}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
