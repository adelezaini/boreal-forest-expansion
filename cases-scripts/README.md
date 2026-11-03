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
- LCC_PD_landonly_spinup: `12b-NF2000norbc_tropstratchem_landonly_spinup_lcc_f19_f19.sh` (100 yr, CPLHIST_PD forcing)
- CTRL_PD_landonly_spinup: `12c-NF2000norbc_tropstratchem_landonly_spinup_ctrl_f19_f19.sh` (CTRL twin of 12b)
- CTRL_PD_spinup: `13c-NF2000norbc_tropstratchem_spinup_ctrl_f19_f19.sh` (20 yr, land from 12c)
- LCC_PD_spinup: `13b-NF2000norbc_tropstratchem_spinup_lcc_f19_f19.sh` (20 yr, land from 12b)
- CTRL_PD: `13a-NF2000norbc_tropstratchem_nudg_ctrl_f19_f19.sh` (from 13c)
- LCC_PD: `14a-NF2000norbc_tropstratchem_nudg_lcc_f19_f19.sh` (from 13b)
- LCC_PD_fBVOCctrlPD: `14b-NF2000norbc_tropstratchem_nudg_lcc_fBVOCctrlPD_f19_f19.sh` (from 13b; all 19 MEGAN species from CTRL_PD)
- CTRL_PD_fBVOCctrlPD: `14c-NF2000norbc_tropstratchem_nudg_ctrl_fBVOCctrlPD_f19_f19.sh` (CTRL land + restart as CTRL_PD, its own 19 species prescribed → CTRL_PD_fBVOCctrlPD − CTRL_PD = prescription artefact; baseline for LCC_PD_fBVOCctrlPD. New chain, 15 yr, auto-launched with 14b (user 2026-10-29); the old-chain 3-yr test is case `-20261028`)
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
- CTRL_FUT_fBVOCctrlFUT: `24e-NF2100ssp585norbc_tropstratchem_nudg_ctrl_fBVOCctrlFUT_f19_f19.sh` (CTRL land + restart as CTRL_FUT, its own emissions prescribed → FUT artefact art_FUT; 15 yr, auto-launched with 24c, user 2026-10-30). Not the same as `tests/24e-…` (= 1-day test of 24d)
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

### Quick LCC spin-ups (preliminary, superseded; no land-only step): `quick-spinups/`
- LCC_PD_quick_spinup: `quick-spinups/13bx-NF2000norbc_tropstratchem_quick_spinup_lcc_f19_f19.sh`
- LCC_FUT_quick_spinup: `quick-spinups/23bx-NF2100ssp585norbc_tropstratchem_quick_spinup_lcc_f19_f19.sh`

### Tests (`tests/`)
Short model test runs (1-day, 2-day, timing). The 1-day tests of the all-species fBVOC runs keep their old numbers: `tests/14c-…` = 14b, `tests/24c-…` = 24b, `tests/24d-…` = 24c, `tests/24e-…` = 24d.

- `auto_launch_new_chain.sh`: watcher that launches 13c and the nudged runs 13a/14a/23a/24a on the new (20261025) chain as each spin-up finishes (see header). It finds the scripts by number (`ls 13a-*.sh` etc.), so keep 13a, 13c, 14a, 23a, 24a unique.
