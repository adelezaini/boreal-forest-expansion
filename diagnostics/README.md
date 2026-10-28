# Diagnostics

## Notebooks run on the pre-all-BVOC runs

The notebooks below were run **before the fBVOC setup prescribed all 19 MEGAN species**. At that time:
- the fBVOC runs (`_IM`) prescribed only ISOP and MTERP; switching MEGAN off removed the other 17 species;
- the CTRL runs (`-20260925`) covered 2000–2009 and did not write the 30-min output of all species (`HR_BVOC_ALL`);
- all nudged runs covered 2000–2009 (first 12 months dropped → 2001–2009);
- all runs were on the old chain, before the CO₂ fix.

Their results describe those runs and are **not** results for the current setup.

| Notebook | Runs read (alias, case suffix, years) |
|---|---|
| `other-BVOC-emission-magnitude/D1_farfield_check_pre_co2_fix.ipynb` | LCC_PD/FUT `-20261005`; LCC_PD/FUT_fBVOCctrlPD_IM `-20261008/-20261009`; 2001–2009 |
| `other-BVOC-emission-magnitude/D2_megan_budget_pre_co2_fix.ipynb` | CTRL_PD/FUT `-20260925`; LCC_PD/FUT `-20261005`; 2001–2009 |
| `other-BVOC-emission-magnitude/other_bvoc_check{,_updated,_updated2}.ipynb` | CTRL_PD `-20260925`; LCC_PD `-20261005`; 2001–2009 (exploratory, superseded by D2) |
| `FUT-fBVOC-background-lcc-effect-decomposition/bvoc_emissions_decomposition.ipynb` | CTRL_PD/FUT `-20260925`; LCC_FUT `-20261005`; LCC_FUT_fBVOCctrlPD_IM `-20261009`; 2001–2009 |
| `FUT-fBVOC-background-lcc-effect-decomposition/bvoc_expansion_PD_FUT_interaction.ipynb` | CTRL_PD/FUT `-20260925`; LCC_PD/FUT `-20261005`; 2001–2009 |
| `check-simulation-equilibrium/check_case_equilibrium-CTRL_{PD,FUT}.ipynb` | CTRL_PD/FUT `-20260925`; 2000–2009 |
| `check-simulation-equilibrium/check_CTRL_FUT_vs_LCC_FUT_vegetation_state.ipynb` | CTRL_FUT `-20260925`; LCC_FUT `-20261005`; old spin-ups; 2001–2009 |
| `check-simulation-equilibrium/check-CO2-bug-in-spinups/check_CO2_bug_in_land_only_six_variables.ipynb` | CTRL_PD/FUT `-20260925`; LCC_PD/FUT `-20261005`; old spin-ups; 2001–2009 |
| `impact-of-nudging-on-land/impact_of_nudging_on_land.ipynb` | CTRL_PD/FUT `-20260925`; LCC_PD/FUT `-20261005`; MET; old spin-ups; 2001–2009 |

**Paths, 2026-10-28.** The CTRL `-20260925` and `_IM` runs were moved on NIRD to `BRL-FRST-XPSN_archive/c-before-all-bvoc/`. The notebooks now read from there, and from NIRD instead of `/cluster/work`, which is purged. LCC `-20261005` was later extended to 2014, so the notebooks keep the nudged runs to 2000–2009: an `h0.200*` glob or a `NUDGED_YEARS` filter. The notebooks were **not rerun** after these path changes. The saved outputs are those of the original runs.

**Copies for the CO₂-fix chain (2026-10-28):** `other-BVOC-emission-magnitude/D1_farfield_check.ipynb` and `D2_megan_budget.ipynb` read the new 2000–2014 runs. D1 has the all-species BVOC contrasts (`ctrlPD`, `ctrlFUT`, `lccPD`) and Total = LCC − CTRL. The case names still marked `TODO` must be filled in once the runs are archived; until then the notebooks stop at step 1. They have not been run yet.
