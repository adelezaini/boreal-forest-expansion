# Fixing the FUT land-only spin-up (CO₂ bug)

*2026-10-22. Status: proposal; nothing submitted yet.*
Evidence tags: **(a)** verified in files or output · **(b)** inference · **(c)** unverified.

## 1. Problem

The FUT LCC land-only spin-up (`22b`, case `I2100ssp585Clm50BgcCropCplHist_f19_f19-20260924`) ran 100 years with CLM at **pre-industrial CO₂**. All coupled FUT runs see about 1140 ppm (a).

| Stage | `CLM_CO2_TYPE` | CO₂ seen by CLM |
|---|---|---|
| FUT coupled spin-up (`…spinup_f19_f19-3`) | diagnostic | 1134 ppm |
| **FUT LCC land-only (22b)** | **constant** | **284.32 ppm** |
| CTRL_FUT, LCC_FUT (nudged) | diagnostic | 1142 ppm |
| PD land-only (12b) | constant | 367 ppm (consistent with PD coupled, 370 ppm) |

**Consequences** (a; LCC − CTRL, 2001–2009 means, % of CTRL):

| Region | Variable | PD (CO₂ correct) | FUT (CO₂ bug) |
|---|---|---|---|
| modified cells | TLAI | −1.3 | **−11.7** |
| modified cells | HTOP (canopy height) | +12.7 | **−0.9** |
| modified cells | TOTVEGC | +18.6 | **−11.3** |
| >45°N, unmodified | TLAI | +4.2 | **−17.8** |
| >45°N, unmodified | TOTVEGC | +15.4 | −35.5 |
| tropics 30°S–30°N | TLAI | +0.9 | −16.6 |
| tropics 30°S–30°N | TOTVEGC | +10.2 | −33.7 |

- **Collapse:** global TLAI in the LCC branch fell from about 2.5 to 0.95 within about 5 years of the land-only start (a).
  - **Recovery of leaf area:** after CO₂ was restored, it came back within about 10 years, but only to 12–17 % below CTRL.
  - **Recovery of carbon:** vegetation carbon would need about 160 more years to reach CTRL's level (b, exponential fit).
- **Short-term state:** in FUT the two members also differ. In the tropics, LCC is warmer at 1 m (TSOI +0.37 K, +6 × interannual SD) and stores more water (TWS +29 mm, +3.7 SD) (a). In PD, all short-term differences are within ±1.3 SD.
- **Consequence for the analysis (b):** LCC_FUT − CTRL_FUT mixes the land-cover signal with this vegetation damage, both inside the forest cells and far from them.

Notebooks with all figures and numbers:
- [check_CO2_bug_in_land_only.ipynb](../diagnostics/check-CO2-bug-in-land-only/check_CO2_bug_in_land_only.ipynb): lineage, consequences, recovery.
- [check_CO2_bug_in_land_only_six_variables.ipynb](../diagnostics/check-CO2-bug-in-land-only/check_CO2_bug_in_land_only_six_variables.ipynb): equilibrium of TWS, H2OSOI, TSOI, GPP, TOTVEGC, TOTVEGN.
- [impact_of_nudging_on_land.ipynb](../diagnostics/impact-of-nudging-on-land/impact_of_nudging_on_land.ipynb): the free → nudged jump; drift in both members.

## 2. Root cause

- **The forcing was right (a):** the cplhist files of `…spinup_f19_f19-3` contain the atmospheric CO₂ (`Sa_co2diag` ≈ 1134 ppm in `ha2x1d` and `ha2x3h`). The data atmosphere reads it: `datm.streams.txt.CPLHISTForcing.State3hr` maps `a2x3h_Sa_co2diag → co2diag`.
- **CLM ignored it (a):** with `CLM_CO2_TYPE = constant`, the default of the I compset, CLM uses the fixed value `CCSM_CO2_PPMV` and ignores any CO₂ coming from the atmosphere. Neither 12b nor 22b sets these variables.
- **PD was spared by coincidence (b):** the PD compset's default happens to be 367 ppm.
- **Why the equilibrium checks passed:** the earlier checks tested each run on its own, in the modified cells only, without TLAI. A run that is stable but in the wrong state passes such a test. The land-only TLAI is flat at 0.95 after year ~5.

## 3. Not affected

- **PD:** CO₂ correct in every stage. The 20- vs 140-year spin-up asymmetry remains: +4 % TLAI and +15 % TOTVEGC in unmodified >45°N.
- **Prescribed BVOC climatology:** built from CTRL_PD.
- **Nudging set-up:** all nudged runs, FUT included, are nudged to PD winds and PS (`met_nudge_only_uvps`, 6 h). This is by design and stays.
- **CTRL_FUT's CO₂:** correct (1142 ppm).

## 4. Fix options

| | A. Minimal (LCC only) | B. Symmetric (recommended if time allows) |
|---|---|---|
| Land-only | rerun 22b with correct CO₂ | 22a (CTRL, simyr2000 surfdata) **and** 22b (LCC) in parallel, identical set-up |
| Coupled spin-up | skipped: LCC nudged runs start from the new land restart (`finidat`) and the atmosphere of the existing `spinup_lcc` r.0021 | 20 yr for both: 23b (LCC) and a new CTRL coupled spin-up |
| Nudged reruns | LCC_FUT, LCC_FUT_fBVOC | CTRL_FUT, LCC_FUT, LCC_FUT_fBVOC |
| Removes CO₂ bug | yes | yes |
| Removes spin-up asymmetry | no (CTRL 20 yr vs LCC 120 yr) | yes |
| Rough cost (b) | land-only ~3 days + 2 × 10 nudged yr | 2 × land-only in parallel ~3 days + 2 × 20 coupled yr (~3 days each, in parallel) + 3 × 10 nudged yr |

- **Costs (b):** estimated from the script settings (land-only: 7 h wallclock per 10 yr; coupled: ~7 simulated years per day).
- **Option A, risk (c):** the nudged runs start from a land state that has never been coupled to this atmosphere. Only the first 12 months are discarded.
- **Option B, PD:** the same symmetric chain would also remove the PD asymmetry. That needs a PD CTRL land-only run, plus 13b and the PD nudged runs.

## 5. Script changes

| Script | Change | Status |
|---|---|---|
| `cases-setup.sh`: `clm_spinup_diagnostics`, `clm_long_spinup_diagnostics` | add `TSAI`, `HTOP` (canopy structure, albedo), `PCO2`, `PBOT` (the CO₂ CLM sees: PCO2/PBOT × 10⁶ = ppm), `FSNO`, `SNOWDP` (snow). The six equilibrium variables were already present (TOTVEGN and TWS added after the existing runs). | **done**, not committed |
| `22b-…landonly_spinup_lcc…` | CO₂: recommended `./xmlchange CLM_CO2_TYPE=diagnostic`, so CLM uses the cplhist CO₂ as in the coupled runs. The current uncommitted edit sets `constant` at 1137.78 ppm with a check on `lnd_in`; switch it to `diagnostic`. CASENAME gets `_lcc_`. | edit pending |
| `22a-…landonly_spinup_ctrl…` (new) | copy of 22b with the CTRL surfdata (`…simyr2000_c190304.nc`) and `_ctrl_` | created, not run (B only) |
| `23b-…spinup_lcc…` | `LAND_CASE` / `LAND_REFDATE` → new 22b run | after 22b |
| new CTRL coupled spin-up (e.g. `23c-…spinup_ctrl…`) | copy of 23b with CTRL surfdata and `finidat` from 22a | B only |
| `23a`, `24a`, `24b` | `REFCASE` / `REFDATE` → new spin-ups (A: `finidat` from 22b for 24a/24b) | after the spin-ups |
| `setup_nudging_data` | unchanged (PD winds for all) | — |

## 6. Before submitting each case

1. `./case.setup && ./preview_namelists`, then check `CaseDocs/lnd_in`:
   - `co2_type = 'diagnostic'` (land-only: also no fixed `co2_ppmv` overriding it);
   - correct `fsurdat` and `finidat`.
2. Land-only: check `CaseDocs/datm.streams.txt.CPLHISTForcing.State3hr` lists `a2x3h_Sa_co2diag co2diag`.
3. **Short test run (1 month)** of the land-only case: in the h0, `median(PCO2/PBOT) × 10⁶ ≈ 1134 ppm`. This is the check that would have caught the bug (c: not yet verified that `diagnostic` works with datm CPLHIST in this NorESM version; the test answers it).
4. `hist_fincl1` in `user_nl_clm` contains the new fields.

## 7. After the runs: acceptance checks

Update the case names in `STAGES` of the notebooks above and rerun them in place with `results/tables/logs/run_nb_inplace.py`.

| Check | Criterion |
|---|---|
| CO₂ table | every FUT stage ≈ 1134–1142 ppm |
| Short-term equilibrium at hand-over (TWS, H2OSOI, TSOI at 1 m) | ratio of the drift over a decade (last 10 yr) to the interannual SD ≲ 1 |
| Members agree outside the modified cells (2001–2009) | LCC − CTRL within ±2 interannual SD for TLAI, TSOI@1 m, TWS |
| Signal in the modified cells | HTOP and TOTVEGC change with the same sign as in PD |
| Nudged drift | trend of LCC − CTRL not significant for short-term variables (nudging notebook §5) |

## 8. Meanwhile: what can be analysed now

| Status | What |
|---|---|
| **safe** | All PD: Total_PD in the modified cells, BVOC_PD, D1/D2 PD. All code, pipelines and figure layouts for FUT. |
| **with caveat** | BVOC_FUT (LCC_FUT vs LCC_FUT_fBVOC share the same, damaged state). Total_PD far field (lineage asymmetry +4 % TLAI). TWS and snow at >45°N (drift differs between members). |
| **wait for reruns** | Any LCC_FUT − CTRL_FUT number (Total_FUT, local or far field). The FUT land-cover signal in MEGAN emissions and albedo. |

Put the case names in one config, so the reruns replace them without touching the analysis code. Label FUT figures "provisional (CO₂ bug)".

## 9. Open decisions

1. Option A or B; and whether to make PD symmetric too.
2. 22b: switch to `CLM_CO2_TYPE=diagnostic` (recommended) or keep `constant` at 1137.78 ppm.
3. Keep the new CASENAME suffixes (`_lcc_`, `_ctrl_`).
4. Whether to drop more than 12 months of the nudged runs for land variables. The nudging notebook shows the free → nudged jump is the same in both members, so it cancels in LCC − CTRL.
