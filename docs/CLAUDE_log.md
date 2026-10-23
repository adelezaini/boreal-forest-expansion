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
- **Session 20966a2c (active): all-species fBVOC, task 1/7 DONE, waiting for the user's go on task 2.** Plan: `~/.claude/plans/pasted-content-id-eaeb-context-read-cryptic-seahorse.md`.
  Done: HR_BVOC_ALL patch applied (13a, 23a, cases-setup.sh `cam_diagnostics`); aliases renamed. Old runs → `LCC_PD_fBVOC_PD_IM`, `LCC_FUT_fBVOC_PD_IM` (user decision: `_IM` = ISOP+MTERP only); planned `LCC_PD_fBVOC_PD`, `LCC_FUT_fBVOC_FUT`.
  Next: task 2 = print `mv` commands for the 30 processed `LCC_{PD,FUT}_fBVOC_*` → `…_fBVOC_PD_IM_*` (do NOT run). forcing_maps cannot find those files until they are renamed.
  The user will upload HANDOFF_analysis_D1_D2.md. Not renamed: `docs/setup_fix_FUT_landonly_CO2.md` (ambiguous "rerun LCC_FUT_fBVOC"), history logs, D1.log.
- **Later:** ozone kernel (clone ciceroOslo/Radiative-kernels); Level 4 chemistry.
- **Gotchas:** Python `/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python`, `PYTHONPATH=src`, no nbformat;
  Total_FUT tropical +0.25 W m⁻² likely spin-up offset (b); BVOC_FUT uses PD emissions relabelled to 2100 → not LCC-only;
  fBVOC files lack MEG_*; CLM h0 first month time_bounds start 30 min early; CLM MEG_* units 'kg/m2/sec'; CAM fluxes float32.
  Parallel sessions write these logs: edit only own block. Scratchpad wiped per session.
- **Logging:** rules in repo `CLAUDE.md` § Session logs; hook `~/.claude/hooks/boreal_log.py`.

---

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

## 2026-10-22 · 20:45 → 00:00 (195 min) · session aebc129e
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
