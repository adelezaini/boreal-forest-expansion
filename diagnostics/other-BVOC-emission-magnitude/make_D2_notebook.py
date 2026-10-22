"""Generates D2_megan_budget.ipynb (kept as a script so the notebook is easy to regenerate).

Run from diagnostics/other-BVOC-emission-magnitude/:  python make_D2_notebook.py
"""

import json


def md(s):
    return {"cell_type": "markdown", "metadata": {}, "source": s.splitlines(keepends=True)}


def code(s):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
            "source": s.splitlines(keepends=True)}


cells = [
md("""# D2 – How big are the MEGAN emissions other than ISOP and MTERP?

The fBVOC runs switch MEGAN off and prescribe only ISOP and MTERP *(a)*. CAM receives biogenic VOC only through `megan_specifier` *(a, `chemistry.F90`)*, so in those runs the other 17 CAM species (BCARY, methanol, acetone, CO, …) have no biogenic source.

| Question | Why it matters | Measured as |
|---|---|---|
| **Q1** How large are the others' emissions overall? | Sets the size of the fBVOC artifact (what D1 sees in the far field) | Totals and shares in CTRL |
| **Q2** How much does the land-cover change alter them? | What an "ISOP + MTERP only" definition of BVOC misses | ΔE (LCC − CTRL) of the others vs of ISOP + MTERP |

**Three weightings**, because they answer different questions:

| Weighting | Units | Relevant for |
|---|---|---|
| mass | Tg yr⁻¹ | literature comparison |
| carbon | Tg C yr⁻¹ | **total** OH demand and CO/O₃ production once fully oxidised → global OH, CH₄ lifetime *(b)* |
| OH reactivity | Tmol(CO-eq) yr⁻¹ = moles × k_OH(T_ref) / k_OH(CO) | **instantaneous** OH demand near the source → local oxidants, SOA formation rate *(b)* |

Example: 1 Tmol of methanol has k_OH ≈ 9×10⁻¹³, i.e. 3.8× CO, so it counts as 3.8 Tmol(CO-eq). Isoprene (k ≈ 1×10⁻¹⁰) counts as ≈ 420 Tmol(CO-eq) per Tmol.

**Tags:** (a) verified in source/files · (b) inference · (c) unverified

**Limits (b)**
- Emissions are not impacts. D2 tells you how much material is involved; D1 tells you what removing it does to radiation.
- k_OH is evaluated at one temperature (T_ref, default 298 K). Boreal summer surface air is closer to 285–295 K. Set `T_REF` to test sensitivity; most rates change by < 15% between 280 and 298 K.
- Only ISOP and MTERP form SOA in your mechanism *(a)*. The others affect aerosol and clouds only through oxidants.
- **Spin-up offset (a):** LCC and CTRL start from different land spin-ups, so `global` and `tropics` ΔE contain an offset that is not caused by the land cover (largest in FUT). Read Q2 for `modified_cells` first.
"""),
code("""import sys
from pathlib import Path
import logging
import pandas as pd

sys.path.insert(0, str(Path.cwd().parents[1] / "src"))   # repo src/, no pip install needed
from boreal_forest_expansion.diagnostics import emissions as em
from boreal_forest_expansion.diagnostics import emissions_plots as ep
from boreal_forest_expansion.diagnostics import megan

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
pd.set_option("display.width", 200, "display.max_columns", 30, "display.float_format", "{:.4g}".format)"""),
md("""## Configuration

CLM h0 files: `<ARCHIVE>/<case>/lnd/hist/<case>.clm2.h0.*.nc`. Only the interactive members are needed (fBVOC runs have no MEGAN output).

Loading reads 46 `MEG_*` fields × 10 years per member; expect a few minutes per member."""),
code("""ARCHIVE = Path("/cluster/work/users/adelez/archive")
CASES = {
    "CTRL_PD":  "NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20260925",
    "LCC_PD":   "NF2000norbc_tropstratchem_nudg_lcc_f19_f19-20261005",
    "CTRL_FUT": "NF2100ssp585norbc_tropstratchem_nudg_ctrl_f19_f19-20260925",
    "LCC_FUT":  "NF2100ssp585norbc_tropstratchem_nudg_lcc_f19_f19-20261005",
}
CLM = {a: str(ARCHIVE / c / "lnd" / "hist" / f"{c}.clm2.h0.*.nc") for a, c in CASES.items()}
CAM_CTRL_PD = str(ARCHIVE / CASES["CTRL_PD"] / "atm" / "hist" / f"{CASES['CTRL_PD']}.cam.h0.*.nc")  # cross-check only

REPO = Path("/cluster/home/adelez/BOREAL-FOREST-EXPANSION")
MODIFIED_CELLS = REPO / "diagnostics/check-simulation-equilibrium/lcc-modified-cells/modified_cells.nc"
if not MODIFIED_CELLS.exists():
    MODIFIED_CELLS = MODIFIED_CELLS.with_suffix(".csv")
D1_TABLE = REPO / "results/tables/D1_farfield_regional_stats.csv"   # optional, for the scaling estimate

SPINUP_MONTHS = 12
T_REF = 298.0            # K, for k_OH
FIG_DIR = REPO / "results/figures/D2_megan_budget"
TABLE_DIR = REPO / "results/tables"
FIG_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)

MEMBERS_Q1 = {"CTRL_PD": CLM["CTRL_PD"], "CTRL_FUT": CLM["CTRL_FUT"]}
CONTRASTS = [
    em.EmissionContrast("LCC-CTRL_PD", CLM["LCC_PD"], CLM["CTRL_PD"], note="LCC, PD"),
    em.EmissionContrast("LCC-CTRL_FUT", CLM["LCC_FUT"], CLM["CTRL_FUT"], note="LCC only, 2100 climate"),
    em.EmissionContrast("LCC_FUT-CTRL_PD", CLM["LCC_FUT"], CLM["CTRL_PD"],
                        note="LCC + climate change: the emission change inside BVOC_FUT"),
]"""),
md("## Run"),
code("""res = em.run_d2(MEMBERS_Q1, CONTRASTS, str(MODIFIED_CELLS), spinup_months=SPINUP_MONTHS, T_ref=T_REF)
print({k: v for k, v in res.meta.items() if k != "missing_MEG"})
if res.meta["missing_MEG"]:
    print("WARNING - MEG_ fields missing (their groups are incomplete):", res.meta["missing_MEG"])
for name, t in [("totals", res.totals), ("q1", res.q1), ("q2", res.q2), ("q2_summary", res.q2_summary)]:
    t.to_csv(TABLE_DIR / f"D2_{name}.csv", index=False)"""),
md("""## Q1 – how large are the other compounds?

Mean annual totals and shares of all MEGAN emissions, CTRL members. Sanity check for the global mass totals: MEGAN2.1 in CLM is usually around 400–600 Tg yr⁻¹ isoprene and about 100 Tg yr⁻¹ each for monoterpenes and methanol *(c, order of magnitude from memory of Guenther et al. 2012; your model may differ)*."""),
code("""q1 = res.q1[res.q1.group.isin(list(megan.GROUPS) + ["ALL OTHERS", "ALL MEGAN"])]
q1.pivot_table(index=["member", "region", "group"], columns="weighting", values=["value", "share_pct"]).round(3)"""),
code("""for m in MEMBERS_Q1:
    fig = ep.plot_q1_shares(res.q1, m)
    fig.savefig(FIG_DIR / f"D2_Q1_shares_{m}.png", dpi=200, bbox_inches="tight")"""),
md("""## Q2 – how much does the land-cover change alter them?

Key columns:
- `others_over_ISOP_MTERP` = ΔE(all others) / ΔE(ISOP + MTERP). This is the part an ISOP/MTERP-only BVOC definition misses, relative to what it captures. A negative value means the others change in the opposite direction. Set to NaN when ΔE(ISOP + MTERP) is not distinguishable from 0 (e.g. isoprene down, monoterpenes up), because the ratio is then meaningless.
- `others_share_of_gross_change` = Σ|ΔE| of the other species / Σ|ΔE| of all species: robust to that cancellation. **Read this one first.**
- `f_others_changed` = ΔE(others) / E(others in the reference run): the fraction of the others' emissions that the land-cover change alters (used for the D1 scaling below).
- `others_ci_excludes_0`: whether ΔE(others) is distinguishable from zero over the years.

Regions: `modified_cells` is the local change; `global` and `tropics` also contain the spin-up offset between LCC and CTRL (see the limits above)."""),
code("""cols = ["dE_ISOP_MTERP", "dE_others", "others_share_of_gross_change", "others_over_ISOP_MTERP",
        "f_others_changed", "ISOP_MTERP_ci_excludes_0", "others_ci_excludes_0"]
s = res.q2_summary[res.q2_summary.region.isin(["global", "modified_cells", "tropics"])]
s.set_index(["contrast", "region", "weighting"])[cols]"""),
md("""LCC-only contrasts and the LCC + climate-change contrast are plotted separately: the second is usually much larger and would flatten the others on a shared axis."""),
code("""GROUPS_OF_CONTRASTS = {"LCC_only": ["LCC-CTRL_PD", "LCC-CTRL_FUT"], "LCC_plus_CC": ["LCC_FUT-CTRL_PD"]}
for gname, names in GROUPS_OF_CONTRASTS.items():
    for region in ("global", "modified_cells"):
        fig = ep.plot_q2_deltas(res.q2, names, region=region)
        fig.savefig(FIG_DIR / f"D2_Q2_deltas_{gname}_{region}.png", dpi=200, bbox_inches="tight")"""),
md("""Maps of the time-mean change in carbon emissions, north of 45°N. The two columns have separate colour scales (the others are usually much smaller). Black contour: modified cells."""),
code("""from boreal_forest_expansion.analysis.regions import load_modified_cells
ref = next(iter(res.maps.values()))
mod = load_modified_cells(str(MODIFIED_CELLS), ref)
fig = ep.plot_delta_maps(res.maps, modified=mod)
fig.savefig(FIG_DIR / "D2_delta_maps.png", dpi=200, bbox_inches="tight")"""),
md("""## Rough link to D1 *(b, order of magnitude only)*

D1's far-field signal is the effect of removing **100%** of the other compounds there. If the response is roughly linear in emissions, the effect of the land-cover-driven change of the others is about **f × artifact**, with f = `f_others_changed` (carbon weighting, modified cells — the global value contains the spin-up offset).

Caveats: the artifact is mostly tropical while the change is boreal, so the response per unit of emission may differ; the far-field artifact is a lower bound of the global artifact (it excludes the northern extratropics). In FUT the far field also contains the climate-driven ISOP/MTERP change, so the estimate is only meaningful for PD."""),
code("""if D1_TABLE.exists():
    d1 = pd.read_csv(D1_TABLE)
    far = (d1[d1.region.isin(["tropics", "SH_extratropics"]) & d1.term.eq("total_net")]
           .groupby("contrast")["contrib"].sum().rename("D1_far_field_artifact_Wm2"))
    sig = d1[d1.region.eq("modified_cells") & d1.term.eq("total_net")].set_index("contrast")["contrib"].rename("D1_modified_cells_Wm2")
    f = res.q2_summary.query("region == 'modified_cells' and weighting == 'carbon'").set_index("contrast")["f_others_changed"]
    f = f.rename({"LCC-CTRL_PD": "BVOC_PD", "LCC_FUT-CTRL_PD": "BVOC_FUT"})  # BVOC_FUT = LCC + climate change
    est = pd.concat([far, sig, f.rename("f_others_changed")], axis=1).dropna()
    est["est_effect_of_others_change_Wm2"] = est["f_others_changed"] * est["D1_far_field_artifact_Wm2"]
    display(est)
else:
    print(f"No D1 table at {D1_TABLE}: run D1 first for this estimate.")"""),
md("""## How to read the outcome *(b)*

| Q2: `others_share_of_gross_change` (carbon and OH reactivity) | Sign of ΔE(others) vs ΔE(ISOP+MTERP) | Meaning |
|---|---|---|
| small (< ~0.1) | any | An ISOP/MTERP-only BVOC definition misses little. **D1 alone decides** whether the fBVOC artifact must be removed (O1) |
| large | same | The others add to the BVOC signal. Use **O1** (includes all compounds, assuming linearity) or **O2** |
| large | opposite | The others partly cancel the ISOP/MTERP change. Important for the chemistry level; check D1 before choosing |

The 0.1 threshold is a convention *(b)*. Q1 (the others' share of total emissions) sets how large the D1 artifact can be, not whether the BVOC definition misses anything.

The OH-reactivity weighting is the more relevant one for local oxidants and SOA over the boreal region; the carbon weighting for the global OH budget and CH₄ lifetime.
"""),
md("""## Optional – CAM vs CLM cross-check

CAM's `MEG_ISOP`/`MEG_MTERP` (what the atmosphere actually received) against the CLM compounds summed per CAM species, in moles. They should agree closely *(b)*; a large mismatch would mean the CLM budget does not represent what CAM saw."""),
code("""em.cam_clm_crosscheck(CLM["CTRL_PD"], CAM_CTRL_PD, SPINUP_MONTHS)"""),
]

nb = {"cells": cells, "nbformat": 4, "nbformat_minor": 5,
      "metadata": {"kernelspec": {"name": "lcc-env", "display_name": "lcc-env", "language": "python"},
                   "language_info": {"name": "python"}}}
with open("D2_megan_budget.ipynb", "w") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
print("wrote D2_megan_budget.ipynb")
