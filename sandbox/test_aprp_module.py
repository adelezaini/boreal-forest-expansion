"""Check src aprp.aprp against the cloud-masking-aprp.ipynb cache (LCC_PD − CTRL_PD, 2001–2002)."""
import sys
from pathlib import Path

import numpy as np
import xarray as xr

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
from boreal_forest_expansion.analysis.aprp import aprp, aprp_parameters  # noqa: E402
from boreal_forest_expansion.plotting import forcing_maps as fm  # noqa: E402

Y0, Y1 = 2001, 2002
NEW, REF = "LCC_PD", "CTRL_PD"
VARS = ["SOLIN", "FSNTOA", "FSNTOAC", "FSNTC", "FSNTCDRF", "FSUTADRF", "FSDS", "FSNS", "FSDSC", "FSNSC",
        "FSDS_DRF", "FSUS_DRF", "FSDSCDRF", "SW_cloud"]


def read(alias):
    r = fm.open_class(alias, "RADIATIVE", Y0, Y1)
    bnds = [v for v in r.variables if "bnds" in v or "bounds" in v]
    c = fm.open_class(alias, "CLOUDPROP", Y0, Y1)[["CLDTOT"]]
    return xr.merge([r[VARS + bnds], c]).load()


d1, d2 = read(NEW), read(REF)
cache = xr.load_dataset(REPO / "analysis/cloud-masking-aprp_outputs/cache" / f"{NEW}__{REF}_clean_2001_2025.nc")
for fs in ("clean", "allsky"):
    t = aprp(d1, d2, fs)
    print(fs, "variables:", len(t.data_vars))
    if fs != "clean":
        continue
    worst = 0.0
    for k in cache.data_vars:
        y = fm.annual_mean(t[k], d2)
        ref = cache[k].sel(year=y["year"])
        diff = float(np.abs(y.astype("float32") - ref).max())
        worst = max(worst, diff)
        if diff > 1e-4:
            print(f"  {k}: max |diff| = {diff:.2e}")
    print(f"  clean: {len(cache.data_vars)} cached terms, max |module - cache| = {worst:.2e} W m-2")
p = aprp_parameters(d2, "clean")
print("parameters:", list(p.data_vars), "a_clr range", float(p.a_clr.min()), float(p.a_clr.max()))
