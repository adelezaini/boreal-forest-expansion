"""Isoprene diurnal composites for the fixed-BVOC (fBVOC) runs + 30-min regional time series for all runs.

Part A, prescribed input (what every production fBVOC run receives):
    /cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions/ems_<case>_2001-2014_SFISOP.nc
    ISOP(time=17520, lat, lon) molecules cm-2 s-1, one cyclic year of 30-min records (2001-2014 mean per
    day-of-year and step). With bypass_isoprene_diurnal_adjustment the model emits the file value unchanged
    (checked: CTRL_PD_fBVOCctrlPD_HR h1 = its source CTRL_PD h1 to 0.05 %, same time stamps), so the file is the flux.
    -> fbvoc/diurnal_ems_<SRC>.nc (same layout as diurnal_<ALIAS>_<YEAR>.nc) and timeseries/ts_ems_<SRC>.nc
Part B, fBVOC runs with 30-min output (old-chain 3-yr tests, 2001-2002 used):
    CTRL_PD_fBVOCctrlPD_HR (14d, replay of each year), CTRL_PD_fBVOCctrlPD_C0102 (14f, 2001-02 climatology)
    and their MEGAN source CTRL_PD -20261023 (alias CTRL_PD_old).
    -> fbvoc/diurnal_<ALIAS>_<YEAR>.nc (reduce_year of reduce_isoprene_diurnal.py)
Part C, regional totals at 30 min (Mg h-1, UTC step centre) from the raw h1 tape:
    MEGAN exact-split branch runs (years of reduce_isoprene_diurnal.py) and the Part B runs.
    -> timeseries/ts_<ALIAS>_<YEAR>.nc, SFISOP(region, time)

Time convention as reduce_isoprene_diurnal.py: a record stamped t is assigned to the step centre t - 15 min.
Regions: LCC-modified cells (diagnostics/lcc-modified-cells/modified_cells.nc) and all cells >= 45N.
Raw h1 on /cluster/work is purged ~Dec 2026; outputs live on NIRD (data/processed-data).

Usage: $PY diagnostics/2_isoprene-diurnal-cycle/reduce_isoprene_fbvoc_and_timeseries.py [--nproc 12] [--parts A B C]
Skips existing outputs.
"""
import argparse
import glob
import os
import sys
import time
from multiprocessing import Pool

import netCDF4
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reduce_isoprene_diurnal as R  # noqa: E402

ROOT = "/cluster/home/adelez/BOREAL-FOREST-EXPANSION"
BASE = f"{ROOT}/data/processed-data/isoprene-diurnal"
OUT_FB = f"{BASE}/fbvoc"
OUT_TS = f"{BASE}/timeseries"
MASK = f"{ROOT}/diagnostics/lcc-modified-cells/modified_cells.nc"
EMS = "/cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions"
ISOP_TO_KG = 1 / 8.8410346153959096e20     # molecules cm-2 s-1 -> kg m-2 s-1 (factor used to build the files)
STEPS, NREC = 48, 365 * 48
KG_S_TO_MG_H = 3600 / 1e3
REGIONS = ("LCC-modified cells", ">= 45N")

# prescribed inputs of the production fBVOC runs (cases-scripts 14b/14c/14e/24b-e/24g)
EMS_SRC = {
    "CTRL_PD": "ems_NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20261029_2001-2014",      # 14b, 14c, 24b
    "LCC_PD": "ems_NF2000norbc_tropstratchem_nudg_lcc_f19_f19-20261028_2001-2014",        # 14e, 24d
    "CTRL_FUT": "ems_NF2100ssp585norbc_tropstratchem_nudg_ctrl_f19_f19-20261028_2001-2014",  # 24c, 24e
    "LCC_FUT": "ems_NF2100ssp585norbc_tropstratchem_nudg_lcc_f19_f19-20261028_2001-2014",    # 24g
}
ARCH = R.ARCHIVE
FB_RUNS = {
    "CTRL_PD_fBVOCctrlPD_HR": f"{ARCH}/NF2000norbc_tropstratchem_nudg_ctrl_fBVOCctrlPD_HR_f19_f19-20261029",
    "CTRL_PD_fBVOCctrlPD_C0102": f"{ARCH}/NF2000norbc_tropstratchem_nudg_ctrl_fBVOCctrlPD_C0102_f19_f19-20261109",
    "CTRL_PD_old": f"{ARCH}/NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20261023",
}
FB_YEARS = (2001, 2002)


def weights(lat, lon):
    """(region, lat, lon) area weights in m2 (sphere R = 6371.22 km, as the notebook)."""
    r = 6.37122e6
    lat_e = np.concatenate([[-90], 0.5 * (lat[1:] + lat[:-1]), [90]])
    area = (r**2 * np.deg2rad(lon[1] - lon[0]) * np.diff(np.sin(np.deg2rad(lat_e))))[:, None] * np.ones(lon.size)
    with netCDF4.Dataset(MASK) as ds:
        mod = np.asarray(ds.variables["modified"][:]).astype(bool)
        assert np.allclose(ds.variables["lat"][:], lat) and np.allclose(ds.variables["lon"][:], lon)
    north = np.broadcast_to(lat[:, None] >= 45, area.shape)
    return np.stack([area * mod, area * north])


def write_composite(path, lat, lon, means, attrs):
    tmp = path + ".part"
    with netCDF4.Dataset(tmp, "w") as ds:
        for d, n in (("month", 12), ("step", STEPS), ("lat", lat.size), ("lon", lon.size)):
            ds.createDimension(d, n)
        ds.createVariable("month", "i4", ("month",))[:] = np.arange(1, 13)
        st = ds.createVariable("step", "f8", ("step",))
        st[:] = (np.arange(STEPS) + 0.5) * 24 / STEPS
        st.long_name, st.units = "UTC hour of the step centre", "hours"
        ds.createVariable("lat", "f8", ("lat",))[:] = lat
        ds.createVariable("lon", "f8", ("lon",))[:] = lon
        ds.createVariable("n_days", "i4", ("month", "step"))[:] = R.DAYS_PER_MONTH[:, None] * np.ones(STEPS, int)
        for v, arr in means.items():
            var = ds.createVariable(v, "f4", ("month", "step", "lat", "lon"), zlib=True, complevel=4)
            var[:] = arr
            var.units = "kg/m2/s"
        for k, v in attrs.items():
            setattr(ds, k, v)
        ds.created_by = "diagnostics/2_isoprene-diurnal-cycle/reduce_isoprene_fbvoc_and_timeseries.py"
        ds.created = time.strftime("%Y-%m-%d %H:%M")
    os.replace(tmp, path)


def write_ts(path, tot, year, attrs):
    """tot: (region, 17520) Mg h-1 in (doy, step) order."""
    tmp = path + ".part"
    with netCDF4.Dataset(tmp, "w") as ds:
        ds.createDimension("region", len(REGIONS))
        ds.createDimension("time", NREC)
        rg = ds.createVariable("region", str, ("region",))
        for i, r in enumerate(REGIONS):
            rg[i] = r
        t = ds.createVariable("time", "f8", ("time",))
        t[:] = (year - 2000) * 365 + (np.arange(NREC) + 0.5) / STEPS
        t.units, t.calendar = "days since 2000-01-01 00:00:00", "noleap"
        t.long_name = "UTC step centre"
        v = ds.createVariable("SFISOP", "f8", ("region", "time"))
        v[:] = tot
        v.units, v.long_name = "Mg/h", "regional total isoprene emission (SFISOP x cell area)"
        for k, val in attrs.items():
            setattr(ds, k, val)
        ds.created_by = "diagnostics/2_isoprene-diurnal-cycle/reduce_isoprene_fbvoc_and_timeseries.py"
        ds.created = time.strftime("%Y-%m-%d %H:%M")
    os.replace(tmp, path)


def part_a():
    for src, prefix in EMS_SRC.items():
        pc, pt = f"{OUT_FB}/diurnal_ems_{src}.nc", f"{OUT_TS}/ts_ems_{src}.nc"
        if os.path.exists(pc) and os.path.exists(pt):
            print(f"A {src}: exists, skipped", flush=True)
            continue
        t0 = time.time()
        f = f"{EMS}/{prefix}_SFISOP.nc"
        with netCDF4.Dataset(f) as ds:
            tt = np.asarray(ds.variables["time"][:])
            assert tt.size == NREC and np.allclose(tt, np.arange(NREC) / STEPS), "unexpected time axis"
            lat, lon = ds.variables["lat"][:].data, ds.variables["lon"][:].data
            x = np.asarray(ds.variables["ISOP"][:], dtype="f4") * np.float32(ISOP_TO_KG)
        # record k stamped k/48 d -> step centre k/48 - 1/96 d = (doy, step) index k - 1 (cyclic year)
        x = np.roll(x, -1, axis=0).reshape(365, STEPS, lat.size, lon.size)
        cum = np.concatenate([[0], np.cumsum(R.DAYS_PER_MONTH)])
        means = np.stack([x[cum[m]:cum[m + 1]].mean(0) for m in range(12)])
        attrs = dict(case=f"prescribed input {prefix}", source_file=f, year="cyclic (2001-2014 mean)",
                     time_convention="record stamped t assigned to step centre t - 15 min")
        write_composite(pc, lat, lon, {"SFISOP": means}, attrs)
        w = weights(lat, lon)
        tot = np.tensordot(x.reshape(NREC, lat.size, lon.size), w, axes=([1, 2], [1, 2])).T * KG_S_TO_MG_H
        write_ts(pt, tot, 2000, attrs)
        print(f"A {src}: written ({time.time() - t0:.0f} s)", flush=True)


def part_b(nproc):
    for alias, d in FB_RUNS.items():
        for y in FB_YEARS:
            path = f"{OUT_FB}/diurnal_{alias}_{y}.nc"
            if os.path.exists(path):
                print(f"B {alias} {y}: exists, skipped", flush=True)
                continue
            t0 = time.time()
            res, msg = R.reduce_year(d, y, nproc)
            if res is None:
                print(f"B {alias} {y}: {msg}, not written", flush=True)
                continue
            R.write(path, d, y, *res)
            print(f"B {alias} {y}: written ({time.time() - t0:.0f} s)", flush=True)


_W = None


def _init(w):
    global _W
    _W = w


def _ts_file(path):
    year, doy, step, data = R.read_file(path)
    tot = np.tensordot(data["SFISOP"].astype("f8"), _W, axes=([1, 2], [1, 2])) * KG_S_TO_MG_H   # (rec, region)
    return year, doy, step, tot


def ts_year(case_dir, year, nproc, w):
    files = sorted(glob.glob(f"{case_dir}/atm/hist/*.cam.h1.{year}-*.nc"))
    files += sorted(glob.glob(f"{case_dir}/atm/hist/*.cam.h1.{year + 1}-01-01-*.nc"))[:1]
    if not files:
        return None, "no cam.h1 files"
    out = np.full((len(REGIONS), NREC), np.nan)
    with Pool(nproc, initializer=_init, initargs=(w,)) as pool:
        for yr, doy, step, tot in pool.imap(_ts_file, files, chunksize=4):
            k = yr == year
            out[:, doy[k] * STEPS + step[k]] = tot[k].T
    if np.isnan(out).any():
        return None, f"incomplete: {int(np.isnan(out[0]).sum())} steps missing"
    return out, "ok"


def part_c(nproc):
    jobs = {(a, y): d for (a, y), d in R.find_cases().items()}
    jobs.update({(a, y): d for a, d in FB_RUNS.items() for y in FB_YEARS})
    w = None
    for (alias, y), d in sorted(jobs.items()):
        path = f"{OUT_TS}/ts_{alias}_{y}.nc"
        if os.path.exists(path):
            print(f"C {alias} {y}: exists, skipped", flush=True)
            continue
        if w is None:
            f0 = sorted(glob.glob(f"{d}/atm/hist/*.cam.h1.*.nc"))[0]
            with netCDF4.Dataset(f0) as ds:
                w = weights(ds.variables["lat"][:].data, ds.variables["lon"][:].data)
        t0 = time.time()
        tot, msg = ts_year(d, y, nproc, w)
        if tot is None:
            print(f"C {alias} {y}: {msg}, not written", flush=True)
            continue
        write_ts(path, tot, y, dict(case=os.path.basename(d), year=y))
        print(f"C {alias} {y}: written ({time.time() - t0:.0f} s)", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nproc", type=int, default=12)
    ap.add_argument("--parts", nargs="+", default=["A", "B", "C"])
    args = ap.parse_args()
    os.makedirs(OUT_FB, exist_ok=True)
    os.makedirs(OUT_TS, exist_ok=True)
    if "A" in args.parts:
        part_a()
    if "B" in args.parts:
        part_b(args.nproc)
    if "C" in args.parts:
        part_c(args.nproc)


if __name__ == "__main__":
    sys.exit(main())
