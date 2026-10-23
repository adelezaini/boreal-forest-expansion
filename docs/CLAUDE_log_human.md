# Project log: plain-language summary

> **Where things stand (updated every prompt)**
> The postprocessing is done (all 90 files). The forcing maps have been rebuilt.
> **Main problem (likely, not proven):** CTRL and LCC started from different land spin-ups. This probably distorts the LCC − CTRL "Total" signal, especially in the future and in the tropics.
> The fBVOC runs can't isolate the BVOC effect of forest expansion. In the future case they use present-day emissions, so the difference also includes the effect of the future climate.
> **D1/D2 are now standalone notebooks** (`D1_farfield_check.ipynb`, `D2_megan_budget.ipynb`); the D1/D2 code was removed from `src`. Both run and give exactly the same numbers as before. Their figures and tables now live next to them, in `diagnostics/other-BVOC-emission-magnitude/D1_farfield/` and `D2_megan_budget/`.
> **New, important:** the future 100-year land-only spin-up (LCC branch) ran with **pre-industrial CO₂ (284 ppm)** instead of ~1140 ppm: CLM was set to ignore the CO₂ in the forcing. The vegetation collapsed and has only partly regrown. In the future runs LCC differs from CTRL even far from the forest cells: −16 % leaf area, and wetter, warmer soil. Present day is fine for the short-term variables. Notebooks with figures: `diagnostics/check-CO2-bug-in-land-only/`. **Decision on reruns pending.**
> **New fixed-BVOC setup (session 20966a2c):** the CTRL scripts now also write the emissions of all 19 MEGAN species (for the new all-species fixed-BVOC runs). The existing fBVOC runs are renamed `LCC_PD_fBVOC_PD_IM` / `LCC_FUT_fBVOC_PD_IM` in the code ("IM" = only isoprene and monoterpenes prescribed). **The processed data files still have the old names, so the forcing maps won't find them until they are renamed (next step, needs your OK).**
> **Waiting on you:** whether to redo the CTRL spin-up, whether to commit the code, and the go for renaming the fBVOC data files.

One block per working window (a new block starts after more than 1 hour without prompts, or in a new session). Newest first.

---

## 2026-10-22 · 23:45 → 00:08 (23 min) · session 20966a2c
**Goal:** Prepare the new fixed-BVOC runs, which will prescribe all 19 MEGAN species. Step 1: emission output in the CTRL scripts + new run names.
**Done:**
- The CTRL_PD and CTRL_FUT scripts (13a, 23a) now save every 30 min the emissions of the 8 short-lived species, and monthly those of all 19 MEGAN species. Checked against the model code and the CTRL_PD species list.
- The existing fBVOC runs got the suffix `_IM` in all scripts, notebooks, README and CLAUDE.md. The planned runs will be `LCC_PD_fBVOC_PD` and `LCC_FUT_fBVOC_FUT`.
**Found:**
- In runs without MEGAN, the model just skips the missing emission fields with a log message; it doesn't crash.
**Open-next:**
- Rename the 30 processed fBVOC data files (commands to be written; not run).
- The user will upload the handoff file.
- Before rerunning CTRL: the 30-min output is ~8 GB per model year (~80 GB per run); do a 1-day test first.
- The future fixed-emission run would start from the LCC restart affected by the CO₂ bug. Decide this first.
**Files changed:** `cases-scripts/{13a,23a,cases-setup.sh,README.md,extend_nudg_runs_2010-2014.sh,test_LCC_PD_fBVOC_2days.sh}`, `postprocess/run_all_{parallel,postprocessing}.sh`, `src/.../plotting/forcing_maps.py`, `CLAUDE.md`, `analysis/forcing_maps.ipynb`, D1 notebook, 2 FUT-decomposition notebooks.

## 2026-10-23 · 00:05 → 00:13 (8 min) · session bd6c4048
**Goal:** Move the D1/D2 figures and tables out of `results/` into the diagnostics folder.
**Done:**
- 18 figures and 8 tables moved to `diagnostics/other-BVOC-emission-magnitude/D1_farfield/` and `D2_megan_budget/` (each with `figures/` and `tables/`).
- The run logs `D1.log` and `D2.log` moved too, into a `logs/` folder in each.
- The two notebooks now save there; CLAUDE.md paths updated.
**Open-next:** commit (the move shows in git as deleted files under `results/`).
**Files changed:** the two notebooks, `CLAUDE.md`, moved PNG/CSV files.

---

## 2026-10-22 · 20:45 → 00:00 (195 min) · session aebc129e
**Goal:** Check whether CTRL_FUT's vegetation differs from LCC_FUT's outside the forest-expansion region; then understand why.
**Done:**
- Traced both spin-up chains. CTRL_FUT had 20 years of land spin-up, LCC_FUT 140.
- Notebook `diagnostics/check-simulation-equilibrium/check_CTRL_FUT_vs_LCC_FUT_vegetation_state.ipynb`, written and run.
- Checked: the two surfdata files differ **only** in the PFT fractions at 46–82°N (all variables compared).
- Checked: the coupled future runs see ≈1140 ppm CO₂.
- Read the earlier equilibrium notebooks. They were correct (vegetation carbon was already visibly rising), but they checked each run alone and only inside the forest cells, so they could not see a run that is stable but in the wrong state.
- New notebook `diagnostics/check-CO2-bug-in-land-only/check_CO2_bug_in_land_only.ipynb` (figures: PD vs FUT spin-up histories, why the drift checks passed, LCC − CTRL for PD vs FUT, recovery estimate). Running now.
**Found:**
- The future 100-year land-only spin-up used **284 ppm CO₂ instead of ~1140 ppm**. Leaf area collapsed (2.5 → 0.95) and has only partly recovered.
- LCC_FUT − CTRL_FUT (2001–2009), outside the forest cells: leaf area −16 %, vegetation carbon −34 %.
- In the forest cells, compared with present day: PD expansion gives +13 % canopy height and +19 % vegetation carbon. FUT gives about 0 % height, −11 % carbon and −12 % leaf area. So **the future land-cover signal in our region is distorted by the bug**.
- Present day is affected too, but less, and in the opposite direction: +4 % leaf area outside the forest cells, from the longer LCC spin-up.
- CTRL_FUT north of 45°N: leaf area is stable; vegetation carbon is still growing ~4 % per decade.
- The 20-year coupled LCC spin-up did not repair it: after 29 years at the right CO₂, LCC still has −14 % leaf area north of 45°N.
- Before plan mode came back, I edited the land-only script `22b` (CO₂ setting) and created a CTRL twin `22a`. **Not run or submitted.** The user still has to decide whether to keep them or revert them.
- Second copy of the notebook, `check_CO2_bug_in_land_only_six_variables.ipynb`, adds the six equilibrium variables (TWS, soil water and soil temperature at 1 m, GPP, vegetation carbon, vegetation nitrogen). It includes 20-year rolling means, their derivative, verdict tables, and a CTRL vs LCC comparison of the short-term variables. Running. The original notebook is left unchanged.
- Known gap: TWS and vegetation nitrogen were not saved in the land-only runs or the LCC coupled spin-ups.
- **Why the CO₂ was wrong:** the forcing files (cplhist) *do* contain the right CO₂ (~1134 ppm), and the data atmosphere reads it. But CLM was set to "constant CO₂" (`CLM_CO2_TYPE=constant`), the default of the land-only setup, so it ignored the CO₂ from the forcing and used 284 ppm. Better fix than my earlier 22b edit: set `CLM_CO2_TYPE=diagnostic`, so CLM uses the CO₂ in the forcing, exactly like the coupled runs.
- The first CO₂-bug notebook run crashed on a corrupted cache file (an HDF5 file-locking glitch). Deleted the file and rerunning with file locking off.
- **CO₂-bug notebook done** (rerun OK; summary filled in):
  - Present day shows no collapse; the future collapse starts exactly with the low-CO₂ stage.
  - The per-run drift check "passes" even though the state is wrong.
  - Leaf area came back within ~10 years of the CO₂ fix, but only to 12–17 % below CTRL. Vegetation carbon would need ~160 more years.
- **Why the notebooks were slow:** xarray took ~5 s to open each history file on NIRD, against 0.3 s with plain netCDF4. With ~800 files that is about 1 hour. Switched the reader to netCDF4 with 8 files read in parallel: 240 files now take 26 s, with identical numbers.
- New helper `results/tables/logs/run_nb_inplace.py` runs a notebook in the `lcc-env` Jupyter kernel and **saves outputs and figures into the notebook**. No need to rerun it to see results.
- Two cache files had been written corrupted, probably by HDF5 file locking on `/cluster/home`. The notebooks now switch locking off, write caches safely, and rebuild a cache they cannot read.
- **Both CO₂ notebooks now run in ~2 min each, with all outputs saved inside the notebooks.**
- **Six-variable result:**
  - Within each run, soil water, soil temperature and water storage settle within 10–30 years.
  - In present day, CTRL and LCC have the **same** short-term state, so the requirement is met.
  - In the future, LCC's soil is wetter and warmer than CTRL's, especially in the tropics (+0.37 K at 1 m, 6× the year-to-year noise). That comes from the damaged vegetation, so **the CO₂ bug also affects the short-term variables**.
  - Soil temperature also jumps between stages (land-only runs are warmer), and the 20-year coupled LCC spin-ups have not fully shed that.
- **User's plan:** analyse the current outputs while starting the corrected runs. Agreed, with a split:
  - **safe now:** all present-day results, and the code and figures for the future;
  - **with a caveat:** BVOC_FUT;
  - **wait for the reruns:** any LCC_FUT − CTRL_FUT number.
  - MEGAN is affected mainly through leaf area (about −6 % per cell), but D2 already shows −250 Tg/yr globally, and the future local signal flips sign compared with present day.
- **Why the soil jumps when a spin-up hands over to a nudged run:** mostly the nudging itself. New notebook `diagnostics/impact-of-nudging-on-land/` compares the nudged CTRL_PD with the free run that supplied its winds (same years):
  - nudging makes the land cloudier: about 5 W/m² less sunshine on global land, 1 m soil 0.3 K cooler, a little less rain;
  - in the future the jump is bigger, and the boreal soils get much wetter, because the runs use present-day winds (kept on purpose);
  - the jump is the same in CTRL and LCC, so it cancels in LCC − CTRL;
  - the "drift" during 2001–2009 is mostly the shared weather sequence;
  - one exception: water storage and snow north of 45°N drift differently between the members (small, ~0.1 % per decade).
- Added the free met run (purple) to the six-variable figures.
- **Document `docs/setup_fix_FUT_landonly_CO2.md`:** problem, cause, what is not affected, two fix options (A: redo only the LCC land-only run; B: redo CTRL and LCC the same way, recommended if time allows), script changes, checks before submitting and after the runs, what can be analysed meanwhile, open decisions.
- **Spin-up output now also saves** canopy structure (TSAI, HTOP), the CO₂ seen by the land (PCO2, PBOT) and snow (FSNO, SNOWDP), in `clm_spinup_diagnostics` and `clm_long_spinup_diagnostics`. The six equilibrium variables were already there.
**Open / next:**
- (done) Figures of both CO₂-bug notebooks shown. The deciding question (user): are the **short-term** variables (water storage, soil water, soil temperature) in equilibrium? Carbon does not need to be.
- Decide: no rerun (FUT Total unusable as a land-cover effect), a partial rerun (only the LCC land-only run with the right CO₂ → nudged runs), or a full symmetric rerun.
- Keep or revert the `22a`/`22b` edits.
**Files changed:** `docs/setup_fix_FUT_landonly_CO2.md` (new); `cases-scripts/cases-setup.sh` (spin-up diagnostics); `diagnostics/impact-of-nudging-on-land/` (new notebook + outputs); `results/tables/logs/run_nb_inplace.py` (new); 2 new notebooks + outputs; `cases-scripts/22b-…` edited, `22a-…` new (not run); both logs

---

## 2026-10-22 · 19:48 → 21:14 (86 min) · session 5a5f936c
**Goal:** Make the D1 and D2 notebooks self-contained and remove the D1/D2 code from `src`.
**Done:**
- The new D1/D2 notebooks already contained all their code. Filled in the real case names and cleaned up the introductions.
- Deleted the old D1/D2 notebooks and the scripts that generated them; the new notebooks now have the plain names.
- Removed 7 modules from `src` that only D1/D2 used, and trimmed 2 more to the functions other code still needs. Everything deleted is still in git history.
- Checked: nothing else in the project used the removed code; the remaining package still imports.
- Ran both notebooks on the real data. Fixed 3 over-strict checks on the way. **All numbers match the old tables exactly** (D1: 96 rows; D2: 516 rows).
- D2 now also gives the background change (CTRL_FUT − CTRL_PD) and the region outside the modified cells.
**Found:** The first test run failed in both notebooks on two over-strict internal checks (rounding in D1; CLM's first month starting 30 min early in D2). Loosened both. **D1 now runs and gives exactly the same BVOC numbers as before.** D2 needed one more fix (CLM spells the unit `kg/m2/sec`). D1 now saves its summary as `D1_farfield_assessment.csv`; the old `D1_farfield_verdict.csv` is no longer updated.
**Open / next:**
- Commit (also includes these deletions).
- D1 no longer computes the "Total" (LCC − CTRL) contrasts. The old Total numbers are kept in `D1_farfield_regional_stats_with_Total_2026-10-21.csv`. Decide whether D1 should compute them again.
**Files changed:** `diagnostics/other-BVOC-emission-magnitude/` (2 notebooks renamed + edited, 4 files deleted), `src/boreal_forest_expansion/analysis/` and `diagnostics/`, `CLAUDE.md`, `results/tables/D1_*`, `D2_*` (regenerated) + figures, both logs

---

## 2026-10-22 · 19:24 → 19:58 (34 min) · session da72ac23
**Goal:** Document the codebase in `CLAUDE.md`.
**Done:**
- Added project sections to `CLAUDE.md`: what the project is, a folder map, the simulations table (labels ↔ case names, spin-up chains, contrasts), commands (postprocessing, running notebooks), key Betzy/NIRD paths, science pitfalls, working style.
- Checked several facts against the scripts (postprocessing options, paths, Python environment, case folders, queue).
- The logging rules were left as they are.
- Assessed an outside review of `CLAUDE.md`. The important points are correct:
  - "LCC − LCC_fBVOC isolates the BVOC response" was wrong. The FUT fBVOC run uses PD emissions with the year changed to 2100.
  - The spin-up statements were written too much as fact.
  - Writing to the output folder on NIRD should be allowed.
- Put the review into `CLAUDE.md` (opened and closed in this block):
  - correct meaning of the BVOC contrast;
  - spin-up statements marked as likely, not proven, with what the +0.25 W m⁻² number is;
  - a "Data checks" list;
  - code rules (notebooks first, `src/` only for reused code, no notebook generators);
  - data safety (protected inputs vs outputs that can be rebuilt);
  - `$PY` and the parallel-job count explained.
  - The logging rules are unchanged.
**Found:** The FUT prescribed emissions are the CTRL_PD climatology with only the year changed to 2100. No spin-up months are dropped twice.
**Open / next:**
- Science: check the D2 tables; decide on the CTRL re-spin-up; commit `CLAUDE.md` + `docs/`.
**Files changed:** `CLAUDE.md`, `docs/CLAUDE_log.md`, `docs/CLAUDE_log_human.md`

---

## 2026-10-22 · 19:26 → 19:30 (4 min) · session 1f288034
**Goal:** Check that automatic logging works in a new session; keep a record of solved items.
**Done:**
- The logging script is switched on and works in a new session (open since 2026-10-22 19:07).
- New rule: earlier Open items are never deleted from this log. When one is done, it goes under **Done** in the current block, with the date it was opened.
**Open / next:** Nothing for the logs. Science: check the D2 tables; decide on the CTRL re-spin-up.
**Files changed:** `docs/CLAUDE_log_human.md`, `docs/CLAUDE_log.md`

---

## 2026-10-22 · 19:07 → 19:56 (49 min) · session 12e1d74a
**Goal:** Make the project log update itself automatically.
**Done:**
- The logging rules are now in the project's `CLAUDE.md` (the instructions Claude reads), where you can see and edit them.
- A small script runs at every prompt. It tells Claude whether to continue the current block or start a new one, and it won't let Claude finish a reply without updating both logs.
- The script is switched on (you added it to `~/.claude/settings.json`) and it works.
- Fix: several sessions can run at once, so each session now updates **its own** block instead of "the top one".
**Open / next:** Nothing for the logs. Science: check the D2 tables; decide on the CTRL re-spin-up.
**Files changed:** `CLAUDE.md` (new), `docs/CLAUDE_log_human.md` (new), `docs/CLAUDE_log.md`, `~/.claude/hooks/boreal_log.py`

---

## 2026-10-21 (later): D1 results and MEGAN maps
**Found:**
- **D1:** the fBVOC runs change the forcing far from the modified area (tropics +0.05 W m⁻² in PD, −0.44 W m⁻² in FUT), which is more than the local effect.
- PD Total is clean. FUT Total has a +0.25 W m⁻² tropical offset from the spin-up mismatch.
- **MEGAN:** the PD summer monoterpene increase north of 45°N (+1.6 %) comes from vegetation composition, not from weather or the activity factor (γ).
**Done:** maps of the MEGAN emission factors (ε, γ); smaller significance dots on the maps.
**Open / next:** check the D2 tables.

## 2026-10-21: forcing maps rebuilt, spin-up problem found
**Found:**
- **CTRL and LCC use different land spin-ups.** LCC had an extra 100-year spin-up. In FUT, tropical vegetation in LCC is 31 % lower than in CTRL. This contaminates LCC − CTRL.
- fBVOC lacks the other BVOC compounds, which causes a chemistry artifact.
**Done:** rewrote the forcing-map code (fixed a bug: FUT Total now uses CTRL_FUT); imported the D1/D2 diagnostics.
**Open / next:** decide on a CTRL re-spin-up; get the ozone kernel; commit the code.

## 2026-10-20/21 (night): postprocessing sped up
**Done:** all 90 processed files were produced in ~26 min (before: hours). Fixed a bug that stopped land files from ever being processed.
