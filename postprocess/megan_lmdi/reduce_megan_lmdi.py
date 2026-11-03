#!/usr/bin/env python3
"""Exact (LMDI) split of the MEGAN emission change LCC - CTRL, from patch-level branch output.

Option 1 of analysis/MEGAN_ATTRIBUTION.md. Reads the CLM tape-2 files (clm2.h1.*: MEGAN fields per patch,
every 30-min step, instantaneous) of a CTRL and an LCC branch run covering the same days, and writes one
small netCDF with, per compound, month and grid cell, the mean emission of both runs and the exact
contribution of each factor to the difference. Nothing is deleted unless --delete-raw is given AND all
checks pass.

Usage:
    PY=/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python
    $PY postprocess/megan_lmdi/reduce_megan_lmdi.py --ctrl <CTRL branch case> --lcc <LCC branch case> \
        --label PD_2005 [--lat-min 45] [--out data/processed-data/megan-lmdi] [--delete-raw]

Method (per compound c, matched patch p = same grid cell + same PFT, time step t):
    E = w * MEG,  MEG = k * EPS * GAMMAL * GAMMAT * GAMMAP * GAMMAA (* GAMMAC for isoprene)
    w = patch weight in the grid cell (pfts1d_wtgcell), k = unit constant (cancels).
    Both E > 0:  LMDI-I, dE = L(E1, E0) * sum_f dln f,  L(a, b) = (a - b) / (ln a - ln b)
                 factors f: composition (w * EPS; EPS is the same for the same PFT), gammaL, gammaT, gammaP,
                 gammaA, gammaC. Exact: the terms add up to dE.
    One E = 0:   dE goes to the factor(s) that are zero in that run (limit of the small-value strategy,
                 Ang & Liu 2007): patch absent or w = 0 -> composition; GAMMAL = 0 -> gammaL; etc.
                 Several zero factors share dE equally.
                 'cutoff': CLM's safeguard in VOCEmission: if the total gamma is outside [0, 100), MEG is set to 0
                 and GAMMAT/P/A are not saved (missing), while GAMMAL/GAMMAC are. Such steps (E = 0, weight > 0,
                 a gamma missing) go to 'cutoff'. Anything else -> 'unexplained' (must be 0).
    Both E = 0:  nothing.
Grid cell = sum over its matched patches; month = mean over its time steps. All terms are additive, so they
can be summed over cells and months afterwards; 100 * dln E_region * C_f / dE_region gives the figures' units.

Checks (stop with exit 1, nothing deleted, if any fails):
    - the two runs have the same time steps, file by file;
    - (grid cell, PFT) is unique among vegetated patches in each run;
    - per patch and step, MEG = k * EPS * product of the gammas (relative difference < 1e-10);
    - per grid cell and month, sum of the contributions = E_lcc - E_ctrl (relative to max E, < 1e-10);
    - 'unexplained' is zero.
"""
import argparse, glob, os, sys, time
from pathlib import Path
import numpy as np
from netCDF4 import Dataset

COMPOUNDS = ["isoprene", "pinene_a", "carene_3", "pinene_b", "myrcene", "limonene", "ocimene_t_b", "sabinene"]
FACTORS = ["composition", "gammaL", "gammaT", "gammaP", "gammaA", "gammaC", "cutoff", "unexplained"]
GAMMAS = ["gammaL", "gammaT", "gammaP", "gammaA", "gammaC"]
ARCHIVE, WORK = "/cluster/work/users/adelez/archive", "/cluster/work/users/adelez/noresm"
TOL = 1e-10


def tape2_files(case):
    """Daily CLM tape-2 files of `case` (archive first, then run directory), keyed by date stamp."""
    for d in (f"{ARCHIVE}/{case}/lnd/hist", f"{WORK}/{case}/run"):
        files = sorted(glob.glob(f"{d}/{case}.clm2.h1.*.nc"))
        if files:
            return {f.split(".clm2.h1.")[1][:-3]: f for f in files}
    return {}


def read_patches(nc, lat_min):
    """Vegetated patches north of lat_min: key (ixy, jxy, pft) -> index in the file, and their weight."""
    itype = nc["pfts1d_itype_veg"][:]
    sel = np.where((itype > 0) & (nc["pfts1d_lat"][:] >= lat_min))[0]
    keys = list(zip(nc["pfts1d_ixy"][sel], nc["pfts1d_jxy"][sel], itype[sel]))
    if len(set(keys)) != len(keys):
        raise SystemExit("FAIL: (grid cell, PFT) is not unique among vegetated patches")
    return dict(zip(keys, sel)), np.asarray(nc["pfts1d_wtgcell"][:])


def field(nc, name, idx):
    """(time, patch) values of `name` at file indices `idx` (-1 = patch absent -> 0); masked -> NaN."""
    # whole field read once, indexed in memory (netCDF4 fancy indexing on the patch axis is very slow)
    x = np.ma.filled(nc[name][:], np.nan).astype(np.float64)[:, np.maximum(idx, 0)]
    x[:, idx < 0] = 0.0
    return x


def lmdi(E0, E1, f0, f1):
    """Contributions (factor, time, patch) of each factor to E1 - E0, exact (see module docstring)."""
    nf = len(FACTORS)
    out = np.zeros((nf,) + E0.shape)
    both = (E0 > 0) & (E1 > 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        dlnE = np.log(E1) - np.log(E0)
        L = np.where(np.abs(dlnE) > 1e-12, (E1 - E0) / dlnE, E0)
        for k, f in enumerate(FACTORS[:6]):
            out[k] = np.where(both, L * (np.log(f1[f]) - np.log(f0[f])), 0.0)
    # one run zero: dE to the factors that are zero in that run
    for zero_run, fz in ((E0 == 0) & (E1 > 0), f0), ((E1 == 0) & (E0 > 0), f1):
        if not zero_run.any():
            continue
        # absent patch / zero weight -> composition only; otherwise the gammas that are exactly 0
        # (a missing value, NaN, is not zero: it ends in 'unexplained' and fails the check)
        comp0 = fz["composition"] == 0
        zeros = np.stack([comp0] + [(fz[f] == 0) & ~comp0 for f in GAMMAS])          # (6 factors, t, p)
        n = zeros.sum(axis=0)
        share = np.where(n > 0, (E1 - E0) / np.maximum(n, 1), 0.0)
        out[:6] += np.where(zero_run & zeros, share, 0.0)
        cut = zero_run & (n == 0) & ~comp0 & np.any([np.isnan(fz[f]) for f in GAMMAS], axis=0)
        out[6] += np.where(cut, E1 - E0, 0.0)
        out[7] += np.where(zero_run & (n == 0) & ~cut, E1 - E0, 0.0)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ctrl", required=True)
    ap.add_argument("--lcc", required=True)
    ap.add_argument("--label", required=True, help="e.g. PD_2005; output megan_lmdi_<label>.nc")
    ap.add_argument("--lat-min", type=float, default=45.0)
    ap.add_argument("--out", default="data/processed-data/megan-lmdi")
    ap.add_argument("--delete-raw", action="store_true", help="delete both runs' tape-2 files if all checks pass")
    a = ap.parse_args()
    t_start = time.time()

    f_ctrl, f_lcc = tape2_files(a.ctrl), tape2_files(a.lcc)
    days = sorted(set(f_ctrl) & set(f_lcc))
    if not days or set(f_ctrl) != set(f_lcc):
        raise SystemExit(f"FAIL: day files differ: CTRL {len(f_ctrl)}, LCC {len(f_lcc)}, common {len(days)}")
    print(f"{len(days)} common days, {days[0]} ... {days[-1]}")

    with Dataset(f_ctrl[days[0]]) as n0, Dataset(f_lcc[days[0]]) as n1:
        keys0, w0_all = read_patches(n0, a.lat_min)
        keys1, w1_all = read_patches(n1, a.lat_min)
        lat, lon = n0["lat"][:], n0["lon"][:]
        area = np.asarray(n0["area"][:])
    keys = sorted(set(keys0) | set(keys1))
    i0 = np.array([keys0.get(k, -1) for k in keys])
    i1 = np.array([keys1.get(k, -1) for k in keys])
    w0 = np.where(i0 >= 0, w0_all[np.maximum(i0, 0)], 0.0)
    w1 = np.where(i1 >= 0, w1_all[np.maximum(i1, 0)], 0.0)
    jx = np.array([k[0] for k in keys]) - 1          # lon index
    jy = np.array([k[1] for k in keys]) - 1          # lat index
    print(f"patches >= {a.lat_min} N: CTRL {len(keys0)}, LCC {len(keys1)}, matched {int(((i0 >= 0) & (i1 >= 0)).sum())}, "
          f"only CTRL {int((i1 < 0).sum())}, only LCC {int((i0 < 0).sum())}")

    nc_, nf, ny, nx = len(COMPOUNDS), len(FACTORS), len(lat), len(lon)
    sums = {}                                        # month -> dict of accumulated arrays
    max_prod_err = 0.0
    for day in days:
        with Dataset(f_ctrl[day]) as n0, Dataset(f_lcc[day]) as n1:
            t0, t1 = n0["time"][:], n1["time"][:]
            if not np.array_equal(t0, t1):
                raise SystemExit(f"FAIL: time steps differ in {day}")
            month = str(int(n0["mcdate"][0]))[:6]
            s = sums.setdefault(month, {"E0": np.zeros((nc_, ny, nx)), "E1": np.zeros((nc_, ny, nx)),
                                        "C": np.zeros((nc_, nf, ny, nx)), "n": 0})
            s["n"] += len(t0)
            gl0, gl1 = field(n0, "GAMMAL", i0), field(n1, "GAMMAL", i1)
            for ic, c in enumerate(COMPOUNDS):
                f0, f1, E = {}, {}, []
                for fac, nc, idx, w, gl in ((f0, n0, i0, w0, gl0), (f1, n1, i1, w1, gl1)):
                    meg = field(nc, f"MEG_{c}", idx)
                    eps = field(nc, f"EPS_{c}", idx)
                    fac["composition"] = w[None, :] * eps
                    fac["gammaL"] = gl
                    fac["gammaT"] = field(nc, f"GAMMAT_{c}", idx)
                    fac["gammaP"] = field(nc, f"GAMMAP_{c}", idx)
                    fac["gammaA"] = field(nc, f"GAMMAA_{c}", idx)
                    fac["gammaC"] = field(nc, "GAMMAC_isoprene", idx) if c == "isoprene" else np.ones_like(meg)
                    e = w[None, :] * meg
                    E.append(e)
                    # check: MEG = k * EPS * prod(gamma) where E > 0
                    prod = fac["composition"] * fac["gammaL"] * fac["gammaT"] * fac["gammaP"] * fac["gammaA"] * fac["gammaC"]
                    ok = e > 0
                    if ok.any():
                        ratio = e[ok] / prod[ok]
                        if not np.isfinite(ratio).all():         # a factor missing where there is emission
                            max_prod_err = np.inf
                        else:
                            max_prod_err = max(max_prod_err, float(np.abs(ratio / np.median(ratio) - 1).max()))
                C = lmdi(E[0], E[1], f0, f1)                 # (factor, t, p)
                for k in range(nf):
                    np.add.at(s["C"][ic, k], (jy, jx), C[k].sum(axis=0))
                np.add.at(s["E0"][ic], (jy, jx), E[0].sum(axis=0))
                np.add.at(s["E1"][ic], (jy, jx), E[1].sum(axis=0))
        print(f"  {day} done ({time.time() - t_start:.0f} s)")

    # checks
    months = sorted(sums)
    E0 = np.stack([sums[m]["E0"] / sums[m]["n"] for m in months], axis=1)        # (compound, month, lat, lon)
    E1 = np.stack([sums[m]["E1"] / sums[m]["n"] for m in months], axis=1)
    C = np.stack([sums[m]["C"] / sums[m]["n"] for m in months], axis=2)          # (compound, factor, month, lat, lon)
    scale = np.maximum(np.abs(E0).max(), np.abs(E1).max())
    closure = np.nanmax(np.abs(C.sum(axis=1) - (E1 - E0))) / scale
    unexplained = np.abs(C[:, -1]).max() / scale
    checks = {"MEG = k*EPS*prod(gamma), max rel diff": (max_prod_err, max_prod_err < TOL),
              "sum of contributions = dE, max rel diff": (closure, closure < TOL),
              "unexplained, max rel": (unexplained, unexplained < TOL)}
    for name, (v, ok) in checks.items():
        print(f"  {'PASS' if ok else 'FAIL'}  {name}: {v:.2e}")
    passed = all(ok for _, ok in checks.values())

    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    path = out / f"megan_lmdi_{a.label}.nc"
    with Dataset(path, "w") as d:
        d.createDimension("compound", nc_); d.createDimension("factor", nf)
        d.createDimension("month", len(months)); d.createDimension("lat", ny); d.createDimension("lon", nx)
        d.title = "Exact (LMDI) split of the MEGAN emission change LCC - CTRL (analysis/MEGAN_ATTRIBUTION.md, option 1)"
        d.ctrl_case, d.lcc_case, d.label = a.ctrl, a.lcc, a.label
        d.days = f"{days[0]} ... {days[-1]} ({len(days)} files)"
        d.lat_min = a.lat_min
        d.compounds, d.factors = ",".join(COMPOUNDS), ",".join(FACTORS)
        d.method = __doc__.split("Method")[1].split("Checks")[0].strip()
        d.checks = "; ".join(f"{k}: {v:.2e} ({'pass' if ok else 'FAIL'})" for k, (v, ok) in checks.items())
        d.script = os.path.abspath(__file__)
        d.createVariable("month", "i4", ("month",))[:] = [int(m) for m in months]
        d["month"].long_name = "YYYYMM"
        d.createVariable("nsteps", "i4", ("month",))[:] = [sums[m]["n"] for m in months]
        d.createVariable("lat", "f8", ("lat",))[:] = lat
        d.createVariable("lon", "f8", ("lon",))[:] = lon
        d.createVariable("area", "f8", ("lat", "lon"))[:] = area
        d["area"].units = "km2"
        for name, x, dims, ln in (
                ("E_ctrl", E0, ("compound", "month", "lat", "lon"), "mean MEGAN emission, CTRL, matched vegetated patches"),
                ("E_lcc", E1, ("compound", "month", "lat", "lon"), "mean MEGAN emission, LCC, matched vegetated patches"),
                ("contribution", C, ("compound", "factor", "month", "lat", "lon"),
                 "exact contribution of each factor to E_lcc - E_ctrl (sums to it)")):
            v = d.createVariable(name, "f8", dims, zlib=True)
            v[:] = x
            v.units = "kg m-2 s-1 (per grid-cell land area)"
            v.long_name = ln
    print(f"written {path} ({time.time() - t_start:.0f} s)")

    if not passed:
        raise SystemExit("FAIL: checks failed, raw files kept")
    if a.delete_raw:
        for f in list(f_ctrl.values()) + list(f_lcc.values()):
            os.remove(f)
        print(f"deleted {len(f_ctrl) + len(f_lcc)} raw tape-2 files")


if __name__ == "__main__":
    main()
