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
| `fbvoc-prescription-artefact/fbvoc_prescription_artefact.ipynb` | CTRL_PD `-20261023`, LCC_PD `-20261005`, LCC_PD_fBVOCctrlPD `-20261025` (2001–2014) + CTRL_PD_fBVOCctrlPD `-20261028` (2001–2002); old chain. Rerun automatically by `cases-scripts/run_when_done/run_when_done.sh` (nohup, login-3; finished 29 Oct) once the artefact run was archived |
| `fbvoc-prescription-artefact/fbvoc_artefact_causes.ipynb` (kept on the old chain on purpose, user 2026-11-02: PD, CTRL land only; note at the top) | Causes of the +3 % SOA artefact (H1–H5): CTRL_PD `-20261023`, CTRL_PD_fBVOCctrlPD `-20261028`, replay CTRL_PD_fBVOCctrlPD_HR `-20261029` (2001–2002); old chain. H5 verdict: the climatology is the cause (replay R = +0.49 % vs A = +3.03 %) |
| `fbvoc-prescription-artefact/how_big_artefact_is_PD.ipynb` | Does the artefact depend on the land cover? δ_PD = (LCC_PD_fBVOClccPD − LCC_PD) − (CTRL_PD_fBVOCctrlPD − CTRL_PD), BVOC effect design A vs B (2001–2002). New chain only (checks each file's casename against the auto-launcher's state). Pending until LCC_PD_fBVOClccPD (14e) is processed; rerun by hand |
| `FUT-fBVOC-background-lcc-effect-decomposition/bvoc_emissions_decomposition.ipynb` | CTRL_PD/FUT `-20260925`; LCC_FUT `-20261005`; LCC_FUT_fBVOCctrlPD_IM `-20261009`; 2001–2009 |
| `FUT-fBVOC-background-lcc-effect-decomposition/bvoc_expansion_PD_FUT_interaction.ipynb` | CTRL_PD/FUT `-20260925`; LCC_PD/FUT `-20261005`; 2001–2009 |
| `check-simulation-equilibrium/check_case_equilibrium-CTRL_{PD,FUT}.ipynb` | CTRL_PD/FUT `-20260925`; 2000–2009 |
| `check-simulation-equilibrium/check_CTRL_FUT_vs_LCC_FUT_vegetation_state.ipynb` | CTRL_FUT `-20260925`; LCC_FUT `-20261005`; old spin-ups; 2001–2009 |
| `check-simulation-equilibrium/check-CO2-bug-in-spinups/check_CO2_bug_in_land_only_six_variables.ipynb` | CTRL_PD/FUT `-20260925`; LCC_PD/FUT `-20261005`; old spin-ups; 2001–2009 |

**Paths, 2026-10-28.** The CTRL `-20260925` and `_IM` runs were moved on NIRD to `BRL-FRST-XPSN_archive/c-before-all-bvoc/`. The notebooks now read from there, and from NIRD instead of `/cluster/work`, which is purged. LCC `-20261005` was later extended to 2014, so the notebooks keep the nudged runs to 2000–2009: an `h0.200*` glob or a `NUDGED_YEARS` filter. The notebooks were **not rerun** after these path changes. The saved outputs are those of the original runs.

**Copies for the CO₂-fix chain (2026-10-28):** `other-BVOC-emission-magnitude/D1_farfield_check.ipynb` and `D2_megan_budget.ipynb` read the new 2000–2014 runs. D1 has the all-species BVOC contrasts (`ctrlPD`, `ctrlFUT`, `lccPD`) and Total = LCC − CTRL. The case names still marked `TODO` must be filled in once the runs are archived; until then the notebooks stop at step 1. They have not been run yet.

## MEGAN exact split (2026-10-29)

| Notebook | Runs read | What |
|---|---|---|
| `megan-exact-split-test/megan_patch_branch_5day_test.ipynb` | CTRL_PD `-20261023` (old chain) and its 5-day branch `…-test-meganpatch-5day-20261029` (2005-01-01 to 01-05) + LCC_PD `-20261005` 5-day branch with MEGAN-only output `…-test-meganpatch-5day-slim-20261029` (§6, passed) | go/no-go test of option 1 of `analysis/MEGAN_ATTRIBUTION.md`: bit-identity (240/240 steps identical), output fields, exact γ product, file size (216 GB per run-year), speed (4× slower) |
| `megan-exact-split-test/gamma_eff_vs_GAMMA_check.ipynb` (2026-11-02) | patch tape of the CTRL_PD 5-day branch `…-test-meganpatch-5day-20261029`; parent CTRL_PD `-20261023` h0 Jan 2005 (EPS check) | why γ_eff ≠ GAMMA in single-PFT cells (`megan_maps.py`): rebuilds CLM's grid averaging from patches. Mismatch = sub-dominant patches (weighting, expected); **bug: `f_valid` counts lake** (EPS missing on lake; γ_eff too low by > 5 % in 394/1733 land cells ≥ 45°N); cutoff minor. Fixed 2026-11-03 |
| `megan-exact-split-test/lake_fix_effect.ipynb` (2026-11-03) | processed lnd BVOC/ET/LAND of CTRL_PD, LCC_PD, CTRL_FUT, LCC_FUT (new chain), 2001–2014 | effect of the lake fix in `megan_maps.f_valid` on the attribution: composition +0.05 to +0.07 (100·Δln, ≥45°N), activity/residual/weighting −the same; locally up to 9.7 in 12 tundra cells. Negligible; old figures in `results/figures/megan_factors/before_lake_fix/` |

## How warm is FUT? (2026-10-30)

| Notebook | Runs read | What |
|---|---|---|
| `how-warmer-future-climate-is/how_warmer_future_climate_is.ipynb` | CTRL_PD `-20261029`, CTRL_FUT `-20261028` (new chain), 2001–2014; SST/sea-ice forcing files; NorESM2-LM CMIP6 `tas` (`/nird/datapeak/NS9034K/CMIP6`) | FUT − PD TREFHT/TS/PRECT by region and season (global +3.5 K, Arctic +8.9 K, LCC cells +7.5 K), prescribed SST/sea-ice/CO₂ differences, maps; FUT − PI estimate (+3.9 K global) = ours + NorESM2-LM CMIP6 historical r1–r3 PD − PI (1995–2005 − 1850–1900, +0.40 K) |

## Independence of the yearly differences (2026-11-02)

| Notebook | Runs read | What |
|---|---|---|
| `yearly-difference-autocorrelation/yearly_difference_autocorrelation.ipynb` | processed files 2001–2014, new chain (CTRL_PD `-20261029`, LCC_PD/CTRL_FUT/LCC_FUT `-20261028`, LCC_FUT_fBVOCctrlPD `-20261031`); `forcing_maps.budget_contrasts` | lag-1 autocorrelation of the 14 paired yearly differences (regional and cell-wise ≥45°N) vs white noise; trend vs memory; FDR with n_eff. Radiation/T/cloud ≈ white noise; emissions and SOA have trends. Rerun when LCC_PD_fBVOCctrlPD is processed |

## FUT vegetation state after the CO₂ fix (2026-11-02)

| Notebook | Runs read | What |
|---|---|---|
| `check-simulation-equilibrium/check_CTRL_FUT_vs_LCC_FUT_vegetation_state-after-co2-fix.ipynb` | new chain: shared FUT spin-up `-3`; land-only CTRL/LCC `-20261023`; coupled spin-ups `-20261025`; CTRL_FUT/LCC_FUT `-20261028`; 2001–2014 | new-chain twin of `check_CTRL_FUT_vs_LCC_FUT_vegetation_state.ipynb` (kept as the old-chain record) + §D paired test/FDR by region and old vs new. Unmodified land: ΔTLAI/TOTVEGC/TOTECOSYSC/GPP ≤ 0.15 % (old: −11 to −34 %); pools flagged by the paired test because their yearly Δ is persistent |

## Contrast maps: LCC effect, FUT emission source, PD → FUT (2026-11-03)

| Notebook | Runs read | What |
|---|---|---|
| `lcc-bvoc-background-contrast-maps/contrast_maps_uncorrected.ipynb` | processed files 2001–2014, new chain: CTRL_PD `-20261029`; LCC_PD, CTRL_FUT, LCC_FUT `-20261028`; LCC_PD_fBVOCctrlPD, LCC_FUT_fBVOC{ctrlPD,ctrlFUT,lccPD} `-20261031` | map grids (rows = contrasts, columns = radiation / BVOC→SOA→cloud / surface variables) for Q1 LCC effect in each background (6 contrasts), Q2 FUT BVOC emission source (4), Q3 PD → FUT (3); **raw differences, no artefact correction**; regional-mean table and additivity check of the contrast identities |

**Moved to the new chain (2026-11-03, user request):** `impact-of-nudging-on-land/impact_of_nudging_on_land.ipynb` now reads CTRL_PD `-20261029`, LCC_PD/CTRL_FUT/LCC_FUT `-20261028`, their coupled spin-ups (`-20261025/26`), MET and the shared spin-ups; 2001–2014. The old-chain version (CTRL `-20260925`, LCC `-20261005`, 2001–2009) is in git (commit `2f2e672`), its outputs in `impact_of_nudging_on_land_outputs/pre_co2_fix/`.
