"""Design test of the cloud-type figures (new section 3 of analysis/bvoc-soa-cloud-interactions.ipynb).
Writes only to sandbox/test_cloud_types_outputs/. Run from the repo root: PYTHONPATH=src $PY sandbox/test_cloud_types.py"""
from dataclasses import replace
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from boreal_forest_expansion.plotting.style import set_default_style
from boreal_forest_expansion.plotting import forcing_maps as fm

set_default_style()
OUT = Path(__file__).parent / "test_cloud_types_outputs"
S, E = 2001, 2014
JJA = fm.SEASONS["JJA"]

# sanity: regional CTRL_PD means >= 45N
ds = fm.open_class("CTRL_PD", "CLOUDPROP", S, E)
mask = fm.region_masks(ds)["≥45°N"]
means = {v: float(fm.regional(fm.yearly_field(ds, v), ds, mask).mean()) for v in ("CLDTOT", "CLDLOW", "CLDMED", "CLDHGH")}
print("CTRL_PD ≥45°N annual means:", {k: round(v, 3) for k, v in means.items()})
assert all(0 <= v <= 1 for v in means.values()) and means["CLDTOT"] >= max(means.values()) - 1e-9

for cset in fm.contrast_sets():
    for tag, panels in (("", fm.CLOUD_TYPE_PANELS),
                        ("_JJA", [replace(p, months=JJA, title=f"{p.title} (JJA)") for p in fm.CLOUD_TYPE_PANELS])):
        fig, _ = fm.make_contrast_grid_figure(cset, panels, f"cloud_types{tag}", start_year=S, end_year=E, figdir=OUT)
        plt.close(fig)

FIELDS = ["CLDLOW", "CLDMED", "CLDHGH", "TGCLDLWP", "TGCLDIWP", "SW_cloud"]
REGIONS = ["≥45°N", "modified cells"]
COL = {"PD": "#3b75af", "FUT": "#c44e52"}
for label, role in (("LCC − LCC_fBVOC", "fbvoc"), ("LCC − CTRL", "ctrl")):
    lines = {f"{p}: {r['lcc']} − {r[role]}": (r["lcc"], r[role], COL[p], "-") for p, r in fm.BVOC_PAIRS.items()}
    fig, _ = fm.make_monthly_chain_figure(FIELDS, REGIONS, lines, f"seasonal_cloud_types_{role}",
                                          f"Seasonal cloud-type change, {label} (mean ± 95 % CI)",
                                          start_year=S, end_year=E, figdir=OUT)
    plt.close(fig)

for season, months in (("ANN", None), ("JJA", JJA)):
    fig, _ = fm.make_cloud_profile_figure(months=months, season=season, start_year=S, end_year=E, figdir=OUT)
    plt.close(fig)
