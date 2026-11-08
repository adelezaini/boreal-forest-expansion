## Cases technical names:
The numbering refers to the order of simulations.
  - first digit: `1` PD, `2` is FUT
  - second digit: step of running (`1` is required for `2`)
  - letter: parallel runs (`a` and `b` can run simultaneously)
----
Aliases follow the chain figure. Every run, with case names, versions (old / CO₂-fix chain), parents and status: [`run_aliases.csv`](run_aliases.csv).

**Present day (PD)**
- PD_spinup: `11-NF2000norbc_tropstratchem_spinup_f19_f19.sh` (20-yr coupled spin-up; its cpl history = CPLHIST_PD)
- MET: `12a-NF2000norbc_tropstratchem_met_f19_f19.sh` (u, v for nudging all PD and FUT nudged runs)
- MET extension: `12d-NF2000norbc_tropstratchem_met_ext_f19_f19.sh test|production` (same case name as MET, branch from its 2015-01-01 restart → 2026-01-02; `test` = 10-day reproduction test from 2010-01-01, check with `preprocess/nudging/check_met_reproduction.py`; then `preprocess/nudging/copy-nudging-data-to-inputForNudging-directory-2000-2025.sh` builds the `_6h_2000-2025` folder, regrouping the branch-run h1 files (06 h → next day 00 h) into calendar days with `regroup_met_ext_days.py`; watcher `preprocess/nudging/met_ext_watch_and_build.sh` does it after each segment and reruns a failed st_archive on the login node)
- LCC_PD_landonly_spinup: `12b-NF2000norbc_tropstratchem_landonly_spinup_lcc_f19_f19.sh` (100 yr, CPLHIST_PD forcing)
- CTRL_PD_landonly_spinup: `12c-NF2000norbc_tropstratchem_landonly_spinup_ctrl_f19_f19.sh` (CTRL twin of 12b)
- CTRL_PD_spinup: `13c-NF2000norbc_tropstratchem_spinup_ctrl_f19_f19.sh` (20 yr, land from 12c)
- LCC_PD_spinup: `13b-NF2000norbc_tropstratchem_spinup_lcc_f19_f19.sh` (20 yr, land from 12b)
- CTRL_PD: `13a-NF2000norbc_tropstratchem_nudg_ctrl_f19_f19.sh` (from 13c)
- LCC_PD: `14a-NF2000norbc_tropstratchem_nudg_lcc_f19_f19.sh` (from 13b)
- LCC_PD_fBVOCctrlPD: `14b-NF2000norbc_tropstratchem_nudg_lcc_fBVOCctrlPD_f19_f19.sh` (from 13b; all 19 MEGAN species from CTRL_PD)
- CTRL_PD_fBVOCctrlPD: `14c-NF2000norbc_tropstratchem_nudg_ctrl_fBVOCctrlPD_f19_f19.sh` (CTRL land + restart as CTRL_PD, its own 19 species prescribed → CTRL_PD − CTRL_PD_fBVOCctrlPD = prescription artefact (interactive − prescribed, user 2026-11-07); baseline for LCC_PD_fBVOCctrlPD. New chain, 15 yr, auto-launched with 14b (user 2026-10-29); the old-chain 3-yr test is case `-20261028`)
- CTRL_PD_fBVOCctrlPD_HR: `14d-NF2000norbc_tropstratchem_nudg_ctrl_fBVOCctrlPD_HR_f19_f19.sh` (replay test, old chain, 3 yr 2000–2002, user OK 2026-10-29: as the old-chain 14c test but with CTRL_PD's **actual** emissions of each year, files `ems_<CTRL_PD>_Y-Y_*`; three 1-yr jobs, `replay_prerun.sh` (CIME `PRERUN_SCRIPT`) points `user_nl_cam` to the year's files; h1 30-min SFISOP/SFMTERP)

**Future (FUT)**
- FUT_spinup: `21-NF2100ssp585norbc_tropstratchem_spinup_f19_f19.sh` (20-yr coupled spin-up; its cpl history = CPLHIST_FUT)
- LCC_FUT_landonly_spinup: `22b-NF2100ssp585norbc_tropstratchem_landonly_spinup_lcc_f19_f19.sh` (100 yr, CPLHIST_FUT forcing)
- CTRL_FUT_landonly_spinup: `22c-NF2100ssp585norbc_tropstratchem_landonly_spinup_ctrl_f19_f19.sh` (CTRL twin of 22b)
- CTRL_FUT_spinup: `23c-NF2100ssp585norbc_tropstratchem_spinup_ctrl_f19_f19.sh` (20 yr, land from 22c)
- LCC_FUT_spinup: `23b-NF2100ssp585norbc_tropstratchem_spinup_lcc_f19_f19.sh` (20 yr, land from 22b)
- CTRL_FUT: `23a-NF2100ssp585norbc_tropstratchem_nudg_ctrl_f19_f19.sh` (from 23c)
- LCC_FUT: `24a-NF2100ssp585norbc_tropstratchem_nudg_lcc_f19_f19.sh` (from 23b)
- LCC_FUT_fBVOCctrlPD: `24b-NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOCctrlPD_f19_f19.sh` (from 23b; all 19 species from CTRL_PD, relabelled to 2100)
- LCC_FUT_fBVOCctrlFUT: `24c-NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOCctrlFUT_f19_f19.sh` (from 23b; all 19 species from CTRL_FUT, relabelled to 2100)
- LCC_PD_fBVOClccPD: `14e-NF2000norbc_tropstratchem_nudg_lcc_fBVOClccPD_f19_f19.sh` (LCC land, its own LCC_PD emissions prescribed; 3 yr 2000–2002, user 2026-10-30; test of the matched-baseline assumption; auto-launched after the LCC_PD climatology)
- CTRL_FUT_fBVOCctrlFUT: `24e-NF2100ssp585norbc_tropstratchem_nudg_ctrl_fBVOCctrlFUT_f19_f19.sh` (CTRL land + restart as CTRL_FUT, its own emissions prescribed → FUT artefact art_FUT = CTRL_FUT − CTRL_FUT_fBVOCctrlFUT; 15 yr, auto-launched with 24c, user 2026-10-30). Not the same as `tests/24e-…` (= 1-day test of 24d)
- LCC_FUT_HRBVOC: `24f-NF2100ssp585norbc_tropstratchem_nudg_lcc_HRBVOC_f19_f19.sh s1|s2|s3` (output-only rerun of LCC_FUT -20261028 writing the 30-min BVOC h1 (`cam_diagnostics HR_BVOC_ONLY`), for a possible LCC_FUT_fBVOClccFUT; 3 parallel 5-yr segments: s1 hybrid 2000-04, s2/s3 branch from LCC_FUT 2005/2010; same-model check before build; merge with `preprocess/bvoc-emissions/merge_lcc_fut_hrbvoc.sh`; user 2026-11-04)
- LCC_FUT_fBVOClccPD: `24d-NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOClccPD_f19_f19.sh` (from 23b; all 19 species from LCC_PD, relabelled to 2100; needs an LCC_PD run with HR_BVOC_ALL; set LCC_PD_CASE)

**ISOP/MTERP only (`just-ISOP-MTERP/`, on hold: `exit 1` at the top)**
- LCC_PD_fBVOCctrlPD_IM: `just-ISOP-MTERP/14b-NF2000norbc_tropstratchem_nudg_lcc_fBVOC_f19_f19.sh`
- LCC_FUT_fBVOCctrlPD_IM: `just-ISOP-MTERP/24b-NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOC_f19_f19.sh`
- 2-day test: `tests/test_LCC_PD_fBVOC_2days.sh`

### Analysis aliases

| Alias | Environment and vegetation | Prescribed BVOC emissions |
|---|---|---|
| `CTRL_PD` | Present-day, control vegetation | Interactive |
| `LCC_PD` | Present-day, expanded vegetation | Interactive |
| `LCC_PD_fBVOCctrlPD_IM` | Present-day, expanded vegetation | ISOP, MTERP from `CTRL_PD` (existing run) |
| `LCC_PD_fBVOCctrlPD` | Present-day, expanded vegetation | All 19 MEGAN species from `CTRL_PD` |
| `CTRL_FUT` | Future, control vegetation | Interactive |
| `LCC_FUT` | Future, expanded vegetation | Interactive |
| `LCC_FUT_fBVOCctrlPD_IM` | Future, expanded vegetation | ISOP, MTERP from `CTRL_PD` (existing run; sensitivity) |
| `LCC_FUT_fBVOCctrlPD` | Future, expanded vegetation | All 19 MEGAN species from `CTRL_PD` |
| `LCC_FUT_fBVOCctrlFUT` | Future, expanded vegetation | All 19 MEGAN species from `CTRL_FUT` |
| `LCC_FUT_fBVOClccPD` | Future, expanded vegetation | All 19 MEGAN species from `LCC_PD` (planned) |

Suffix `_fBVOC<source run>` = run the prescribed emissions come from; `_IM` = ISOP and MTERP only.

### Extensions (2010-2014, continue runs within nudging data 2000-2015):
- `extend_nudg_runs_2010-2014.sh` (comment in/out the cases to extend)
- `extend_nudg_runs_2015-2025.sh phase1|phase2 [--check]` (10 new-chain nudged runs, 2015-01-01 → 2020-01-01 → 2026-01-01 with the `_6h_2000-2025` MET folder; switches `user_nl_cam` and the met path stored in the run-dir restart, `switch_case_to_met_2000_2025` in `cases-setup.sh`; excludes the b5xxx nodes)

### Quick LCC spin-ups (preliminary, superseded; no land-only step): `quick-spinups/`
- LCC_PD_quick_spinup: `quick-spinups/13bx-NF2000norbc_tropstratchem_quick_spinup_lcc_f19_f19.sh`
- LCC_FUT_quick_spinup: `quick-spinups/23bx-NF2100ssp585norbc_tropstratchem_quick_spinup_lcc_f19_f19.sh`

### Tests (`tests/`)
Short model test runs (1-day, 2-day, timing). The 1-day tests of the all-species fBVOC runs keep their old numbers: `tests/14c-…` = 14b, `tests/24c-…` = 24b, `tests/24d-…` = 24c, `tests/24e-…` = 24d.

- `auto_launch_new_chain.sh`: watcher that launches 13c and the nudged runs 13a/14a/23a/24a on the new (20261025) chain as each spin-up finishes (see header). It finds the scripts by number (`ls 13a-*.sh` etc.), so keep 13a, 13c, 14a, 23a, 24a unique.

### Watchers for the fBVOC artefact runs (`run_when_done/`)
Moved from `diagnostics/fbvoc-prescription-artefact/run_when_done/` on 2026-11-04 (user). Each waits for a run's archive job, then copies to NIRD, postprocesses, and reruns the matching notebook in `diagnostics/fbvoc-prescription-artefact/`. State in `pids/` (`*.ok`/`*.err`, gitignored), logs in `logs/`. Start from `cases-scripts/`: `nohup setsid bash run_when_done/<script> [args] >> run_when_done/logs/<script>.log 2>&1 &`.
- `run_when_done.sh` (CTRL_PD_fBVOCctrlPD old-chain test, finished 29 Oct), `run_replay_when_done.sh` (14d replay, finished 30 Oct), `run_14e_extension_when_done.sh` (LCC_PD_fBVOClccPD 2003–2007, finished 4 Nov; `ARCHIVE_JOB=manual` if st_archive was run by hand), `run_14e_to2014_when_done.sh` (LCC_PD_fBVOClccPD 2008–2014: submits `extend_case`, or takes `RUN_JOBID ARCHIVE_JOBID`; running).
