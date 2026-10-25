# Project log: plain-language summary

> **Where things stand (updated every prompt)**
> The postprocessing is done (all 90 files). The forcing maps have been rebuilt.
> **Main problem (likely, not proven):** CTRL and LCC started from different land spin-ups. This probably distorts the LCC − CTRL "Total" signal, especially in the future and in the tropics.
> The fBVOC runs can't isolate the BVOC effect of forest expansion. In the future case they use present-day emissions, so the difference also includes the effect of the future climate.
> **D1/D2 are now standalone notebooks** (`D1_farfield_check.ipynb`, `D2_megan_budget.ipynb`); the D1/D2 code was removed from `src`. Both run and give exactly the same numbers as before. Their figures and tables now live next to them, in `diagnostics/other-BVOC-emission-magnitude/D1_farfield/` and `D2_megan_budget/`.
> **New, important:** the future 100-year land-only spin-up (LCC branch) ran with **pre-industrial CO₂ (284 ppm)** instead of ~1140 ppm: CLM was set to ignore the CO₂ in the forcing. The vegetation collapsed and has only partly regrown. In the future runs LCC differs from CTRL even far from the forest cells: −16 % leaf area, and wetter, warmer soil. Present day is fine for the short-term variables. Notebooks with figures: `diagnostics/check-CO2-bug-in-land-only/`. **Decision on reruns pending.**
> **New fixed-BVOC setup (session 20966a2c):** the CTRL scripts now also write the emissions of all 19 MEGAN species (for the new all-species fixed-BVOC runs). The existing fBVOC runs are renamed `LCC_PD_fBVOC_PD_IM` / `LCC_FUT_fBVOC_PD_IM` in the code ("IM" = only isoprene and monoterpenes prescribed). **The processed data files still have the old names. The rename commands are ready but not run; the forcing maps won't find the files until they are.** The emission script now covers all 19 species (tested on fake data). CTRL reruns (15 yr) are done. All-species fixed-emission runs (14c, 24c, 24d) passed their 1-day tests and are running (15 years, ~2 days); provisional, on the current set of runs.
> **Spin-up reruns (session 0c58bc16):** scripts ready, not run: FUT 22b/22c (CO₂ fixed) → 23b/23c; PD 12b/12c → 13b/13c (optional).
> **Significance test maps (01:22):** `analysis/test_significance_marking.ipynb` compares dots on significant cells with marks on non-significant ones (IPCC AR6 style); figures are now visible inside the notebook. **Chosen and now default:** thin grey hatching on non-significant cells, ocean not faded. The forcing maps now use the fBVOC file names as they are on disk, and `forcing_maps.ipynb` runs fully (figures in `results/figures/`).
> **Runs (01:38):** CTRL_PD and CTRL_FUT (15 yr), the LCC extensions and three land-only spin-ups are all running. The future 1-day test passed all checks. Its archiving step failed on a filesystem error, but the output is safe. Its archiving has since been redone and succeeded. The present-day test also passed all checks. Archived (compressed) hourly output: about **28 GB per 15-year run** (the earlier 116 GB was the uncompressed file).
> **Land-only spin-ups (16:33):** the CO₂ is now right (≈370 ppm PD, ≈1134 ppm FUT), but all three runs **stopped early** on filesystem errors during archiving: PD LCC at year 20, FUT CTRL at 10, FUT LCC at 40 (of 100). The PD CTRL land-only run was never started. **The coupled LCC spin-ups cannot start yet.** Restarted at 16:37; all three are running again (16:38). The stops were caused by temporary filesystem errors.
> **New problem (16:40):** the future LCC extension crashed on its very last day (31 Dec 2014). The nudging data end at 1 Jan 2015 00:00, and the model needs one more step. Year 2014 must be rerun. The PD LCC extension will hit the same wall in about half an hour, and CTRL_PD/CTRL_FUT at their end. The PD LCC extension did crash the same way. **Fixed (17:40):** the last nudging file now has 3 extra 6-hourly records (copies of 31 Dec); the original is saved in `data/nudging-met-backup/` with a README. Year 2014 of both LCC extensions is rerunning (~3 h each).
> **BVOC emissions notebooks (17:55):** the three overlapping notebooks in `diagnostics/FUT-fBVOC-background-lcc-effect-decomposition/` are now one, `bvoc_emissions_decomposition.ipynb`. The PD-vs-FUT notebook has run: forest expansion slightly **raises** northern BVOC emissions in present day (+0.4 Tg/yr isoprene) but **lowers** them in the future (−2.6 Tg/yr). Most of the future drop is outside the cells whose vegetation changed. **Likely reason (18:22):** leaf area is lower in LCC_FUT than CTRL_FUT almost everywhere north of 45°N (−0.4 m²/m² in summer, also where vegetation did not change). That looks like the leftover of the low-CO₂ land spin-up bug, not the effect of the forests.
> **Vegetation-state maps (18:35):** the CTRL_FUT vs LCC_FUT check notebook now uses the same thin grey hatching on non-significant cells as the forcing maps; rerun, results unchanged.
> **Expansion maps (18:55):** in the PD-vs-FUT notebook the present-day map now has its own colour scale (its changes are ~5× smaller), so its pattern is visible; future and interaction still share one scale.
> **All runs finished (25 Oct):** the three land-only spin-ups reached year 100 with the right CO₂; the LCC extensions (2014 rerun) and the new 15-year CTRL_PD/CTRL_FUT runs went through to 2015 without errors, so the nudging-file fix worked. **Equilibrium check (14:40):** all three land-only runs are in short-term equilibrium at year 100 (new notebook in `diagnostics/check-simulation-equilibrium/check-land-only-equilibrium-after-co2-fix/`). The coupled spin-up scripts 13b, 23b and 23c now point to them; the copy to NIRD is done (14:45). **Coupled spin-ups 13b, 23b, 23c running since 15:15** (20 years each, ~3 days), each starting from its new land-only state. **PD made symmetric too (15:10):** the PD CTRL land-only run (12c) is running since 15:16 (~13 h); then 13c (~3 days), then CTRL_PD rerun (~2.5 days).
> **Output folders renamed (15:31):** every diagnostics notebook now writes to `<notebook name>_outputs/` next to it (also the older equilibrium and D1/D2 folders). Cached `.nc` files sit in `cache/` subfolders, which git ignores; they are safe to delete and are rebuilt automatically. The CO₂-bug notebooks can run again (mask path fixed). Rule in `CLAUDE.md`.
> **Land-only equilibrium notebook (21:35):** regions are now modified cells, global land and tropics; the only old run shown is FUT_LCC_old. FUT_CTRL was hidden behind FUT_LCC (they are identical outside the modified cells); it is now drawn as a thin line on top. Rerun; verdict unchanged (all three runs in equilibrium).
> **Vegetation-state notebook (14:50):** now shows only three regions: global land, modified cells, all unmodified land. Rerun; conclusions unchanged.
> **Status 16:20:** running: PD CTRL land-only 12c, coupled spin-ups 13b, 23b, 23c (all since 15:15). **The BVOC-climatology jobs submitted at 16:12 (CTRL_PD and CTRL_FUT, all 19 species) all failed at once:** the compute nodes can't find the Python on NIRD.
> **Status 21:20:** 12c at year 40 of 100 (done around 03:30). 13b/23b/23c running. **New since 17:11:** all-species fBVOC runs 14c (LCC_PD_fBVOCctrlPD), 24c (LCC_FUT_fBVOCctrlPD), 24d (LCC_FUT_fBVOCctrlFUT) are running; their 1-day tests passed.
> **BVOC climatologies (22:45):** done; all 76 files are in the shared folder, and the duplicate copies in the work folder have been deleted (29 GB freed). From now on the scripts **move** each finished file to the shared folder. **Processed files:** no rename. When the current fBVOC runs (14c/24c/24d, for the meeting) are postprocessed, the existing 2001–2009 files first move to `postprocessing/2001-2009-pre-co2-fix/`; after the CO₂ fix the 2001–2014 files will go to `2001-2014-pre-co2-fix/`.
> **Waiting on you:** the go for one commit (CLAUDE.md, a comment in `forcing_maps.py`, the two logs, `run_nb_inplace.py`). **Automatic launches (since 22:57):** a watcher on login-3 starts 13c when 12c finishes (~03:30, 26 Oct), and each nudged run (13a, 14a, 23a, 24a) as soon as its coupled spin-up finishes, after copying the spin-up to NIRD and pointing the script at it. If a run stops early, that branch halts and the log says so. Check: `bash cases-scripts/auto_launch_new_chain.sh --check`. The fBVOC runs on the new chain are not automated yet.
> **New analysis notebooks (00:16):** `analysis/forcing_maps.ipynb` is split into `radiative_forcing.ipynb` (Ghan decomposition: 12 annual + 12 seasonal figures), `bvoc-soa-cloud-interactions.ipynb` and `biogeophysical-hydro.ipynb` (hydrology, snow/albedo, surface energy, sunlight at the surface, water budget). New figures in `results/figures/` (old ones in `first-round/`, reproduced exactly). Runoff and water storage were added to the processed data (new HYDRO files, 2001–2009). Present day north of 45°N: LCC − CTRL warms by **+0.24 W m⁻²**, mostly through the clear-sky term (albedo, +0.37), partly offset by clouds (−0.11). **Update (00:0x):** the LCC−CTRL grids now have a 4th row, CTRL_FUT − CTRL_PD (the climate change alone). The water budget now closes everywhere (< 1 mm/yr) after adding ice runoff from glaciers. **Attribution notebook (00:40):** `analysis/pd-fut-attribution.ipynb` explains the PD/FUT flip. In FUT, almost all of it is clouds: the LCC runs emit far more BVOC than the fixed-emission runs (which get present-day emissions), giving more SOA, more droplets and brighter clouds (−0.7 W m⁻²); the same effect appears with the opposite sign in fixed-BVOC − CTRL (+0.97). So the FUT BVOC contrast mostly measures future vs present-day emissions. In PD, the lower SOA in LCC − fixed-BVOC shows up all year, also in winter, so it comes from the fixed-BVOC setup (probably the missing other MEGAN compounds), not from the forests. Not committed.

One block per working window (a new block starts after more than 1 hour without prompts, or in a new session). Newest first.

---

## 2026-10-25 · 22:47 → 00:38 (111 min) · session 7648e6ae
- **Goal:** more radiative-forcing maps (Ghan split per contrast), maps with one row per contrast, and the processes behind the forcing (hydrology, snow, surface energy, sunlight at the surface).
- **Done:** 12 Ghan figures + 12 seasonal ones; 10 contrast-grid figures; water-budget table and 2 charts. Three notebooks replace `forcing_maps.ipynb`; all run with outputs saved. New runoff/water-storage data for all 6 runs.
- **Found:** PD, north of 45°N: forest expansion +0.24 W m⁻² (clear-sky/albedo +0.37, clouds −0.11, aerosol ~0). The BVOC part in PD is +0.13 (clouds +0.07, clear-sky +0.05). In FUT the BVOC contrast is strongly negative in summer (−2.3 W m⁻² SW, clouds). The water budget closes over the changed cells, not over the other northern land (+28 mm/yr).
- **Done:** water-budget gap closed by adding ice runoff (opened and closed in this block); 4th row CTRL_FUT − CTRL_PD in all LCC−CTRL figures.
- **Done:** attribution notebook `pd-fut-attribution.ipynb` (6 analyses, 8 figures, 4 tables) and fixed-BVOC − CTRL Ghan maps.
- **Found (attribution):** FUT BVOC contrast ≈ future vs present-day emissions acting through clouds; PD SOA/aerosol deficit is a setup offset (present in winter too).
- **Open/next:** all results are provisional (old CTRL version); commit when you say so.
- **Files changed:** `src/.../plotting/forcing_maps.py`, `src/.../postprocess/variables.py`, `postprocess/run_postprocess.py` (docstring), `CLAUDE.md`, `analysis/README.md`, new `analysis/{radiative_forcing,bvoc-soa-cloud-interactions,biogeophysical-hydro}.ipynb`, removed `analysis/forcing_maps.ipynb`; new `analysis/pd-fut-attribution.ipynb`; new data `*_lnd_HYDRO_2001-2009.nc`, `results/tables/water_budget_2001_2009.csv`.

## 2026-10-25 · 21:53 → 23:05 (72 min) · session 3b25e01e
- **Goal:** where are the BVOC climatologies? Which files would the fBVOC rename touch? Make the scripts move files instead of copying them.
- **Done:** the climatologies are finished and in the shared folder. The scripts now delete the work copy once the shared copy has been checked as identical.
- **Found:** the 19 future-run emission files with year-2000 dates were missing from the shared folder (now copied). The rename is dropped: old processed files will move to `2001-2009-pre-co2-fix/` instead.
- **Done:** automatic launcher started for 13c and the nudged runs 13a/14a/23a/24a on the new spin-up chain.
- **Open/next:** decide whether the fBVOC runs on the new chain should also be automated. When 14c/24c/24d finish: move the old processed files to `2001-2009-pre-co2-fix/`, then postprocess 14c/24c/24d when they finish.
- **Files changed:** `preprocess/bvoc-emissions/{run_bvoc_climatology_array.sh, create_bvoc_emissions_climatology.sh, check_bvoc_climatology.py, create_bvoc_emissions_climatology_staged.py (comment), README.md}`, `cases-scripts/24e*.sh` (comments), `CLAUDE.md`, `forcing_maps.py` (comment only), new `cases-scripts/auto_launch_new_chain.sh`, `cases-scripts/README.md`.

## 2026-10-25 · 21:28 → 21:35 (7 min) · session af52cc01
**Goal:** clearer plots in the land-only equilibrium notebook.
**Done:** regions changed to modified cells / global land / tropics; PD_LCC_old dropped, only FUT_LCC_old kept as reference; FUT_CTRL made visible; rerun with outputs saved; summary updated.
**Found:** FUT_CTRL was missing from plots because it is identical to FUT_LCC everywhere except the modified cells.
**Open / next:** nothing new.
**Files changed:** `diagnostics/check-simulation-equilibrium/check-land-only-equilibrium-after-co2-fix/check_land_only_equilibrium_after_co2_fix.ipynb` (+ its outputs).

## 2026-10-25 · 16:15 → 16:16 (1 min) · session dc6addbf
**Goal:** Understand a git warning when staging the equilibrium notebooks.
**Done:** Checked: everything was staged except `__pycache__`, which git ignores on purpose. 200 files staged in total, not committed yet.
**Found:** The warning is harmless.
**Open / next:** Commit when ready.
**Files changed:** both logs.

## 2026-10-25 · 21:17 → 21:25 (8 min) · session dc9990de
**Goal:** Table of the previous round of runs, in the same format as the running ones.
**Done:** Tables of the previous round (23–25 Oct, all finished) and of the current queue.
**Found:** The queue has changed since 16:12. 12c is at year 40/100. Three new all-species fBVOC runs (14c, 24c, 24d) were started at 17:11–17:30.
**Open / next:** nothing new.
**Files changed:** both logs.

## 2026-10-25 · 16:12 → 16:20 (8 min) · session dc9990de
**Goal:** Which runs are going, and what was started in the last round.
**Done:** Checked the queue. Running since 15:15: 12c (PD CTRL land-only, ~7 h), 13b, 23b, 23c (coupled spin-ups, 20 yr).
**Found:** The 19-species BVOC climatology jobs (CTRL_PD and CTRL_FUT, submitted 16:12) all failed within 10 s: the Python on NIRD is not found on the preproc nodes.
**Open / next:** Fix the Python path in `run_bvoc_climatology_array.sh` and resubmit (whoever submitted it).
**Files changed:** both logs.

## 2026-10-25 · 15:37 → 17:44 (127 min) · session 20966a2c
**Goal:** Keep the original ISOP/MTERP scripts; keep run versions up to date everywhere; start the all-species fixed-emission runs on the current set of runs (for the meeting).
**Done:**
- Original ISOP/MTERP-only scripts and plotting notebook kept in `preprocess/bvoc-emissions/prescribe-just-ISOP-MTERP/`; the main folder has a new 19-species plotting notebook (CTRL_PD vs CTRL_FUT; runs once the files are copied) and a README with the workflow.
- CLAUDE.md now lists the current run versions (new CTRL_PD and CTRL_FUT, 15 years) and a checklist of what to update and rerun whenever a run gets a new version.
- New names: the old fixed-emission runs are `LCC_PD_fBVOCctrlPD_IM` / `LCC_FUT_fBVOCctrlPD_IM`; the new ones `LCC_PD_fBVOCctrlPD`, `LCC_FUT_fBVOCctrlPD`, `LCC_FUT_fBVOCctrlFUT` (scripts 14c, 24c, 24d). `LCC_FUT_fBVOClccPD` has its script (24e), but it waits for the new spin-ups: it needs an LCC_PD run with emission output (14a now writes it); the script refuses to run until that case name is filled in.
- Emission files from the new CTRL runs (19 species, 2001–2014) are made and checked: all 38 match the model output (to 0.00003 %). Future emissions are 1.7–4× present-day (isoprene 517 → 892 Tg/yr).
- All three fixed-emission runs started (1-day test + 15-year run each): 14c (jobs 1780292 test, 1780293 run), 24c (1780311 test, 1780317 run), 24d (1780315 test, 1780312 run).
**Found:**
- All three 1-day tests passed (14c, 24c, 24d): MEGAN off, all 19 emission files read by the model, emissions present. The three 15-year runs are running (~2 days).
- The first submission failed in seconds: the cluster nodes can't see the NIRD Python. Fixed with the system Python module (same results).
**Open-next:**
- Finish emission files → shift to year 2100 → copy → start 1-day tests + the three 15-year runs.
- Your rename of the old fixed-emission data files (commands in chat), and moving the old CTRL processed files before reprocessing.
- When the new spin-ups finish: follow the CLAUDE.md checklist, regenerate emissions, rerun the fixed-emission runs, add LCC_FUT_fBVOClccPD.
**Files changed:** CLAUDE.md, cases-setup.sh (new function), 14a, new 14c/24c/24d + test scripts, README, postprocess scripts, preprocess/bvoc-emissions (defaults, array script, checker), forcing_maps.py comment, D1 + decomposition notebooks (names).

## 2026-10-25 · 14:45 → 14:50 (5 min) · session af52cc01
**Goal:** simpler region set in the CTRL_FUT vs LCC_FUT vegetation-state notebook.
**Done:** regions reduced to global land, modified cells and all unmodified land; notebook rerun with outputs saved; summary tables updated.
**Open / next:** nothing new.

## 2026-10-25 · 14:38 → 16:24 (106 min) · session 0521733a
**Goal:** consistent output folder names (`<notebook name>_outputs`); decide whether the `.nc` files are needed; tidy the rest.
**Done:**
- All diagnostics output folders renamed (6 in the first round, then the old `equilibrium_outputs/` split into 7 per-notebook folders, and D1/D2); notebooks point to the new names.
- `.nc` cache files moved to `cache/` subfolders; git now ignores every `cache/` folder; rule added to `CLAUDE.md`.
- Mask path in the two CO₂-bug notebooks fixed (opened earlier today, session 035c87f8).
- Test reruns of three notebooks: no errors, they read the moved caches.
- Full rerun of the same three with the caches rebuilt from the model archive (16:24): no errors, new caches exactly identical to the old ones. Vegetation-state tables identical to the committed version for the three remaining regions; the only change is the two regions dropped earlier today.
**Found:** the `.nc` files are only caches of annual means. Without them a rerun rereads ~800 model files (~15 min). They take ~0.9 GB of home space. The mask file `modified_cells.nc` is an input, not a cache, so it stays where it is.
**Open / next:** commit (the moved files that git tracked show as deleted + new until committed).
**Files changed:** 15 notebooks (paths only) and their output folders; `CLAUDE.md`; `.gitignore`; logs.

## 2026-10-25 · 14:16 → 15:21 (65 min) · session 035c87f8
**Goal:** how did the last runs go; then check the land-only equilibrium, copy to NIRD, fix the scripts.
**Done:**
- 2014 reruns of the LCC extensions finished and archived (open since 2026-10-23 16:33).
- The three land-only spin-ups ran to year 100 without further stops (open since 2026-10-23 16:33).
- CTRL_PD and CTRL_FUT 15-year runs finished (2000–2014, with the hourly BVOC output).
- Equilibrium check of the land-only runs: new notebook, run with outputs saved. All short-term variables are in equilibrium (opened this block).
- Coupled spin-up scripts 13b, 23b, 23c point to the new land-only runs (opened this block).
- Land-only runs copied to NIRD (opened this block).
**Found:** CO₂ stayed right (≈370 ppm PD, ≈1135 ppm FUT). The land-only forcing repeats every 10 years, so the old "last-10-year trend" test mistakes the forcing sequence for drift; comparing one 10-year cycle with the previous one shows the drift is far below the year-to-year spread.
- Coupled spin-ups 13b, 23b, 23c submitted and running (opened this block).
- New rule: every nudged run is 15 years (2000–2014). Written in `CLAUDE.md`; scripts 14a, 14b, 24a, 24b changed from 10 to 15 years (13a, 23a already were).
- fBVOC runs (14b, 24b) on hold until the all-species BVOC set-up is ready: rule in `CLAUDE.md`, and both scripts now stop at the first line.
- PD symmetric chain decided: 12c launched (opened 2026-10-23 as a pending decision).
- 12c submitted and running; script 13c now points to it (opened this block).
**Open / next:** after 12c: copy to NIRD, launch 13c; after 13c: rerun CTRL_PD; fix the mask path in the moved CO₂-bug notebooks.
**Files changed:** new notebook + `check_land_only_equilibrium_after_co2_fix_outputs/` in `diagnostics/check-simulation-equilibrium/check-land-only-equilibrium-after-co2-fix/`; `cases-scripts/13b`, `23b`, `23c` (LAND_CASE); `13c` (LAND_CASE); `14a`, `14b`, `24a`, `24b` (15 yr), `14b`, `24b` (hold); `CLAUDE.md`; logs.

## 2026-10-23 · 18:44 → 18:55 (11 min) · session 0ec901d3
**Goal:** make the weak present-day expansion pattern visible on the maps.
**Done:** PD panels get their own colour scale; FUT and Interaction share one; extreme 2 % of cells clipped. Notebook rerun with outputs saved.
**Found:** PD expansion raises emissions over western Canada, Alaska and eastern Siberia, with lower emissions along the southern edge of the changed area.
**Open / next:** old map PNGs with the previous names are still in the output folder (can be deleted).
**Files changed:** `diagnostics/FUT-fBVOC-background-lcc-effect-decomposition/bvoc_expansion_PD_FUT_interaction.ipynb`, its map PNGs, logs.

## 2026-10-23 · 18:30 → 18:35 (5 min) · session 0ec901d3
**Goal:** use the hatching style in the CTRL_FUT vs LCC_FUT vegetation-state maps.
**Done:** dots replaced by grey hatching on non-significant cells (p ≥ 0.05); notebook rerun with outputs saved.
**Found:** nothing new; numbers unchanged.
**Open / next:** none.
**Files changed:** `diagnostics/check-simulation-equilibrium/check_CTRL_FUT_vs_LCC_FUT_vegetation_state.ipynb`, its `B_delta_maps.png`, logs.

## 2026-10-23 · 17:43 → 18:46 (63 min) · session e2a259e9
**Goal:** one notebook instead of three duplicates; run the PD-vs-FUT interaction notebook.
**Done:** merged into `bvoc_emissions_decomposition.ipynb` (all sections + maps + conclusions), deleted the other two and their output folders; ran both notebooks with outputs saved (set the LCC_PD path, which was missing).
**Found:** expansion effect on emissions (≥45°N, Tg/yr, isoprene / monoterpenes): PD +0.43 / +0.18, FUT −2.61 / −3.85. The sign flips every year. 92 % / 69 % of the future drop is in cells whose vegetation did **not** change.
**Then:** switched on the last sections (temperature, light, leaf area, plant-type changes, check of the fixed-emission run, cloud/radiation response); they were off only because their file paths had never been filled in. Small fix so land-model fields line up with the atmosphere grid. Re-ran: everything works (18:45).
**Found too:** in the future runs with LCC, leaf area is lower than in CTRL nearly everywhere north of 45°N, all year round, even where vegetation did not change. Temperature and sunlight go *up*, so the drop in emissions follows the lost leaf area. This most likely comes from the low-CO₂ land spin-up bug, not from the new forests (not proven). The fixed-emission run gets the right emissions (within 0.05 %).
**Open / next:** look at the new plots; the future fixed-emission run (`LCC_FUT_fBVOC_FUT`) does not exist yet, so the clean cloud/radiation comparison is still missing.
**Files changed:** `diagnostics/FUT-fBVOC-background-lcc-effect-decomposition/` (2 notebooks + output folders), logs.

## 2026-10-23 · 16:33 → 17:42 (69 min) · session 035c87f8
**Goal:** are we ready to start the coupled LCC spin-ups (PD and FUT)?
**Done:** checked the three new land-only runs: settings, progress, and the CO₂ CLM actually sees.
**Found:** CO₂ is correct now. But the runs are not finished: each stopped when the archiving step hit a filesystem read/write error, which also stops the automatic resubmission. The PD CTRL land-only run (12c) does not exist. The coupled scripts still point to the old land runs.
**Restarted (16:37):** the three runs are running again. Cause of the stops: temporary filesystem errors during archiving.
**Found too:** the FUT LCC extension crashed at 31 Dec 2014 because the nudging data stop at 1 Jan 2015 00:00. The other nudged runs ending in 2014 will crash the same way.
**Fixed:** the nudging data now go past 1 Jan 2015 (3 records copied from 31 Dec; script `preprocess/nudging/extend_last_met_file.py`, original backed up in `data/nudging-met-backup/`). Year 2014 of LCC_PD and LCC_FUT resubmitted.
**Open / next:** check the 2014 reruns finish and archive; decide on 12c; when the runs reach year 100, copy them to NIRD and update `LAND_CASE` in 13b/23b (and 13c/23c).
**Files changed:** new `preprocess/nudging/extend_last_met_file.py`, `data/nudging-met-backup/` (backup + README); patched met file in `/cluster/shared/…/inputForNudging/AZ/…_6h_2000-2015/`; logs.

## 2026-10-23 · 01:40 → 01:45 (5 min) · session 78f6d842
**Goal:** how to check there is room for the hourly output; finish the 1-day test checks.
**Done:** checked the quotas on Betzy (`dusage`). The project area is at 920 GB of 1 TB. The model archive (`/cluster/work`) holds 178 GB. The NIRD disk as a whole is 98 % full. The present-day 1-day test passed all checks (check open since 01:36). The future test is now archived too (open since 01:36).
**Found:** the hourly output is about **28 GB per 15-year run** once archived (compressed), not 116 GB as said at 01:38. The 116 GB came from measuring the uncompressed file before archiving.
**Open / next:** check the NIRD project quota from a NIRD login (`dusage -p NS9188K`) before moving ~60 GB of new hourly output there.
**Files changed:** logs only.

## 2026-10-23 · 01:36 → 01:39 (3 min) · session 78f6d842
**Goal:** check the status of the runs just submitted and of the 1-day tests.
**Done:** checked the queue and CaseStatus. All production runs are running (CTRL_PD, CTRL_FUT, the LCC_PD/FUT extensions, three land-only spin-ups). The future 1-day test passes every output check.
**Found:** the archiving of the future test failed on a filesystem read/write error (it looks temporary); its output is safe in the run folder. The new hourly output is larger than estimated: about 116 GB for 15 years, not about 30 GB.
**Open / next:** check the present-day test when it finishes; re-archive the future test; decide whether 116 GB of hourly output is acceptable.
**Files changed:** logs only.

## 2026-10-23 · 01:24 → 02:00 (36 min) · session 339178f2
**Goal:** notebooks should always keep their outputs; lighter significance marks.
**Done:**
- Significance test: ocean no longer faded; now compares thin dense grey hatching (`////`, `/////`) and fading the non-significant cells (two strengths). Outline dropped.
- New standing rule (Claude memory + `CLAUDE.md`): notebooks are run with `run_nb_inplace.py`, which saves outputs and figures in the notebook. The significance test notebook was re-run this way.
- Significance style chosen (opened this block): thin grey hatching `/////` on non-significant cells is now the default in the forcing maps; ocean no longer faded by default.
- Forcing maps use the current fBVOC file names; `forcing_maps.ipynb` re-run with all figures (opened this block).
**Open / next:** if the fBVOC files are renamed later, switch the forcing maps back to the `_PD_IM` names.
**Files changed:** `CLAUDE.md`, `analysis/test_significance_marking.ipynb`, `analysis/forcing_maps.ipynb`, `src/.../plotting/forcing_maps.py`.

## 2026-10-23 · 01:10 → 01:22 (12 min) · session 339178f2
**Goal:** see whether to mark significant or non-significant cells on the forcing maps.
**Done:** test notebook `analysis/test_significance_marking.ipynb` with 4 styles × 3 panels, PD and FUT. Figures in `results/figures/tests/`.
**Found:** PD BVOC panels: almost nothing significant (0 %); FUT BVOC: ~90 % significant; Total: ~25–28 %. So no style is sparse everywhere.
**Open / next:** choose the style; then add it as an option to the forcing-map functions.
**Files changed:** `analysis/test_significance_marking.ipynb` (new), `results/figures/tests/*.png`.

## 2026-10-23 · 00:35 → 00:58 (23 min) · session 0c58bc16
**Goal:** prepare the spin-up reruns so that CTRL and LCC go through the same steps, with the right CO₂.
**Done (scripts only, nothing run):**
- Future: new CTRL coupled spin-up `23c`; the land-only spin-ups `22b`/`22c` now read CO₂ from the forcing files (plus the switch `CCSM_BGC=CO2A`, without which the model would crash at start).
- Present day: same CO₂ fix in `12b`; new CTRL twins `12c` (land-only) and `13c` (coupled). Whether to run them is still to be decided.
- `23c` and `13c` refuse to run until the name of the land-only run they start from is filled in.
- README and setup document updated.
**Found:** today's 22b case stopped during compilation without an error message, probably interrupted. It never ran.
**Open / next:** run 22b + 22c, check the CO₂ the land model sees (~1134 ppm); fill in names in 23c (and in 23b by hand); point 23a at 23c later. Decide on the PD reruns.
**Files changed:** `cases-scripts/` 12b, 12c (new), 13c (new), 22b, 22c, 23c (new), README; `docs/setup_fix_FUT_landonly_CO2.md`.

## 2026-10-23 · 00:29 → 00:30 (1 min) · session 0042d825
**Goal:** decide whether the fixed isoprene/monoterpene files should come from SF* or MEG_*.
**Found:** use **SF*** (total emissions). The fBVOC runs already remove the fire emissions of these two species and apply no extra diurnal cycle, so the prescribed file must contain everything. MEG_* would leave out the fire part.
**Open / next:** none from this question.
**Files changed:** none.

## 2026-10-23 · 00:17 → 01:53 (96 min) · session 20966a2c
**Goal:** Rename commands for the fBVOC data files; extend the emission-climatology script to all 19 MEGAN species; start the two CTRL reruns.
**Done:**
- Commands written for renaming the 30 data files + 30 logs (not run). Nothing gets overwritten.
- Read the handoff document; it agrees with the earlier changes.
- The emission script now handles all 19 species: 8 every 30 minutes (from h1) and 11 as monthly means (from h0). Same file format and units as the existing ISOP/MTERP files. The two helper shell scripts loop over all species.
- Tested on fake model files: all values and time axes come out as expected, and the ISOP output is identical to the old script's. Not yet run on real model output.
- CTRL runs set to 15 years (2000–2014), like the extended LCC runs. Started and in the queue (01:18): two 1-day output tests (jobs 1775817 PD, 1775813 FUT) and the CTRL_FUT 15-year run (job 1775814). **The CTRL_PD 15-year run must be started by you** (the automatic safety check blocked it). Wrote a check script for the 1-day tests (`cases-scripts/tests/check_hr_bvoc_all_1day.py`) and kept the test scripts in `cases-scripts/tests/`. The 30-min output is smaller than feared: about 2 GB per model year (~30 GB per run), not 8.
**Found:**
- **1-day tests passed** for both CTRL runs: every new emission field is written, with sensible values. The 30-min output is 1.8 GB per model year (~28 GB per run).
- The PD test's first day is bit-for-bit identical to the old CTRL_PD, so adding output doesn't change the simulation.
- The data files store their old name inside them too; it only shows up in error messages.
- The model reads monthly files by interpolating between mid-month values, so the monthly means are reproduced only approximately (standard for monthly emission files).
**Open-next:**
- You run the rename (or tell me to).
- Start CTRL_PD: `cd cases-scripts && bash 13a-NF2000norbc_tropstratchem_nudg_ctrl_f19_f19.sh`.
- Start CTRL_PD (still not launched).
- Delete the two test cases when you like (they use home-directory file quota).
- Next task: set up the all-species fixed-emission namelists in cases-setup.sh.
- Still open from 23:45: CTRL rerun size check (1-day test), and the CO₂-bug restart question for the future fixed-emission run.
**Files changed:** `preprocess/bvoc-emissions/create_bvoc_emissions_climatology_staged.py`, `create_bvoc_emissions_climatology.sh`, `create_bvoc_emissions_for_year_2100.sh`, `cases-scripts/13a-…`, `23a-…` (15 years), new `cases-scripts/tests/check_hr_bvoc_all_1day.py` and `tests/{13a,23a}-…-hrbvocall-1day.sh`.

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

## 2026-10-22 · 20:45 → 00:25 (220 min) · session aebc129e
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
- **How the bug changes BVOC emissions outside the forest cells (future runs):** almost entirely through leaf area. In CLM5 the leaf-area factor is linear (not saturating, as I had assumed before). Isoprene −18 % (−164 Tg/yr) and monoterpenes −17 % (−80 Tg/yr) on global land. Slightly warmer leaves give back about +5 %. The CO₂ factor itself is unchanged.
- **Inside the forest cells**, the bug flips the future isoprene signal: +8 % in present day becomes −2 % in the future.
**Open / next:**
- Optional: save the MEGAN γ decomposition as a notebook section (so far a one-off calculation).
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
