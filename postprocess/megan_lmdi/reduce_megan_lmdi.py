#!/usr/bin/env python3
"""Exact split of the MEGAN emission change LCC - CTRL from patch-level branch output: LMDI (factors) + driver swaps.

Options 1 and 1b of analysis/MEGAN_ATTRIBUTION.md. Reads the CLM tape-2 files (clm2.h1.*: MEGAN fields per patch,
every 30-min step, instantaneous) of a CTRL and an LCC branch run covering the same days, and writes one small
netCDF with
  (1) LMDI: per compound, month and grid cell, the mean emission of both runs and the exact contribution of each
      gamma factor to the difference (variables E_ctrl, E_lcc, contribution);
  (2) driver swaps: per compound, month and matched patch pair, the monthly integrated emission of both runs and
      the exact contribution of plant cover and of each driver group (Shapley values; megan_swaps.py), in a 4-group
      and a 3-group version (variables pair_*, Ep_ctrl, Ep_lcc, swap4, swap3).
Nothing is deleted unless --delete-raw is given AND all checks pass.

Usage:
    PY=/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python
    $PY postprocess/megan_lmdi/reduce_megan_lmdi.py --ctrl <CTRL branch case> --lcc <LCC branch case> \
        --label PD_2005 [--year 2005] [--lat-min 45] [--out data/processed-data/megan-lmdi] [--delete-raw | --delete-dry-run]
    --year Y: only the day files of year Y, read from the ARCHIVE only (multi-year chain cases, production);
              without it, all day files of the case (archive, else run directory: the 5-day tests).
    --max-days N, --from-day YYYY-MM-DD: only part of the days (tests; no deleting).

Method (LMDI; per compound c, matched patch p = same grid cell + same PFT, time step t):
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
Driver swaps: see the docstring of megan_swaps.py. swap4/swap3 are integrated over each month (kg per m2 of grid-cell
land, sum over steps of rate * 1800 s), per patch pair; sum over terms = Ep_lcc - Ep_ctrl exactly.

Checks (stop with exit 1, nothing deleted, if any fails):
    - the two runs have the same time steps, file by file;
    - (grid cell, PFT) is unique among vegetated patches in each run;
    - per patch and step, MEG = k * EPS * product of the gammas (relative difference < 1e-10);
    - per grid cell and month, sum of the contributions = E_lcc - E_ctrl (relative to max E, < 1e-10);
    - 'unexplained' is zero;
    - swaps: grid-cell light consistent among the patches of a cell, rebuilt PAR_* = CLM's at fresh steps, replayed
      G = CLM's GAMMA / GAMMAC, replay_residual at replayed steps (all < 1e-10); share of |dE| on flagged steps
      (not replayable, whole dE -> replay_residual) < 1e-3.
"""
import argparse, glob, os, sys, time
from pathlib import Path
import numpy as np
from netCDF4 import Dataset

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import megan_swaps as sw
from megan_replay import class_constants

COMPOUNDS = ["isoprene", "pinene_a", "carene_3", "pinene_b", "myrcene", "limonene", "ocimene_t_b", "sabinene"]
FACTORS = ["composition", "gammaL", "gammaT", "gammaP", "gammaA", "gammaC", "cutoff", "unexplained"]
GAMMAS = ["gammaL", "gammaT", "gammaP", "gammaA", "gammaC"]
ARCHIVE, WORK = "/cluster/work/users/adelez/archive", "/cluster/work/users/adelez/noresm"
TOL = 1e-10
FLAG_TOL = 1e-3


def tape2_files(case, year=None):
    """Daily CLM tape-2 files of `case`, keyed by date stamp. year=None: archive first, then run directory.
    year=Y: archive only, files of year Y only (the run directory may hold an incomplete later year)."""
    dirs = (f"{ARCHIVE}/{case}/lnd/hist",) if year else (f"{ARCHIVE}/{case}/lnd/hist", f"{WORK}/{case}/run")
    pattern = f"{case}.clm2.h1.{year:04d}-*.nc" if year else f"{case}.clm2.h1.*.nc"
    for d in dirs:
        files = sorted(glob.glob(f"{d}/{pattern}"))
        if files:
            return {f.split(".clm2.h1.")[1][:-3]: f for f in files}
    return {}


def predecessor(case, day):
    """Tape-2 file of `case` just before date stamp `day` (archive or run directory), or None."""
    files = {}
    for d in (f"{ARCHIVE}/{case}/lnd/hist", f"{WORK}/{case}/run"):
        for f in glob.glob(f"{d}/{case}.clm2.h1.*.nc"):
            files.setdefault(f.split(".clm2.h1.")[1][:-3], f)
    before = sorted(k for k in files if k < day)
    return files[before[-1]] if before else None


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
    ap.add_argument("--year", type=int, help="only this year's day files, from the archive (chain cases)")
    ap.add_argument("--max-days", type=int, help="only the first N common days (tests)")
    ap.add_argument("--from-day", help="only days with date stamp >= this, e.g. 2010-07-01 (tests)")
    ap.add_argument("--delete-raw", action="store_true", help="delete both runs' tape-2 files if all checks pass")
    ap.add_argument("--delete-dry-run", action="store_true", help="only list what --delete-raw would delete")
    a = ap.parse_args()
    t_start = time.time()

    if a.delete_raw and a.delete_dry_run:
        raise SystemExit("--delete-raw and --delete-dry-run exclude each other")
    if (a.max_days or a.from_day) and (a.delete_raw or a.delete_dry_run):
        raise SystemExit("--max-days is for tests: no deleting")
    f_ctrl, f_lcc = tape2_files(a.ctrl, a.year), tape2_files(a.lcc, a.year)
    days = sorted(set(f_ctrl) & set(f_lcc))
    if not days or set(f_ctrl) != set(f_lcc):
        raise SystemExit(f"FAIL: day files differ: CTRL {len(f_ctrl)}, LCC {len(f_lcc)}, common {len(days)}")
    if a.from_day:
        days = [x for x in days if x >= a.from_day]
    if a.max_days:
        days = days[:a.max_days]
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
    pft = np.array([k[2] for k in keys])
    print(f"patches >= {a.lat_min} N: CTRL {len(keys0)}, LCC {len(keys1)}, matched {int(((i0 >= 0) & (i1 >= 0)).sum())}, "
          f"only CTRL {int((i1 < 0).sum())}, only LCC {int((i0 < 0).sum())}")

    # driver swaps: patch presence, grid cells, class constants
    nc_, nf, ny, nx = len(COMPOUNDS), len(FACTORS), len(lat), len(lon)
    pres = [(i0 >= 0) & (w0 > 0), (i1 >= 0) & (w1 > 0)]
    cid = jy * nx + jx                                 # grid-cell id of every key
    ucell, pcell = np.unique(cid, return_inverse=True)  # pair -> compact cell index
    K = class_constants()
    n4, n3, npair = len(sw.TERMS4), len(sw.TERMS3), len(keys)
    swap_stats = {"light_spread": 0.0, "par_rebuild": 0.0, "G_replay": 0.0, "residual": 0.0,
                  "flag_absdE": 0.0, "absdE": 0.0, "n_flag": 0, "n_ok": 0}

    # previous step of the PREV drivers (CLM uses them one step late): from the file before the first day if it exists
    prev = [None, None]
    for r, (case, idx, f) in enumerate(((a.ctrl, i0, f_ctrl), (a.lcc, i1, f_lcc))):
        pf = predecessor(case, days[0])
        if pf:
            with Dataset(pf) as n, Dataset(f[days[0]]) as nd:
                dt_ok = abs(float(nd["time"][0]) - float(n["time"][-1]) - 1 / 48) < 1e-6
                if dt_ok:
                    prev[r] = {v: field(n, v, idx)[-1] for v in sw.PREV}
        print(f"  previous step for {'CTRL' if r == 0 else 'LCC'}: {pf if prev[r] is not None else 'none (step 1 flagged)'}")

    sums = {}                                        # month -> dict of accumulated arrays
    max_prod_err = 0.0
    for day in days:
        with Dataset(f_ctrl[day]) as n0, Dataset(f_lcc[day]) as n1:
            t0, t1 = n0["time"][:], n1["time"][:]
            if not np.array_equal(t0, t1):
                raise SystemExit(f"FAIL: time steps differ in {day}")
            dt = float(np.round((t0[1] - t0[0]) * 86400)) if len(t0) > 1 else 1800.0
            month = str(int(n0["mcdate"][0]))[:6]
            s = sums.setdefault(month, {"E0": np.zeros((nc_, ny, nx)), "E1": np.zeros((nc_, ny, nx)),
                                        "C": np.zeros((nc_, nf, ny, nx)), "n": 0,
                                        "Ep0": np.zeros((nc_, npair)), "Ep1": np.zeros((nc_, npair)),
                                        "S4": np.zeros((nc_, n4, npair)), "S3": np.zeros((nc_, n3, npair))})
            s["n"] += len(t0)
            T = len(t0)

            # drivers of both runs (PREV fields shifted one step), grid-cell light, flags
            drv, flag = [], np.zeros((T, npair), bool)
            for r, (nc, idx) in enumerate(((n0, i0), (n1, i1))):
                raw = {v: field(nc, v, idx) for v in sw.DRIVERS}
                fresh = np.isfinite(field(nc, "GAMMA_isoprene", idx)) & (idx >= 0)[None, :]
                d = {v: raw[v] for v in ("TV", "FSUN")}
                first = prev[r] if prev[r] is not None else {v: raw[v][0] for v in sw.PREV}
                if prev[r] is None:
                    flag[0] = True
                for v in sw.PREV:
                    d[v] = np.vstack([first[v][None, :], raw[v][:-1]])
                prev[r] = {v: raw[v][-1] for v in sw.PREV}
                sad, sai, spread = sw.cell_light(raw["PAR_sun"], raw["PAR_shade"], raw["FSUN"],
                                                 fresh & (idx >= 0)[None, :], pcell, len(ucell))
                swap_stats["light_spread"] = max(swap_stats["light_spread"], spread)
                d["solad"], d["solai"] = sad[:, pcell], sai[:, pcell]
                with np.errstate(invalid="ignore"):
                    rb = (d["solad"] + raw["FSUN"] * d["solai"]) * 4.6
                    rel = np.abs(rb - raw["PAR_sun"]) / np.maximum(np.abs(raw["PAR_sun"]), 1.0)
                m = fresh & np.isfinite(rel)
                if m.any():
                    swap_stats["par_rebuild"] = max(swap_stats["par_rebuild"], float(rel[m].max()))
                drv.append(d)

            gl0, gl1 = field(n0, "GAMMAL", i0), field(n1, "GAMMAL", i1)
            for ic, c in enumerate(COMPOUNDS):
                f0, f1, E, sv = {}, {}, [], []
                for fac, nc, idx, w, gl in ((f0, n0, i0, w0, gl0), (f1, n1, i1, w1, gl1)):
                    meg = field(nc, f"MEG_{c}", idx)
                    eps = field(nc, f"EPS_{c}", idx)
                    gam = field(nc, f"GAMMA_{c}", idx)
                    fac["composition"] = w[None, :] * eps
                    fac["gammaL"] = gl
                    fac["gammaT"] = field(nc, f"GAMMAT_{c}", idx)
                    fac["gammaP"] = field(nc, f"GAMMAP_{c}", idx)
                    fac["gammaA"] = field(nc, f"GAMMAA_{c}", idx)
                    fac["gammaC"] = field(nc, "GAMMAC_isoprene", idx) if c == "isoprene" else np.ones_like(meg)
                    e = w[None, :] * meg
                    E.append(e)
                    sv.append((eps, fac["gammaC"], np.isfinite(gam), gam))
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

                # driver swaps
                with np.errstate(invalid="ignore", divide="ignore", over="ignore"):
                    comp = sw.components(drv, pft, K[c])
                    P0 = np.broadcast_to(pres[0][None, :], E[0].shape)
                    P1 = np.broadcast_to(pres[1][None, :], E[0].shape)
                    t4, t3, G0, G1, okm, bad = sw.split(E[0], E[1], P0, P1, sv[0][2], sv[1][2], w0, w1,
                                                        sv[0][0], sv[1][0], sv[0][1], sv[1][1], comp, flag)
                    use = okm & ~bad
                    dE = E[1] - E[0]
                    for G, (eps, gc, valid, gam) in ((G0, sv[0]), (G1, sv[1])):
                        Gc = gam / gc
                        rel = np.abs(G - Gc) / np.maximum(np.abs(Gc), 1e-30)
                        mm = use & (np.abs(Gc) > 1e-12)
                        if mm.any():
                            swap_stats["G_replay"] = max(swap_stats["G_replay"], float(rel[mm].max()))
                    scale_e = max(float(np.abs(E[0]).max()), float(np.abs(E[1]).max()), 1e-300)
                    if use.any():
                        swap_stats["residual"] = max(swap_stats["residual"], float(np.abs(t4[-1][use]).max()) / scale_e,
                                                     float(np.abs(t3[-1][use]).max()) / scale_e)
                    swap_stats["flag_absdE"] += float(np.abs(dE[bad]).sum())
                    swap_stats["absdE"] += float(np.abs(dE).sum())
                    swap_stats["n_flag"] += int(bad.sum()); swap_stats["n_ok"] += int(okm.sum())
                s["S4"][ic] += t4.sum(axis=1) * dt
                s["S3"][ic] += t3.sum(axis=1) * dt
                s["Ep0"][ic] += E[0].sum(axis=0) * dt
                s["Ep1"][ic] += E[1].sum(axis=0) * dt
        print(f"  {day} done ({time.time() - t_start:.0f} s)")

    # checks
    months = sorted(sums)
    E0 = np.stack([sums[m]["E0"] / sums[m]["n"] for m in months], axis=1)        # (compound, month, lat, lon)
    E1 = np.stack([sums[m]["E1"] / sums[m]["n"] for m in months], axis=1)
    C = np.stack([sums[m]["C"] / sums[m]["n"] for m in months], axis=2)          # (compound, factor, month, lat, lon)
    scale = np.maximum(np.abs(E0).max(), np.abs(E1).max())
    closure = np.nanmax(np.abs(C.sum(axis=1) - (E1 - E0))) / scale
    unexplained = np.abs(C[:, -1]).max() / scale
    Ep0 = np.stack([sums[m]["Ep0"] for m in months], axis=1)                       # (compound, month, pair)
    Ep1 = np.stack([sums[m]["Ep1"] for m in months], axis=1)
    S4 = np.stack([sums[m]["S4"] for m in months], axis=2)                         # (compound, term, month, pair)
    S3 = np.stack([sums[m]["S3"] for m in months], axis=2)
    pscale = max(float(np.abs(Ep0).max()), float(np.abs(Ep1).max()), 1e-300)
    sw_closure = max(float(np.abs(S4.sum(axis=1) - (Ep1 - Ep0)).max()), float(np.abs(S3.sum(axis=1) - (Ep1 - Ep0)).max())) / pscale
    flag_share = swap_stats["flag_absdE"] / max(swap_stats["absdE"], 1e-300)
    checks = {"MEG = k*EPS*prod(gamma), max rel diff": (max_prod_err, max_prod_err < TOL),
              "sum of contributions = dE, max rel diff": (closure, closure < TOL),
              "unexplained, max rel": (unexplained, unexplained < TOL),
              "swaps: grid-cell light spread among patches, max rel": (swap_stats["light_spread"], swap_stats["light_spread"] < TOL),
              "swaps: rebuilt PAR_sun vs CLM at fresh steps, max rel": (swap_stats["par_rebuild"], swap_stats["par_rebuild"] < TOL),
              "swaps: replayed G vs CLM GAMMA/GAMMAC, max rel": (swap_stats["G_replay"], swap_stats["G_replay"] < TOL),
              "swaps: replay_residual at replayed steps, max rel to max E": (swap_stats["residual"], swap_stats["residual"] < TOL),
              "swaps: sum of terms = dE per pair and month, max rel": (sw_closure, sw_closure < TOL),
              "swaps: share of |dE| on flagged steps": (flag_share, flag_share < FLAG_TOL)}
    for name, (v, ok) in checks.items():
        print(f"  {'PASS' if ok else 'FAIL'}  {name}: {v:.2e}")
    print(f"  swaps: {swap_stats['n_ok']} replayable pair-steps x compounds, {swap_stats['n_flag']} flagged")
    passed = all(ok for _, ok in checks.values())

    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    path = out / f"megan_lmdi_{a.label}.nc"
    tmp = path.with_suffix(".nc.tmp")
    with Dataset(tmp, "w") as d:
        d.createDimension("compound", nc_); d.createDimension("factor", nf)
        d.createDimension("month", len(months)); d.createDimension("lat", ny); d.createDimension("lon", nx)
        d.createDimension("pair", npair)
        d.createDimension("term4", n4); d.createDimension("term3", n3)
        d.title = "Exact split of the MEGAN emission change LCC - CTRL: LMDI + driver swaps (analysis/MEGAN_ATTRIBUTION.md, options 1 and 1b)"
        d.ctrl_case, d.lcc_case, d.label = a.ctrl, a.lcc, a.label
        d.days = f"{days[0]} ... {days[-1]} ({len(days)} files)"
        if a.year:
            d.year = a.year
        d.lat_min = a.lat_min
        d.compounds, d.factors = ",".join(COMPOUNDS), ",".join(FACTORS)
        d.terms4, d.terms3 = ",".join(sw.TERMS4), ",".join(sw.TERMS3)
        d.method = __doc__.split("Method")[1].split("Checks")[0].strip()
        d.method_swaps = sw.__doc__.strip()
        d.checks = "; ".join(f"{k}: {v:.2e} ({'pass' if ok else 'FAIL'})" for k, (v, ok) in checks.items())
        d.swap_flagged_pair_steps = swap_stats["n_flag"]
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
        for name, x, ln in (("pair_ixy", jx + 1, "grid-cell lon index (1-based)"), ("pair_jxy", jy + 1, "grid-cell lat index (1-based)"),
                            ("pair_pft", pft, "PFT (pfts1d_itype_veg)")):
            d.createVariable(name, "i4", ("pair",))[:] = x
            d[name].long_name = ln
        for name, x, ln in (("pair_lat", np.asarray(lat)[jy], "latitude"), ("pair_lon", np.asarray(lon)[jx], "longitude"),
                            ("pair_area", area[jy, jx], "grid-cell area (km2)"),
                            ("w_ctrl", w0, "patch weight in the grid cell, CTRL (0 = absent)"),
                            ("w_lcc", w1, "patch weight in the grid cell, LCC (0 = absent)")):
            d.createVariable(name, "f8", ("pair",))[:] = x
            d[name].long_name = ln
        for name, x, dims, ln in (
                ("Ep_ctrl", Ep0, ("compound", "month", "pair"), "MEGAN emission of the patch, CTRL, integrated over the month"),
                ("Ep_lcc", Ep1, ("compound", "month", "pair"), "MEGAN emission of the patch, LCC, integrated over the month"),
                ("swap4", S4, ("compound", "term4", "month", "pair"),
                 "exact contribution to Ep_lcc - Ep_ctrl: plant cover + 4 driver groups (Shapley) + extra terms"),
                ("swap3", S3, ("compound", "term3", "month", "pair"),
                 "exact contribution to Ep_lcc - Ep_ctrl: plant cover + 3 driver groups (Shapley) + extra terms")):
            v = d.createVariable(name, "f8", dims, zlib=True)
            v[:] = x
            v.units = "kg m-2 (per grid-cell land area, integrated over the month)"
            v.long_name = ln
    os.replace(tmp, path)
    print(f"written {path} ({time.time() - t_start:.0f} s)")

    if not passed:
        raise SystemExit("FAIL: checks failed, raw files kept")
    raw = list(f_ctrl.values()) + list(f_lcc.values())
    if a.delete_dry_run:
        size = sum(os.path.getsize(f) for f in raw) / 1e9
        print(f"DRY RUN: would delete {len(raw)} raw tape-2 files ({size:.1f} GB), e.g. {raw[0]} ... {raw[-1]}")
    if a.delete_raw:
        for f in raw:
            os.remove(f)
        print(f"deleted {len(raw)} raw tape-2 files")


if __name__ == "__main__":
    main()
