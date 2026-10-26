# Claude log

Working memory across Claude Code sessions. **Read NOW first; read older blocks only if needed.**
**Evidence tags:** **(a)** verified in source, scripts, files or output · **(b)** inference · **(c)** unverified.
User preferences: short labelled sections, tables, bold key terms, worked examples; be critical,
separate facts from inference; never assume variables that look alike are equivalent.
Protocol: hook `~/.claude/hooks/boreal_log.py` injects NEW/CONTINUE BLOCK each prompt. NOW = overwritten every turn.
Blocks = one per prompt-cache window (new session or >60 min gap), newest first, rewritten in place within the window.
Human twin: `docs/CLAUDE_log_human.md`.

---

## NOW (overwrite every turn)
- **Session 7648e6ae (22:47–00:38): new analysis notebooks + HYDRO category (a).** `analysis/forcing_maps.ipynb` git-rm'd → split into `analysis/radiative_forcing.ipynb` (6-panel moved; 12 Ghan per contrast `{PD,FUT}_ghan_{LCC-CTRL,LCC-fBVOC}_{NET,SW,LW}_2001_2009.png`; 12 seasonal `…_ghan_seasonal_…`), `analysis/bvoc-soa-cloud-interactions.ipynb` (context maps moved; `contrast_grid_context_{LCC-CTRL,LCC-fBVOC}`), `analysis/biogeophysical-hydro.ipynb` (`contrast_grid_{hydro,snow_albedo,surface_energy,fsds_split}_*`, `water_budget_*`, table `results/tables/water_budget_2001_2009.csv`). All 3 run in place, exit 0, 0 error cells. Moved 8 PNGs pixel-identical to `results/figures/first-round/` (user moved old ones there 23:13). Ghan closure ≤2.2e-5 W/m2 (60 checks). Grids: rows = contrasts (LCC-CTRL: PD−CTRL_PD, FUT−CTRL_FUT, FUT−CTRL_PD; LCC-fBVOC: PD, FUT), cols = vars, own cbar per panel; Ghan figs one shared scale (per row for seasonal; DJF = J+F+D same year).
  Code `forcing_maps.py`: MapPanel.months, `annual_mean(months=)`, SEASONS, YEARLY_DERIVED lambdas now (ds, months), new derived PRECT_mmday/QRUNOFF_mmday/QSNOMELT_mmday/SNOW_PERSISTENCE_days/ALBEDO(FSR/FSDS)/BOWEN/FSDS_cloud/FSDS_aer, `panel_difference`, `_plot_panel(d=)`, `ghan_panels`, `make_ghan_figure(seasonal=)`, `contrast_sets()`, `make_contrast_grid_figure`, HYDRO/SNOW_ALBEDO/SURFACE_ENERGY/FSDS_SPLIT_PANELS, `water_budget_table`, `make_water_budget_figure`. `variables.py` lnd **HYDRO** (17 vars). Postprocessed 6 × `<ALIAS>_lnd_HYDRO_2001-2009.nc` with OLD casenames (CTRL -20260925; run_postprocess.py directly with absolute --raw-path/--out-path: defaults are relative to cwd postprocess/), ~5 min each; QRUNOFF processed == raw (LCC_PD 2005-07). These belong to the 2001-2009 set → move with it to 2001-2009-pre-co2-fix/.
  Water budget (2002–2009, 8 yr; ΔTWS Dec-to-Dec): modified cells residual −1.1 PD / −10.9 FUT mm/yr; unmodified ≥45N PD **+27.7** (≈5 % P; Greenland ice runoff QSNWCPICE/QICE not in HYDRO, (b) unchecked). Ice runoff done, see update. README `analysis/README.md` written; CLAUDE.md layout row + HYDRO in category list. All UNCOMMITTED.
  **Update 23:40–00:0x (a):** LCC-CTRL contrast set now 4 rows (+ CTRL_FUT − CTRL_PD; `contrast_sets()` in forcing_maps.py) → all LCC-CTRL grids + water-budget chart. HYDRO extended (+QSNWCPICE, QSNOCPLIQ, QICE(_FRZ/_MELT), QRUNOFF_TO_COUPLER, QRUNOFF_ICE_TO_COUPLER, QFLX_LIQ/ICE_DYNBAL); old HYDRO files moved to scratchpad hydro_v1/, all 6 regenerated (exit 0). Water budget now R_liq = QRUNOFF_TO_COUPLER, R_ice = QRUNOFF_ICE_TO_COUPLER → residual |·| < 1 mm/yr in every run/region (was +27.7 unmod ≥45N PD with QRUNOFF). Hydro + BVOC nbs rerun, 0 errors. Radiative nb not rerun (unaffected).
  **DONE 00:40 (a): `analysis/pd-fut-attribution.ipynb`** (A–F, run in place, 0 errors; findings md cell 2). New fm functions: region_masks/region_weights/regional/cell_area (gw-based, sums to 4πR²), MONTHLY_FIELDS, monthly_regional/monthly_difference (Tg/month spot check = hand calc to 1e-15), radiative_budget_table (closure Ghan 1e-7, contrasts 4.4e-4), summarize_years, make_radiative_budget_figure, make_paired_years_figure, make_emission_origin_figure, make_monthly_chain_figure, baseline_table, make_percent_change_figure; GHAN_CONTRASTS += fbvoc_ctrl → radiative_forcing.ipynb rerun (18 annual + 18 seasonal Ghan figs, 90 closures ≤2.2e-5, 0 errors). Figures: radiative_budget_3contrasts, emission_origin_monthly, seasonal_chain_bvoc_soa_cloud_sw, bvoc_percent_change_maps, paired_years_{NET,SW,LW}, pd_mechanism_source_boxes (all _2001_2009.png); tables results/tables/{radiative_budget_3contrasts(_yearly),emission_origin_annual,baseline_aerosol_cloud}_2001_2009.csv.
  **00:56 (a):** `contrast_sets()` += "fBVOC-CTRL" [(LCC_PD_fBVOC, CTRL_PD), (LCC_FUT_fBVOC, CTRL_FUT)] → 5 new grids `contrast_grid_{context,hydro,snow_albedo,surface_energy,fsds_split}_fBVOC-CTRL_2001_2009.png` + `water_budget_fBVOC-CTRL_2001_2009.png` (residuals |·|<0.7 mm/yr); bsc + bgh nbs rerun, 0 errors, 0 skipped panels. ≥45N fBVOC−CTRL: PD N_AER +26 cm⁻³, SOA +0.04 mg/m2 (emissions ~0); FUT SOA −2.4, N_AER −183, droplets −3.2, LWP −3.2 g/m2, radius +0.45 µm.
  Findings ≥45N NET: FUT LCC−CTRL +0.27 = fBVOC−CTRL +0.97 (cloud +1.05) + LCC−fBVOC −0.70 (cloud −0.83); PD +0.24 = +0.12 (clrcln +0.31, cloud −0.19) + 0.13. Albedo proxy fBVOC−CTRL PD/FUT +0.46/+0.41 → not the cause. FUT LCC−fBVOC emissions +7.4 ISOP/+15 MTERP Tg/yr modified cells vs LCC−CTRL −0.2/−1.2 → BVOC_FUT ≈ FUT-vs-PD emission reference (b). LCC_FUT−CTRL_FUT LAI deficit in unmodified land, early≈late (no recovery). PD: emission Δ identical in LCC−fBVOC and LCC−CTRL, but SOA/N_AER lower only in LCC−fBVOC, also in winter → setup offset (b: missing non-terpene MEGAN compounds in fBVOC), not precursor timing. NUCLRATE units label blank (file attr empty?) – cosmetic.
- **Session 3b25e01e (22:10–23:05): AUTO-LAUNCHER RUNNING (a).** User OK 22:54: launch 13c after 12c, and nudged runs after the coupled spin-ups with corrected restarts. `cases-scripts/auto_launch_new_chain.sh` started 22:57 on **login-3** (nohup setsid, pid 3659097), polls 900 s; state/logs `/cluster/work/users/adelez/auto-launch/` (launch.log, launch_<NN>.log, rsync_<case>.log, <step>.done/.failed, 13c.case). Branches: A 12c `I2000…ctrl…-20261025` (rest 0101-01-01) → rsync to NIRD → 13c → 13c done (0021-01-01) → rsync → 13a REFCASE=13c case; B 13b → 14a; C 23c → 23a; D 23b → 24a (REFCASE = `…spinup_{lcc,ctrl}_f19_f19-20261025`, REFDATE 0021-01-01 checked). Done = no squeue job with workdir = realpath caseroot (/cluster/projects/…) + RESUBMIT 0 + last CaseStatus st_archive success + archive rest/<date>/*.r.*; else FAILED → branch halted (remove .failed + restart to retry). Tested (a): --check → 4 RUNNING; finished cases → DONE; wrong date → FAILED; set_refcase on scratch copy of 14a OK. Case scripts are NOT yet edited (watcher edits at launch). Bugs fixed during test: ~/cases symlink vs squeue %Z; CaseStatus says 'st_archive' not 'case.st_archive'. NOT automated: fBVOC on new chain (needs new CTRL nudged → climatology → EMS_* in 14c/24c/24d) — asked user. ETA (b): 13b/23b/23c 20 yr ≈ 2.5–3 d from 15:15 → ~10-28; 12c ≈03:30 10-26 → 13c → ~10-29; nudged +~2 d. Earlier this block: climatology move rule, CTRL_FUT base files to shared, 76 work copies deleted, no `_IM` rename / pre-co2-fix archive plan (CLAUDE.md step 2). Uncommitted: CLAUDE.md, forcing_maps.py comment, logs, run_nb_inplace.py, auto_launch_new_chain.sh, cases-scripts/README.md.
- **Session af52cc01 (21:28–21:35):** `check-land-only-equilibrium-after-co2-fix/check_land_only_equilibrium_after_co2_fix.ipynb`: REGIONS = modified cells / global land / tropics (>45N unmodified dropped); PD_LCC_old removed from RUNS, FUT_LCC_old_bug renamed FUT_LCC_old (cache file renamed, PD_LCC_old cache deleted); RUNS order PD_LCC, FUT_LCC, FUT_CTRL + `LW={'FUT_CTRL':0.5}` so FUT_CTRL is drawn thin on top (it was hidden: identical to FUT_LCC outside modified cells). Re-run in place, all cells OK (a). New: ratio_cycle max 0.155 (TWS global FUT), 27/27 eq; OLS flags 11/27; global-land Δ FUT_LCC−CTRL TLAI −1.0 %, TOTVEGC +0.7 %, HTOP +1.4 %. Summary md updated. Backup scratchpad bak_landonly_eq.ipynb.
- **Session dc9990de (21:17–21:25): run tables (a).** Queue 21:17: 13b 1780140, 23b 1780136, 23c 1780137 running 6 h; 12c `I2000…_ctrl_…-20261025` segment 5/10 (1780375, RESUBMIT 5, 10 yr/segment ~1h22 → done ≈03:30 10-26 (b)); NEW since 17:11 (other session): 14c `NF2000…nudg_lcc_fBVOCctrlPD_…-20261025` 1780293, 24c `NF2100…lcc_fBVOCctrlPD_…-20261025` 1780317, 24d `NF2100…lcc_fBVOCctrlFUT_…-20261025` 1780312 (1-day tests 17:11–17:41 COMPLETED). Previous round (10-23→10-25): 12b/22b/22c land-only, 13a/23a CTRL 15 yr, 14a/24a 2014 reruns, all COMPLETED.
- **Session dc6addbf (2026-10-25 16:15–16:16):** user ran `git add diagnostics/check-simulation-equilibrium/*`; only `__pycache__` refused (gitignored, correct). Index now 200 staged files (incl. renames equilibrium_outputs/→*_outputs/, D1/D2, BVOC dirs from earlier `git add`s) (a). Not committed.
- **Session dc9990de (2026-10-25 16:12–16:20): status query (a).** RUNNING since 15:15–15:16: 12c PD CTRL land-only `I2000Clm50BgcCropCplHist_ctrl_f19_f19-20261025` run 1780142 (7 h limit)/arch 1780143; 13b `NF2000…spinup_lcc_f19_f19-20261025` 1780140/1780141; 23b `NF2100…spinup_lcc_…-20261025` 1780136/1780139; 23c `NF2100…spinup_ctrl_…-20261025` 1780137/1780138. **bvoc-clim arrays 1780158 (CTRL_PD `…nudg_ctrl_…-20261023` 2001–2014) + 1780159 (CTRL_FUT same) submitted 16:12 by another session: all 38 tasks FAILED in <10 s** — `$PY` (NIRD lcc-env python) 'No such file' on preproc nodes b5201/b5202 (exists on login node) → NIRD likely not mounted on preproc (b). Not touched; logs `/cluster/work/users/adelez/bvoc-emissions/logs/bvoc-clim_178015[89]_*.out`.
- **Session af52cc01 (14:45–14:50):** `diagnostics/check-simulation-equilibrium/check_CTRL_FUT_vs_LCC_FUT_vegetation_state.ipynb` REGIONS reduced to global land / modified cells / all unmodified land (tropics + NH>30N unmodified dropped; unused LAT removed); C_REGIONS = list(REGIONS). Re-run in place (run_nb_inplace.py), all cells OK; CSV/PNG in equilibrium_outputs/CTRL_FUT_vs_LCC_FUT/ overwritten. Summary md (cell 15) tables now global/modified/unmodified; drift table → all unmodified land (TOTVEGC CTRL_FUT +4.3, LCC_FUT +11.4 %/dec). Backup: scratchpad bak_vegstate_regions.ipynb.
- **Session 0521733a (2026-10-25 14:38–15:31): all diagnostics outputs now `<notebook_stem>_outputs/`, .nc caches in `…_outputs/cache/` (a).** Rule in `CLAUDE.md` § Code conventions; `.gitignore` += `**/cache/` (no tracked file was under any cache/). Plain `mv` (no git mv: 81 tracked files under old equilibrium_outputs/ + D1/D2 now show as deleted + untracked; `git add -A` will pair them as renames).
  Map 14:4x: impact-of-nudging-on-land `outputs/`→`impact_of_nudging_on_land_outputs/`; FUT-fBVOC… `bvoc_emissions_decomposition/`, `bvoc_expansion_PD_FUT_interaction/` → `+_outputs/`; check-CO2-bug-in-land-only `outputs/`→`check_CO2_bug_in_land_only_outputs/`, `outputs_six/`→`check_CO2_bug_in_land_only_six_variables_outputs/`; after-co2-fix `outputs/`→`check_land_only_equilibrium_after_co2_fix_outputs/`.
  Map 15:2x: `check-simulation-equilibrium/equilibrium_outputs/<CASE>/` → `check_case_equilibrium-<X>_outputs/` (6 nbs, `OUTPUT = Path('<stem>_outputs')`, CASE level dropped); `equilibrium_outputs/CTRL_FUT_vs_LCC_FUT/` → `check_CTRL_FUT_vs_LCC_FUT_vegetation_state_outputs/` (+cache/ for 5 annual_*.nc); `equilibrium_outputs/` removed (empty). D1 `D1_farfield/`→`D1_farfield_check_outputs/`, D2 `D2_megan_budget/`→`D2_megan_budget_outputs/` (FIG_DIR/TABLE_DIR edited; CLAUDE.md:21,91 repointed).
  MASK_FILE fixed in both check-CO2 nbs → `../lcc-modified-cells/modified_cells.nc`.
  Verified (a): re-run in place, exit 0, 0 error cells, caches read (mtimes unchanged): impact_of_nudging_on_land, check_CO2_bug_in_land_only, check_CTRL_FUT_vs_LCC_FUT_vegetation_state. Veg-state A/B/C csv differ from HEAD only through the 5→3 region reduction done earlier on 10-25 (not this session). Not re-run: six_variables, after-co2-fix, BVOC ×2, 6 case-equilibrium nbs, D1/D2 (static path check only).
  Not moved (deliberately): `lcc-modified-cells/modified_cells.nc` (input mask, ~12 users); `check-spinup-equilibrium-uncomplete/backup/sandbox/cam_spinup_dataset.nc` (legacy).
  16:05–16:24: user asked to re-run the 3 again. Veg-state HEAD vs now: all shared (region,variable) rows identical (max diff 0, A 12 / B 9 / C 9 rows); only `NH >30N unmodified` + `tropics 30S-30N` dropped (a). Full CACHE-REBUILD rerun (caches set aside, recomputed from archive; sequential): veg 523 s, impact 279 s, CO2 153 s, all exit 0, 0 error cells, outputs saved in nbs (a). Rebuilt caches bit-identical to old (24 files, same years/vars, max abs diff 0) (a); veg tables after rebuild still = HEAD on shared rows (a). cache_old deleted.
- **Session 035c87f8 (2026-10-25 14:16): ALL RUNS DONE (a).** Queue empty; every job since 10-23 17:00 COMPLETED; CaseStatus case.run + st_archive success, RESUBMIT 0.
  Land-only (archive `/cluster/work/users/adelez/archive/<case>`, rest up to 0101-01-01): PD LCC `I2000…_lcc_…-20261023`, FUT CTRL `I2100…_ctrl_…-20261023`, FUT LCC `I2100…_lcc_…-20261023`. CO2 yr1→yr101 h0: 369/1135/1135 ppm; unweighted TLAI 1.05→1.07, 1.89→1.95, 1.88→1.93.
  Nudged: LCC_PD/LCC_FUT ext (`…nudg_lcc_…-20261005`) 2014 reruns OK (cam.h0 180 files 2000-01…2014-12, rest 2015-01-01) → met-file patch worked. CTRL_PD/CTRL_FUT 15-yr (`…nudg_ctrl_…-20261023`) done: cam.h0 180, cam.h1 5476 files, atm/hist 45 GB each, rest 2015-01-01.
  14:3x user: (1) 1775779 = original LCC_PD ext job that crashed on met end; superseded by 1777448 (OK). (2) CO2 nbs moved by user to `diagnostics/check-simulation-equilibrium/check-CO2-bug-in-land-only/` → their MASK_FILE `../check-simulation-equilibrium/lcc-modified-cells/…` now resolves wrong (should be `../lcc-modified-cells/…`); not fixed.
  **Equilibrium nb DONE (a):** `diagnostics/check-simulation-equilibrium/check-land-only-equilibrium-after-co2-fix/check_land_only_equilibrium_after_co2_fix.ipynb` (run in place, summary filled; `check_land_only_equilibrium_after_co2_fix_outputs/` CSV+PNG; builder throwaway scratchpad). Forcing loops cplhist yrs 11–20 (DATM_CPLHIST_YR_START/END, 10-yr cycle) → main test = mean(91–100) − mean(81–90) / IAV: 27/27 short-term < 1 (max 0.27 TWS >45N FUT). OLS last-10-yr flags 10/27 → aliased by forcing cycle (b: earlier nbs' OLS ratios pessimistic). Carbon +0.3–0.9 %/cycle. FUT_LCC−FUT_CTRL exactly 0 outside modified cells.
  **Scripts (a, bash -n OK, UNCOMMITTED):** LAND_CASE → 13b `I2000…_lcc_…-20261023`, 23b `I2100…_lcc_…-20261023`, 23c `I2100…_ctrl_…-20261023`; 13c still placeholder (no 12c).
  **NIRD copy DONE 14:45 (a):** save-archived-case-to-boreal for the 3 land-only cases, rsync exit 0, sizes match (5.0/4.6/4.6 G), rest/0101-01-01-00000 13 files each (.nc.gz; prepare_restart_files gunzips into ~/restart; home 10.4/20 GiB, 93.9k/100k files).
  Nb outputs moved to new CLAUDE.md rule: `check_land_only_equilibrium_after_co2_fix_outputs/` (+ `cache/` annual_*.nc); nb re-run in place, same verdict (a).
  **13b/23b/23c SUBMITTED 15:15, RUNNING (a):** cases `NF2000…spinup_lcc_f19_f19-20261025` run 1780140/arch 1780141; `NF2100…spinup_lcc_f19_f19-20261025` 1780136/1780139; `NF2100…spinup_ctrl_f19_f19-20261025` 1780137/1780138. CaseDocs/lnd_in finidat = new land-only r.0101 (lcc/lcc/ctrl), fsurdat LPJGUESS/LPJGUESS/simyr2000 (a). 20 yr each (5+3×5).
  Pending user: 12c/13c decision (answered pros/cons, user leans no).
- **Session 0ec901d3 (18:44–18:55):** `bvoc_expansion_PD_FUT_interaction.ipynb` §9 maps: SCALE_MODE "grouped" (default; PD own scale, FUT+Interaction shared), SCALE_QUANTILE 1.0→0.98; md cells 18+22 updated. Re-run in place, all cells OK (a). New PNGs `*_interaction_continuous_grouped.png`; old `*_shared.png` + 17:53 `*_expansion_interaction_maps.png` are stale leftovers (not deleted). Annual 98 % limits ISOP: PD 0.21, FUT/Int 1.07; MTERP 0.22 / 1.84 mg m⁻² d⁻¹ (a). Backup: scratchpad bak_interaction.ipynb. bvoc_emissions_decomposition.ipynb maps NOT changed (its §9b row scale uses max of Background/Expansion/…; narrow-scale expansion map cell 27 already exists).
- **Session 0ec901d3 (18:30–18:35):** `diagnostics/check-simulation-equilibrium/check_CTRL_FUT_vs_LCC_FUT_vegetation_state.ipynb` §B maps: dots on p<0.05 → grey `/////` hatching (lw 0.3, dimgrey) on NON-sig land cells (Welch p≥0.05, no FDR), inlined (nb self-contained, no src import); md cell 10 + titles updated. Re-run with run_nb_inplace.py, all cells OK, outputs saved (a). Tables unchanged (same code). Backup: scratchpad bak_vegstate.ipynb.
- **Session e2a259e9 (17:43–17:55): BVOC emissions notebooks merged + interaction nb run.** `diagnostics/FUT-fBVOC-background-lcc-effect-decomposition/` now holds only 2 nbs (a): `bvoc_emissions_decomposition.ipynb` (= old followup nb [which contained all of three_regions] + 3-comparison maps (§9b) + old conclusions (§10); OUT `bvoc_emissions_decomposition/`, RUN_MAPS=True) and `bvoc_expansion_PD_FUT_interaction.ipynb` (LCC_PD path set to `…nudg_lcc_f19_f19-20261005`, RUN_MAPS=True, results md cell added). Deleted: followup + three_regions nbs, their output dirs, .ipynb_checkpoints. Both executed in lcc-env kernel via nbconvert, outputs saved, no errors; all closure asserts pass (a). Merged nb reproduces old table: all-north Background +12.99/+25.45, Expansion −2.61/−3.85 Tg/yr ISOP/MTERP (a).
  Interaction (≥45°N, 2001–2009, Tg/yr) (a): Expansion PD +0.43 ISOP / +0.18 MTERP (9/9 yrs >0); Expansion FUT −2.61/−3.85 (9/9 <0); Interaction −3.04/−4.03. FUT decrease mostly in UNMODIFIED cells (ISOP 92 %, MTERP 69 %) → vegetation-induced environmental response in FUT background (b); mechanism §14 (RUN_MECHANISMS) not run.
  18:05 (a): §13–17 were off only because the original nb had no data access (inputs None). Now filled: RUN_MECHANISMS=True (TREFHT, FSDS from CAM; TV, TLAI from CLM lnd/hist), SURFDATA = fsurdat from CaseDocs/lnd_in (CTRL: release-clm5.0.18 hist_78pfts_CMIP6_simyr2000; LCC: LPJGUESS 2100), FIXED LCC_FUT_fBVOC_PD_IM = `NF2100…lcc_fBVOC…-20261009` atm h0, ATM_INPUTS 13 CAM h0 vars (cb_ISOP/MTERP/SOA_LV/SOA_SV, AOD_VIS, CDNUMC, ACTREL, TGCLDLWP, CLDTOT, SWCF, LWCF, FSNT, FLNT) LCC_FUT vs fBVOC_PD_IM. Fix: load_monthly_field used join="exact" but CLM lat/lon differ from CAM by 2e-13 → now assert_allclose 1e-5 then assign CAM coords. Re-run via run_nb_inplace.py in background (log scratchpad run2.log) — RESULT PENDING. Backup of pre-edit nb: scratchpad bak_merged_v1.ipynb.
  18:22 (a): §14 done (675 s): JJA LCC_FUT−CTRL_FUT TLAI −0.46 modified / −0.41 UNMODIFIED / −1.26..−1.39 hotspots m²/m²; TV +0.46/+0.31 K; TREFHT +0.19/+0.09 K; FSDS +0.79/+0.25 W/m². §15 PFT (modified cells, pp): pft0 −3.5, pft12 −7.9, pft8 +4.8, pft3 +2.8, pft2 +2.3. (b) LAI drop outside the modified cells = FUT land-only CO₂-bug legacy (284 ppm spin-up) → explains FUT expansion emission decrease mostly in unmodified cells and PD/FUT sign flip; NOT a forest-expansion effect.   18:45 (a): full run DONE, exit 0, all cells ok (run_nb_inplace.py). §16: fBVOC_PD_IM SFISOP/SFMTERP = CTRL_PD −0.047 % all regions, RMSE ≤4e-4 mg/m²/d. §17 full contrast LCC_FUT−fBVOC_PD_IM ≥45°N ann: AOD_VIS +0.0054, CDNUMC +1.6e9 /m², ACTREL −0.057 µm, TGCLDLWP +2.2e-3 kg/m², SWCF −0.58, LWCF −0.06, FSNT −0.81, FLNT −0.11 W/m². TLAI deficit is year-round (also winter) → spin-up legacy (b); TV/FSDS up → emissions decrease follows LAI (b). Findings md cell added before 'Recommended reading order'. Gotcha: `pgrep -f <pattern>` inside a Monitor matches the monitor's own command → never ends; use the PID instead.
- **Session 035c87f8 (16:33): LCC coupled spin-ups NOT ready.** All 3 land-only runs (2026-10-23) STOPPED on st_archive `[Errno 5]` Lustre I/O errors, resubmit chain broken, no job queued (a). Progress: PD LCC `I2000…_lcc_…-20261023` yr 20/100 (RESUBMIT 8); FUT CTRL `I2100…_ctrl_…` yr 10/100 (RESUBMIT 9, CONTINUE_RUN FALSE); FUT LCC `I2100…_lcc_…` yr 40/100 (RESUBMIT 6). CO₂ OK (a): PCO2/PBOT PD 369–370, FUT 1134–1135 ppm; FUT TLAI ≈1.9 yr 1→10 (no collapse). PD CTRL land-only (12c) never created. 13b/23b LAND_CASE still → old buggy/asymmetric cases; 13c/23c placeholders. Coupled scripts read land restart from NIRD `BRL-FRST-XPSN_archive/<case>/rest/0101-01-01-00000` → archive must be copied there. 16:37 user OK → `./case.submit --job case.st_archive` (sbatch … --resubmit) submitted: PD LCC 1777355, FUT CTRL 1777356, FUT LCC 1777357 (a). 16:38 archives COMPLETED, runs back: 1777358/59/62 RUNNING, RESUBMIT 7/8/5 (a).
  Why stopped (a): Errno 5 on copy run→archive, all on preproc node b5201, but b5201 also ran the successful ones → intermittent /cluster/work Lustre I/O (b), not node/code.
  **Met-end bug (a):** LCC_FUT ext 1775781 (16:34) and LCC_PD ext 1775779 (~17:05) FAILED on 2014-12-31: atm.log `FIND_TIMES … 735110.0208`; last met file `…_6h_2000-2015/…cam.h1.2015-01-01-00000.nc` had 1 record. Restarts only 2014-01-01 → 2014 lost.
  **FIXED 17:40 (a):** new `preprocess/nudging/extend_last_met_file.py` appended recs 06/12/18 h (data = 2014-12-31 same hours; time 5475.25/.5/.75, datesec, time_bnds, ndcur/nscur, nsteph +12 rebuilt; global attr history_patch); asserts PS/U/V/T/Q rec0 = orig, recs1-3 = Dec31. Backup + README: `data/nudging-met-backup/` (data = NIRD symlink, gitignored; only copy of the original).
  **2014 reruns SUBMITTED 17:41 (a):** rpointer.rof reset 2015→2014 (MOSART had written 2015; backup `rpointer.rof.bak-2015`), all 6 rpointers 2014-01-01; xmlchange STOP_N=1,RESUBMIT=0; LCC_PD run 1777448/arch 1777449, LCC_FUT 1777450/1777451. ~3.2 h each. Next: check CaseStatus success, archive h0 2014-12 + rest/2015-01-01, no FIND_TIMES. CTRL_PD/FUT 15-yr need nothing (use patched file at end).
- **Active task:** none. D1/D2 self-contained + src pruned + both nbs run and verified identical to old tables (session 5a5f936c).
- **Next action (science):** none queued from this task. Optional: `CLAUDE.md:88` cites Total_FUT +0.25 from stale `D1_farfield_verdict.csv`;
  new D1 has no Total contrasts; old rows kept in `diagnostics/other-BVOC-emission-magnitude/D1_farfield/tables/D1_farfield_regional_stats_with_Total_2026-10-21.csv`.
- **Session bd6c4048 (00:05):** D1/D2 outputs MOVED out of `results/` → `diagnostics/other-BVOC-emission-magnitude/{D1_farfield,D2_megan_budget}/{figures,tables}/` (a). Notebook FIG_DIR/TABLE_DIR + CLAUDE.md:21,22,88 repointed. Plain `mv` (git index untouched; some PNGs were tracked under results/figures → show as deleted). D1.log/D2.log moved to `<D1_farfield|D2_megan_budget>/logs/` (00:12); `results/tables/logs/` now only run_nb*.py.
- **Pending user decisions:** (1) CTRL land-only re-spin-up + rerun CTRL before O1; (2) commit: now also 4 git-rm'd D1/D2 files,
  7 git-rm'd src modules, trimmed analysis/{regions,stats}.py, renamed nbs (untracked), new results CSVs/figures;
  (3) whether to add Total_PD/FUT contrasts back to D1 or drop the stale verdict CSV.
- **Session aebc129e (active):** CO₂ bug confirmed (a): FUT land-only `I2100…-20260924` ran CLM_CO2_TYPE=constant 284.32 ppm; coupled FUT see ≈1138–1142 ppm.
  Running `diagnostics/check-CO2-bug-in-land-only/check_CO2_bug_in_land_only.ipynb` + `_six_variables.ipynb` (scratchpad `run_co2.log`, `run_six.log`) DONE (both run in place, summaries filled). Short-term: PD OK; FUT members differ in TSOI/TWS (bug).
  UNCOMMITTED, NOT run: setup doc `docs/setup_fix_FUT_landonly_CO2.md`; cases-setup.sh spin-up diag vars; `cases-scripts/22b-…` edited (CO2_PPMV=1137.78 + lnd_in guard, CASENAME `_lcc_`), new `22a-…landonly_spinup_ctrl…sh`; user to decide keep/revert.
  User decided (22:49): analyse current outputs + start corrected runs. Was: no rerun / partial (22b only → nudged LCC_FUT(+fBVOC) with new finidat) / full symmetric (22a+22b → coupled → nudged). Supersedes decision (1) above.
- **Session 20966a2c (active, 16:23): provisional all-species fBVOC runs on the CURRENT chain (user: figures for a meeting; rerun on the new 20261025 chain later).**
  Versions: CTRL_PD/FUT `-20261023` DONE (2000–2014, HR_BVOC_ALL). CLAUDE.md: versions table + § "When a run version changes" (user rule; also memory `boreal-run-versions`). Aliases now `LCC_<P>_fBVOC<src>[_IM]`: old runs `LCC_{PD,FUT}_fBVOCctrlPD_IM`; new `LCC_PD_fBVOCctrlPD` (14c), `LCC_FUT_fBVOCctrlPD` (24c), `LCC_FUT_fBVOCctrlFUT` (24d); `LCC_FUT_fBVOClccPD` postponed (LCC_PD has no h1; 14a now HR_BVOC_ALL). fBVOC hold in CLAUDE.md lifted for 14c/24c/24d only.
  Emissions: sbatch arrays 1780199 (CTRL_PD, idx 8 = MEG_CH3OH done on login) + 1780200 (CTRL_FUT), `preprocess/bvoc-emissions/run_bvoc_climatology_array.sh` → `/cluster/work/users/adelez/bvoc-emissions/` (module netcdf4-python, since /nird is not mounted on compute nodes; the first try 1780158/59 failed with exit 127). Arrays DONE 16:39 (37/37 COMPLETED, 19 files per source). The session was interrupted during the check; rerun as background chain bvzgfwmvn (check both → relabel 2100 → cp -n to the projects EMS dir; log `/cluster/work/users/adelez/bvoc-emissions/logs/relabel_2100.log`).
  Arrays DONE 16:38 (37 COMPLETED, 19+19 files). check_bvoc_climatology: 38/38 PASS (clim/h0 within 3e-7) (a). Tg/yr PD→FUT: SFISOP 517→892, SFMTERP 147→513, BCARY 13.5→57, CH3OH 103→295, CO 76→241.
  17:03 CTRL_PD 19 files copied + cmp to `/cluster/projects/nn9188k/adelez/noresm-inputdata/processed/bvoc-emissions/`; 14c SUBMITTED: test run 1780292/arch 1780294 (case `…lcc_fBVOCctrlPD_f19_f19-test-1day-20261025`), production run 1780293/arch 1780295. Relabel 38/38 OK (dates +1000000, units 2100, values equal); copied+cmp (23 GB in dir). 17:20 launched 24c/24d tests + productions (bg b0jcaclgo, b1w22ph8l, baivomev5, bn1vrp5hn); watcher runs `tests/check_fbvoc_all_1day.py` on the 14c test when it ends.
  24c SUBMITTED: test 1780311/1780313, production 1780317/1780318. 24d: test 1780315/1780316, production 1780312/1780314 (all running 17:30). Watchers: bp40q69qq (14c test), second for 24c/24d tests.
  14c 1-day test ALL PASS (a): MEGAN off, 19/19 ems entries, no BB ISOP/MTERP, 16 species keep anthro/BB files, all 19 files opened (GETFIL + trcdata_init CYCLICAL), no MEG_*, SFBCARY > 0 (25 % of cells). First checker run said 12/19 opened = checker bug (atm.log wraps names >80 chars) → fixed (whitespace-insensitive match).
  24c + 24d 1-day tests ALL PASS (a). Day-1 SFISOP max: 14c = 24c = 2.142e-09 (same CTRL_PD emissions, read at cycle yr 2000 vs 2100 → relabel works); 24d 3.056e-09 (CTRL_FUT). Productions 1780293 (14c), 1780317 (24c), 1780312 (24d) RUNNING since ~17:10/17:30; expect ~2 days (CTRL runs took ~2 days).
  **Next:** when the productions finish: postprocess as LCC_PD_fBVOCctrlPD / LCC_FUT_fBVOCctrlPD / LCC_FUT_fBVOCctrlFUT (add to postprocess CASES; new case names `…lcc_fBVOC<src>_f19_f19-20261025`). Test cases `…-test-1day-20261025` (3) + `…-test-hrbvocall-20261023` (2) can be deleted by the user. (`…-test-1day-20261025`); if FAIL → propose scancel of the matching production.
  **Next:** (1) `$PY preprocess/bvoc-emissions/check_bvoc_climatology.py <CTRL case> 2001 2014` for both (monthly PD already PASS, ratio 1.00000000); (2) `EMS_DIR=/cluster/work/users/adelez/bvoc-emissions bash create_bvoc_emissions_for_year_2100.sh <case>_2001-2014` for CTRL_PD and CTRL_FUT; (3) copy finals (PD yr2000 + both _on_yr2100) to `/cluster/projects/nn9188k/adelez/noresm-inputdata/processed/bvoc-emissions/` (= EMS_PREFIX dir in 14c/24c/24d); (4) launch tests `tests/{14c,24c,24d}-…-1day.sh` + productions 14c/24c/24d in parallel; check with `tests/check_fbvoc_all_1day.py`.
  17:02: check_bvoc_climatology PASS for all 38 files (ratios 1 ± 3e-7). Global Tg/yr PD→FUT: ISOP 517→892, MTERP 147→513, CH3OH 103→295, CO 76→241. My relabel STOPPED (SFISOP_on_yr2100 existed): ANOTHER process (not visible on this login node; default species order) is writing CTRL_PD `_on_yr2100` files in /cluster/work/users/adelez/bvoc-emissions since 16:51 (7/19 at 17:01; 6 complete, MEG_CH2O still being written at 17:03). → 17:08: it is a PARALLEL COPY of session 20966a2c on another login node (it wrote the 17:03 line above; built 14c test+prod at 17:01, relabel PD done 19/19, FUT in progress). This copy (login-2) STANDS DOWN on the fBVOC pipeline to avoid duplicate launches; the other copy owns relabel → copy → 24c/24d launch.
  17:19 USER RULE: final ems_* files read by fBVOC runs live in the SHARED `/cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions/` (default); staged work stays in /cluster/work. Done (a): 57 files cp -n + cmp to shared (CTRL_PD yr2000 19, CTRL_PD _on_yr2100 19, CTRL_FUT _on_yr2100 19; all 38 relabelled have 2100 metadata). EMS_PREFIX in 14c/24c/24d/24e (+ tests) → shared; 2100 script default EMS_DIR → shared; array + serial wrapper copy the final file to shared; .py default output → work; notebook DATA_DIR → shared; README + CLAUDE.md (key paths, data-safety exception). 14c test 1780292 + prod 1780293 (launched by the other copy) RUNNING with the projects path: identical bytes; keep the projects copies until they finish (or relaunch, user's choice).
  plot_bvoc_emissions.ipynb: original copied (cmp-identical) to prescribe-just-ISOP-MTERP/; main folder = NEW 19-species version (CTRL_PD vs CTRL_FUT, Tg/yr table, maps, polar, seasonal cycles; imports MOLAR_MASS etc. from the .py). **NOT executed yet**: run `$PY results/tables/logs/run_nb_inplace.py preprocess/bvoc-emissions/plot_bvoc_emissions.ipynb` once chain bvzgfwmvn has copied the files. New `preprocess/bvoc-emissions/README.md` (workflow).
  NEW 24e `…lcc_fBVOClccPD` (from 24d; EMS from `LCC_PD_CASE` placeholder YYYYMMDD + guard, exits before any action; + tests/24e-…-1day.sh). CLAUDE.md/README rows added.
  `prescribed_bvoc_emissions_all <2000|2100> <prefix>` in cases-setup.sh: tested in scratch (64 → 81 entries, only ISOP/MTERP changed + 17 added).
  Data rename still NOT run (user): `LCC_{PD,FUT}_fBVOC_*` → `…_fBVOCctrlPD_IM_*`; forcing_maps.BVOC_PAIRS still uses the old file aliases (other session). Postprocess CASES now point CTRL_* to `-20261023` → move old `CTRL_*` processed files first (skip-existing).
  `prescribe-just-ISOP-MTERP/` = original scripts (CTRL_PD -20260925), kept unchanged.
- **Session 78f6d842 (01:38): job status check.** FUT 1-day test: run 1775813 COMPLETED (case.run success 01:29), archive 1775815 FAILED (st_archive `[Errno 5] Input/output error` copying `mosart.r.2000-01-02` to archive; file readable afterwards → transient Lustre I/O (b)). Hist files still in run dir. **Checker on FUT test: all PASS, exit 0** (a). h1 size: **116 GB/15 yr was WRONG** — checker measured the uncompressed run-dir file (21 MB/day); archived h1 (NorESM st_archive, netCDF-4 deflate 5) = 5.04 MB/day FUT, 5.05 MB/day PD → **~1.8 GB/yr, ~28 GB / 15 yr per run** (a). FUT test re-archived 01:40 (st_archive success; not by me). **PD test: run+archive COMPLETED, checker all PASS, exit 0 (a). Both 1-day tests PASS → no need to cancel CTRL prod runs.**
  Quotas 01:41 (a, `dusage`): home 10.6/20 GiB, 93.7k/100k files; project nn9188k 920/1024 GiB; /cluster/work/users/adelez/archive 178 GB (USERWORK, no quota, auto-cleanup (c)); NIRD project quota not visible from Betzy (`df` = whole fs1 270T, 98 % full) → user to run `dusage -p NS9188K` on login.nird.sigma2.no. Need ≈2×28 GB h1 for CTRL_PD+CTRL_FUT (a, archived size).
  All 8 running jobs at "model execution starting" in CaseStatus; CTRL_FUT prod at model date 2000-01-20 at 01:38; CTRL_PD prod 1775819 (user launched 13a, 01:19) and PD test 1775817 slow init (~13 min) then fast. "NetCDF: Variable not found" in cesm.log also in passing FUT test → benign (b). Background wait on 1775817/1775818 → then run checker on PD test.
- **Session 0c58bc16 (00:58):** Scripts only, none run. FUT: new `23c` (CTRL coupled spin-up, LAND_CASE placeholder+guard); 22b+22c CO₂ → `CCSM_BGC=CO2A,CLM_CO2_TYPE=diagnostic` (CO2A needed, else CLM endrun lnd_import_export.F90:90 (a)); checks on lnd_in/drv_in. PD (user: write scripts, decide run later): 12b same CO₂ fix + CASENAME `_lcc_`; new 12c (CTRL twin of 12b), new 13c (CTRL twin of 13b, placeholder+guard). 22b header 22a→22c. User: do NOT touch 23a, 23b (23b LAND_CASE still → buggy 20260924, user updates by hand). (a) spinup-3 fsurdat = simyr2000 CTRL file; coupled runs co2_type=diagnostic; old 12b constant 367. Case `I2100…_lcc_f19_f19-20261023`: gptl bldlog ends after gmake line, no error → likely interrupted (b); I set CO2A/diagnostic there for a preview check. Runtime check pending: PCO2/PBOT×1e6 in first h0.
- **Session 339178f2 (01:22):** new `analysis/test_significance_marking.ipynb` (sig dots vs non-sig dots/AR6 hatching/outline), run OK; PNGs `results/figures/tests/significance_marking_{PD,FUT}_NET.png`. Uses old fBVOC aliases as fallback (rename not run). src untouched. Re-run with `run_nb_inplace.py` (01:26): outputs + figures saved in the nb (a). New rule (user): notebooks always keep outputs → memory `notebooks-keep-outputs.md` + `CLAUDE.md:66`. 01:50: user chose C → DEFAULT in src (a): `add_stippling` new style "lines" (`/////`, dimgrey, hatch lw 0.3); `_plot_panel` stipple=True → "lines" on NON-sig cells (`~sig & isfinite(p) & lat>=extent`), other styles still mark sig; `shade_ocean` default False in plot_single_boreal_panel + both make_* figs. forcing_maps.ipynb: markdown + common dict updated. 01:58: user asked → `BVOC_PAIRS` fbvoc = current file aliases `LCC_{PD,FUT}_fBVOC` (comment: switch to `_PD_IM` after rename); nb cell 11 uses `fm.BVOC_PAIRS`; test nb fallback removed. Both nbs run in place OK, 8 figures saved in `results/figures/` (a). UNCOMMITTED. NOTE: if the rename is run later, revert BVOC_PAIRS to `_PD_IM`.
- **Later:** ozone kernel (clone ciceroOslo/Radiative-kernels); Level 4 chemistry.
- **Gotchas:** Python `/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python`, `PYTHONPATH=src`, no nbformat;
  Total_FUT tropical +0.25 W m⁻² likely spin-up offset (b); BVOC_FUT uses PD emissions relabelled to 2100 → not LCC-only;
  fBVOC files lack MEG_*; CLM h0 first month time_bounds start 30 min early; CLM MEG_* units 'kg/m2/sec'; CAM fluxes float32.
  Last met file 2015-01-01 PATCHED (3 copied records) → original in data/nudging-met-backup/.
  Parallel sessions write these logs: edit only own block. Scratchpad wiped per session.
- **Logging:** rules in repo `CLAUDE.md` § Session logs; hook `~/.claude/hooks/boreal_log.py`.

---

## 2026-10-25 · 22:47 → 00:56 (129 min) · session 7648e6ae
**Task:** Ghan 4-panel maps per contrast (12) + seasonal (12); contrast grids rows=contrasts cols=vars (context, hydro, snow-albedo, surface energy, FSDS split); land water budget; split forcing_maps.ipynb into 3 notebooks. Details in NOW (a). Plan: `~/.claude/plans/sparkling-foraging-dream.md`.
**Key numbers (a):** PD LCC−CTRL NET ≥45N +0.24±0.04 = ARI −0.01 + cloud −0.11 + clear-clean +0.37 W/m2; PD LCC−fBVOC NET +0.13±0.06 = ARI 0.00 + cloud +0.07 + clear-clean +0.05. FUT LCC−fBVOC SW JJA −2.3±0.3 (cloud −2.1). Water budget table `results/tables/water_budget_2001_2009.csv`.
**Gotchas:** run_postprocess.py default paths are cwd-relative; run_all_parallel.sh CASES already on CTRL -20261023 → don't use it for the 2001–2009 set.

## 2026-10-25 · 21:53 → 23:05 (72 min) · session 3b25e01e
- Status recap (a): climatologies CTRL_PD/FUT -20261023 done (37/37 array tasks, check 38/38 PASS, relabel 2100, 57 files in shared); 14c/24c/24d productions running.
- Rename dropped (user): 2001–2009 processed files move to `postprocessing/2001-2009-pre-co2-fix/` before postprocessing 14c/24c/24d; later 2001–2014 → `2001-2014-pre-co2-fix/` (CLAUDE.md step 2).
- CTRL_FUT base 19 files copied to shared (were missing); 76 work .nc re-cmp'd and deleted (29 GB).
- Auto-launcher `cases-scripts/auto_launch_new_chain.sh` running on login-3 since 22:57: 12c→13c→13a, 13b→14a, 23c→23a, 23b→24a (NIRD rsync + REFCASE edit before each launch). fBVOC new chain not automated.
- User rule: climatology scripts now move final files to shared (cp -n + cmp + rm). Edited array + serial scripts, check default dir, 24e comments, README, CLAUDE.md. Not run.

## 2026-10-25 · 21:28 → 21:35 (7 min) · session af52cc01
Land-only equilibrium nb: regions modified/global/tropics, only FUT_LCC_old as old reference, FUT_CTRL visible (thin, on top). Re-run, summary updated (a). See NOW.

## 2026-10-25 · 16:15 → 16:16 (1 min) · session dc6addbf
- git add of check-simulation-equilibrium: only __pycache__ ignored (intended); 200 files staged, nothing committed (a).

## 2026-10-25 · 15:37 → 17:44 (127 min) · session 20966a2c
- Restored the ISOP/MTERP-only scripts (HEAD) into `preprocess/bvoc-emissions/prescribe-just-ISOP-MTERP/` (cmp-identical).
- (a) CTRL_PD/FUT `-20261023` finished 2000–2014 (180 h0). New spin-ups 20261025 running (I2000 ctrl land-only, spinup_lcc PD+FUT, spinup_ctrl FUT; other sessions).
- (a) fBVOC srf list = CTRL list minus BB ISOP/MTERP (diff of CaseDocs/atm_in); 17 species keep anthro/BB. shr_kind_cl=256 > longest entry 188. skip-existing matches any year span (fileio.processed_exists).
- (a) Real-data smoke test MEG_CH3OH CTRL_PD 2001–2014: monthly clim = h0 mean ×factor, rel err 1e-7. Module python (netcdf4-python/1.7.1.post2-foss-2024a) output = conda output (synthetic).
- New: run_bvoc_climatology_array.sh, check_bvoc_climatology.py, prescribed_bvoc_emissions_all, 14c/24c/24d (+ tests/*-1day.sh, tests/check_fbvoc_all_1day.py); 14a HR_BVOC_ALL; defaults → CTRL_PD -20261023, 2001–2014; alias rename to fBVOCctrlPD scheme in code.

## 2026-10-25 · 14:45 → 14:50 (5 min) · session af52cc01
Vegetation-state nb: regions cut to 3 (global, modified, all unmodified), re-run, summary updated (a). See NOW.

## 2026-10-25 · 14:38 → 16:24 (106 min) · session 0521733a
- Task: rename output folders to `<notebook_stem>_outputs/` + general rule; .nc → `cache/`; gitignore cache/; fix check-CO2 MASK_FILE; rename equilibrium_outputs + D1/D2. All done (a), map in NOW.
- .nc = annual-mean caches (rebuildable from archive, ~800 hist files ≈15 min/nb); ~0.9 GB on /cluster/home. Cache reused even if VARS changes → stale-cache risk (REBUILD_CACHE=True).
- Backups of edited nbs: scratchpad `bak/`, `bak2/`.

## 2026-10-25 · 14:16 → 15:21 (65 min) · session 035c87f8
- 14:30 tasks: equilibrium nb (done, 27/27 short-term in eq. by cycle test), LAND_CASE in 13b/23b/23c (done), NIRD copy (done 14:45), symmetry question (answered). 15:06 user: launch 13b/23b/23c → launched. 15:10 user: PD symmetric chain → 12c launched. 15:12 rule: nudged runs 15 yr → CLAUDE.md + 14a/14b/24a/24b. 15:15 hold on fBVOC runs (CLAUDE.md + guard in 14b/24b). See NOW.
- Q: how did the last runs go? All 7 cases finished, case.run + st_archive success (a). Land-only reached yr 100 with correct CO2; LCC ext 2014 reruns and CTRL 15-yr runs ran through 2015-01-01 with the patched met file (a). Details in NOW.

## 2026-10-23 · 18:44 → 18:55 (11 min) · session 0ec901d3
- User: PD expansion maps washed out by shared scale in interaction nb → grouped scales + 0.98 quantile, re-run. Done (a), see NOW.

## 2026-10-23 · 18:30 → 18:35 (5 min) · session 0ec901d3
- User: apply hatching maps in vegetation-state nb + rerun. Done (a), see NOW.

## 2026-10-23 · 17:43 → 18:46 (63 min) · session e2a259e9
- Task: dedupe `diagnostics/FUT-fBVOC-background-lcc-effect-decomposition` notebooks into one; run interaction nb. Done (a), details in NOW.
- §13–17 inputs filled + CLM/CAM coord tolerance fix; full re-run done, exit 0 (see NOW). LCC_FUT_fBVOC_FUT not yet run → §16/17 only PD_IM.

## 2026-10-23 · 16:33 → 17:42 (69 min) · session 035c87f8
- 16:37 user: restart the three → st_archive --resubmit jobs 1777355/56/57 submitted (a); 16:38 all three running again.
- 16:39 Q why stopped: transient Lustre Errno 5 in st_archive (b). Found met-data end bug killing LCC_FUT ext at 2014-12-31 (a; see NOW).
- 17:04–17:41 user chose: add 06/12/18 h records copied from 2014-12-31 (plan; script in preprocess/nudging, backup in data/ + README). Done + 2014 reruns of both LCC ext submitted (a; see NOW).
- Q: ready for LCC coupled spin-ups (13b/23b) after land-only CO₂-diagnostic runs? No (a): land-only runs halted by st_archive I/O errors at yr 20/10/40 of 100; 12c not created; 13b/23b LAND_CASE not updated.
- CO₂ verified in h0 (a): PD ≈370, FUT ≈1134 ppm; lnd_in co2_type='diagnostic', CCSM_BGC=CO2A in all 3. fsurdat: PD/FUT LCC = LPJGUESS 2100 file, FUT CTRL = simyr2000.

## 2026-10-23 · 01:40 → 01:45 (5 min) · session 78f6d842
- Q: how to check quota for the h1 output. Ran `dusage` (a): project nn9188k 920 GiB / 1 TiB; home files 93.7k/100k; work archive 178 GB; NIRD /nird/datapeak fs 98 % full (whole fs, not project). NIRD project quota: `dusage -p NS9188K` on NIRD login (not run).
- PD 1-day test: 1775817/1775818 COMPLETED, st_archive success 01:41, checker all PASS (a).
- Size correction (a): archived h1 = 5.0 MB/day (deflate 5) both tests → ~28 GB/15 yr/run; earlier 116 GB came from the uncompressed run-dir file. Checker `tests/check_hr_bvoc_all_1day.py:74` uses size of whatever file it finds (run dir before archiving → overestimate ×4).

## 2026-10-23 · 01:36 → 01:39 (3 min) · session 78f6d842
- Q: CaseStatus of just-submitted runs + 1-day tests. 16 jobs (8 run, 8 pending on dependency). All 9 case dirs in `/cluster/projects/nn9188k/adelez/cases/BRL_FRST_XPSN/` (a).
- FUT test: run OK, st_archive I/O error (transient, b). Checker PASS on all items (a). h1 15-yr ≈ 116 GB (a).
- PD test + CTRL_PD prod: running, slow start then normal speed (a).

## 2026-10-23 · 01:24 → 02:00 (36 min) · session 339178f2
- C set as default (non-sig thin grey hatching, no ocean fade) in `plotting/forcing_maps.py`. forcing_maps.ipynb blocked by missing renamed fBVOC files (a).
- BVOC_PAIRS pointed back to the on-disk aliases `LCC_{PD,FUT}_fBVOC`; forcing_maps + test nbs re-run in place, all cells OK (a).
- Rule (user): every notebook created/run keeps its cell outputs. `run_nb_inplace.py` already existed (jupyter_client kernel; no nbclient). CLAUDE.md:66 rewritten; memory saved.
- test_significance_marking.ipynb re-executed in place; PD/FUT cells hold image/png outputs (a).
- Softer styles (grey, thin; hatch lw via `Collection.set_hatch_linewidth`); outline masked >86°N removes pole spikes, small closed loops at 80–86°N remain (a, figure).
- User: no ocean fade; likes B → denser `////`; try fading non-sig cells. Without ocean shading, radial streaks near the pole are visible in the raw maps (pole cells, all rows) (a, figure).

## 2026-10-23 · 01:10 → 01:22 (12 min) · session 339178f2
- Q: mark sig vs non-sig cells? IPCC (c, from memory): AR5 stipple robust + hatch non-robust; AR6 leaves robust unmarked, diagonal = no robust signal, crossed = conflicting.
- New `analysis/test_significance_marking.ipynb`, run via run_nb.py (a). % cells ≥45°N significant (FDR 0.10, NET): PD total 24.4, bvoc_total 0.0 (1 cell), bvoc_cloud 0.0; FUT total 28.3, bvoc_total 88.8, bvoc_cloud 94.2 (a).
- Outline style: pole spike artefacts (contour on lat-lon grid near 90°N) and no line when all/none sig (a, figure).

## 2026-10-23 · 00:35 → 00:58 (23 min) · session 0c58bc16
- Q: add CTRL coupled FUT spin-up? Yes for symmetric chain (22c → 23c → 23a). 23a currently starts from `spinup_f19_f19-3` (a).
- Wrote `23c-…spinup_ctrl…` from 23b. 23a untouched per user.
- 22b/22c: CO₂ → `CCSM_BGC=CO2A,CLM_CO2_TYPE=diagnostic` (a: CCSM_BGC default none for _DATM, config_component_cesm.xml:163; flds_co2a needs CO2A; datm maps stream co2diag→Sa_co2diag). preview_namelists on case -20261023: co2_type='diagnostic', flds_co2a=.true. (a).
- Chain review (a): spinup-3 fsurdat = simyr2000 (archive CaseDocs + h0 attr); coupled nudged runs co2_type diagnostic; PD land-only I2000…-20260925 constant 367 ppm.
- PD scripts (run decision pending): 12b CO₂ fix + `_lcc_`; new 12c, 13c (twins, 13c guard). 22b header 22a→22c. README + setup doc rows. All `bash -n` OK; diffs twin vs original = header/CASENAME/surfdata/LAND_CASE/guard only.
- 23b left as is (user). Plan: `~/.claude/plans/rosy-prancing-sunrise.md`.

## 2026-10-23 · 00:29 → 00:30 (1 min) · session 0042d825
- Q: SF* vs MEG_* for prescribed ISOP/MTERP → SF* (total, BB already removed from fBVOC srf_emis; diurnal bypass assumes total). MEG_ISOP/MTERP in fincl2 only as optional diagnostic (~1 GB/yr extra, b).

## 2026-10-23 · 00:17 → 01:53 (96 min) · session 20966a2c
- Task 2: rename commands for processed fBVOC files (not run). 30 nc + 30 logs; no `_IM_` targets exist (a). Global attr `alias` stays old unless `ncatted` is applied (optional).
- HANDOFF read; no conflict with task 1.
- Task 4 facts (a): adv_mass of all 19 species from `pp_tropstrat_mam_oslo/mo_sim_dat.F90` (ISOP/MTERP match the old values). OsloAero `chemistry.F90:1031,1129`: MEG_ = -meganflx·adv_mass·1e-3 (kg/m2/sec), added to cflx. `tracer_data.F90:1052-1070,1626`: CYCLICAL wraps Dec→Jan with linear interpolation. fBVOC atm_in: srf_emis_type CYCLICAL, cycle_yr 2000 / 2100.
- CTRL reruns (01:07): readiness (a): 13a/23a HR_BVOC_ALL; parallel-session cases-setup edits only in spin-up diag functions; nudging to 2015-01-01; home files 93.7k/100k soft. RESUBMIT=2. Tests + CTRL_FUT production launched; CTRL_PD production blocked by the classifier.
- Task 4 tests (synthetic, 3×4 grid, 2 noleap years; h1 monthly files at phase 1800; h0 stamped end-of-month): C3H6 half-hourly + CH3OH monthly match the analytic values (rel err ≤1.2e-7); monthly time 15.5, 45, 74.5 d (noleap) / 45.5 Feb (gregorian); old == new SFISOP (all vars + attrs). Negative: missing month, wrong cell_methods, SF<other> are all rejected.

## 2026-10-22 · 23:45 → 00:08 (23 min) · session 20966a2c
- Task: all-species fBVOC prep, task 1 (apply HR_BVOC_ALL + alias rename). The HANDOFF file is missing; the user will upload it.
- (a) `megan_specifier` CTRL_PD `CaseDocs/drv_flds_in` = 19 species. fincl1 already had MEG_ISOP/MTERP/BCARY, so h0 now has all 19 MEG_*, no duplicates (rendered user_nl_cam with stub xmlchange).
- (a) `chemistry.F90:953` addfld MEG_<name> kg/m2/sec. `cam_history.F90:2231-2239` drops unknown fincl with a log line; abort flag `.false.` parameter at `:2218`.
- (a) HR_BVOC_ALL h1 = SFISOP,SFMTERP + MEG_{BCARY,C3H6,BIGENE,CH3CHO,CH2O,C2H4}, nhtfrq 0,1, 'A','I'. HR_BVOC/no-arg output unchanged apart from +16 h0 MEG_*.
- aliases.patch was stale (D1 nb self-contained; make_D1_notebook.py and diagnostics/farfield.py removed with git rm). Rename done with a whole-word regex in: postprocess x2, forcing_maps.py, README, CLAUDE.md, extend_nudg_runs, test_LCC_PD_fBVOC_2days.sh (comment only), analysis/forcing_maps.ipynb, D1 nb, FUT-decomposition nbs (`LCC_FUT_fBVOC_PD` → `_PD_IM` there as well). Checks passed: bash -n, json.load, import.

## 2026-10-23 · 00:05 → 00:13 (8 min) · session bd6c4048
- Moved D1/D2 figures+tables from `results/figures/{D1_farfield,D2_megan_budget}/` and `results/tables/{D1_farfield_*,D2_*}.csv` to `diagnostics/other-BVOC-emission-magnitude/<D1_farfield|D2_megan_budget>/{figures,tables}/` (5+13 PNG, 4+4 CSV) (a).
- Edited `FIG_DIR`/`TABLE_DIR` in `D1_farfield_check.ipynb`, `D2_megan_budget.ipynb` (JSON valid, not rerun); CLAUDE.md repo-layout + D1 verdict path.
- Run logs `results/tables/logs/D{1,2}.log` → `<D1_farfield|D2_megan_budget>/logs/` (user asked, 00:12). No code referenced them. Empty source dirs removed.

---

## 2026-10-22 · 20:45 → 00:25 (220 min) · session aebc129e
- Task: notebook CTRL_FUT vs LCC_FUT vegetation state (PDF §7 checks 1+3). Done, run headless OK (`run_nb.py`, 8 min; cell 5 loading 401 s).
- Lineage (a, lnd_in + scripts + hist attrs): NSSP585frc2 r.2100-01-01 → `NF2100…spinup_f19_f19-3` (20 yr coupled free, simyr2000) → CTRL_FUT.
  LCC: spinup-3 r.0021 → `I2100ssp585Clm50BgcCropCplHist…-20260924` (100 yr land-only, LPJGUESS, annual h0, complete yrs 1–100) → `NF2100…spinup_lcc…-20260928` (20 yr, finidat I2100 r.0101) → LCC_FUT. Land years: CTRL 20, LCC 140.
- Results 2001–2009 LCC_FUT−CTRL_FUT (a, `A_nudged_regional_means.csv`, area×landfrac means of annual means): all unmodified land TLAI −0.42 (−16 %), TOTVEGC −34 %, TOTECOSYSC −21 %, GPP −11 %;
  tropics TLAI −0.56 (−17 %; CTRL IAV SD 0.020), TOTVEGC −34 %; modified cells TLAI −12 %, TOTVEGC −11 %. p<0.05 area on unmodified land: TLAI 50 %, TOTVEGC 87 %, nearly all negative (`B_delta_area_stats.csv`).
- Drift (a, `C_last10yr_trend_pct_per_decade.csv`, tropics TOTVEGC): spinup +5.9, CTRL_FUT +4.4, landonly −3.8, spinup_LCC +15.9, LCC_FUT +11.7 %/decade.
- Cause (a setting / b link): I2100 env CLM_CO2_TYPE=constant, CCSM_CO2_PPMV=284.32, DATM_CO2_TSERIES=none; coupled cases co2_type=diagnostic. PD I2000: constant 367.0 → annual global TLAI ≈1.4 flat, TOTVEGC 3602→3974 (a, by hand). FUT land-only TLAI 2.5→0.95 within ~5 yr.
  Coupled FUT atm CO₂ value not checked (c, ~1100 ppm expected). FUT cplhist forcing problem not excluded (c).
- Also (a): I2100 hist `case_id` = `…-test-20260924`; archive has identical `-test-` folder. CLM time_bounds start −30 min → years by interval midpoint. `Initial_conditions_dataset` = finidat_interp_dest.nc → finidat only via lnd_in.
- Implication (b): Total_FUT and the O1 BGP term are invalid until the FUT land-only spin-up is redone with 2100 CO₂; rerunning CTRL_FUT from the LCC lineage would inherit the problem.
- Notebook built with a throwaway scratchpad script (nbformat absent); not in repo.

- 21:16+ (a): coupled FUT CLM PCO2/PBOT ≈1142 ppm (CTRL_FUT, LCC_FUT, spinup-3), CAM co2vmr 1.1378e-3; CTRL_PD 370 ppm. Surfdata CTRL vs LCC: all vars identical except PCT_NAT_PFT (1174 cells, 46.4–82.4°N, max 57.8 pp).
  22b header explains the "test-" label (not a test). DMS identical across all FUT scripts.
- CTRL_FUT >45°N (spinup-3 + nudged, 29 yr): TLAI trend +0.5 %/dec (IAV 1 %), TOTVEGC +3.7 %/dec, TOTECOSYSC +0.3 %/dec.
- LCC − CTRL 2001–2009 from processed files (a): modified cells PD TLAI −1.3 %, HTOP +12.7 %, TOTVEGC +18.6 %; FUT TLAI −11.7 %, HTOP −0.9 %, TOTVEGC −11.3 %.
  >45°N unmodified: PD TLAI +4.2 %, TOTVEGC +15.4 %; FUT TLAI −17.8 %, TOTVEGC −35.5 %.
- Existing equilibrium nbs (`check_case_equilibrium-*`, `equilibrium.py`): per-case drift only, CLM region = modified only, no TLAI/HTOP/TSAI, no cross-member or forcing check → could not catch a stable-but-wrong state.
  FUT_SPINUP fig already showed TOTVEGC +~25 gC/m²/yr.
- Edited (approved plan steps 1–2, before plan mode returned): 22b CO₂ + guard, new 22a. NOT run. bash -n OK.
- New nb `diagnostics/check-CO2-bug-in-land-only/`: 10 stages PD+FUT; figs = lineage TLAI/TOTVEGC, drift vs cross-member, endstate PD vs FUT bars, exp-recovery fit. Built by throwaway scratchpad `build_co2_nb.py`.
- User criterion (21:52): short-term vars (TWS, H2OSOI, TSOI @~1 m) must be in equilibrium; carbon (GPP, TOTVEGC, TOTVEGN) not required. Source `diagnostics/check-spinup-equilibrium-uncomplete/clm_equilibrium_variables.txt`.
  Availability (a): TWS, TOTVEGN missing in land-only (PD/FUT) and LCC coupled spin-ups. levgrnd[8]=1.06 m (levsoi has no coord; = first 20 levgrnd).
- Copy nb `check_CO2_bug_in_land_only_six_variables.ipynb` (cache `outputs_six/`; secs 8–11: per-var lineage + 20-yr rolling mean, rolling derivative for land-only, verdict tables ratio |trend/dec|/IAV, short-term LCC−CTRL in IAV units). Builder scratchpad `build_co2_six_nb.py`. Both nbs running (logs `run_co2.log`, `run_six.log`).
- Q1 (a): cplhist `…spinup_f19_f19_20260422_01-20` ha2x1d/ha2x3h contain Sa_co2diag ≈1134 ppm (co2prog = 0); land-only datmconf `datm.streams.txt.CPLHISTForcing.State3hr` maps a2x3h_Sa_co2diag→co2diag.
  So datm passed CO₂ but CLM_CO2_TYPE=constant → CLM used co2_ppmv=284.32. Run-dir lnd_in gone (not verifiable post hoc). PD I2000 default CCSM_CO2_PPMV=367 matched by coincidence (b).
  → Better 22b fix: `CLM_CO2_TYPE=diagnostic` (uses the cplhist CO₂), not constant 1137.78. Not yet changed (user decision).
- First CO₂ nb run crashed: `outputs/annual_FUT_landonly_LCC.nc` corrupt (HDF error/PermissionError on reopen; quota fine: 10/20 GiB, 93k/100k files ← close to file limit).
  Deleted (own regenerable file), rerunning with HDF5_USE_FILE_LOCKING=FALSE. Six-var run continues (no env var set).
- CO₂ nb rerun OK; endstate numbers = processed-file values exactly (a). Summary cell filled. Recovery fit (b): TLAI τ 2–3 yr to plateau 12–17 % below CTRL (fit asymptote < CTRL; >45N still +3.4 %/dec);
  TOTVEGC τ 22 (mod), 58 (>45N unmod), 48 (trop) yr; ~155–165 yr to CTRL level. Fig2: FUT land-only TLAI (mod cells) ≈ PD land-only after yr 15 (~1.17). Six-var run still at cell 3/5 loading.
- Speed (a): xr.open_dataset ≈5.3 s/file on NIRD vs netCDF4 0.29 s. Loader in both CO₂ nbs → netCDF4 + ProcessPool(8, fork) (serial fallback on PicklingError when cells are exec'd outside a kernel, e.g. old run_nb.py).
  Verified vs old caches: max rel diff 0, same NaN mask (PD_spinup_LCC 240 files 26 s; FUT_landonly 11 files 1 s). CO₂ table also via netCDF4.
- New `results/tables/logs/run_nb_inplace.py` (jupyter_client + kernel `lcc-env`; saves outputs into the .ipynb; stops at the first error). nbformat/nbclient absent.
- Corrupt caches (HDF error): outputs/annual_FUT_landonly_LCC (deleted, rebuilt) and outputs_six/annual_CTRL_FUT. Cause (b): HDF5 locking on /cluster/home with concurrent jobs.
  Nbs now set HDF5_USE_FILE_LOCKING=FALSE at the top, write the cache to tmp + os.replace, and rebuild on OSError. Throwaway builders are out of sync → nbs are the source now.
- Killed the old six-var run_nb.py (redundant). Running both nbs in place (logs inplace1/2.log).
- My `pkill -f` killed its own wrapper shell (the pattern text was in its command line) → both bg jobs exit 144. Restarted the in-place runs without pkill (bg bsh3jmvma).
- In-place runs OK: nb1 113 s (9/9 cells, 5 figs), nb2 129 s (13/13, 13 figs). Six-var summary filled.
  (a) Land-only rolling-20 derivative: PD short-term ≈0 from yr ~30; FUT H2OSOI ≈0 by yr 30–40, TSOI +0.0003–0.001 K/yr at yr 100 (inside band).
  Stage offsets: land-only TSOI ~0.5–1 K warmer than coupled; nudged colder than free. End of FUT_spinup_LCC TSOI −0.74 K/dec >45N unmod (ratio 4.5); PD_spinup_LCC mod +0.35 K/dec (2.8).
  Nudged trends CTRL ≈ LCC (forced by nudging). Short-term LCC−CTRL 2001–09: PD |Δ| ≤1.3 IAV; FUT tropics TSOI +0.37 K (+6 IAV), TWS +29 mm (+3.7), H2OSOI +2.4; >45N unmod TWS −2.6 IAV.
- 22:49 user plan: analyse current outputs + launch corrected runs in parallel. My advice: safe now = PD all (Total_PD local, BVOC_PD, D1/D2 PD) + FUT code/figures; caveat = BVOC_FUT (shared state);
  wait = any LCC_FUT−CTRL_FUT number. MEGAN (b): γ_LAI saturating → ≈−6 % (tropics LAI 3.37→2.81; mod 2.37→2.09), but D2 FUT global −250 Tg/yr (99 % outside), local FUT −1.4 vs PD +0.45 Tg/yr (sign flip not attributable).
  Coupled LCC spin-up did NOT fix short-term fully (FUT tropics TSOI +6 IAV, TWS +3.7). Rerun checklist: 22b → CLM_CO2_TYPE=diagnostic (my edit uses constant 1137.78; change pending OK), check lnd_in co2_type,
  decide 22a symmetric, add TWS/TOTVEGN/TLAI/HTOP/TSAI to land-only output, rerun LCC_FUT + LCC_FUT_fBVOC (+CTRL_FUT if symmetric); BVOC climatology from CTRL_PD unaffected.
- 23:0x Q "why short-term jump spinup_LCC → LCC nudged": same in CTRL branch → free→nudged. (a) setup_nudging_data hard-codes PD met `NF2000…met_f19_f19_20260422` for ALL nudged runs incl. FUT (atm_in verified); 42/43 FUT met scripts empty files.
  User decision: FUT stays nudged to PD winds (by design). Earlier "met >45N 258.9 K" was my quick-script bug (never-valid cells summed as 0); TSOI/H2OSOI defs identical, no partial-NaN cells in any run.
- New nb `diagnostics/impact-of-nudging-on-land/impact_of_nudging_on_land.ipynb` (run in place 209 s, 0 errors). PD Δ2 nudging effect (CTRL_PD − PD_met, 2001–09, paired): global land FSDS −4.9 W/m² (−10.6 IAV), FSH −1.6, LH −1.2,
  TSA −0.28 K, TSOI1m −0.28 K (−4.5 IAV), PRECIP −0.07 mm/d, TWS −2.6 mm. Tropics FSDS −7.7 (−14 IAV). Δ1 free (met − spinup) <1 IAV except mod cells TSOI −0.38 K.
  FUT jump larger (TSOI global −9 vs PD −5 IAV; H2OSOI >45N +6.8 vs +0.6, mod +7.3 vs +2.2; less snow). CTRL ≈ LCC jumps → cancel in LCC−CTRL.
  Drift test (diff-series trend, lag-1 n_eff): 9/96 flagged (~5 by chance); short-term: TWS >45N unmod flagged PD (−6.7 vs −11.4 mm/dec) and FUT (−8.1 vs −18.1; mostly H2OSNO), TSOI mod PD (+0.034 K/dec). Member anomalies nearly identical → nudged-year trends = shared met weather (b).
- Six-var nb: added PD_met stage (MET, purple), reran in place OK; summary sentence added.
- cases-setup.sh: clm_spinup_diagnostics + clm_long_spinup_diagnostics += 'TSAI','HTOP','PCO2','PBOT','FSNO','SNOWDP' (NB comments; bash -n OK). Six eq. vars were already there (TOTVEGN/TWS added post-runs).
  _clm_diagnostics_base unchanged (has TSAI/HTOP/FSNO/SNOWDP; PCO2/PBOT on default tape). Did not touch the other session's uncommitted extend_case.
- New doc `docs/setup_fix_FUT_landonly_CO2.md` (problem table, root cause, options A minimal / B symmetric, script-change table, pre-submit checklist incl. 1-month test PCO2/PBOT≈1134, acceptance checks, interim analysis status, open decisions).
  Open: 22b → CLM_CO2_TYPE=diagnostic (current uncommitted edit = constant 1137.78) needs user OK; (c) diagnostic + datm CPLHIST untested.
- 00:0x MEGAN γ decomposition (one-off, read-only, raw nudged h0 2001–09, area×landfrac means; NOT saved in a nb). (a) SourceMod: γ_L = 0.30·ELAI (linear!; my earlier −6 % saturating estimate was wrong), γ_SM = 1, γ_C needs CO₂ (same in both).
  FUT LCC−CTRL %: >45N unmod ELAI −17.6, γ_L −17.4, γ_T_iso +4.7, γ_P −0.9, γ_A +0.5, γ_C +0.1, EPS 0, γ_iso −13.0, MEG_iso −23.2, MTERP7 −21.9; tropics γ_L −17.8, γ_T +4.7, MEG_iso −18.3, MTERP7 −17.4;
  global land MEG_iso −164 Tg/yr (−18.5 %), MTERP7 −80 Tg/yr (sum ≈ −244, matches D2 −250). Modified cells: EPS +21 % both periods; PD γ_iso −3.7, MEG_iso +7.9 % (+0.32 Tg); FUT γ_L −12.7, γ_T +8.7, MEG_iso −1.8 % (−0.21 Tg), MTERP7 −5.7 % → sign flip (b).
  PD outside modified ±2 % (lineage asymmetry). Caveats: MTERP7 = 7 saved MEG species; γ area-mean (emission falls more than γ).
---

## 2026-10-22 · 19:48 → 21:14 (86 min) · session 5a5f936c
- Task: make `diagnostics/other-BVOC-emission-magnitude/D1_farfield_check_updated.ipynb` + `D2_megan_budget_updated.ipynb` self-contained, prune src.
- Found (a): both `_updated` nbs already defined all helpers inline (no `boreal_forest_expansion` import); unexecuted; CASES had `YYYYMMDD` placeholders.
  Reverse deps: `analysis/stats.{cellwise_pvalue,fdr_mask}` used by plotting/megan_maps + forcing_maps; `analysis/regions.load_modified_cells` by megan_maps;
  `postprocess/derived.ghan_decomposition` is independent of `analysis/ghan`. All deleted files were committed+clean (last 156af25) → git = backup.
- User decisions: delete old nbs + generators, `_updated` take plain names; prune modules + unused functions.
- Done: filled CASES (lcc 20261005, fBVOC PD 20261008 / FUT 20261009, ctrl 20260925); rewrote intro md (dropped reviewer meta-text, fBVOC set-up stated as fact).
  `git rm` D1_farfield_check.ipynb, D2_megan_budget.ipynb, make_D1/D2_notebook.py; `mv` `_updated` → plain names (untracked).
  `git rm` src diagnostics/{farfield,farfield_plots,emissions,emissions_plots,megan}.py, analysis/{loading,ghan}.py;
  regions.py → only load_modified_cells; stats.py → only cellwise_pvalue, fdr_mask; __init__ docstrings; CLAUDE.md src/diagnostics rows.
  Verified (a): grep 0 refs to removed code outside legacy dirs; imports of megan_maps, forcing_maps, diagnostics, analysis, pipeline OK.
- Run 1 (20:41) both FAILED (a): D1 Ghan closure `assert_allclose` (float32 CAM, diff ~1e-6 W m-2, default atol 1e-8);
  D2 `Intervals are not full monthly means`: CLM first file time_bounds start 1999-12-31 23:30 (one 30-min step early → 31.02 d).
  Fix: closure rtol=0, atol=1e-3; month-length check atol=0.05 d (both nbs). Run 2 (20:47): D1 OK. D1 new vs old regional_stats: 96/96 BVOC rows identical (max|diff| 0), years 2001-2009 (a).
  New table lacks Total_* rows → old kept as `results/tables/D1_farfield_regional_stats_with_Total_2026-10-21.csv`.
  D2 failed units check: CLM MEG_* units = 'kg/m2/sec' (a) → added to accepted set. D2 run 3 SyntaxError from my patch (comment placed before ':'), fixed + ast-parse check of all cells; run 4 OK (21:11).
  D2 new vs old (a): q1 192/192, q2 288/288, q2_summary 36/36 matched rows identical (max|diff| 0). New extra rows: region
  `unmodified_cells`, contrast `CTRL_FUT-CTRL_PD`. Global carbon dE (Tg C/yr) ISOP+MTERP / others: LCC-CTRL_PD -8.65/+0.58;
  LCC-CTRL_FUT -221.8/-88.9; LCC_FUT-CTRL_PD 428.4/305.4; CTRL_FUT-CTRL_PD 650.2/394.3.

---

## 2026-10-22 · 19:24 → 19:58 (34 min) · session da72ac23
- 19:58 review applied to CLAUDE.md:
  - fBVOC bullet: both periods use the CTRL_PD climatology.
  - Contrasts: how to read BVOC_PD vs BVOC_FUT, plus the MEGAN-off caveat.
  - `PY=` defined; njobs is positional.
  - Gotchas rewritten with evidence tags; the +0.25 is defined (D1, net TOA, 30S–30N, verdict CSV).
  - New sections: Data checks, Code conventions, Data safety (replace the blanket "never overwrite NIRD").
  - Session logs section untouched.
- 19:40 user pasted external review of CLAUDE.md; assessed. Checks (a):
  `create_bvoc_emissions_for_year_2100.sh` = CTRL_PD 2000 climatology relabelled to 2100 (values unchanged) → LCC_FUT−LCC_FUT_fBVOC
  mixes FUT background + LCC; my "isolates BVOC response" line is wrong. No escaped markdown in CLAUDE.md (grep 0).
  drop_spinup in both `postprocess/pipeline.py:55` and `analysis/loading.py:155`; D1/D2 (farfield, emissions) read raw hist via open_cam_monthly → no double drop now (b: holds as long as nobody feeds processed files to the loader).
  `run_all_parallel.sh` NJOBS = positional `${1:-24}`; `$PY` undefined in CLAUDE.md; "never overwrite NIRD" conflicts with outputs under `data/` (NIRD).
- Task: document the codebase in CLAUDE.md (plan: `~/.claude/plans/synthetic-foraging-octopus.md`). Inserted ~95 lines before § Session logs; logs section untouched
  (the user had meanwhile added the "Human log keeps the history of open items" rule, which is kept).
- Verified (a): `run_postprocess.py` args (casename alias {atm,lnd} --categories --tape --raw-path --out-path --spinup-months --skip-existing);
  `run_all_parallel.sh` PYTHON default = lcc-env, RAW `~/BRL-FRST-XPSN_archive` (symlink exists), OUT `data/processed-data/postprocessing`, NJOBS 24;
  `BVOC_PAIRS` PD/FUT {lcc, fbvoc, ctrl}; case root `~/cases/BRL_FRST_XPSN/`; queue normal / st_archive preproc; LCC surfdata name in 14a.
- From Explore agent (b, not re-checked): case-name date suffixes in the labels table, category lists (taken from `postprocess/variables.py` via the agent), `run_nb.py` behaviour.
- Ran in parallel with session 1f288034 (overlapping window); both blocks kept, ordered by end time.

---

## 2026-10-22 · 19:26 → 19:30 (4 min) · session 1f288034
- Fresh session after enabling hooks. `~/.claude/settings.json` has both hooks (a); UserPromptSubmit fired NEW BLOCK on first prompt (a).
  No science work.
- 19:30 user rule (now in `CLAUDE.md` § Session logs): human log never deletes old Open items; resolved ones go under
  **Done** in the current block with "(open since <date>)", including items opened and closed within one block.

---

## 2026-10-22 · 19:07 → 19:56 (49 min) · session 12e1d74a
- Built session-log automation: `~/.claude/hooks/boreal_log.py` (modes `prompt`/`stop`; state in `~/.claude/hooks/state/`;
  active if cwd in repo or prompt/transcript mentions BOREAL-FOREST-EXPANSION / BRL_FRST_XPSN / BRL-FRST-XPSN). Tested (a): NEW, CONTINUE,
  gap>60 → NEW with previous-block summary, stop blocks when logs untouched, stop_hook_active guard, unrelated session silent.
- Created `docs/CLAUDE_log_human.md`; added this header + NOW here. No science work.
- 19:25: rules moved into new repo `CLAUDE.md`; hook RULES text reduced to a pointer to it (+ times). Hook confirmed firing (a).
- 19:56: parallel sessions (da72ac23, 1f288034) write to the same logs → rule changed from "rewrite top block" to "rewrite own
  session's block" (CLAUDE.md § Session logs + hook CONTINUE text). Explained the role of each piece to the user.

---

## 2026-10-21 (later) — D1 results, MEGAN factor maps, smaller significance dots

### D1 notebook result (a; `results/tables/D1_farfield_verdict.csv`, CIs with lag-1 n_eff)
| Contrast, net | tropics contrib (W m⁻²) | modified cells | verdict |
|---|---|---|---|
| BVOC_PD total | +0.047 | +0.007 | MATTERS (clean clear-sky +0.026 also MATTERS; cloud p = 0.065) |
| BVOC_FUT total | −0.442 | −0.048 | MATTERS, all terms |
| Total_PD | — | — | none detected (PD Total maps usable) |
| Total_FUT total | +0.252 | +0.039 | MATTERS (cloud +0.22) → spin-up offset confirmed |
D2 notebook run: log was truncated, CSVs exist in `results/tables/D2_*.csv` but were **not yet checked** for completeness.

### MEGAN factors (a unless tagged)
- SourceMod: γ computed for every vegetated patch, also where ε = 0; patch→cell = area mean over non-spval patches.
  `MEG_*` averaged over all land (bare/urban/lake = 0); `EPS_*`, `GAMMA*` over vegetated soil/crop + lake only.
  → grid-cell `GAMMA_*` is an area mean, not emission-weighted.
- **γ_eff = MEG / (k·f_valid·EPS)**, k = 1e-9/3600, f_valid = natveg·(1−bare) + crop + lake (b, derived). Check: γ_eff/GAMMA = 0.90–1.14
  in single-PFT cells; f_valid median 0.98 ≥45N.
- EPS/GAMMA exist for **7** (not 8) of 21 MTERP compounds; they are **89 % of MEG_MTERP ≥45N** (CTRL_PD JJA).
- PD JJA, LCC vs CTRL, emission-weighted ≥45N (100·Δln): MTERP E +1.6 = composition (f·ε) +2.4 + γ_eff −0.9;
  partials γT +1.7, γL +0.2, γP −0.4, γA −0.2, residual −2.3 (residual > partials → area-mean gammas unreliable for attribution).
  Isoprene: ε mean ≥45N 2150 → 2480 µg m⁻² h⁻¹; γ_eff 0.051 → 0.048.

### Code changes (uncommitted)
| File | Change |
|---|---|
| `src/boreal_forest_expansion/plotting/megan_maps.py` (new) | `load_factors`, `make_factor_maps` (CTRL / LCC / % change; ε, γ_eff, γ, γL, γT, γP, γA, γC), `make_attribution_maps` (Δln split + residual). Seasons JJA/MAM/SON/DJF/ANN. Figures → `results/figures/megan_factors/` |
| `analysis/megan_factor_maps.ipynb` (new) | **Main content: `make_gamma_maps`** = plain maps of raw CLM `EPS_*`, `GAMMA*` (annual mean default, rows = isoprene + 7 MTERP, one figure per member, shared column scales). User asked for plain maps only, no Δln / JJA by default; factor/attribution figures kept as optional |
| `plotting/forcing_maps.py` | Significance marks: small dots thinned by 1/cos(lat) (default); `stipple="contour"` or `"hatch"` alternatives. All forcing/context maps regenerated |
| `results/tables/logs/run_nb.py` | Path bug fixed (chdir before open) |

---

## 2026-10-21 — Forcing maps rebuilt, D1/D2 imported, spin-up problem found

Context in: `HANDOFF_analysis_D1_D2.md` (design conversation 2026-10-15 to 10-21, not in repo).

### Key findings

**1. CTRL and LCC start from different land spin-ups (a) — Total contrast is contaminated.**
- Surfdata differ only in `PCT_NAT_PFT`, only at 46.4–82.4°N (a, diff of the two surfdata files).
- LCC chain: CTRL spin-up restart → **100-yr land-only BGC spin-up** (12b/22b, `I2000/I2100…CplHist`) → 20 yr coupled (13b/23b).
  CTRL chain: 20 yr coupled only (11/21; refcases `NHIST_tropstratchem_01_f19_tn14_r1990_s01_20241118` @2000, `NSSP585frc2_f19_tn14_20191014` @2100).
  fBVOC members use the LCC spin-up restart (a, `lnd_in` finidat) → BVOC contrast not affected by this.
- Namelists of CTRL vs LCC differ only in fsurdat, finidat, ncdata (and the CTRL_PD h1 tape) (a).
- Tropical (30S–30N) LCC − CTRL, 9-yr mean (a): PD TLAI +1 %, TOTVEGC +10 %, SFISOP −1.7 %;
  **FUT TLAI −13 %, TOTVEGC −31 %, SFISOP −18 %, SFMTERP −17 %**; constant from first to last year (offset, not drift).
- Effect: Total_FUT global +0.29 W m⁻², of which +0.25 ± 0.02 from the tropics (cloud term). Total_PD tropics not significant.
- Fix (b): land-only spin-up for CTRL with CTRL surfdata (same as 12b/22b), then rerun CTRL. Must be done before O1,
  otherwise CTRL_fBVOC inherits the offset.

**2. fBVOC artifact is larger than the local BVOC signal (a for numbers, b for mechanism).**
Contribution to the global-mean ΔF (W m⁻², net, ad hoc script):

| | modified cells | ≥45N rest | 30S–30N | <30S | global |
|---|---|---|---|---|---|
| BVOC_PD | +0.007 | +0.011 | +0.047 | +0.023 | +0.100 |
| BVOC_FUT | −0.048 | −0.052 | −0.442 | −0.005 | −0.571 |

- PD: SOA burden 3–4.5 % lower in LCC than in fBVOC everywhere incl. SH (emissions unchanged there); N_AER ~2 % lower.
  Likely: fBVOC lacks the other MEGAN compounds → more OH → more ISOP/MTERP → SOA (b, not proven).
- FUT: LCC_FUT vs CTRL_PD-climatology emissions: SFMTERP +186 % tropics, +100 % SH; SFISOP +40 % tropics, +2.6 % SH
  (CO₂ inhibition of isoprene, b). BVOC_FUT ≈ climate-change emission response, not LCC.
- PD BVOC clean-clear-sky term significant over most of the domain (+0.05 W m⁻² ≥45N) → chemistry/O₃ from missing compounds (b).

**3. D2 (user's notebook `diagnostics/other-BVOC-emission-magnitude/other_bvoc_check_updated.ipynb`, run with FUT added) (a).**
Others' share of the LCC − CTRL change: PD ≥45N **35 % by mass, 4 % by OH reactivity**; FUT ≥45N 61 % / 23 % (FUT contaminated by finding 1).
Global PD ΔISOP −7.6 Tg yr⁻¹ while ≥45N is +0.43 → global emission deltas are dominated by the spin-up offset.

**Verdict (b):** current fBVOC runs cannot isolate an LCC BVOC effect. Recommended order: fix CTRL spin-up → rerun CTRL →
add CTRL_PD_fBVOC + CTRL_FUT_fBVOC (option O1).

### Open checks resolved (a)
- `rad_diag`: absent in `atm_in` of all production cases.
- CO₂ seen by CLM: `co2_type='diagnostic'` → CAM `co2diag = chem_surfvals_get('CO2VMR')`, set from the LBC-file global mean
  (`chem_surfvals_set`, CHEM_LBC_FILE). atm.log: **370 ppm PD, 1137 ppm FUT**. `CCSM_CO2_PPMV=284.32` in FUT is unused.
  CO₂ is in `fincl1` but **not written** to h0.
- CAM h0: O3, OH, CH4, T are `(time, lev, lat, lon)`; hyai, P0, time_bnds present → CH₄ lifetime / O₃ column feasible for all members.
- CLM h0: 46 `MEG_*`, `EPS_*`/`GAMMA*` (10 compounds; only 7 of 21 MTERP), TREFMXAV/MNAV, FSH_V/G, SNOCAN, ERRSEB/SOL/H2O,
  SNOFSRVD present; **SNOFSDS\* absent** → no snow albedo. fBVOC CLM h0 has no MEG_* (expected).
- Ozone kernel: **not on Betzy**. Clone `github.com/ciceroOslo/Radiative-kernels` (Zenodo 10.5281/zenodo.16759214).

### Code changes (uncommitted)
| File | Change |
|---|---|
| `src/boreal_forest_expansion/plotting/forcing_maps.py` | Rewritten loading: reads `data/processed-data/postprocessing/{alias}_{atm,lnd}_{CAT}_2001-2009.nc` (old `data/postprocessed-diagnostics/` is gone). **Bug fix: FUT Total now uses CTRL_FUT** (was CTRL_PD). Paired yearly diffs, FDR stippling, mean ≥45N ± 95 % CI, `band="NET"/"SW"/"LW"`, monthly albedo proxy, unit conversions, in-cloud ACTREL/ACTNL via FCTL. Uses `analysis.stats`. |
| `analysis/forcing_maps.ipynb` | New notebook (lcc-env kernel, adds `src/` to path). Figures in `results/figures/`. |
| `src/boreal_forest_expansion/analysis/` (loading, ghan, regions, stats) + `diagnostics/` (farfield, emissions, megan + plots) | D1/D2 package from the handoff (loading, ghan, regions, stats, farfield(+plots), megan, emissions(+plots)). Edits: `NH_45_90_rest` region; ghan docstring maps to `postprocess.derived` names; `plot_contributions` refuses >1 contrast per period; `fdr_mask(within=)` broadcasts. |
| `diagnostics/other-BVOC-emission-magnitude/make_D1_notebook.py`, `make_D2_notebook.py` | No nbformat dependency; real case names; TEST_MODE removed (synthetic test helpers not in repo); D1 also runs Total contrasts (spin-up offset). |
| `results/tables/logs/run_nb.py` | Headless notebook runner. D1/D2 logs → `results/tables/logs/`. |

### Environment notes (a)
- Python: `/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python` (scipy, cartopy, xarray 2026.7; **no nbformat/nbconvert**;
  package not pip-installed → use `PYTHONPATH=src` or `sys.path.insert`). Jupyter kernel `lcc-env`.
- Cases: `~/cases/BRL_FRST_XPSN/`; archive: `/cluster/work/users/adelez/archive/`; source: `~/NorESM2.3_beta01`.
- Production case names: CTRL_PD/FUT `…_nudg_ctrl_f19_f19-20260925`, LCC_PD/FUT `…_nudg_lcc_f19_f19-20261005`,
  LCC_PD_fBVOC `…-20261008`, LCC_FUT_fBVOC `…-20261009`.
- Scratchpad is cleared when a session ends: keep logs in the repo.

### Next steps
1. Read D1/D2 notebook results (`results/tables/D1_*.csv`, `D2_*.csv`) once the background runs finish.
2. Decide on CTRL re-spin-up + O1 with the user.
3. Get the ozone kernel; Level 4 chemistry later.
4. Commit the code changes (user to confirm).

---

## 2026-10-20/21 (night) — Postprocessing sped up, all 90 processed files produced

### Result (a)
- **All 90 files** in `data/processed-data/postprocessing/` = 6 cases × (8 atm + 7 lnd) categories, span 2001–2009.
- 16 atm files (CTRL_PD, LCC_PD) existed before and were skipped. The other 74 were made in **~26 min** (23:56 → 00:22),
  0 failures, no leftover `.part` files. Before: 20–60 min per category per case, run one after another.
- Per-job times with 36 in parallel: small atm 8–10 min, atm SOA ~16 min, lnd BVOC ~21 min, other lnd 5–12 min.

### Why it was slow (a for structure, b for the lock)
- Cases and categories ran one after another.
- Each category was written lazily from 120 history files → the same data re-read per category through dask;
  reads are effectively single-threaded (HDF5 lock, b).
- Opening + header scan of 120 files ≈ 2 min per run on the NIRD filesystem (a, timed).

### Code changes (uncommitted)
| File | Change |
|---|---|
| `src/boreal_forest_expansion/postprocess/pipeline.py` | `ds.load()` once after spin-up drop (no re-reading per category); new `skip_existing` option |
| `src/boreal_forest_expansion/postprocess/fileio.py` | Header scan with `netCDF4.Dataset` (faster); new `processed_exists()`; write to `<file>.part` then rename (a killed job leaves no valid-looking file); **1 h tolerance** in `validate_monthly_means` |
| `postprocess/run_postprocess.py` | `--skip-existing` flag; timestamps in log lines |
| `postprocess/run_all_parallel.sh` (new) | One process per case × component × category, `NJOBS` at a time (default 24; used 36), largest first; failures don't stop other jobs; `DASK_SCHEDULER=synchronous`, 1 thread per process |

### Bug found and fixed (a)
**lnd processing could never have run** (why CTRL_PD lnd was missing): CLM's first h0 record starts one timestep early
(1999-12-31 23:30) → 31.02 days → rejected by the strict 28–31 day check. Fixed with 1 h tolerance.
That record is in the dropped spin-up year → outputs unchanged.

### Notes
- **fBVOC BVOC files lack `MEG_*`** (atm: MEG_ISOP/MTERP/BCARY; lnd: all MEG_<compound>), recorded in the
  `missing_variables` attribute. Expected: interactive MEGAN off in fBVOC runs (b).
- Ran on login node `login-2`: Slurm nodes almost all drained/down at the time (a, `sinfo`).
- Logs: `data/processed-data/postprocessing/logs_run_all.txt` (one OK/FAILED line per job) and `logs/<alias>_<comp>_<cat>.log`.
- Re-run / new cases: `bash postprocess/run_all_parallel.sh [NJOBS]`, skips existing outputs.
