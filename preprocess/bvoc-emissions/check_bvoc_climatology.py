#!/usr/bin/env python3
"""Check prescribed-BVOC climatologies against the CAM h0 monthly means of the source run.

Usage (login node; needs the archive and the conda env):
    $PY check_bvoc_climatology.py CASE START_YEAR END_YEAR [EMS_DIR]
    e.g. $PY check_bvoc_climatology.py NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20261023 2001 2014

For each of the 19 species in create_bvoc_emissions_climatology_staged.MOLAR_MASS:
  - the file exists, has 17520 (half-hourly) or 12 (monthly) records, units molecules/cm2/s
  - annual mean of the climatology (monthly: month-length weighted) vs the month-length weighted
    START-END mean of the same field in h0, converted with the same factor. h1 samples every
    30-min step, so the half-hourly ratio should be ~1 too (float32 rounding only).
  - global total in Tg(species)/yr (area from cos(lat) on the f19 grid, Earth radius 6.371e6 m)
Exit status 1 if a file is missing or a ratio is off by more than 1e-3.
"""
import os, sys
import numpy as np
from netCDF4 import Dataset

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from create_bvoc_emissions_climatology_staged import MOLAR_MASS, MONTHLY_VARS, OUTPUT_VAR_NAME, AVOGADRO

case, y0, y1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
ems_dir = sys.argv[4] if len(sys.argv) > 4 else "/cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions"
hist = f"/cluster/work/users/adelez/archive/{case}/atm/hist"
MDAYS = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31], float)

# h0 reference: month-length weighted mean over all years, per field
ref, n = {v: 0. for v in MOLAR_MASS}, 0
for y in range(y0, y1 + 1):
    for m in range(12):
        with Dataset(f"{hist}/{case}.cam.h0.{y}-{m+1:02d}.nc") as d:
            for v in MOLAR_MASS:
                ref[v] = ref[v] + MDAYS[m] * d[v][0].astype("f8")
            lat = d["lat"][:]
        n += MDAYS[m]
area = np.cos(np.deg2rad(lat))[:, None] * np.ones((1, 144))
area *= 4 * np.pi * 6.371e6**2 / area.sum()          # m2 per cell

failed = False
print(f"{'field':14s} {'records':>7s} {'clim/h0':>12s} {'Tg/yr':>9s}")
for v in MOLAR_MASS:
    path = f"{ems_dir}/ems_{case}_{y0}-{y1}_{v}.nc"
    if not os.path.exists(path):
        print(f"{v:14s} MISSING {path}"); failed = True; continue
    with Dataset(path) as d:
        x, units = d[OUTPUT_VAR_NAME[v]][:].astype("f8"), d[OUTPUT_VAR_NAME[v]].units
    nrec = x.shape[0]
    clim = (np.tensordot(MDAYS, x, 1) / MDAYS.sum()) if v in MONTHLY_VARS else x.mean(0)
    kg = clim / (AVOGADRO / MOLAR_MASS[v] * 1e-4)        # back to kg/m2/s
    h0 = ref[v] / n
    ratio = (kg * area).sum() / (h0 * area).sum()
    tg = (kg * area).sum() * 365 * 86400 / 1e9
    ok = (nrec == (12 if v in MONTHLY_VARS else 17520) and units == "molecules/cm2/s" and abs(ratio - 1) < 1e-3)
    failed |= not ok
    print(f"{v:14s} {nrec:7d} {ratio:12.8f} {tg:9.2f}  {'PASS' if ok else 'FAIL'}")
sys.exit(1 if failed else 0)
