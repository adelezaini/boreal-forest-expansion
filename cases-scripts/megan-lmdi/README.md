# MEGAN exact split: production branch runs

Option 1 of `analysis/MEGAN_ATTRIBUTION.md`. Each run is a branch of a new-chain nudged run that adds patch-level MEGAN output. A per-year job turns the output into the exact (LMDI) split, then deletes the raw files.

## Files

| File | What |
|---|---|
| `branch_meganpatch.sh RUN START [--days N] [--check-only]` | Creates and **builds** one branch case; never submits. Uses the parent's namelists verbatim, with SLIM output: CAM monthly + 30-min SFISOP/SFMTERP, CLM monthly MEG_*/GAMMA*, CLM tape 2 = 72 fields per patch every step. Stops before building if the XML or namelists differ from the parent's beyond history/start keys. |
| `launch_megan_lmdi.sh test PD` / `batch PD\|FUT YEARS…` | Builds and submits cases, records the plan and starts the watcher. `--plan-only` prints what it would do; `--no-submit` builds only. |
| `watch_megan_lmdi.sh PERIOD [--check]` | Login-node loop, every 10 min. When both runs of a year are archived (and both parents have that year's output), it runs `postprocess/megan_lmdi/reduce_year_job.sh` **on the login node**, one year at a time (≈ 3 h per year; `MEGAN_LMDI_RUN=sbatch` submits it to `preproc` instead). When it has finished, it copies the result to NIRD, along with both cases' **restarts** (one per model year, i.e. the end of every job and batch; history copies left out) to `BRL-FRST-XPSN_archive/<case>/rest/`, because /cluster/work deletes files after 42 days. `--check` prints the status of each year. |
| `postprocess/megan_lmdi/reduce_year_job.sh` | Run once per year (login node, or sbatch on `preproc`). Order: identity check of both branches against their parents (`check_identity.py`), then LMDI reduction (`reduce_megan_lmdi.py --year`), then deletion of the raw tape-2 files (`yes` / `dry` / `no`). In test mode it also runs the replay validation on 31 Jan + 1 Feb. |

State, plan, logs and outputs on work: `/cluster/work/users/adelez/megan-lmdi/<PD|FUT>/` (`plan.txt`, `chains.txt`, `<label>.{submitted,ok,failed,copied}`, `logs/`, `out/`). Final files go to `data/processed-data/megan-lmdi/megan_lmdi_<PERIOD>_<YEAR>.nc` (+ `logs/`).

## Parents and years

| Run | Parent (new chain) |
|---|---|
| CTRL_PD | `NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20261029` |
| LCC_PD | `NF2000norbc_tropstratchem_nudg_lcc_f19_f19-20261028` |
| CTRL_FUT | `NF2100ssp585norbc_tropstratchem_nudg_ctrl_f19_f19-20261028` |
| LCC_FUT | `NF2100ssp585norbc_tropstratchem_nudg_lcc_f19_f19-20261028` (no 30-min output, so its identity check uses the monthly means only) |

The parents kept restarts **only at 2005, 2010 and 2015**; the other yearly restart folders are empty (found 2026-11-04). The user chose to change the years rather than regenerate restarts. So each run has **two chains**, one case each:

- chain from 2005-01-01: years 2005–2008 (2009 possible);
- chain from 2010-01-01: years 2010–2012 (2013 and 2014 possible).

- **chain from 2000-01-01 (user 2026-11-04, instead of 2015–2017):** a hybrid start from the parent's coupled spin-up restart, exactly as the parent started (precedent: LCC_FUT_HRBVOC s1, identical to LCC_FUT). Year 2000 is the spin-up year dropped in every analysis: it gets the identity check, then its raw files are deleted without a split (plan mode `only`). Years used: 2001–2003.
- (possible, not planned) chain from 2015-01-01: years 2015–2017 (up to 2019). It needs the extended met folder `_6h_2000-2025` (MET run 2015–2025, segment 1 to 2021 running on 4 Nov), and the branch script switches `met_data_file`/`met_filenames_list` to it. Its identity check needs the parents' own 2015–2017 output (`extend_nudg_runs_2015-2025.sh`, not submitted yet): the watcher waits for it.

**Years (user 2026-11-04 16:17, fewer years): 2000–2002 (2000 discarded), 2005–2006, 2010–2011 = 6 years: 2001, 2002, 2005, 2006, 2010, 2011.** (Earlier plans: 10 years 2001–03/05–08/10–12; 7 years 2005–08/10–12.) The restart at the end of every job (one per model year) stays in the archive. The next batch continues each chain from the last one, e.g. a batch 2005–2006 ends with `rest/2007-01-01-00000`, and the next batch starts there. The watcher also copies the restarts to NIRD. Each job runs one model year (≈ 14 h, 30 h wall limit). A batch sets `RESUBMIT = years − 1` per chain, and `CONTINUE_RUN=TRUE` when the chain already exists. A batch has to continue each chain from where it stands.

Suggested batches (PD; FUT the same):

1. `batch PD 2000 2001 2005 2010`
2. `batch PD 2002 2006 2011`

The launcher refuses a batch in four cases: the production test has not passed; an earlier year of the same period is not yet reduced, or has failed; the years are not contiguous within a chain; a chain is not at the batch's first year.

## Order (every submission needs the user's OK)

1. `bash launch_megan_lmdi.sh test PD`: CTRL_PD + LCC_PD from 2005-01-01, **2 jobs × 30 days = 2 months + 1 day** (to 2005-03-02 00:00), restart on 31 Jan. Approved in principle 3 Nov as a 32-day test; start date 2005 and 2 × 30 days decided by the user on 2026-11-04. It tests two complete months, two month boundaries and a job restart (continuation, 2nd archive step) before production. ≈ 2,500–2,800 core-hours, ≈ 70 GB raw (kept; delete step is a dry run).
2. Check the test log: `logs/PD_test60d.*log` (identity Jan + Feb, replay on 30–31 Jan, 1 Feb, 28 Feb, 1 Mar, reduction checks, dry-run delete).
3. PD batch 1 → compare LMDI with the approximate split for its years → PD batches 2–3 → FUT the same way.

## Tests done (2026-11-04)

- `check_identity.py` on the old-chain 5-day test vs CTRL_PD `-20261023`: 30-min SFISOP/SFMTERP **PASS** (6,635,520 values, 0 differ; steps matched by time, because the branch's daily files start at 00:30 and the parent's at 00:00). Monthly **FAIL**, as expected: a 5-day run has no complete month.
- Launcher `--plan-only`: test, new chains, gate (test not passed; earlier year not reduced), year outside the chains, non-contiguous years, chain not at the first year.
- `preproc` partition, 4 Nov 15:30: jobs on b5203 and b5204 printed `lmod/init/bash: Invalid argument` and hung, even a trivial "load module, import netCDF4" job, whether submitted from Claude's shell or from a clean login shell. That is why the reduction runs on the login node by default. b5203 is excluded from case submissions as well.
- Watcher end to end, test state on /cluster/work, old 5-day pair: started the reduction on login-3; the identity check failed as expected (monthly) → `.failed` → watcher exits. Success path: `.ok` → file and logs copied with `cp -n` + `cmp` → `.copied`.
- `reduce_megan_lmdi.py --year 2005 --delete-dry-run` on the 5-day pair with the module Python: checks 8.9 × 10⁻¹⁶ / 9.0 × 10⁻¹⁶ / 0 (same as 29 Oct), 26 s per day, dry run lists 10 files (5.9 GB).
- `branch_meganpatch.sh --check-only` (case set up and compared with the parent, not built, case folder then deleted): CTRL_PD 32-day test from 2005 and LCC_FUT from 2010. XML and namelists match the parent apart from history/start keys. The first CTRL_PD try stopped on `CAM_AEROCOM` (the parent has TRUE), so the script now copies it from the parent.
- Restart copy (4 Nov, 15:58): watcher test on the old 5-day cases, rest/ → test NIRD folder, 17 files per case, the 2 history copies excluded. 2015 chain `--plan-only` OK; 2020 refused.
- 2000 chain (4 Nov, 16:10): `--check-only` CTRL_PD from 2000 (hybrid from `…spinup_ctrl_f19_f19-20261026` 0021-01-01): XML and namelists match the parent apart from history output and run bookkeeping (no start-file difference). Plan-only batch `2000 2001 2005 2010` OK; a chain-2000 batch that doesn't start at 2000 is refused.
