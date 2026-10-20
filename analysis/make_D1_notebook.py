"""Generates D1_farfield_check.ipynb (kept as a script so the notebook is easy to regenerate).

Run from analysis/:  python make_D1_notebook.py
"""

import json


def md(s):
    return {"cell_type": "markdown", "metadata": {}, "source": s.splitlines(keepends=True)}


def code(s):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
            "source": s.splitlines(keepends=True)}


cells = [
md("""# D1 – Far-field check of the BVOC contrast

**Question.** Does the way the fBVOC runs are built contaminate the BVOC contrast `LCC − LCC_fBVOC`?

In `LCC_fBVOC` all interactive MEGAN emissions are off; only ISOP and MTERP are prescribed from CTRL_PD as a 2001–2009 climatology *(a, `prescribed_bvoc_emissions` in `cases-setup.sh`)*. The other MEGAN compounds (BCARY, methanol, acetone, CO, …) are **missing worldwide**. Their effect is not a land-cover effect.

**Test.** Far from the land-cover change (30°S–30°N, 90°S–30°S), the land-cover-driven BVOC signal should be ≈ 0. A clearly non-zero difference there measures the artifact. It is compared with the signal from the modified cells as **contributions to the global mean** (regional mean × area fraction), so both are on the same scale.

**Second use: the Total contrast.** The same test on `LCC − CTRL` measures anything other than the land cover that differs between the members. LCC and CTRL start from different land spin-ups *(a: LCC had an extra 100-yr land-only BGC spin-up, scripts 12b/22b; CTRL did not)*, so a far-field Total signal measures that offset.

**Tags:** (a) verified in source/files · (b) inference · (c) unverified

**Limits (b)**
- The artifact also exists inside the LCC region; D1 only measures it outside, and its size there may differ.
- Assumes the land-cover signal does not reach the far field. Plausible for aerosol and short-lived species, less so for O₃ (lifetime of weeks).
- The verdict threshold (ratio ≥ 0.2) is a convention, not a physical criterion.
"""),
code("""import sys
from pathlib import Path
import logging
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path.cwd().parent / "src"))   # repo src/, no pip install needed
from boreal_forest_expansion.analysis import farfield as ff
from boreal_forest_expansion.analysis import farfield_plots as fp

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
pd.set_option("display.width", 200, "display.max_columns", 30)"""),
md("""## Configuration

Raw monthly **h0** files from the archive: `<ARCHIVE>/<case>/atm/hist/<case>.cam.h0.YYYY-MM.nc` (they have `gw` and `time_bnds`). A pattern that matches two cases raises an error rather than mixing them.
"""),
code("""ARCHIVE = Path("/cluster/work/users/adelez/archive")
CASES = {
    "CTRL_PD":       "NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20260925",
    "LCC_PD":        "NF2000norbc_tropstratchem_nudg_lcc_f19_f19-20261005",
    "LCC_PD_fBVOC":  "NF2000norbc_tropstratchem_nudg_lcc_fBVOC_f19_f19-20261008",
    "CTRL_FUT":      "NF2100ssp585norbc_tropstratchem_nudg_ctrl_f19_f19-20260925",
    "LCC_FUT":       "NF2100ssp585norbc_tropstratchem_nudg_lcc_f19_f19-20261005",
    "LCC_FUT_fBVOC": "NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOC_f19_f19-20261009",
}
PATTERNS = {alias: str(ARCHIVE / case / "atm" / "hist" / f"{case}.cam.h0.*.nc") for alias, case in CASES.items()}

REPO = Path("/cluster/home/adelez/BOREAL-FOREST-EXPANSION")
MODIFIED_CELLS = REPO / "diagnostics/check-simulation-equilibrium/lcc-modified-cells/modified_cells.nc"
if not MODIFIED_CELLS.exists():          # the CSV in the repo has the same cells
    MODIFIED_CELLS = MODIFIED_CELLS.with_suffix(".csv")

SPINUP_MONTHS = 12        # first 12 months dropped (decision in the postprocessing work)
RATIO_THRESHOLD = 0.2     # far-field / modified-cells contribution above which the artifact "matters" (b)
FDR_ALPHA = 0.10          # Benjamini-Hochberg, Wilks (2016)
FIG_DIR = REPO / "results/figures/D1_farfield"
TABLE_DIR = REPO / "results/tables"
FIG_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)

CONTRASTS = [
    ff.Contrast("BVOC_PD",  "PD",  PATTERNS["LCC_PD"],  PATTERNS["LCC_PD_fBVOC"],  "LCC_PD − LCC_PD_fBVOC"),
    ff.Contrast("BVOC_FUT", "FUT", PATTERNS["LCC_FUT"], PATTERNS["LCC_FUT_fBVOC"], "LCC_FUT − LCC_FUT_fBVOC"),
]
TOTAL_CONTRASTS = [
    ff.Contrast("Total_PD",  "PD",  PATTERNS["LCC_PD"],  PATTERNS["CTRL_PD"],  "LCC_PD − CTRL_PD"),
    ff.Contrast("Total_FUT", "FUT", PATTERNS["LCC_FUT"], PATTERNS["CTRL_FUT"], "LCC_FUT − CTRL_FUT"),
]"""),
md("## Run"),
code("""res = ff.run_d1(CONTRASTS, str(MODIFIED_CELLS), spinup_months=SPINUP_MONTHS, ratio_threshold=RATIO_THRESHOLD)
res_tot = ff.run_d1(TOTAL_CONTRASTS, str(MODIFIED_CELLS), spinup_months=SPINUP_MONTHS, ratio_threshold=RATIO_THRESHOLD)
print(res.meta)
for r in (res, res_tot):
    for name, d in r.diffs.items():
        print(f"{name}: {d.attrs['label']}  |  {d.attrs['minuend']} − {d.attrs['subtrahend']}  |  years {int(d.year[0])}–{int(d.year[-1])} (n={d.sizes['year']})")
pd.concat([res.table, res_tot.table]).to_csv(TABLE_DIR / "D1_farfield_regional_stats.csv", index=False)
pd.concat([res.verdict, res_tot.verdict]).to_csv(TABLE_DIR / "D1_farfield_verdict.csv", index=False)"""),
md("""## Verdict

One row per contrast and term. Units: W m⁻², downward positive.
- `tropics_mean`, `tropics_ci_lo/hi`: 30°S–30°N mean difference and its 95% interval over years.
- `*_contrib`: contribution to the global mean.
- `ratio`: |far-field contribution| / |modified-cells contribution|.

| verdict | meaning |
|---|---|
| `none detected` | far field indistinguishable from 0 |
| `detected, small` | real but < 20% of the LCC-region contribution |
| `detected, MATTERS` | ≥ 20%: the artifact would distort the global BVOC term |
| `detected, no LCC signal` | the modified-cells signal itself is not significant, so the ratio is meaningless; judge by absolute size |
"""),
code("""cols = ["contrast", "term", "tropics_mean", "tropics_ci_lo", "tropics_ci_hi", "tropics_p",
        "tropics_contrib", "modified_cells_contrib", "ratio", "verdict"]

def show_verdict(verdict):
    v = verdict[cols].copy()
    return v.style.format({c: "{:.4f}" for c in cols[2:-2]} | {"ratio": "{:.2f}"}).apply(
        lambda r: ["font-weight: bold" if "MATTERS" in r.verdict else "" for _ in r], axis=1)

show_verdict(res.verdict)"""),
md("""**Second far-field region (90°S–30°S)** – an independent check. If the tropics and the southern extratropics agree, the far-field signal is unlikely to be noise or transport. `NH_45_90_rest` (unmodified cells north of 45°N) is the near field, reached by transport."""),
code("""regs = ["modified_cells", "NH_45_90_rest", "tropics", "SH_extratropics"]
sh = res.table[res.table.region.isin(regs) & res.table.band.eq("net")]
sh.pivot_table(index=["contrast", "component"], columns="region", values=["contrib", "ci_lo", "ci_hi"]).round(4)"""),
md("""## Figure 1 – contribution to the global mean: signal vs far field

Blue = modified cells (the BVOC signal you want). Orange/aqua = far field (artifact). If the orange bars are comparable to the blue ones, the BVOC contrast is contaminated at the global scale."""),
code("""fig = fp.plot_contributions(res.table)
fig.savefig(FIG_DIR / "D1_contributions.png", dpi=200, bbox_inches="tight")"""),
md("""## Figure 2 – maps of the time-mean BVOC contrast

Dots: cells significant after FDR control (α = 0.10, global test). Dashed: 30°S/30°N. Black contour: modified cells. Colour scale shared within each row (98th percentile of |Δ| outside the modified cells).

What to look for (b): a far-field signal from the missing compounds should be **spatially coherent** (e.g. over tropical forests, where those compounds are emitted most). Isolated dots are noise."""),
code("""TERMS = ["total_net", "cloud_SW", "clear_SW", "clear_LW"]
means, sigs = {}, {}
for name, d in res.diffs.items():
    means[name], sigs[name] = ff.mean_maps(d, TERMS, alpha=FDR_ALPHA)
fig = fp.plot_maps(means, sigs, TERMS, modified=res.regions["modified_cells"])
fig.savefig(FIG_DIR / "D1_maps.png", dpi=200, bbox_inches="tight")"""),
md("""## Figure 3 – year-by-year far-field means

A real artifact has the same sign every year; a drift suggests the members are still adjusting (e.g. prognostic LAI)."""),
code("""fig = fp.plot_yearly(res.diffs, res.weights, res.regions["tropics"],
                     periods={c.name: c.period for c in CONTRASTS})
fig.savefig(FIG_DIR / "D1_yearly_tropics.png", dpi=200, bbox_inches="tight")"""),
md("""## Total contrast (LCC − CTRL): spin-up offset

Here the far field should be zero if CTRL and LCC differ only in land cover. A detected far-field signal is the effect of the different land spin-ups (or other differences), not of the land cover."""),
code("""show_verdict(res_tot.verdict)"""),
code("""fig = fp.plot_contributions(res_tot.table)
fig.savefig(FIG_DIR / "D1_contributions_total.png", dpi=200, bbox_inches="tight")
means_t, sigs_t = {}, {}
for name, d in res_tot.diffs.items():
    means_t[name], sigs_t[name] = ff.mean_maps(d, TERMS, alpha=FDR_ALPHA)
fig = fp.plot_maps(means_t, sigs_t, TERMS, modified=res_tot.regions["modified_cells"])
fig.savefig(FIG_DIR / "D1_maps_total.png", dpi=200, bbox_inches="tight")"""),
md("""## How this decides step 2 (b)

| D1 outcome (net and cloud terms, both periods) | Step 2 |
|---|---|
| `none detected` or `detected, small` | Keep the current fBVOC runs. Add CTRL_FUT_fBVOC only to split BVOC_FUT into LCC and climate change |
| `detected, MATTERS` | Fix needed: **O1** (CTRL_PD_fBVOC + CTRL_FUT_fBVOC, subtract) as the cheapest robust option; **O2 + O3** (all species, year-specific files) if the fBVOC members must be clean on their own |
| Signal only in `clear_SW` / `clear_LW` | Points to ozone (or water vapour) from the missing compounds, not aerosol. Matters mainly for the chemistry level |
| Total far field detected | CTRL and LCC differ in more than land cover: fix the CTRL spin-up before O1 (the CTRL_fBVOC members would inherit it) |

Caveats when reading the result:
- In FUT the BVOC contrast is "LCC + climate change" by design (emissions prescribed from CTRL_PD). A far-field signal in FUT can therefore also come from the 2000→2100 change in ISOP/MTERP, not only from the missing compounds. Compare with PD: if the far field is non-zero in FUT but not in PD, the climate-driven ISOP/MTERP change is the likely cause (b).
- Nudged members share their weather, so the noise is small and even tiny signals can be "detected". That is why the verdict also uses the ratio.
"""),
]

nb = {"cells": cells, "nbformat": 4, "nbformat_minor": 5,
      "metadata": {"kernelspec": {"name": "lcc-env", "display_name": "lcc-env", "language": "python"},
                   "language_info": {"name": "python"}}}
with open("D1_farfield_check.ipynb", "w") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
print("wrote D1_farfield_check.ipynb")
