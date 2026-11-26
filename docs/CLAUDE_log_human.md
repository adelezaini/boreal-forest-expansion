# Project log: plain-language summary

**Topic colours:** <span style="color:#7B2FBE">Artefact</span> · <span style="color:#B8860B">CO₂ fix</span> · <span style="color:#CC0000">Waiting on you</span> · <span style="color:#008080">Diagnostics</span> · <span style="color:#A84300">Analysis</span> · <span style="color:#AAAAAA">Run status</span> · <span style="color:#555555">Run setup, archiving, postprocessing</span> · <span style="color:#62733B">Preprocessing</span> · <span style="color:#E58AA5">Figure style</span> · <span style="color:#999999">Housekeeping</span>

> **Where things stand (updated every prompt)**
>
> <span style="color:#CC0000"><!--5b362f0a--><span style="background:#CC0000;color:#FFFFFF;padding:0 4px;border-radius:3px">**WAITING ON YOU**</span> **Git commits, home folder full (26 Nov, 15:12):** 5 of the 7 commits are made (vegetation regions, sandbox, old archives out of git, new analyses APRP/land temperature/forcing tree, draft Methods+SI). The big one, the **2001–2040 rerun (notebooks + ~310 figures)**, needs ~1.2 GB and only ~0.8 GB is free in the home folder (20 GiB quota). Free ~1 GB more and it can go in. The VS Code backup was moved to `/cluster/work/users/adelez/home-backups/`. Nothing pushed.</span>
>
> <span style="color:#A84300"><!--448d3011-->**APRP for evapotranspiration? (26 Nov, 14:52):** question answered in chat. APRP itself is radiation-only, but the same "swap one factor at a time" idea works for ET with Penman–Monteith (energy, air dryness, temperature, aerodynamic and stomatal resistance). Offered a sandbox test. No files changed.</span>
>
> <span style="color:#E58AA5"><!--9576fddd-->**Forcing tree, new layout (26 Nov, 14:43):** section labels on the tree; non-BVOC / BVOC maps beside TOTAL; closure note centred, "(δ not drawn)" removed (renaming art to "prescription artefact" was tried and undone at your request); 'other' note grey italic; rows 3–5 share one tall colourbar (non-BVOC left, BVOC right). **The * footnote changed for all figures** (\"left out from regional means\", centred, grey, italic, smaller); old figures change only when redrawn. Test figure: `sandbox/test_forcing_tree_5rows_outputs/`. The 4 paper figures are redrawn (14:47) in `results/figures/radiative-forcing-tree-5rows/`.</span>
>
> <span style="color:#999999"><!--9261baaa-->**Vegetation test scripts cleaned (25 Nov, 19:51):** 5 sandbox scripts removed (recoverable from git, not committed); `left_out` now reads the current lines file and gives the same figure. 11 scripts kept, all working.</span>
>
> <span style="color:#E58AA5"><!--aa1522f0-->**Region names back to broadleaf exp. / needleleaf exp. (25 Nov, 19:58):** code, region file, CLAUDE.md and notebook texts changed back (cells unchanged). Redrawn in results/: forcing decomposition (13) and MEGAN attribution (8). Land-temperature and cloud-masking notebooks restarted 19:54 with the old names. Draft SI section S1, Methods line and SI figure changed back; draft compiles, table fits.</span>
>
> <span style="color:#999999"><!--eab501a1-->**Vegetation-region scripts tidied (25 Nov, 20:08):** in `diagnostics/lcc-modified-cells/` there are now 3 scripts (`region_cells.py`, `si_vegetation_classes.py`, `dominant_pft_change.py`) + one helper file `vegetation_helpers.py`, outputs in `region_cells_outputs/`. `si_region_map.py` was folded into `si_vegetation_classes.py` (which now also prints the SI table numbers) and deleted; the SI figure is unchanged. Not committed.</span>
>
> <span style="color:#CC0000"><!--b631a2eb--><span style="background:#CC0000;color:#FFFFFF;padding:0 4px;border-radius:3px">**WAITING ON YOU**</span> **APRP function and formula subtitles (25 Nov, 18:33):** the APRP calculation is now a reusable function, `aprp()` in `src/boreal_forest_expansion/analysis/aprp.py`, and it gives exactly the notebook's numbers. Test figures with, under each panel title, how it is calculated from the model output variables (SOLIN, FSUTADRF, CLDTOT …), plus a footnote are in `sandbox/test_aprp_formula_titles_outputs/`. Say if the design is OK; it goes into `cloud-masking-aprp.ipynb` once the 2001–2040 run of that notebook has finished.</span>
>
> <span style="color:#E58AA5"><!--cdb1451a-->**Forcing tree, now 5 rows (25 Nov, 19:00):** row 5 = cloud SW split into real cloud change + surface-albedo masking + atmosphere masking & other, same colour scale as rows 3–4 (your choice). Renamed everywhere to `radiative_forcing_tree_5rows.py` / `radiative-forcing-tree-5rows/`. The 2001–2040 figures are redrawn automatically once the cloud-masking notebook (running now) finishes; the old 4-row figures are then removed.</span>
>
> <span style="color:#A84300"><!--499a01f9-->**2001–2040 analysis (25 Nov, 18:29):** all 10 main notebooks done; `results/figures/` holds only 2001–2040 (and MEGAN) figures. Forcing tree (3 rows) done for 2001–2040. NIRD froze the other jobs at 16:45; restarted at 18:28 on login-2: forcing decomposition, cloud masking, 4-row tree and the new land-temperature notebook. Draft Methods outline: 2001–2040 numbers, significance shares, MEGAN grouping + safeguard, soil-moisture factor (switched off in CLM), forest-vs-climate section (corrected: the difference at the top of the atmosphere is longwave, not clouds; nudging point softened). **19:01:** forcing decomposition and 4-row tree done for 2001–2040; cloud masking and land temperature still running. MEGAN maps: new layout (LAI in row 1, no safeguard panel) applied to the paper notebook, rerun running. **19:05:** MEGAN paper maps redrawn with the new layout (LAI in row 1, no safeguard panel); the replacement / net-tree-gain numbers are back. **20:30:** land temperature done: forest warming is 1.5 % of the climate warming over the modified cells (0.11 vs 7.4 K; 3.4 % in spring), in the draft. Cloud masking failed (my mistake: cloud fields missing from the copy), rerunning; the 5-row tree follows it. Two figure flaws fixed in the land-temperature code, waiting for your OK to redraw.</span>
>
> <span style="color:#A84300"><!--dbee06ab-->**Forcing-tree scripts now in analysis (24 Nov, 17:33):** `analysis/forcing_tree.py` (3 rows) and `analysis/forcing_tree_4rows.py` (4 rows) write to `results/figures/forcing-tree{,-4rows}/` and `results/tables/forcing-tree{,-4rows}/`. All 16 figures were redrawn; the tables match the earlier ones exactly. Not committed. The old copies in `analysis/test_forcing_tree*_outputs/` can be deleted.</span>
>
> <span style="color:#A84300"><!--47db7f49-->**Vegetation-region names (25 Nov, 19:29):** you chose **A**. The two regions are now **replacement** (broadleaf replaces needleleaf) and **net tree gain** (any other tree gain, mostly needleleaf, including the 47 light-teal cells). Same cells, new names in the plotting code, the SI section, its figure (redrawn) and the methods text. Test maps in `sandbox/vegetation_regions/src_maps_outputs/` redrawn and checked: the new labels and footnote fit; the figures in `results/` still have the old names until the analysis notebooks are rerun (your OK needed).</span>
>
> <span style="color:#999999"><!--40b2b6a1-->**Commits made (24 Nov, 17:12):** 7 topic commits in the project repo (MEGAN LMDI folders; background aerosol notebooks; leaf area CLM vs LPJ-GUESS; Tang 2023; MET nudging fix; sandbox; logs) and 1 in the draft repo (vegetation regions in Methods + SI). Not pushed.</span>
>
> <span style="color:#CC0000"><!--0fee2434--><span style="background:#CC0000;color:#FFFFFF;padding:0 4px;border-radius:3px">**WAITING ON YOU**</span> **MEGAN attribution maps (23 Nov, 21:55):** test figures with one colour scale per row are in the sandbox. LAI saturates at ±10, so choose whether it gets its own scale. More MEGAN years are not recommended. Paper figures are unchanged.</span>
>
> <span style="color:#555555"><!--ee15eedf-->**Last run being postprocessed again (24 Nov, 16:30):** with your OK, the 19 broken files were removed and postprocessing of `LCC_PD_fBVOClccPD` restarted with fewer parallel jobs (up to 3 tries). It should take about 4–6 hours. When all 19 files are there, the 2001–2040 analysis starts by itself.</span>
>
> <span style="color:#CC0000"><!--4cd451a7--><span style="background:#CC0000;color:#FFFFFF;padding:0 4px;border-radius:3px">**WAITING ON YOU**</span> **Forcing decomposition tree, two layouts (24 Nov, 16:47):** (1) 3 rows with albedo, colourbars on rows 1–2, LW added: `sandbox/test_forcing_tree_outputs/` (12 figures). (2) NEW 4-row layout: total → non-BVOC / BVOC → Ghan terms of both → each split into SW and LW, no physical labels: `sandbox/test_forcing_tree_4rows_outputs/` (4 figures). Choose one for `analysis/`. **Cloud masking (17:42):** APRP notebook `analysis/cloud-masking-aprp.ipynb` done: the negative SW cloud term of the land-cover part is masking of the darker surface, the clouds themselves reflect slightly less; for BVOC the cloud term is a real cloud brightening.</span>
>
> <span style="color:#CC0000"><span style="background:#CC0000;color:#FFFFFF;padding:0 4px;border-radius:3px">**WAITING ON YOU**</span> **New paper story (22 Nov, 17:14):** the story moves from "BVOC-cloud effects offset the albedo warming" to "future land-cover change plays a minor regional role because climate change dominates". Decide the final framing. The manuscript is unchanged.</span>
>
> <span style="color:#008080"><!--36563bcd--><span style="background:#CC0000;color:#FFFFFF;padding:0 4px;border-radius:3px">**WAITING ON YOU**</span> **Background aerosol, two notebooks (21 Nov, 17:17):** PD vs FUT and LCC vs CTRL now have the same merged analysis, run and checked. Decide whether to keep the extra combined notebook.</span>
>
> <span style="color:#A84300"><!--560cc914-->**Vegetation regions on all result maps (24 Nov, 17:47):** the two lines and the broadleaf/needleleaf-expansion numbers are in the shared plotting code, checked on 7 kinds of figures. Also fixed: white lines on dark MEGAN maps, tighter gamma maps, and snow persistence (now snow-season length, ≤ 365 days; it was −18,900 days because the model counter never resets under permanent snow). The 12 notebooks with maps are rerunning in the background (started 17:29). Draft Supplementary numbered S1. Not committed.</span>
>
> <span style="color:#A84300">**Fig. 1c checked (21 Nov, 16:26):** row 2 is not a copy of row 1. It uses the right runs (`LCC_FUT − LCC_PD`). The rows look alike because climate change dominates both. Nothing changed.</span>
>
> <span style="color:#A84300">**Commits made, old backup removed (21 Nov, 16:21):** 6 topic commits in the project repo and 1 in the draft repo, not pushed. MEGAN, background aerosol and Tang/LPJ-GUESS stay uncommitted, as you chose. The 16 Nov backup folders are deleted (348 files, all recoverable from git).</span>
>
> <span style="color:#A84300">**MEGAN LMDI FUT done (21 Nov, 17:42):** the maps notebook ran cleanly and the last open number in the Methods outline is filled. With the forest expansion in FUT, isoprene changes by +0.60 ± 0.60 and monoterpenes by −1.48 ± 0.52 (100·Δln, ≥45°N, annual): the composition change lowers emissions, higher leaf area partly offsets it. The watcher is alive, and `LCC_PD_fBVOClccPD` should finish last, around 09:00–10:00 on 22 Nov.</span>
>
> <span style="color:#CC0000">**Status check (21 Nov, 15:55):** 11 of the 12 nudged runs are in their last stretch (2036–2041), the slowest should end around 23:00. PD `lcc_fBVOClccPD` crashed at start-up at 02:12, probably a one-off bad read since the surface file is intact. **Waiting on you:** OK to resubmit it. The 2001–2040 analysis waits for this run. The MEGAN LMDI maps notebook also still needs a rerun.</span>
>
> <span style="color:#A84300">**Six-map forcing figures cleaned up, deck rebuilt (20 Nov, 16:50):** in `results/figures/radiative-forcing-decomposition/` only the shared-scale (`_split…`) figures are kept: 4 cases × NET/SW/LW. Removed: the old `_split6-2` files, the duplicate case `LCCFUT-CTRLPD_fBVOCctrlPD` (same as `LCCFUT_fBVOCctrlPD` since 19 Nov), and the versions with one colourbar per map. Notebook and deck script now make only the shared-scale version. Main figures deck rebuilt: 307 slides, 297 figures. Not committed.</span>
>
> <span style="color:#AAAAAA">**Status check (20 Nov):** the 12 nudged runs finished 2026–2031 and are now running 2031–2036 (LCC_FUT started ~9 h after the others). FUT MEGAN batch 2 finished at 04:12, so all FUT years are in. The automatic rerun of `megan-lmdi-attribution-maps.ipynb` failed 3 times (the Python environment on NIRD failed to load), so it has to be rerun by hand. The archive guard is running. Nothing changed.</span>
>
> <span style="color:#008080">**Leaf area: CLM vs LPJ-GUESS (19 Nov, 17:47):** new `diagnostics/lai-clm-vs-lpjguess/clm_vs_lpjguess_lai.ipynb`. Present day the two models agree (summer LAI 1.8 in the forest-change cells). By 2100 CLM's leaf area doubles (×2.1) while LPJ-GUESS's rises ×1.6; through MEGAN this alone can make our future emissions up to ~25–30 % higher. Tang's GFDL-ESM4 SSP5-8.5 warms about as much as our runs (+6–7 K), so the warming is not what makes our monoterpenes so much larger. Not committed.</span>
>
> <span style="color:#A84300">**Offline vs coupled emissions (19 Nov, 17:23):** running LPJ-GUESS offline vs our coupled MEGAN is not the main reason our emissions differ from Tang's. Our future increase is warmer leaves (×2.3–2.8, +7.5 K) times twice the leaf area (×2), with CO₂ halving isoprene but nothing holding back monoterpenes. The coupling itself (the new forest warming its own leaves by ~0.3 K in summer) adds only ~3–5 %, though that is as large as the whole vegetation effect on the emission totals.</span>
>
> <span style="color:#A84300">**Design A six-map figures, FUT with PD emissions (19 Nov, 16:51):** maps 1–2 (albedo, total) now show LCC_FUT − LCC_PD (lccPD-emission figure) and LCC_FUT − CTRL_PD (ctrlPD-emission figure) instead of [LCC − CTRL]_FUT. They are much bigger (≥45°N NET total +1.07 and +1.33 W m⁻²; albedo +9.7 and +10.2), so the scale is now ±40 / ±15 / ±2 and the files end in `_split40-15-2_designA.png`. The 12 figures are redrawn. The notebook rerun failed on NIRD read errors (NIRD unstable this afternoon), so the notebook still shows that error in its figure cell: rerun it when NIRD is stable. Old `_split6-2` files of these two cases are still there. Not committed.</span>
>
> <span style="color:#A84300">**Tang comparison extended (19 Nov, 16:30):** Fig. 5 now outlines the forest-change cells with a thick line. The emission-totals chart now has Tang's CanESM5 too: around 2100 Tang gets isoprene +18 % (GFDL) / +64 % (CanESM5) and monoterpenes −5 % / +13 %; we get +211 % and +352 %. New figure like Tang Fig. 1b,f: our emission change per year 2000→2100 (same unit as Tang, mgC m⁻² yr⁻²) is positive almost everywhere (only 7–9 % of cells go down), while Tang's monoterpenes go down over large parts of the boreal zone. **16:44:** the figure now also shows the vegetation change alone (LCC − CTRL emissions, FUT and PD climate): per year it is 25–50× smaller than the total (ISO +0.11 / +0.07, MT −0.04 / +0.01 mgC m⁻² yr⁻² in the forest-change cells), with the up/down pattern Tang describes. Not committed.</span>
>
> <span style="color:#E58AA5">**Tang emission totals bar colour fixed (19 Nov, 15:05):** Tang's ~2100 bar is now orange like our lccFUT (both include the vegetation change), not red (ctrlFUT). Rerun done. **15:10:** in the Tang-range copy of Fig. 5, SOA burden and AOD vis are no longer put on Tang's ranges (they are not the same quantities as Tang's optical depths); the SOA burden bar goes to ±3 in both figures.</span>
>
> <span style="color:#E58AA5">**Tang comparison figure restyled (19 Nov, 15:00):** the Tang Fig. 5-style figure now has discrete colour bars like Tang's (blue–red in equal steps, a tick on every step). A second copy uses exactly Tang's colour-bar ranges (`tang_fig5_layout_tanglimits_2001_2025.png`): on those ranges our climate-driven changes in monoterpenes, SOA, AOD and CCN fill the darkest colour almost everywhere, which shows how much bigger they are than Tang's. Not committed.</span>
>
> <span style="color:#A84300">**Methods numbers filled (19 Nov, 14:45):** all yellow \NUM boxes except the FUT emission split (waits for FUT batch 2). New: LCC vs CTRL vegetation outside the forest cells differs by ≤ 0.1 % in PD and FUT (2001–2025); the PD LCC − CTRL SOA burden is persistent from year to year, so its map hatching is permissive (675 → 185 significant cells with an effective sample size).</span>
>
> <span style="color:#AAAAAA">**Nudged runs 2026–2040 repaired (19 Nov, 14:22):** LCC_FUT resubmitted (job 1809562, bad nodes excluded); MET copied to NIRD (retry OK 14:15); the 3 false failure flags cleared; the watcher now asks the queue up to 3 times and looks twice before calling a run failed, and was restarted at 14:19 (now on login-2). All 12 runs are running or queued. Results 2026–2040 expected ~22–23 Nov.</span>
>
> <span style="color:#008080">**Second BVOC means figure (16 Nov, 22:29):** `diagnostics/2_bvoc-emissions/plot_bvoc_means.ipynb` now also plots the other 17 BVOC species MEGAN sends to CAM (methanol, CO, acetone, ethene, …), same CTRL/LCC × PD/FUT layout, in Gg/yr. Over the forest-expansion cells the new forest <i>lowers</i> all of them slightly (PD up to −5 %, FUT up to −8 %), unlike isoprene (+6 % PD); the future climate raises them 4–7×. Yearly totals saved to a CSV so the figure survives the work-archive purge.</span>
>
> <span style="color:#008080">**Isoprene: each fBVOC run against its own source (23:26):** section 10 of `isoprene_diurnal_cycle_fBVOC.ipynb`. Every fBVOC run emits exactly its source's 2001–2014 average (all 8 runs, every month 2001–2025), with the same daily cycle (peak ~13:15, ~4 % at night). What it misses is weather: the source's summers vary by ±7–9 % and its day-to-day swings are ~25–35 %, of which the input keeps only 14–25 %. Over 2015–2025 the PD sources emit ~2 % less than the input, FUT ~1 % more. Notebook rerun done without errors. Not committed.</span>
>
> <span style="color:#555555">**Slide decks rebuilt (16 Nov, 22:13):** the four CICERO decks in `results/pptx/` were rebuilt from the current figures: main figures deck 325 slides (315 figures), land carbon/water 13 slides, MEGAN factors 55 slides, simulation contrasts 12 slides. Every figure was placed.</span>
>
> <span style="color:#008080">**BVOC emissions notebook saves its figures (16 Nov, 22:50):** `diagnostics/2_bvoc-emissions/plot_bvoc_emissions.ipynb` now writes every figure (12 PNGs, 200 dpi) to the new folder `plot_bvoc_emissions_outputs/`, like the time-series notebook. Rerun done without errors (~35 min, mostly reading the files); outputs saved in the notebook. Not committed.</span>
>
> <span style="color:#A84300">**Tang et al. 2023 comparison done (17 Nov, 00:30):** `diagnostics/tang2023-comparison/tang2023_comparison.ipynb`. Our vegetation change gives Tang's pattern (monoterpenes down in the southern boreal belt, up in the north; SOA up over northern Canada) but it is ~1 % of the climate effect on emissions, which is several times bigger than in Tang. Note: `AEROD_v` is empty in our output, use `AOD_VIS`.</span>
>
> <span style="color:#008080">**Isoprene diurnal cycle, fixed-BVOC runs + hourly time series (16 Nov, 21:10):** new `diagnostics/2_isoprene-diurnal-cycle/isoprene_diurnal_cycle_fBVOC.ipynb`, same figures as the interactive notebook. The production fBVOC runs write no 30-min output, so their isoprene is taken from the prescribed input files (checked: a test run emits exactly what the file gives, to 0.05 %). The prescribed isoprene keeps the interactive daily cycle (peak ~13:15 local, ~4 % at night) and the LCC − CTRL difference (PD summer, expansion area ~+6.5 %), but loses the day-to-day weather swings. Full hourly series for every year of the MEGAN runs, the input files and the 2001–02 test runs are in `isoprene_diurnal_cycle_fBVOC_outputs/figures/`. FUT 2002/2006/2011 follow when FUT batch 2 is done (rerun the reducer, then the notebook). Not committed.</span>
>
> <span style="color:#008080">**Isoprene diurnal cycle + BVOC plots moved (16 Nov, 19:14):** new `diagnostics/2_isoprene-diurnal-cycle/isoprene_diurnal_cycle.ipynb` from the 30-min output of the MEGAN split runs (PD 6 years, FUT 3 so far). Isoprene peaks at ~13:00 local time with almost nothing at night; forest expansion raises it by ~6.5 % (PD, summer, expansion area) at every hour, so the timing does not change. The 30-min data are saved as monthly diurnal averages on NIRD, so they survive the /cluster/work purge. The `plot*` notebooks moved from `preprocess/bvoc-emissions/` to `diagnostics/2_bvoc-emissions/` (paths fixed, not rerun). Nothing committed.</span>
>
> <span style="color:#555555">**Archive guard checked (16 Nov, 18:29):** still running on login-3 (since 5 Nov), so not restarted. Its log is quiet because it only writes when it fixes something; last fix 13:12 today.</span>
>
> <span style="color:#62733B">**BVOC means plot (16 Nov, 20:57):** `diagnostics/2_bvoc-emissions/plot_bvoc_means.ipynb` redrawn: x axis VEG_CTRL / VEG_LCC, arrows with the run names along them, colours in a legend, "25-year mean ± 1σ" as subtitle. The PD → FUT arrow now ends on the LCC_FUT point (the earlier shift was only for visibility; same run).</span>
>
> <span style="color:#999999">**Commits made (16 Nov, 18:08):** 5 commits on `main` (not pushed): MEGAN month fix; background aerosol 25 yr; notes; sandbox; logs. Split-figure labels (`forcing_maps.py` + `artefact-corrected-split`) held, as you asked. Another session is rerunning the background aerosol notebooks right now, so those will need one more commit.</span>
>
> <span style="color:#999999">**NOTES.md filled + CLAUDE.md fixed (16 Nov, 16:27):** `NOTES.md` now has the new cleaning list and notes (your lines kept, typo `.ipynb_checkpoints` fixed; MEGAN month line left out until the swap is done). `CLAUDE.md` spin-up rule now points to the right files.</span>
>
> <span style="color:#555555">**MEGAN 2001/2002 month fix (16 Nov, 16:40):** fixed files swapped in at 16:34; old ones in `data/processed-data/megan-lmdi/old-month-offset-20261115/` (moved, same NIRD disk). The 3 MEGAN notebooks are rerunning (megan-lmdi-vs-approx, megan_factor_maps, megan-lmdi-attribution-maps). Both details are now in `NOTES.md`, plus the nudging fix of the last 2015 met file.</span>
>
> <span style="color:#008080">**Background aerosol notebooks split (16 Nov, 18:10):** the PD/FUT notebook is now two: `background_aerosol_pd_fut_prescribed.ipynb` (emission files, ocean DMS, greenhouse gases) and `background_aerosol_pd_fut_online.ipynb` (what the model makes of it + MEGAN, dust, sea salt, DMS flux, lightning). The LCC notebook is renamed `background_aerosol_lcc_ctrl_fut_online.ipynb`. Bar charts and time series now also exist for north of 40°N. Both ran without errors; the old notebook is removed. North of 40°N: sulfur emissions 19.5 → 4.2 Tg S, MEGAN 56 → 191 Tg, DMS flux +39 %. Earlier (15:55): 25 years, Arctic maps, global maps in an appendix; north of 66.5°N the droplet column rises 25 % in FUT although sulfate falls 41 %.</span>
>
> <span style="color:#A84300">**Results folder reorganised, all reruns done (16 Nov, 20:40):** `results/figures/<notebook>/{a_interactive,b_fBVOC,c_non-BVOC}/` (same for tables); pure artefacts (art_LCC, art_CTRL, δ) in `artefacts/d_artefacts/`, design B in `artefacts/design-B/`; titles without years ("25-year mean" in the subtitle); new notebook `radiative-forcing-decomposition`. All 10 notebooks reran without errors (18:15–20:16). Old set: `results/figures-pre-reorg-20261116/`. Slide-deck builders updated (20:55) and test-built; the decks in `results/pptx/` themselves are not rebuilt yet (waiting for your OK).</span>
>
> <span style="color:#999999">**Commits made (16 Nov, 13:34):** 8 commits on `main` (not pushed): notes moved to `docs/`; design A figures; MEGAN LMDI reruns; caches on `/cluster/work`; sandbox script; simulation-contrasts figures moved to `results/`; `lake_fix_effect` fixed and rerun cleanly; logs. Home folder was full (file count); 6 old VS Code server copies deleted (your OK), now 74 000 of 100 000 files.</span>
>
> <span style="color:#999999">**Analysis notes moved to `docs/` (16 Nov, 13:10):** `FBVOC_ARTEFACT.md`, `MEGAN_ATTRIBUTION.md`, `PLOTTED_VARIABLES.md` are now in `docs/`; all mentions point there.</span>
>
>
> <span style="color:#999999">**Contrast figures moved to `results/` (16 Nov, 13:20):** the `simulation-contrasts.ipynb` figures (Figs. 1a–4b) are now in `results/figures/simulation-contrasts/` (2001–2025) and `results/figures-2001-2014/simulation-contrasts/` (2001–2014). The notebook, the deck script and both READMEs point there; the old `analysis/simulation-contrasts_outputs/` is gone. Nothing was rerun.</span>
>
> <span style="color:#999999">**Old folders checked (16 Nov, 11:50):** nothing changed. `diagnostics/0_check-spinup-equilibrium-uncomplete` is replaced by `0_check-simulation-equilibrium`; only the quick-spin-up figures are unique (worth keeping as a record). `_old/` has nothing that is still needed: its functions are all in `src/`.</span>
>
> <span style="color:#999999">**Commits by topic (16 Nov, 11:44):** 4 commits made on `main` (not pushed): MET + nudged runs 2026–2040; MEGAN exact split; design A; background aerosol. Sandbox scripts and logs left out, as you asked. You had already committed the artefact folder rename yourself.</span>
>
> <span style="color:#008080">**Background aerosol notebooks (16 Nov, 11:31):** done; both run with results saved, now in `diagnostics/background-aerosol/` (the folders were merged at 11:27). PD/FUT notebook: what each compound does, methane 1778 → 2415 ppb, natural sources (forests emit 3.5× more monoterpenes in FUT). New LCC_FUT − CTRL_FUT notebook: the forest expansion barely changes the aerosol background (global ≤ 0.2 %).</span>
>
> <span style="color:#7B2FBE">**Slides updated to design A (16 Nov, 12:33):** All decks checked: none broken. the 4 CICERO decks in `results/pptx/` are rebuilt (figures 340 slides, contrasts, MEGAN with the new exact-split section, land). Two missing design-A figure sets were made: the design-A budget split and maps of the artefact on LCC land with its own emissions (FUT ≥45°N: +0.07 W m⁻², mostly cloud; δ stays ≈ 0). Not rebuilt: the old non-CICERO deck and `simulations-interpretation.pptx`. NIRD problem: many files read only with `HDF5_USE_FILE_LOCKING=FALSE`.</span>
>
> <span style="color:#E58AA5">**Period wording in titles (16 Nov, 13:43):** three versions to compare in `sandbox/test_period_wording_outputs/` (A current, B small fix "25-yr mean", C full proposal). Waiting for your choice; paper figures untouched. Earlier: suggested wording for titles: no calendar years (the winds come from a free-running present-day model run, so "2001–2025" are model labels, not real years); use "25-year mean" + "same nudged winds". Waiting for your choice. Before: 6 drift figures in `sandbox/test_cyclical_sim_year_outputs/` (x = simulation year, analysis years shaded, conditions in titles). Seasonal (Jan–Dec) figures not made yet: they need the monthly files on NIRD, which gives read errors today. Seen in the plots: FUT runs with present-day emissions need ~3 years for SOA to settle (year 1 1.9 → 1.3 mg m⁻²); this moves the 25-year mean by only 0.5 %. All `cache/` folders now sit on `/cluster/work` (home quota was full).</span>
>
> <span style="color:#AAAAAA">**MET + nudged runs 2026–2040 (16 Nov, 11:02):** MET is running (model year 2029 of 2041; its first 6-yr job ends ~19:00 today). The automatic watcher is now on (started 11:00; it had not started yesterday, which cost nothing). Expected: the 12 runs start ~17 Nov, reach 2041 ~19–20 Nov; postprocessing + analysis ~20–21 Nov.</span>
>
> <span style="color:#A84300">**MEGAN attribution maps with the exact split (16 Nov, 13:18):** FUT maps will be added automatically when all FUT years are in (~17 Nov evening). new maps like the old `PD_*_attribution_*` ones, now from the exact LMDI split (PD, 6 years, isoprene and monoterpenes, ANN and JJA): `results/figures/megan_factors/PD_*_attribution_LMDI_*_6yr.png`, notebook `analysis/megan-lmdi-attribution-maps.ipynb`. No residual row any more. Monoterpenes ≥45°N, ANN: emission −0.5 % = composition −4.5 % + activity +4.0 % (leaf area +3.7 %, temperature +0.5 %).</span>
>
> <span style="color:#AAAAAA">**FUT MEGAN runs (16 Nov, 11:00):** 2000 and 2005 reduced, 2010 being reduced, 2001 running (done ~17:30). Batch 2 (2002, 2006, 2011) starts by itself tonight; all FUT years expected ~17 Nov evening if the queue is quick.</span>
>
> <span style="color:#E58AA5">**FUT − PD figures in the sandbox (15 Nov, 19:24):** new `sandbox/test_fut_minus_pd_outputs/` shows FUT − PD year by year (same nudging year in both), for CTRL, LCC and the fBVOC pairs, plus how the forest effect changes from PD to FUT. Script `sandbox/test_fut_minus_pd.py`. Paper figures not touched.</span>
>
> <span style="color:#555555">**MEGAN exact-split workflow drawn (15 Nov, 19:05):** new figure `docs/workflows/workflow_MEGAN_LMDI_logic.png` shows each step of the MEGAN LMDI workflow and why it is done that way (problem → method → tests → runs → reduction → checks → status). Rebuild it with `docs/workflows/draw_workflow_MEGAN_LMDI.py`. The 6 Nov figure is kept.</span>
>
> <span style="color:#999999">**What can be cleaned (15 Nov, 18:56):** checked only, nothing deleted. The folder holds 9.7 GB. About 1.9 GB can go with no loss (notebook `cache/` folders + Python caches); about 1.8 GB more are old figure sets you could delete or move to NIRD, including `*-designB-standin-20261111/` (the results as they were on 11 Nov, just before the switch to design A). Git takes 3.8 GB; a cleanup there should wait until the other session's history rewrite is pushed.</span>
>
> <span style="color:#CC0000"><span style="background:#CC0000;color:#FFFFFF;padding:0 4px;border-radius:3px">**WAITING ON YOU**</span> **MET + nudged runs 2026–2040 (15 Nov, 19:02):** MET is in the queue (3 jobs of 6 yr, to 2041-01-02). The automatic watcher that does the rest (met files, check, the 12 runs in 3 phases, NIRD copy, processing, analysis) is written and tested, but I was not allowed to start it. Please start it once: `cd cases-scripts/run_when_done && setsid nohup bash met_nudg_2026-2040_when_done.sh > /cluster/work/users/adelez/met-nudg-2040/watch.log 2>&1 < /dev/null &`. Full workflow: `docs/met-nudg-2026-2040.md`.</span>
>
> <span style="color:#999999">**`analysis-2001-2019/` deleted (15 Nov, 18:43):** the failed temporary 2001–2019 set is gone, and its mentions in `.gitignore`, `CLAUDE.md`, `analysis/README.md` and one script comment are removed. Not committed yet.</span>
>
> <span style="color:#999999">**Palette check (15 Nov, 16:57):** the project palette is option Q1 (not P): teal, navy, plum, red `#BC423E`, orange, gold (gold = totals). Nothing changed.</span>
>
> <span style="color:#999999">**Plans list (11 Nov, 15:44):** `~/.claude/plans/INDEX.md` lists all Claude plans by date with their status, and now stays in order by itself. Still open: Methods rewrite, MET + nudged runs 2026–2040, MEGAN comparison + FUT batches (raw deletion on hold).</span>
>
> <span style="color:#A84300">**Exact vs approximate MEGAN split (15 Nov, 19:01):** the current attribution maps get the two main terms wrong, even in sign: for isoprene north of 45°N, composition +12 % (approximate) vs −2 % (exact), leaf area −3 % vs +3 %; the big residual of the old maps hid this. Temperature is much smaller than it looked (+0.5 % vs +2.4 %). Notebook `analysis/megan-lmdi-vs-approx.ipynb`.</span>
>
> <span style="color:#AAAAAA">**FUT MEGAN branch runs (15 Nov, 19:18):** all of batch 1 is submitted (2000–2001, 2005, 2010; the 2000 chain is already running) and the reduction watcher is on. Batch 2 (2002, 2006, 2011) starts by itself after batch 1 is reduced. Raw files kept, as for PD.</span>
>
> <span style="color:#555555">**MEGAN 2001–2002 time shift being fixed (16 Nov, 11:06):** as you decided: the reduction now puts every half-hour step in its own month; PD 2001 and 2002 are being re-reduced (~3 h), checked, and swapped in by a script, which then reruns the comparison and the MEGAN factor maps. FUT 2001–2002 will use the fixed code directly.</span>
>
> <span style="color:#A84300">**Exact MEGAN attribution maps (16 Nov, 11:06):** the exact maps you asked for last night (`megan-lmdi-attribution-maps.ipynb`, another session) are now the only attribution maps; `megan_factor_maps.ipynb` no longer draws the approximate ones. They are redrawn once 2001–2002 are fixed; FUT follows when 3 FUT years are reduced. The two diagnostics notebooks hit by the ANN bug are rerunning.</span>
>
> <span style="color:#A84300">**Bug in the MEGAN annual maps (15 Nov):** "ANN" years were Dec of the year before + Jan–Nov, and the first year was dropped. Fixed in the code; the existing ANN maps of `megan_factor_maps.ipynb` are not redone yet (your call).</span>
>
> <span style="color:#7B2FBE">**Design A and B in one notebook, done (15 Nov, 18:52):** both notebooks ran without errors and show the two designs side by side. δ (the part where they differ) is ≈ 0: PD −0.002 ± 0.030, FUT +0.014 ± 0.025 W m⁻² (≥45°N), now in the Methods outline.</span>
>
> <span style="color:#A84300">**Exact vs approximate MEGAN split (15 Nov, 19:00):** on the same 6 PD years, the current (approximate) maps get the main factors wrong: for isoprene north of 45°N they show composition +12 % and leaf area −3 %, the exact split shows −2 % and +3 % (opposite signs), and the approximate residual (−10 %) is spread over several factors. Use the exact split in the paper. The raw files were not needed for this (`analysis/megan-lmdi-vs-approx.ipynb`).</span>
>
> <span style="color:#555555">**MEGAN raw files checked (15 Nov, 18:45):** all 6 PD years match the reduced files exactly; re-reducing July 2005 from the raw files gives a bit-identical file. Before deleting: decide on the 2001–2002 half-hour shift.</span>
>
> <span style="color:#A84300">**Methods outline rewritten (15 Nov, 17:35):** `methods-claude.tex` now uses design A, the 2×2 emission sources (all four kept), 2001–2025 numbers, the correct FUT DMS, and no ON-HOLD items. `main.tex`/`methods.tex` not touched (your edits).</span>
>
> <span style="color:#AAAAAA">**Status (15 Nov, 17:05):** nothing is running and no job has run since 11 Nov; only the archive guard is alive. The switch to design A finished on 11 Nov 16:24 (8 notebooks, deck built). Git: 3 commits not pushed, ~600 files changed or untracked.</span>
>
> <span style="color:#CC0000"><span style="background:#CC0000;color:#FFFFFF;padding:0 4px;border-radius:3px">**WAITING ON YOU**</span> **Two notebooks are design B by construction (11 Nov, 12:33):** `artefact-corrected-split.ipynb` and `cumulative_radiative_decomposition.ipynb` are not rerun. A design-A version would no longer add up exactly (it needs an extra δ term). Your call.</span>
>
> <span style="color:#7B2FBE">**Artefact doc updated (11 Nov, 12:30):** `analysis/FBVOC_ARTEFACT.md` now has the H6 result: ~2.5 of the 3 % extra SOA comes from the lost weather link; the climatology's wrong mean adds ≈ 0 globally. A better-matched climatology would not fix it.</span>
>
> <span style="color:#AAAAAA">**Status (11 Nov):** nothing is running. **MEGAN batch 2 finished** (2002, 2006, 2011, all checks pass), so all 6 PD years are reduced. **LCC_FUT_fBVOClccFUT reached 2025** (10 Nov 18:56) but is not processed yet, so the notebooks still use the design-B stand-in. Git: 1 commit not pushed + many uncommitted changes.</span>
>
> <span style="color:#008080">**Background aerosol PD vs FUT (9 Nov, 17:00):** FUT repeats the **year 2100 of SSP5-8.5** for all prescribed emissions (industry, traffic, aircraft, fires, volcanic degassing), plus ocean DMS and SST of 2090–2100; the stratospheric volcanic background is the same file in PD and FUT. Note: the present-day DMS file set in the CTRL_FUT `user_nl_cam` is **ignored** (wrong format), so FUT uses the 2090–2100 DMS. New notebook `diagnostics/background-aerosol-pd-fut/background_aerosol_pd_fut.ipynb` is done. Year read, global: sulfur emissions 70.6 → 29.7 Tg S (in FUT half is volcanic), black carbon −56 %, NOx −23 %, ammonia +48 %, fires within ±20 %. In the model: sulfate −39 %, surface NOx −36 %, ozone +3 %, yet AOD +6 % (more dust/sea salt, likely).</span>
>
> <span style="color:#999999">**Commits made and pushed (15 Nov, 18:56):** 11 commits on `main` (not pushed): Ghan title fix; LCC_FUT_fBVOClccFUT → design A; `.gitignore` (archive folders and built decks stay local, CICERO template kept); analysis reruns 2001–2025; results 2001–2014 → 2001–2025; fBVOC artefact H6; background aerosol; watcher scripts; pptx builders; READMEs + logs. **Left out on purpose:** `artefact-corrected-split`, `cumulative_radiative_decomposition` and their outputs, the two `*-designA` notebooks (another session is rerunning them), the new `megan-lmdi-vs-approx.ipynb` (another session, just started), `sandbox/final_palette.png`. (Was “Commits + PowerPoint folder”, waiting since 9 Nov.)</span>
>
> <span style="color:#A84300">**Land carbon and water plots (9 Nov, 17:20):** as you asked, `analysis/land-carbon-water.ipynb` now writes to `results/` like the other notebooks (grids in `results/figures/<category>/`, seasonal cycle in `results/figures/interactive/`, tables in `results/tables/`); rerun done, no errors, same numbers; old `_outputs/` folder removed. Results: GPP −3 % (PD) / −5 % (FUT), vegetation carbon +3.8 / +8.3 PgC, net CO₂ flux unchanged in PD, +50 TgC/yr in FUT; ET +2–3 mm/yr from ground evaporation. The PowerPoint builder will need these 9 new figures added.</span>
>
> <span style="color:#A84300">**Simulation-contrasts PowerPoint (9 Nov, 09:38):** `simulation-contrasts.ipynb` was already on 2001–2025 (run automatically this morning at 05:41–06:04, nothing changed since, so no rerun). Its 9 figures are now in `results/BOREAL_simulation_contrasts_2001-2025_CICERO.pptx` (12 slides, CICERO template), each with the notebook's row explanations.</span>
>
> <span style="color:#A84300">**MEGAN factors PowerPoint (9 Nov, 09:27):** `results/BOREAL_MEGAN_factors_2001-2014_CICERO.pptx` (46 slides, CICERO template): how to read the factors, the fields per run, PD and FUT factor and attribution maps, and the lake-fix check as appendix. Note: these maps exist only for **2001–2014**; the notebook has not been run on 2001–2025.</span>
>
> <span style="color:#A84300">**PowerPoint in the CICERO template (9 Nov, 09:14):** `results/BOREAL_figures_2001-2025_CICERO.pptx` (269 slides, all 260 figures incl. the 10 new artefact maps), built on your template: its title, agenda, chapter and content layouts, colours, fonts, logo and page numbers. The older deck in my own colours is still in `results/`; say if it can go.</span>
>
> <span style="color:#A84300">**PowerPoint of all figures (9 Nov, 08:20):** `results/BOREAL_figures_2001-2025.pptx` (101 MB, 259 slides): all 250 figures of `results/figures/`, in 6 sections (runs → total → non-BVOC → BVOC → PD vs FUT → artefacts) with subsections. Made just before the artefact notebook rerun finished, so its new FUT maps are not in yet; rebuild with `results/build_figures_pptx.py`.</span>
>
> <span style="color:#7B2FBE">**Forcing maps for FUT with PD emissions (9 Nov, 08:50):** made for ctrlPD and lccPD, 2001–2014 and 2001–2025; all forcing maps in `design-B-split/individual-scale/` and `split6-2/`. `artefact-corrected-split.ipynb` includes them again and was rerun (2001–2025, no errors): new Ghan and context maps, table columns `BVOC corr (ctrlPD/lccPD)`. FUT, 45–90°N, NET: −0.98 W m⁻² for both, vs −0.03 with FUT emissions (ctrlFUT).</span>
>
> <span style="color:#A84300">**Results folders split by period (9 Nov, 07:31):** `results/figures/` and `results/tables/` now hold only 2001–2025 outputs. The 2001–2014 ones are in `results/figures-2001-2014/` (274 figures) and `results/tables-2001-2014/` (14 tables), same subfolders. All files checked identical before the originals were removed.</span>
>
> **2001–2025 analysis complete (9 Nov, 07:50):** the 2 failed notebooks reran fine, so all 9 now use 2001–2025. `timeseries-responses` needed a fix (it expected only one processed file per run; it now takes the longest). Cumulative split at ≥45°N, 2001–2025 (vs 2001–2014): future background +1.11 ± 0.17, land cover without BVOC +0.25 (+0.26), corrected BVOC −0.03 ± 0.03 (−0.06 ± 0.05), **total +1.32 ± 0.17 W m⁻² (+1.19)**. The fix is not committed; the notebook text still quotes 2001–2014 numbers.
>
> <span style="color:#E58AA5">**Grids: one colour scale per column, being applied overnight (9 Nov, 02:04):** you OK'd it. Fix added at 02:00: a panel is raised to its row's ÷N only as far as it doesn't turn into saturated noise (cloud fraction did); checked on the fBVOC test grid at 02:11, looks right. A background job (tmux `colscale_chain`) makes it the default once the test figures finish, reruns the 4 notebooks with grids (bvoc-soa-cloud, biogeophysical-hydro, simulation-contrasts, fut-fbvoc-emission-source-choice), then copies `results/figures` to `results/figures-2001-2014`. Progress: `/cluster/work/users/adelez/colscale-rerun/run.log` ("ALL DONE" at the end). The 2001–2025 rerun waits for it and will use the new scales too.</span>
>
> <span style="color:#7B2FBE">**fBVOC artefact: mechanism figure done (9 Nov, 00:47):** `fbvoc_artefact_causes.ipynb` has a new last section and figure `mechanism_soa_lifetime.png`. In the tropics the prescribed run has its isoprene/monoterpenes moved up (+18 %/+12 % at 400–100 hPa, −18 % isoprene at 850–700 hPa), SOA forms and sits higher, OH unchanged; the replay run shows none of this. The convection explanation fits but is not proven. Notebook rerun OK, not committed.</span>
>
> <span style="color:#7B2FBE">**fBVOC artefact: weather link confirmed (9 Nov, 17:25):** with the new run `CTRL_PD_fBVOCctrlPD_C0102` (2001–2002 climatology, right mean) the extra SOA is still **1.6 %** (vs 3.0 % with the 2001–2014 climatology and 0.5 % with the real fluxes). The extra ~1.5 % of the 14-year file comes from averaging away more weather, not from its different mean: in the tropics both means agree within 0.1 % and the difference is still 1.6 %. The wrong mean only moves SOA production between 30–45°N and 45–60°N. So about 2.5 of the 3 % is the lost weather link, and a shorter climatology does not fix it; only real year-by-year fluxes do. Conclusions added to `fbvoc_artefact_causes.ipynb` (section H6), notebook rerun OK.</span>
>
> <span style="color:#7B2FBE">**Sign of the artefact (9 Nov, 01:40):** the prescribed run has **more** SOA: 2.512 vs 2.438 mg m⁻² (interactive). A = interactive − prescribed = −3 %. The figure now says so.</span>
>
>
>
>
>
> <span style="color:#A84300">**Analysis on 2001–2025, automatic overnight (8 Nov, 23:02):** the 11 nudged runs are being processed for 2001–2025 (ends ~02:00). Then a script checks the files, puts them next to the 2001–2014 ones, waits for the reorganisation reruns, switches 9 analysis notebooks to **2001–2025** with **early 2001–2014 / late 2015–2025**, and reruns them, ready in the morning. LCC_FUT_fBVOClccFUT = design B. Result: `/cluster/work/users/adelez/analysis-2001-2025/SUMMARY.txt`.</span>
>
> <span style="color:#AAAAAA">**MEGAN batch 2 running (8 Nov, 22:37):** 2002, 2006, 2011 started ~21:10 (the automatic launch had stopped on 7 Nov); results Monday midday.</span>
>
> <span style="color:#A84300">**analysis/ and results/ reorganised (8 Nov, 23:05, reruns going):** only your 19 contrasts remain, in 4 categories (**interactive, fBVOC, non-BVOC, artefacts**), defined once in the code and with one folder each in `results/figures/` and `results/tables/`. LCC_FUT_fBVOClccFUT = design-B stand-in (one switch to replace it). All analysis notebooks are switched; old results in `results/*-pre-reorg-20261108/`. Dropped: the six-panel forcing summaries, the per-period context maps, and the FUT variants with PD emissions in the artefact split (now in the fBVOC category). Cumulative decomposition redone: the artefact is now removed from both steps; at ≥45°N the land-cover non-BVOC step is +0.26 W m⁻² and the corrected BVOC step −0.06 ± 0.05 W m⁻² (total unchanged, +1.19). The other notebooks are rerunning (tmux `reorgA/B/D`); tonight the other window's job then switches them all to 2001–2025 and reruns them.</span>
>
> <span style="color:#A84300">**Contrast pairs corrected (8 Nov, 22:24):** `analysis/simulation-contrasts.ipynb` now uses your list. Changes: LCC artefacts = LCC_P − LCC_P_fBVOCctrlP (so they include the BVOC effect of LCC); Fig. 3b row 2 = LCC_FUT_fBVOCctrlPD − CTRL_PD_fBVOCctrlPD (the missing CTRL_FUT_fBVOCctrlPD run is no longer needed); Fig. 2 uses a design-B stand-in for LCC_FUT_fBVOClccFUT (LCC_FUT − CTRL_FUT + CTRL_FUT_fBVOCctrlFUT) until that run is processed. Rerun done, all 9 figures, no errors. **22:24:** row names on the left now use your short form (e.g. CTRL_[FUT − PD]); Fig. 3b got a third row (row 2 − row 1, which equals Fig. 3a row 1). Rerunning.</span>
>
> <span style="color:#999999">**New changes to commit (8 Nov, 22:30):** another window fixed the pairs in `simulation-contrasts.ipynb` and is rerunning it; `plot_bvoc_emissions.ipynb` is also rerunning and `plot_bvoc_timeseries.ipynb` changed. Commit these after the runs finish (2 commits). The 7 earlier commits are still not pushed.</span>
>
> <span style="color:#999999">**Commits (8 Nov, 22:03):** all suggested commits are made, **not pushed**: sign flip, contrasts notebook, 2001–2019 set, BVOC emission plots, D1 check, docs (+ `methods-claude.tex` in the draft repo). Run `git push` in both repos when you want them online.</span>
>
> <span style="color:#62733B">**ISOP/MTERP time series per contrast (8 Nov, 23:23):** `preprocess/bvoc-emissions/plot_bvoc_timeseries.ipynb`, now with your corrected pairs, LCC-modified cells only, and the same vertical scale in every panel (ISOP and MTERP). One panel per pair, yearly Tg/yr. Colours: red/navy = LCC runs or fixed *lcc* emissions, orange/teal = CTRL runs or fixed *ctrl* emissions (FUT warm, PD cool); fixed-BVOC runs dashed. LCC_FUT_fBVOClccFUT is still running: 2001–2009 only. The two figures are saved in `preprocess/bvoc-emissions/plot_bvoc_timeseries_outputs/`.</span>
>
> <span style="color:#62733B">**BVOC emission plots moved to the new runs (8 Nov, 21:56):** `preprocess/bvoc-emissions/plot_bvoc_emissions.ipynb` now shows all four new-chain sources (CTRL_PD, LCC_PD, CTRL_FUT, LCC_FUT), with new maps of the forest-expansion change (LCC − CTRL) per period. The totals table and the species notebook follow it. The plotting notebook reran without errors (figures checked). North of 45°N, forest expansion raises isoprene by +3.1 % (PD) and +1.7 % (FUT); monoterpenes change little (+0.7 % / −0.3 %). The species notebook reran too; its table now shows the LCC values for the changed cells. Not committed.</span>
>
> <span style="color:#7B2FBE">**Artefact sign flipped, done (7 Nov, 01:30):** the artefact is now **interactive − prescribed** everywhere (e.g. CTRL_PD − CTRL_PD_fBVOCctrlPD ≈ −3 % SOA), and the corrected BVOC effect is (LCC − LCC_fBVOC) **− art**. The corrected BVOC numbers did not change. Docs, Methods outline and 10 notebooks updated, including the two old-chain cause notebooks. All 7 notebooks with saved results were rerun without errors and their numbers match the text; the 3 old-sign FUT Ghan figures are deleted. Not committed yet.</span>
>
> <span style="color:#A84300">**All contrasts in one notebook (7 Nov, 01:08):** `analysis/simulation-contrasts.ipynb`, 9 figures. Figs. 1b, 1c, 3a, 4b now have a third row = row 2 − row 1, below a line, in orange/blue-teal (other rows stay red/blue); checked on 1b. Note: the 1c third row is mathematically the same as the 1b one. Full rerun going (~6 min). Rows waiting for LCC_FUT_fBVOClccFUT shown as PENDING.</span>
>
> <span style="color:#A84300">**FUT emissions notebook done, conclusions written (7 Nov, 00:25):** both notebooks now run in minutes (FUT ~5 min, was >1 h; D1 ~4 min, was ~75 min; same numbers). D1 maps hatch the non-significant cells. **FUT results (≥45°N, 2001–2014):** the future background raises emissions 2.5× (isoprene) and 4.2× (monoterpenes); forest expansion adds only +0.39 Tg/yr isoprene (+1.7 %) and no measurable monoterpene change, almost all in the changed cells. Radiation: against CTRL_PD emissions the response is −0.91 W m⁻², but that is the climate-driven emission increase; the forest-expansion part, after the artefact correction, is −0.06 W m⁻² and not distinguishable from zero. The artefact is as large as the expansion effect for SOA and droplets, so uncorrected numbers must not be used.</span>
>
> <span style="color:#A84300">**MEGAN batch 2 (7 Nov, 00:10):** your OK given. Batch 1 is not finished yet (2001 and CTRL 2005 still running; 2010 re-reduced with the swaps, all checks pass), so a small script waits for 2001 and 2005 to be reduced and then launches 2002, 2006, 2011 by itself (raw files kept). It does not launch if a batch-1 year fails. Deleting the raw files: on hold (your call). LMDI vs approximate split comparison: later, no rush.</span>
>
> <span style="color:#A84300">**Reruns (6 Nov, 22:46):** **D1 done**, no errors (contributions plot now one column per comparison, checked). **Zonal-mean plot done** in your colours. **FUT emissions notebook not done yet:** the 21:23 run failed in its last data cell because it ran an old copy of the code, and the 22:05 relaunch was killed. Runs started from a Claude window die when that window closes. Relaunched 22:42 in `tmux` (session `futnb`, independent of Claude), ~45 min; don't edit that notebook while it runs (the runner would overwrite the edits). **Why slow:** raw monthly output read one file at a time, ≈ 2,900 file opens of 104 MB files (D1: 75 min for the same reason). Faster loader waits for your OK.</span>
>
> <span style="color:#999999">**Commits (6 Nov, 22:30):** your 12 commits (21:47–22:15) are pushed. My 3 commits of 22:25 are **undone** at your request; their changes (workflow images, `run_all_parallel.sh`, `CLAUDE.md`, `.gitignore`) are back as uncommitted edits. Still open as well: D1 and FUT emissions notebooks (reruns unfinished), 2001–2019 folder (failed), the logs.</span>
>
> <span style="color:#999999">**What to commit now (6 Nov, 22:08):** 6 of the 8 commits are ready (runs/watchers, LCC_FUT emission merge, MEGAN split code, FUT emission-source notebooks, PD artefact, warming plot colours). Wait for: D1 and the FUT emissions notebook (still rerunning), the 2001–2019 folder (see below), then CLAUDE.md, .gitignore and the logs. Nothing committed yet: waiting for your OK. **Log incident 21:55:** `CLAUDE_log.md` was found empty and restored from a 21:29 copy; edits from other windows in between may be missing.</span>
>
> <span style="color:#A84300">**2001–2019 preparation stopped with errors (seen 22:08):** all 11 runs failed on one file type (aerosol size, `AERSIZE`) with a NetCDF/HDF write error; nothing is running any more, so the notebook has not run. The window that started it should look at it.</span>
>
> <span style="color:#CC0000"><span style="background:#CC0000;color:#FFFFFF;padding:0 4px;border-radius:3px">**WAITING ON YOU**</span> **2001–2019 set (6 Nov, 22:05): stopped, my mistake.** I put its processed files in the home folder; they filled the home quota (30 GB) between ~21:50 and 22:00, so the job failed and anything else writing to home in that window may have failed too. Stopped and cleaned (home back to 14.6 GB); no processed files yet. Needs ~135–280 GB → proposed on work (no quota, deletes itself after 42 days). Also to decide: add the artefact-corrected (design B) version for 2001–2019; fix the LCC_FUT_fBVOClccFUT row (as written it would show the artefact as a BVOC effect).</span>
>
> <span style="color:#A84300">**MEGAN swaps explained + unit choices (6 Nov, 21:24):** the swaps were already written by the other window (21:15), so not redone. `analysis/MEGAN_ATTRIBUTION.md` now records them (option 1b, recommended path step 4) and lists 5 possible units for the headline numbers. Recommendation: Tg/yr (≥45°N) as headline, % of CTRL alongside. **Your pick needed** (no rush, nothing waits on it until results exist).</span>
>
> <span style="color:#7B2FBE">**FUT artefact, uncorrected vs corrected (6 Nov, 20:55):** the FUT emission-source notebook (`analysis/fut-fbvoc-emission-source-choice.ipynb`) now shows only artefact-corrected results; the side-by-side uncorrected → corrected map grid is in the new `diagnostics/fbvoc-prescription-artefact/how_big_artefact_is_FUT.ipynb`. Both have run and their figures are checked; the old source notebook is retired to `analysis/_old/`.</span>
>
> <span style="color:#A84300">**`radiative_forcing_2001-2019.ipynb` (6 Nov, 20:35):** a half-finished copy of `radiative_forcing.ipynb` for years 2001–2019, started 5 Nov 17:44 after you asked to analyse up to 2020 for the 9 Nov meeting; you interrupted that step and it was never finished. **Never run**: its input folder (2001–2019 postprocessed files) does not exist yet. Keep it for Monday or delete it: your call.</span>
>
> <span style="color:#999999">**Coordination (6 Nov, 18:14):** a note from another session about the LCC_FUT_fBVOClccFUT emission fix is handled by the session that started that fix (another window of this same session). Nothing changed here.</span>
>
> <span style="color:#A84300">**Evening work (6 Nov, 20:05):** LCC_FUT_fBVOClccFUT fix **finished** (re-merge checked bit-identical, 8 species recomputing, watchers restarted → run starts by itself tonight). Run list `run_aliases.csv` brought up to date (+ MEGAN runs, + LCC_FUT_fBVOClccFUT). FUT emissions notebook: its last section had crashed on 3 Nov (rounding in a check) → fixed, rerunning; conclusions follow. New notebook `analysis/fut-fbvoc-emission-source-choice.ipynb` (CTRL_PD vs CTRL_FUT vs LCC_PD emissions, with artefact correction) running. Methods draft: 5 yellow number boxes filled.</span>
>
>
> <span style="color:#CC0000"><span style="background:#CC0000;color:#FFFFFF;padding:0 4px;border-radius:3px">**WAITING ON YOU**</span> **Status 6 Nov, 17:55: two runs stopped overnight.** (1) **LCC_FUT_fBVOClccFUT never started:** its emission climatology failed for the 8 half-hourly species. Piece 1 of LCC_FUT_HRBVOC stores each day as 00:00–23:30, pieces 2–3 as 00:30–24:00, and the script stops at 2005. Proposed fix: regroup piece 1 the same way, rerun the 8 species, restart the watcher (~1 h of work, then ~1.5 days of runs). (2) **MEGAN CTRL_PD 2005 failed at launch** (Slurm network timeout on one node); **resubmitted 18:08** (job 1791950, ~15 h). Fix for (1) in progress in session 570e9150. Rest on track: nudged runs reached 2020, 8 of 11 already continue to 2026; MEGAN 2000 and 2010 reduced; 2001 running until ~03 h tonight.</span>
>
> <span style="color:#AAAAAA">**When the runs end (estimate 5 Nov, 18:42; without queue waits):** nudging folder ~23:00 today → 11 nudged runs to 2020 Fri 6 Nov ~18 h, to 2025 Sat 7 Nov ~17 h. LCC_FUT_fBVOClccFUT starts ~19:45 today, 2000–2014 done Sun 8 Nov ~01 h, to 2025 Mon 9 Nov evening. MEGAN test passes ~21 h today → batch 1 runs done Sat 7 Nov ~04 h, reduced by Sat morning.</span>
>
> <span style="color:#CC0000"><span style="background:#CC0000;color:#FFFFFF;padding:0 4px;border-radius:3px">**WAITING ON YOU**</span> **MEGAN driver swaps: DONE and validated (6 Nov, 21:15):** written into the reduction (your 4 answers of 17:55), all checks pass on the 60-day test and on 3 July days of 2010. Now live; 2010 being re-reduced (≈ 00:45); 2001 and 2005 get the swaps automatically. Batch 2: OK given 7 Nov 00:07 (see top). Deleting the batch-1 raw files: on hold.</span>
>
> <span style="color:#555555">**LCC_FUT_fBVOClccFUT on its way (5 Nov, 18:27):** LCC_FUT_HRBVOC is done and **identical** to LCC_FUT (360 monthly fields, 0 differences). Its emissions are being turned into the climatology now (19 species); a watcher then checks them, relabels them to 2100, starts LCC_FUT_fBVOClccFUT (2000–2014) and postprocesses it when done. LCC_PD_fBVOClccPD added to the extension to 2025 (11 runs now); LCC_FUT_fBVOClccFUT will follow to 2025 after its first 15 years (your OK 18:34).</span>
>
>
> <span style="color:#555555">**Archives fixed, and fixed automatically from now on (5 Nov, 17:40):** new **archive guard** on login-3 reruns any failed archive job by itself every 10 min (and continues the run chain). Bad nodes b5203 + b5204 now excluded everywhere. LCC_FUT half-hourly piece 1 archived; pieces 2, 3 and the MEGAN test are next.</span>
>
> <span style="color:#555555">**Nudged runs to 2025: automatic (your OK, 5 Nov 17:25):** MET finished and archived (2015–2025). The 2000–2025 nudging folder had never been built (the MET watcher had stopped on a bug, now fixed); it is being built now. A watcher then submits 2015→2020 for the 10 runs, and 2020→2026 for each run once its first part is archived. All 10 runs passed the checks.</span>
>
>
> <span style="color:#7B2FBE">**Why figure D shows big LCC_PD − CTRL_PD differences (4 Nov, 16:30):** **north of 45°N** they are real: they follow the plant-type changes (more boreal broadleaf → isoprene +19 %; needleleaf replacing arctic grass → monoterpenes +41 %; broadleaf replacing needleleaf → monoterpenes −11 %). **In the tropics** the land is the same and the change is tiny: typically **0.7 %** of the local emission, vs 5 % year-to-year noise. The pixels look strong only because tropical emissions are ~15 mg m⁻² day⁻¹ and the colour scale ends at 0.24. They follow small differences in leaf area, mostly in 2001–2002 (−1.4 % / −0.6 %), then ~0: the two runs start from different land restarts and need ~2 years to converge. That is why the notebook also shows 2003–2014. **Now in the notebook (16:50):** Figure D in % of CTRL_PD (tropics pale, ~0.8 %) and section 4f with the tables and a year-by-year plot. New finding: monoterpenes follow the plant types, but isoprene goes up in some cells and down in others with the same plant-type swap, so something else sets its sign (not tested yet).</span>
>
> <span style="color:#7B2FBE">**Is the PD artefact land-dependent? Now with 7 years (4 Nov, 15:50):** the notebook was rerun automatically on 2001–2007 (was 2 years). The ratio R (land part of the artefact ÷ BVOC effect) **dropped**: SOA global 0.54 (was 0.81), ≥45°N 0.39–0.44 (was 1.35–2.98), isoprene ~0.1, monoterpenes 0.40 (was 0.60). The global verdict still says "design A worth it", but only just (threshold 0.5). Over ≥45°N and the LCC cells, R sits between the two thresholds. SOA is still flagged "not resolved", only because 2001 has the opposite sign to the other 6 years. 2008–2014 will settle it.</span>
>
> <span style="color:#999999">**Watcher folder moved (4 Nov, 15:42):** `run_when_done/` is now in `cases-scripts/run_when_done/`. The one watcher still running (LCC_PD_fBVOClccPD 2008–2014) was stopped, moved and restarted on the same jobs; the run itself was not touched. The paths in the scripts, the docs and the two old-chain artefact notebooks are updated. **New rule:** I ask you before changing any old-chain notebook (was: never change them).</span>
>
> <span style="color:#CC0000">**MEGAN exact split: production test STARTED (your OK, 4 Nov 16:18):** CTRL_PD + LCC_PD from 2005-01-01, 2 × 30 days; builds running, then submission and automatic check + reduction (first attempt 16:16 broke because I removed its case folder by mistake; nothing was submitted). **Years now (your choice, 16:17): 2001–2002 (from 2000, 2000 discarded), 2005–2006, 2010–2011 = 6 years**; batches 2000-2001-2005-2010, then 2002-2006-2011. Background: the runs were not on hold, just not started. Found: the new-chain runs kept restarts only for **2005, 2010, 2015**, so the planned years 2002, 2004… can't be branched. Your choice: **new years 2005–2008 + 2010–2012** (two chains per run, one year per job), batches 2005-06-10, then 2007-08-11, then 2012; test from **2005-01-01**, now **2 jobs × 30 days = 2 months + 1 day** (your question, 16:14: two full months, two month boundaries and a restart like production; ≈ 2,500–2,800 core-hours). Scripts in `cases-scripts/megan-lmdi/` (README). To start the test: `bash cases-scripts/megan-lmdi/launch_megan_lmdi.sh test PD`. Still to code before production: the driver swaps (option 1b). **New (16:04):** years now 2001–2003 + 2005–2008 + 2010–2012 (2000 started from the spin-up, checked and deleted); batches 2000-2001-2005-2010, 2002-2003-2006-2011, 2007-2008-2012; each batch's end restart kept (also on NIRD).</span>
>
> <span style="color:#999999">**What to commit (4 Nov, 15:25):** proposed 3 commits (results reorganisation, LCC_PD_fBVOClccPD extension, logs), best after the `artefact-corrected-split.ipynb` rerun ends (~15:45). Files from other sessions (MEGAN LMDI, nudging) left out. Your new `.gitignore` line uses a full path, so it does not ignore `before_lake_fix/`.</span>
>
> <span style="color:#999999">**Results folder reorganised (4 Nov, 15:10):** `results/figures/` now has one folder per contrast: `LCC-CTRL/`, `CTRL_FUT-CTRL_PD/`, `fBVOC/` (design A, empty for now), `fBVOC/pre-artefact-correction/`, `fBVOC/artefact-design-B/` (was `artefact-corrected-split/`), `megan_factors/`, `timeseries/`. Tables stay flat, except `artefact-design-B/` (renamed), `pre-artefact-correction/`, and the old `2001-2014-all-bvoc-pre-co2-fix` tables now in `results/tables-2001-2014-all-bvoc-pre-co2-fix/`. The plotting code picks the folder from the figure name, so reruns land in the right place. All 196 figures kept. **My mistake:** the move broke a run of `artefact-corrected-split.ipynb` that another session had started; I restarted it at 15:07 (~35 min).</span>
>
> <span style="color:#A84300">**Artefact-corrected split, FUT with PD emissions (4 Nov, 14:35):** `analysis/artefact-corrected-split.ipynb` now also shows, for FUT, the corrected BVOC effect with **LCC_FUT_fBVOClccPD** (climate-driven emission change on LCC land) and **LCC_FUT_fBVOCctrlPD** (forest + climate), both corrected with the same FUT artefact. They are in every section (budget, chain table, maps). Rerun running since 14:34; first result: FUT corrected BVOC effect with PD emissions ≈ −1.0 W m⁻² globally (cloud), vs −0.02 with FUT emissions.</span>
>
> <span style="color:#AAAAAA">**LCC_FUT rerun with half-hourly BVOC (4 Nov, 14:32):** piece 1 (2000–04) at Dec 2003, done ~17:45; its BVOC is **identical** to LCC_FUT. Pieces 2 (2005–09) and 3 (2010–14) **resubmitted 14:30** with the right nudging start file and **past the start-up step** where they crashed before (14:33), ~16 h each → ~06:30 tomorrow.</span>
>
> <span style="color:#7B2FBE">**LCC_PD_fBVOClccPD to 2014 (4 Nov, 14:50):** the 2003–2007 part finished 14:35; its archive job died on a bad node, so I archived it by hand. 2003–2007 is being postprocessed now. The **2008 → 2014 run is submitted** (job 1788254, ~27 h, done ~5 Nov evening). A new watcher then postprocesses 2001–2014 and reruns the artefact notebook by itself.</span>
>
> <span style="color:#999999">**Commits and the `run_when_done` folder (3 Nov, 23:30):** I suggested 7 commits, one per topic. **Nothing is committed yet.** Moving `run_when_done/` out of the artefact folder: **wait**. The watcher for the 14e extension is still running and has that path written into it. All three watcher scripts rerun notebooks in that folder, so it can also just stay there.</span>
>
> <span style="color:#CC0000"><span style="background:#CC0000;color:#FFFFFF;padding:0 4px;border-radius:3px">**WAITING ON YOU**</span> **MET extension + nudged runs to 2025 (4 Nov, 01:00):** MET is **running** (2015 → 2026, two pieces; first piece ends ~20:30 today). The test passed. A watcher fills the 2000–2025 nudging folder **by itself** after each piece (first fill ~22–23 h today, 2000–2020). If an archive job dies on a bad node, the watcher redoes it and starts the second piece. The extension of the **10 nudged runs** is ready but **not submitted**: part 1 = 2015–2019, can start once the first fill is done; part 2 = 2020–2025, after MET ends. Your OK is needed to submit part 1. Also: include LCC_PD_fBVOClccPD (the 3-yr test, now running to 2007)?</span>
>
> <span style="color:#008080">**FUT BVOC decomposition notebooks, new runs (3 Nov, 21:23):** the two `-after-co2-fix` notebooks in `diagnostics/FUT-fBVOC-background-lcc-effect-decomposition/` are built and run (new runs 2001–2014, palette, hatched non-significant cells). **Main change:** the big negative FUT expansion effect of the old runs is gone. North of 45°N, forest expansion now adds +0.29 (PD) / +0.39 (FUT) Tg/yr isoprene and about 0 monoterpenes (old: −2.6 / −3.9 in FUT). The conclusion text of the emissions notebook is not rewritten yet. Paused at your request.</span>
>
> <span style="color:#008080">**Contrast maps for your three questions (3 Nov, 20:20):** new notebook `diagnostics/lcc-bvoc-background-contrast-maps/contrast_maps_uncorrected.ipynb`. Map grids (rows = contrasts, columns = variables) for Q1 effect of land-cover change in PD and FUT, Q2 FUT BVOC emission source, Q3 PD → FUT. Raw differences, artefact **not** added. Done: 9 map grids + regional-mean table, the contrasts add up exactly. In FUT, switching from PD to FUT emissions gives −0.94 W m⁻² at the top of the atmosphere (≥45°N), the land-cover-driven emission change only −0.01.</span>
>
> <span style="color:#999999">**Mask folder moved (3 Nov, 20:20):** `lcc-modified-cells/` (the modified-cells mask) now sits directly in `diagnostics/` instead of `diagnostics/check-simulation-equilibrium/`. All notebooks and scripts that read it were updated (~30 files, incl. two plotting modules in `src/` that pointed to a wrong folder name); every path checked to exist.</span>
>
> <span style="color:#008080">**Nudging impact on land, new runs (3 Nov, 20:43):** `impact_of_nudging_on_land.ipynb` is on the new runs (2001–2014). Maps now hatch the non-significant cells, and a new figure shows MET and the four nudged runs on the same years. Nudging gives the land less sun (−4.6 W m⁻²) and makes it cooler (soil −0.24 K), equally in CTRL and LCC, so it cancels in LCC − CTRL. No action needed for the analysis; optional: a stricter significance test on the drift maps.</span>
>
> <span style="color:#A84300">**Time-series notebook (3 Nov, 20:33):** new `analysis/timeseries-responses.ipynb`: yearly values 2001–2014 of the 9 context-map variables + the Ghan terms. Part 1: differences, one figure per contrast, global line + modified-cells/≥45°N line. Part 2 (your follow-up): the actual values of every nudged run, 4 figures (PD/FUT × global/regional), one line per run. Figures in `results/figures/timeseries/`. 2000 is missing (spin-up year). Caveat: droplet radius/number are in-cloud values, so small run-to-run gaps in their global lines are not reliable.</span>
>
> <span style="color:#A84300">**BVOC_A emissions outside the changed cells (3 Nov, 21:00):** **decided 4 Nov: keep design A** (analyse means ≥45°N / LCC cells; no hybrid run).</span>
>
> <span style="color:#AAAAAA">**LCC_PD_fBVOClccPD extension running (3 Nov, 21:46):** the first two submissions died at start on 4 faulty compute nodes (python error; python works on other nodes). The third submission avoids those nodes and is running since 21:33 (2003–2007, ~17 h). The watcher then postprocesses, reruns the notebook and updates CLAUDE.md automatically.</span>
>
> <span style="color:#7B2FBE">**Is the PD artefact land-dependent? (3 Nov, 20:45):** `how_big_artefact_is_PD.ipynb` now has global + Arctic maps, split into artefacts (A1: art_CTRL, art_LCC, δ_PD) and BVOC estimates (A2: C, BVOC_B, BVOC_A), and verdicts over the LCC cells (3b) and north of 45°N (3c). Global δ_PD is a tropical offset of 2001–2002, not the land. Over the LCC cells: **isoprene hardly depends on the land** (ratio 0.12), **monoterpene does, moderately** (0.60, same sign both years), and **SOA is not resolved** with 2 years (the BVOC effect itself flips sign). No need to drop 2001–2002 from the main analysis (≤0.2 percentage points).</span>
>
> <span style="color:#A84300">**New fBVOC analyses (3 Nov, 20:27):** notebook 1 `analysis/artefact-corrected-split.ipynb` (corrected BVOC + non-BVOC split, PD and FUT) is **running** (started 20:26), outputs into `results/{figures,tables}/artefact-corrected-split/`. Old uncorrected fixed-BVOC results are in `pre-artefact-correction/`; the 27 pure LCC − CTRL figures stay. Next: read the results, then notebook 3 (artefact robustness).</span>
>
> <span style="color:#E58AA5">**Contrast label on the forcing-decomposition maps (4 Nov, 15:01):** done: `analysis/radiative_forcing.ipynb` rerun without errors, incl. the new **LCC_FUT_fBVOClccPD** figures, now in `results/figures/fBVOC/pre-artefact-correction/`.</span>
>
> <span style="color:#999999">**Git tidy (3 Nov, 18:40):** you made 18 commits; I added 4 more for what was left (palette in the diagnostics, diagnostics README, D2 on the new chain, palette rerun of 2 analysis notebooks). `main` is 10 commits ahead of GitHub, **not pushed**. Left out on purpose: D1 on the new chain (its saved run fails, ValueError) and `megan_patch_branch_5day_test.ipynb` (only re-saved, same content).</span>
>
>
> <span style="color:#999999">**Conda cache in git, fixed (3 Nov, 17:33):** conda had put a 1.1 GB package cache in `docs/nird/.conda/` because `~/.condarc` used a relative path. The config now uses absolute NIRD paths (backup `~/.condarc.bak`) and the cache is deleted. The other ~320 staged files were staged by VS Code on **2 Nov 19:00**: a commit from Source Control with nothing staged runs "stage all" first (`git add -A`), then the commit stopped because the message was empty. Nothing was committed.</span>
>
> <span style="color:#E58AA5">**Zonal-mean warming plot in palette O (3 Nov, 17:10):** test copies in `sandbox/test_palette_picture_outputs/zonal_mean_dT_P1_*` (annual navy, DJF teal, JJA red, SST plum dashed) and `*_P2_*` (JJA orange, SST gold). Notebook untouched; your pick next.</span>
>
> <span style="color:#E58AA5">**We have a palette (3 Nov, 17:35):** teal, navy, plum, red, orange, gold (gold = totals), light grey for residuals. Now the default in the plotting code and used in all analysis and diagnostics notebooks. The 5 analysis notebooks with bar/line charts are being rerun (started 17:31; progress in `results/tables/logs/rerun_palette_20261103.log`), so `results/figures` gets the new colours. Diagnostics notebooks are updated in the code but still show old colours until rerun.</span>
>
> <span style="color:#008080">**How much warmer is FUT, one version (3 Nov, 15:28):** `diagnostics/how-warmer-future-climate-is/` now has a single notebook, on the new runs (after the CO₂ fix); the old-run version and its outputs are deleted. The numbers are the same to 0.1 K: global **+3.5 K**, Arctic **+8.9 K**, forest-expansion cells **+7.5 K** (was +7.4), **+3.9 K** relative to pre-industrial.</span>
>
> <span style="color:#A84300">**MEGAN lake fix (3 Nov, 15:50):** fixed with your OK; figures remade (old ones in `results/figures/megan_factors/before_lake_fix/`), stale "different spin-ups" note removed. **Effect is negligible:** the split moves by only 0.05–0.07 (in % units) from activity to composition north of 45°N; locally up to ~10 in 12 tundra cells of northern Canada. Notebook: `diagnostics/megan-exact-split-test/lake_fix_effect.ipynb`.</span>
>
> <span style="color:#A84300">**MEGAN exact split, your decisions (3 Nov, 15:45; years and test date replaced 4 Nov, see above):**  32-day test approved (runs once the production script and launcher are written; I check with you before submitting); first batch = 2002, 2008, 2014. **Later:** after PD batch 1, compare the exact split with the current maps for those 3 years before running the rest; then FUT. All in `analysis/MEGAN_ATTRIBUTION.md`.</span>
>
> <span style="color:#999999">**Old figures kept (3 Nov, 15:17):** the rerun did not overwrite the paper figures: the old 118 are in `results/figures-2001-2014-all-bvoc-pre-co2-fix/`. Only the artefact notebooks' own output folders were rewritten, and the old versions there were either a stand-in or the same old data.</span>
>
> <span style="color:#AAAAAA">**Status check (3 Nov, 14:34):** no jobs running or queued. Overnight rerun finished 00:09: all notebooks OK except `D1_farfield_check.ipynb` (FAIL: duplicate labels when plotting). PD artefact test done: δ_PD is about as big as the BVOC effect (global SOA burden δ_PD +1.06 % vs BVOC_B −1.30 %; only 2 years), so the notebook says design A in FUT is worth its 2 runs: **your decision**.</span>
>
> <span style="color:#999999">**Folder tidy (2 Nov, 18:50):** in `diagnostics/fbvoc-prescription-artefact/` the two watcher scripts and their logs/pids now live in `run_when_done/` (logs in `logs/`, pids in `pids/`); scripts and notebook mentions updated.</span>
>
> <span style="color:#A84300">**MEGAN γ_eff bug (2 Nov, 17:52):** lakes were wrongly counted in the area used for γ_eff in `megan_maps.py`. **Answered 3 Nov: fixed**, figures being remade (see 15:30).</span>
>
> <span style="color:#7B2FBE">**Artefact write-up (2 Nov, 17:47):** everything we discussed about the artefact is now in `analysis/FBVOC_ARTEFACT.md` (problem, cause, designs A/B with formulas, decision, first numbers). CTRL_PD_fBVOCctrlPD has finished and is being postprocessed; then the PD test notebook gives δ_PD.</span>
>
> <span style="color:#AAAAAA">**Run status (2 Nov, 16:44):** still to finish: CTRL_PD_fBVOCctrlPD (at Oct 2014, done tonight); LCC_PD_fBVOCctrlPD finished 16:23 but is not postprocessed yet. All other new-chain runs are done and processed. The run list `run_aliases.csv` still says "waiting" for most runs (out of date). 5 old `CTRL_PD_fBVOCctrlPD_HR_*` files are back in the current processed folder: to check.</span>
>
> <span style="color:#7B2FBE">**Artefact runs (2 Nov, 16:43):** both new runs are done and postprocessed: LCC_PD_fBVOClccPD (31 Oct) and CTRL_FUT_fBVOCctrlFUT (today). First numbers (SOA burden): artefact on LCC land, PD 2001–02: **+3.6 %**; FUT artefact (CTRL land, 2001–14): **+2.8 %**, but it varies a lot from year to year (+0.8 to +5.2 %; ~+5 % in 2001–03). The PD test (`how_big_artefact_is_PD.ipynb`) still waits for CTRL_PD_fBVOCctrlPD, which finishes this evening; then I rerun it.</span>
>
> <span style="color:#008080">**Are the 14 years independent? (2 Nov, 16:32):** new notebook `diagnostics/yearly-difference-autocorrelation/`. Yes for radiation, temperature and clouds (like random noise). Emissions and SOA burden differences show slow **trends** over 2001–2014 (e.g. FUT SOA effect +13 % per decade), not year-to-year memory: worth checking for drift. A draft methods sentence is in the notebook.</span>
>
> <span style="color:#A84300">**Analysis on the new runs (2 Nov, 16:21):** old results moved aside (processed files → `postprocessing/2001-2014-all-bvoc-pre-co2-fix/`, figures → `results/figures-2001-2014-all-bvoc-pre-co2-fix/`, tables → `results/tables/2001-2014-all-bvoc-pre-co2-fix/`). SOA burden now uses the model field (same value as before within 0.02 %). Notebooks are being rerun in the background: FUT and MEGAN ones now, the PD ones once LCC_PD_fBVOCctrlPD is processed (~this evening), the artefact notebook after CTRL_PD_fBVOCctrlPD. Progress: `results/tables/logs/rerun_new_chain_20261102.log`.</span>
>
> <span style="color:#CC0000"><span style="background:#CC0000;color:#FFFFFF;padding:0 4px;border-radius:3px">**WAITING ON YOU**</span> **MEGAN test before batch 1 (2 Nov, 19:15):** proposal: a 32-day test (1 Jan – 2 Feb 2002) of CTRL_PD and LCC_PD with the real production script and launcher, ≈ 1,200 core-hours (3 % of batch 1). It also checks the monthly output, never tested so far. OK, or a shorter 5-day test?</span>
>
> <span style="color:#7B2FBE">**Test runs archived (2 Nov, 17:58):** the 2001–2002 test is now `CTRL_PD_fBVOCctrlPD_test2yr` and, with the replay test, sits in `postprocessing/2001-2014-all-bvoc-pre-co2-fix/`. The three artefact notebooks read them from there.</span>
>
> <span style="color:#CC0000"><span style="background:#CC0000;color:#FFFFFF;padding:0 4px;border-radius:3px">**WAITING ON YOU**</span> **Methods outline (4 Nov, 14:50):** main FUT fixed-BVOC emissions **on hold** (your call): options CTRL_PD, CTRL_FUT, **LCC_PD** now in a table in `methods-claude.tex`; until decided, all three are plotted. Journal still open.</span>
>
> <span style="color:#AAAAAA">**Status (2 Nov, 15:58):** the four new nudged runs finished 30–31 Oct and are processed. The launcher started all 7 fixed-BVOC runs on 31 Oct; 5 are finished and processed (LCC_PD_fBVOClccPD, both FUT ctrlFUT runs, LCC_FUT_fBVOClccPD; LCC_FUT_fBVOCctrlPD is being processed now). The last two (CTRL_PD_fBVOCctrlPD, LCC_PD_fBVOCctrlPD) are in their final months of 2014 and finish this evening. **Next:** run the artefact notebook (`how_big_artefact_is_PD.ipynb`) once CTRL_PD_fBVOCctrlPD is processed; switch the analysis to the new runs and rerun; MEGAN batch 1 still needs its launcher and your OK.</span>
>
> <span style="color:#7B2FBE">**Artefact plan decided (30 Oct, 16:48):** we use the **matched baseline**: BVOC effect = (LCC − LCC_fBVOC) + the artefact measured on CTRL land. Two new runs start **automatically**: **CTRL_FUT_fBVOCctrlFUT** (15 years, together with LCC_FUT_fBVOCctrlFUT once CTRL_FUT is done, ~tonight) gives the FUT artefact; **LCC_PD_fBVOClccPD** (3 years, after LCC_PD, ~31 Oct night) checks whether the artefact depends on the land cover. New notebook `diagnostics/fbvoc-prescription-artefact/how_big_artefact_is_PD.ipynb` gives that answer once LCC_PD_fBVOClccPD is processed (for now: "pending"; tested with a stand-in run, it reproduces the earlier numbers). The launcher was restarted to include the two runs.</span>
>
> <span style="color:#008080">**How much warmer is FUT? (30 Oct, 11:27):** new notebook `diagnostics/how-warmer-future-climate-is/how_warmer_future_climate_is.ipynb`. Global mean air temperature: FUT is **+3.5 K** warmer than PD (land +4.9 K, ocean +2.9 K). Arctic **+8.9 K** (winter +13.6 K). Where the forest expands: **+7.4 K**. The warming is mostly imposed through the prescribed 2090–2100 ocean (SST +2.2 K, no Arctic summer sea ice) and CO₂ 369 → 1135 ppm. Relative to pre-industrial (1850–1900): about **+3.9 K** globally (estimate: our +3.5 K plus NorESM2's own +0.4 K warming up to ~2000). Uses the old-chain CTRL runs; rerun on the new chain once archived.</span>
>
> <span style="color:#AAAAAA">**Runs (30 Oct, 11:00):** all four nudged runs are in good shape, about 3.3 h per model year. LCC_FUT and CTRL_FUT are at 2011 in their last block and should finish tonight (~21–22 h); LCC_PD finishes ~00:30; CTRL_PD is a block behind (2008) and should finish early on 1 Nov. The fixed-BVOC runs then start by themselves (the launcher is alive).</span>
>
> <span style="color:#CC0000">**Replay result (30 Oct, 11:19):** with CTRL_PD's real year-by-year emissions SOA is only **+0.5 %** (the climatology run: +3.0 %). So the artefact comes from using a **climatology**. Written as verdict H5 in `fbvoc_artefact_causes.ipynb`. **Waiting on you:** how to set up the fixed-BVOC runs (matched baseline, replay design, or as planned); the first two (24c, 24d) start automatically tonight ~23:00 and ~01:00 unless paused.</span>
>
> <span style="color:#008080">**MEGAN 5-day LCC test (30 Oct, 11:19):** checked, passed: same settings as its parent, all fields written, the per-plant emissions add up exactly to what the atmosphere receives, same cost as the full-output test (the cost is the per-plant output itself). Section 6 of `megan_patch_branch_5day_test.ipynb`.</span>
>
>
> <span style="color:#A84300">**MEGAN attribution (29 Oct, 15:30):** the attribution figures now show the residual split into its two parts, with fixed colour scales (PD ±60, FUT ±100). Because the split by factor (LAI, temperature, light…) will be a paper result, the plan is to compute it **exactly**: rerun 2001–2014 of CTRL and LCC as one-year copies that save the MEGAN factors per plant type every half hour, in batches of 3 years (your decision). Cost ≈ 1 % of the project CPU hours; at most ≈ 1.8 TB on disk. A 5-day test checks that this works: the first try failed at start-up (the nudging data were read from the year 2000 instead of 2005); fixed and resubmitted (job 1784026). Everything is explained in `analysis/MEGAN_ATTRIBUTION.md`.</span>
>
> <span style="color:#999999">**Log colours (29 Oct, 12:49):** each entry in this log now has a colour for its topic (legend under the title); it shows in the VS Code preview. Blank lines between items fixed earlier (12:05).</span>
>
> <span style="color:#7B2FBE">**Fixed-BVOC control on the new chain (29 Oct, 12:49):** the test run CTRL_PD_fBVOCctrlPD will be redone on the new chain for 15 years (2000–2014). It starts automatically when the new CTRL_PD emissions are ready, together with LCC_PD_fBVOCctrlPD. Then the BVOC effect can be measured between two runs that both prescribe emissions, so the +3 % artefact cancels. The coupler check found nothing: switching MEGAN off only removes the 19 MEGAN fields. The replay test is handled by another session.</span>
>
> <span style="color:#555555">**Automatic postprocessing (29 Oct, 13:03):** each new-chain run is now postprocessed automatically when it finishes, right after its old results are moved to the archive folders. Nothing has run yet: the first new runs finish in about 1–2 days.</span>
>
> <span style="color:#B8860B">**Nudged runs after the CO₂ fix (29 Oct, 11:45):** all four are running normally (15 years each, 2000–2014, in three 5-year blocks). CTRL_FUT, LCC_FUT and LCC_PD are at mid-2004 and finish their first block around 13:00–14:00 today; CTRL_PD started at 05:30 and is at late 2001. Expected end (if the queue is quick): CTRL_FUT/LCC_FUT ~30 Oct evening, LCC_PD ~31 Oct after midnight, CTRL_PD ~31 Oct morning. The fixed-BVOC runs then start automatically, but I couldn't confirm from this login node that the launcher is still alive.</span>
>
> <span style="color:#999999">**Notebook check (29 Oct, 10:50):** no notebook lost cells. Only `analysis/cumulative_radiative_decomposition.ipynb` lost its saved results: it was run at 10:22 while `derived.py` was damaged, so it holds an import error. Its figures and table on disk are fine. Rerun at 11:29: all 7 cells ran, no errors (checked 29 Oct 14:10).</span>
>
> <span style="color:#7B2FBE">**Artefact cause and replay run (29 Oct, 13:40):** `fbvoc_artefact_causes.ipynb`: the +3 % SOA of the fixed-BVOC test run is **not** more SOA production (unchanged) but a **3 % longer SOA lifetime**; the extra SOA sits high up (400–100 hPa), and in the tropics SOA forms higher. Missing species and timing are ruled out. Likely cause (b): the average emissions are also released on convective days and lifted before reacting. Test: replay run `CTRL_PD_fBVOCctrlPD_HR` (CTRL_PD's actual 2000–2002 emissions) was submitted at 13:20; result tomorrow. Summary figure with a paper-style caption and a section explaining every calculation (with worked examples) at the end of the notebook.</span>
>
> <span style="color:#7B2FBE">**Fixed-BVOC artefact confirmed (29 Oct, 10:46):** the test run CTRL_PD_fBVOCctrlPD (CTRL_PD with its own emissions prescribed, 2001–2002) has ~3 % more SOA than CTRL_PD everywhere (global +3.0 %, ≥45°N +3.0 %). So prescribing the emissions by itself raises SOA, and this explains 62–74 % of the SOA drop in LCC − LCC_fBVOC (≥45°N: −4.2 % → −1.3 % once corrected). Notebook: `diagnostics/fbvoc-prescription-artefact/`.</span>
>
> <span style="color:#62733B">**BVOC species table (29 Oct, 10:40):** new notebook `preprocess/bvoc-emissions/bvoc_species_processes.ipynb` lists all 19 prescribed species with emissions and what they do in NorESM. Key point: in this model only monoterpenes and isoprene make SOA (β-caryophyllene and toluene only affect gas chemistry), and only monoterpenes create new particles. The seasonal maps in `plot_bvoc_emissions.ipynb` now show zero flux in white.</span>
>
> <span style="color:#A84300">**Cumulative radiative chart (29 Oct, 00:06):** `analysis/cumulative_radiative_decomposition.ipynb` now runs on the real runs (was a demo). Net TOA, ≥45°N: future background +1.01, + forest biophysics +0.14, + BVOC +0.14 → total +1.29 W m⁻² (modified cells: +2.69, +0.52, +0.17 → +3.38). Old-chain runs, provisional. Figures in `results/figures/cumulative-radiative-decomposition/`.</span>
>
> <span style="color:#A84300">**PD–FUT findings rewritten (28 Oct, 23:58):** on the 2001–2014 all-BVOC set: PD has no BVOC radiative effect (+0.01 ± 0.04 W m⁻², ≥45°N); in FUT the sign depends on the emission reference (−0.77 vs CTRL_PD emissions, +0.14 vs CTRL_FUT emissions); the +0.14 comes mostly from lower emissions in unmodified land (likely the CO₂-bug spin-up legacy). Text at the top of `analysis/pd-fut-attribution.ipynb`.</span>
>
> <span style="color:#7B2FBE">**Fixed-BVOC artefact test (29 Oct, 00:05):** in the present-day fixed-BVOC run, SOA is ~3 % higher than in CTRL_PD everywhere, although its emissions are the same, so most of the SOA drop in the PD BVOC maps probably comes from how the emissions are prescribed (not proven yet). The 3-year test run `CTRL_PD_fBVOCctrlPD` is running (started 23:50, done ~11:00–12:00). A notebook for the meeting is ready (`diagnostics/fbvoc-prescription-artefact/`); a background script postprocesses the run when it is archived and reruns the notebook automatically. Until then it shows the contrasts that already exist. Section 3 of the notebook explains why we suspect an artefact: same emissions but +3 % SOA in every region, season and year; it accounts for 70 % of the SOA drop globally and 84 % north of 45°N. North of 45°N it is a winter/spring effect (+5.9 % in winter, +0.5 % in summer).</span>
>
> <span style="color:#E58AA5">**Cloud types (29 Oct, 00:08):** vertical profile figures now hatch the non-significant cells (paper figures updated; the cloud and biogeophysical-hydro notebooks were rerun at 00:46 without errors). section 3 of `bvoc-soa-cloud-interactions.ipynb` (low/mid/high cloud, liquid/ice water) is done and the notebook has been run; figures in `results/figures/`. The LCC − fixed-BVOC grids now have a 4th row (fixed BVOC from CTRL_FUT − from CTRL_PD). **Main finding (old runs, provisional):** in the future, the BVOC cloud response in summer (more low and mid cloud, +4.6 g m⁻² liquid water, less high cloud) comes almost entirely from the future-climate emission increase, not from the forest change. Present day: within noise.</span>
>
> <span style="color:#E58AA5">**MEGAN figures (28 Oct, 23:56):** all 20 MEGAN figures redone in the new style (isoprene + monoterpenes, PD + FUT, annual + summer). FUT: emissions −27 % in summer, but almost all from the LAI factor, also outside the forest-expansion area, so it is the spin-up mismatch, not the forest; only the composition term (+3 %) is clean.</span>
>
> <span style="color:#A84300">**Analysis rerun on the 2001–2014 all-BVOC set (28 Oct, 21:52):** the 5 analysis notebooks now use the new set (fixed-BVOC runs with all 19 species from CTRL_PD), plus a new notebook comparing the two future fixed-BVOC runs (CTRL_PD vs CTRL_FUT emissions). The fBVOC − CTRL contrast is gone; CTRL_FUT − CTRL_PD is added. Third row of the new notebook is now fBVOCctrlFUT − fBVOCctrlPD. Means under the maps now always have at least 2 significant digits; the LCC − fBVOC grids get a third row LCC_FUT − LCC_FUT_fBVOCctrlFUT, and there is a new BVOC/SOA/cloud map figure for LCC_FUT − LCC_FUT_fBVOCctrlFUT. Also added: forcing summary figures for LCC_FUT vs LCC_FUT_fBVOCctrlFUT (next to the FUT ones). Mean format fixed: one rule based on the mean only (small means always ×10ⁿ), and a CI of ~0 (identical prescribed emissions every year) no longer prints 17 decimals. FUT context maps now come as FUT_fBVOCctrlPD and FUT_fBVOCctrlFUT. The new notebook's figures are now in `results/figures/` (no subfolder), and figure names say which fixed-BVOC run they use (`PD_fBVOCctrlPD_…`, `FUT_fBVOCctrlPD_…`, `FUT_fBVOCctrlFUT_…`, Ghan `LCC-fBVOCctrlPD`). Those notebooks reran without errors; `pd-fut-attribution` reran too: all 6 notebooks and their 2001–2014 figures are now up to date. With CTRL_FUT emissions as the reference, the FUT BVOC-related forcing ≥45°N is +0.14 ± 0.04 W m⁻² (vs −0.77 with CTRL_PD emissions). All 6 notebooks are running now; old 2001–2009 figures are kept.</span>
>
> <span style="color:#555555">**New output fields in postprocessing (28 Oct, 21:15):** the recommended new fields are now in the postprocessing, with 3 new categories (BVOC oxidation products, particle size per mode, surface exchange). The 7 runs already processed (all old chain, 2001–2014) don't contain the new atmosphere fields, so only one extra file per run is possible: stomatal resistance (surface exchange), done for all 7 runs (2001–2014, checked). Everything else comes when the new runs are processed.</span>
>
> <span style="color:#555555">**Archive + postprocessing (28 Oct, 20:44):** the 7 runs are now on NIRD and checked complete. Postprocessing of the 2001–2014 all-BVOC, pre-CO₂-fix set is nearly done (in `postprocessing/`, ready for the analysis rerun). From now on new runs are postprocessed straight from /cluster/work; the current processed set will move to `2001-2014-all-bvoc-pre-co2-fix/` when the new chain is postprocessed. **⚠ Another Claude session cancelled and relaunched CTRL_FUT, LCC_FUT, LCC_PD at 20:27 to add SOA burden fields (~5–6 h of run time lost); the auto-launcher is stopped until it is restarted.**</span>
>
> <span style="color:#AAAAAA">**Runs restarted (28 Oct, 21:00):** CTRL_FUT, LCC_FUT and LCC_PD (new chain) were stopped and relaunched (all three running again) so they also write the SOA column burdens `cb_SOA_A1` and the cloud-borne SOA burdens `cb_SOA_A1_OCW`, `cb_SOA_NA_OCW`. About 6 h of model time lost per run. The automatic launcher is running again and will start CTRL_PD (~05:00 tomorrow) and the fixed-BVOC runs by itself. Output tables in `docs/history-output/` updated (117 added fields). The postprocessing will pick up the new SOA fields, and `CLAUDE.md` now has a step to switch the SOA burden plots (and the other new fields) once the post-CO₂-fix runs are processed.</span>
>
> <span style="color:#E58AA5">**Colourbar ticks (28 Oct, 19:00):** the outer of the 5 colourbar ticks now sits at 91–99 % of the bar end (e.g. ±0.28 instead of ±0.2); the ×10⁻ⁿ factor starts at 10⁻² and is now printed above the right end of the bar (it overlapped the label below); the mean under grid maps is bigger (12 pt). Sandbox only: the 5 grid figures were redrawn on their own (not the whole notebook) in `sandbox/test_layout_all_figures_outputs/`.</span>
>
> <span style="color:#E58AA5">**Figure titles (28 Oct, 16:40):** titles now read "fsds_split: LCC − LCC_fBVOC (2001–2009)" and "Ghan decomposition, LW: LCC_PD_fBVOC − CTRL_PD (2001–2009)"; Ghan panels TOTAL / AEROSOL-DIRECT / CLOUD / REST; notebook hatching notes kept. Tested in `sandbox/test_titles_outputs/`; now also in the paper figures (all regenerated 28 Oct 21:52–00:46 on the 2001–2014 set; checked 29 Oct 14:10). Nothing left to decide.</span>
>
> <span style="color:#555555">**Fixed-BVOC runs now automatic (28 Oct, 15:55):** the launcher builds the emission files and starts the four fixed-BVOC runs as soon as CTRL_PD, CTRL_FUT and LCC_PD finish. The isoprene/monoterpene-only runs are dropped. Running now: CTRL_FUT, LCC_FUT, LCC_PD (new chain); CTRL_PD starts ~05:00 tomorrow.</span>
>
> <span style="color:#B8860B">**Nudged-run status (28 Oct, 14:08):** no post-CO₂-fix nudged run is archived yet. Every archived nudged run is still on the old chain: CTRL_PD/CTRL_FUT `-20261023`, LCC_PD/LCC_FUT `-20261005` (both 2000–2014, LCC_FUT with the CO₂ bug), fBVOC all-species 14c/24c/24d `-20261025` (2000–2014, provisional), and the old ISOP/MTERP-only `_IM` runs (2000–2009). New chain: CTRL_FUT `-20261028` running since 14:00 (year 1 of 15); LCC_FUT `-20261028` building; 13b at year 16–20 (LCC_PD next); 13c at year 16–20 (CTRL_PD next).</span>
>
> <span style="color:#555555">**Alias table (28 Oct, 14:22):** `cases-scripts/run_aliases.csv` lists every run, spin-ups and MET included, with the aliases from the chain figure, old and new versions, case names, years, status and parent runs. 24e = `LCC_FUT_fBVOClccPD` (present-day LCC emissions), confirmed.</span>
>
> <span style="color:#555555">**Processed files (28 Oct, 14:02):** all old 2001–2009 processed files (96 + logs) are now in `postprocessing/2001-2009-pre-co2-fix/`. The main folder is empty until new files are made, so the analysis notebooks won't find any data there for now. Postprocessing of 14c/24c/24d is ready but **not started**; it waits for your OK after the alias explanation.</span>
>
> <span style="color:#555555">**Field tables (28 Oct, 14:30):** `docs/history-output/` lists every output variable (CAM, CLM) with units and description; the 114 new ones are in `added_fields_20261028.csv`. The postprocessing doesn't use the new CAM fields yet.</span>
>
> <span style="color:#555555">**New output fields (28 Oct, 14:15):** more chemistry, deposition, particle number/size (CAM) and roughness, resistance, albedo and snow-radiation fields (CLM) are in the new 15-year runs; every name checked (7 suggested CLM names don't exist and would have crashed the runs). **CTRL_FUT started at 14:00 and writes all 262 requested fields**; the land model accepted its list too. LCC_FUT starts next, LCC_PD ~15:30, CTRL_PD ~05:00 tomorrow. Adds ~9 GB per run (a CTRL run is 57 GB now); NIRD is 98 % full.</span>
>
> <span style="color:#AAAAAA">**Runs (28 Oct, 12:50):** the three all-species fixed-BVOC runs (14c, 24c, 24d) **finished overnight** and are archived (2000–2014 complete); they can be postprocessed (provisional, for the meeting). The new coupled spin-ups are almost done: 23c and 23b within the hour, 13b around 15:00, 13c (present-day CTRL) around 05:00 tomorrow. The watcher then starts the new 15-year runs by itself.</span>
>
> <span style="color:#E58AA5">**Map style tests (28 Oct, 16:40):** all in `sandbox/` (`results/figures/` unchanged). Font is now **Cantarell** (italic parts in DejaVu Sans, since Cantarell has no italic). All map figures now use a fixed layout: equal gaps between maps and rows, each colourbar under its own map. A new sandbox notebook draws one figure of every type the analysis makes, to check them all. The analysis notebooks can't find the 2001–2009 data since it moved to `2001-2009-pre-co2-fix/`.</span>
>
> <span style="color:#008080">**Equilibrium notebooks, regions (27 Oct, 16:59):** the land-only equilibrium notebook and the CO₂-bug six-variables notebook now show three regions: modified cells, all unmodified land, global land. Both reran; conclusions unchanged (land-only runs in equilibrium; in the buggy FUT chain the unmodified land is wetter and warmer in LCC, TSOI +0.30 K).</span>
>
> <span style="color:#AAAAAA">**Runs and reruns (27 Oct, 13:34):** everything is running normally. The three all-species fixed-BVOC runs (14c, 24c, 24d) are in their last 5 years and finish tonight (~23:00–01:00). They still use the old spin-ups, so they are only provisional (for the meeting). The new coupled spin-ups 13b, 23b, 23c are at year 13 of 20 (done ~28 Oct afternoon); 13c (present-day CTRL) is at year 9 (done ~29 Oct evening). The watcher then starts the new 15-year runs CTRL_PD, LCC_PD, CTRL_FUT, LCC_FUT on its own. After those finish, the emission files have to be rebuilt and the fixed-BVOC runs redone by hand (~early November).</span>
>
> <span style="color:#555555">The postprocessing is done (all 90 files). The forcing maps have been rebuilt.</span>
>
> <span style="color:#008080">**Main problem (likely, not proven):** CTRL and LCC started from different land spin-ups. This probably distorts the LCC − CTRL "Total" signal, especially in the future and in the tropics.</span>
>
> <span style="color:#008080">The fBVOC runs can't isolate the BVOC effect of forest expansion. In the future case they use present-day emissions, so the difference also includes the effect of the future climate.</span>
>
> <span style="color:#008080">**D1/D2 are now standalone notebooks** (`D1_farfield_check.ipynb`, `D2_megan_budget.ipynb`); the D1/D2 code was removed from `src`. Both run and give exactly the same numbers as before. Their figures and tables now live next to them, in `diagnostics/other-BVOC-emission-magnitude/D1_farfield/` and `D2_megan_budget/`.</span>
>
> <span style="color:#B8860B">**New, important:** the future 100-year land-only spin-up (LCC branch) ran with **pre-industrial CO₂ (284 ppm)** instead of ~1140 ppm: CLM was set to ignore the CO₂ in the forcing. The vegetation collapsed and has only partly regrown. In the future runs LCC differs from CTRL even far from the forest cells: −16 % leaf area, and wetter, warmer soil. Present day is fine for the short-term variables. Notebooks with figures: `diagnostics/check-CO2-bug-in-land-only/`. **Decision on reruns pending.**</span>
>
> <span style="color:#555555">**New fixed-BVOC setup (session 20966a2c):** the CTRL scripts now also write the emissions of all 19 MEGAN species (for the new all-species fixed-BVOC runs). The existing fBVOC runs are renamed `LCC_PD_fBVOC_PD_IM` / `LCC_FUT_fBVOC_PD_IM` in the code ("IM" = only isoprene and monoterpenes prescribed). **The processed data files still have the old names. The rename commands are ready but not run; the forcing maps won't find the files until they are.** The emission script now covers all 19 species (tested on fake data). CTRL reruns (15 yr) are done. All-species fixed-emission runs (14c, 24c, 24d) passed their 1-day tests and are running (15 years, ~2 days); provisional, on the current set of runs.</span>
>
> <span style="color:#B8860B">**Spin-up reruns (session 0c58bc16):** scripts ready, not run: FUT 22b/22c (CO₂ fixed) → 23b/23c; PD 12b/12c → 13b/13c (optional).</span>
>
> <span style="color:#E58AA5">**Significance test maps (01:22):** `analysis/test_significance_marking.ipynb` compares dots on significant cells with marks on non-significant ones (IPCC AR6 style); figures are now visible inside the notebook. **Chosen and now default:** thin grey hatching on non-significant cells, ocean not faded. The forcing maps now use the fBVOC file names as they are on disk, and `forcing_maps.ipynb` runs fully (figures in `results/figures/`).</span>
>
> <span style="color:#AAAAAA">**Runs (01:38):** CTRL_PD and CTRL_FUT (15 yr), the LCC extensions and three land-only spin-ups are all running. The future 1-day test passed all checks. Its archiving step failed on a filesystem error, but the output is safe. Its archiving has since been redone and succeeded. The present-day test also passed all checks. Archived (compressed) hourly output: about **28 GB per 15-year run** (the earlier 116 GB was the uncompressed file).</span>
>
> <span style="color:#B8860B">**Land-only spin-ups (16:33):** the CO₂ is now right (≈370 ppm PD, ≈1134 ppm FUT), but all three runs **stopped early** on filesystem errors during archiving: PD LCC at year 20, FUT CTRL at 10, FUT LCC at 40 (of 100). The PD CTRL land-only run was never started. **The coupled LCC spin-ups cannot start yet.** Restarted at 16:37; all three are running again (16:38). The stops were caused by temporary filesystem errors.</span>
>
> <span style="color:#AAAAAA">**New problem (16:40):** the future LCC extension crashed on its very last day (31 Dec 2014). The nudging data end at 1 Jan 2015 00:00, and the model needs one more step. Year 2014 must be rerun. The PD LCC extension will hit the same wall in about half an hour, and CTRL_PD/CTRL_FUT at their end. The PD LCC extension did crash the same way. **Fixed (17:40):** the last nudging file now has 3 extra 6-hourly records (copies of 31 Dec); the original is saved in `data/nudging-met-backup/` with a README. Year 2014 of both LCC extensions is rerunning (~3 h each).</span>
>
> <span style="color:#008080">**BVOC emissions notebooks (17:55):** the three overlapping notebooks in `diagnostics/FUT-fBVOC-background-lcc-effect-decomposition/` are now one, `bvoc_emissions_decomposition.ipynb`. The PD-vs-FUT notebook has run: forest expansion slightly **raises** northern BVOC emissions in present day (+0.4 Tg/yr isoprene) but **lowers** them in the future (−2.6 Tg/yr). Most of the future drop is outside the cells whose vegetation changed. **Likely reason (18:22):** leaf area is lower in LCC_FUT than CTRL_FUT almost everywhere north of 45°N (−0.4 m²/m² in summer, also where vegetation did not change). That looks like the leftover of the low-CO₂ land spin-up bug, not the effect of the forests.</span>
>
> <span style="color:#E58AA5">**Vegetation-state maps (18:35):** the CTRL_FUT vs LCC_FUT check notebook now uses the same thin grey hatching on non-significant cells as the forcing maps; rerun, results unchanged.</span>
>
> <span style="color:#E58AA5">**Expansion maps (18:55):** in the PD-vs-FUT notebook the present-day map now has its own colour scale (its changes are ~5× smaller), so its pattern is visible; future and interaction still share one scale.</span>
>
> <span style="color:#AAAAAA">**All runs finished (25 Oct):** the three land-only spin-ups reached year 100 with the right CO₂; the LCC extensions (2014 rerun) and the new 15-year CTRL_PD/CTRL_FUT runs went through to 2015 without errors, so the nudging-file fix worked. **Equilibrium check (14:40):** all three land-only runs are in short-term equilibrium at year 100 (new notebook in `diagnostics/check-simulation-equilibrium/check-land-only-equilibrium-after-co2-fix/`). The coupled spin-up scripts 13b, 23b and 23c now point to them; the copy to NIRD is done (14:45). **Coupled spin-ups 13b, 23b, 23c running since 15:15** (20 years each, ~3 days), each starting from its new land-only state. **PD made symmetric too (15:10):** the PD CTRL land-only run (12c) is running since 15:16 (~13 h); then 13c (~3 days), then CTRL_PD rerun (~2.5 days).</span>
>
> <span style="color:#999999">**Output folders renamed (15:31):** every diagnostics notebook now writes to `<notebook name>_outputs/` next to it (also the older equilibrium and D1/D2 folders). Cached `.nc` files sit in `cache/` subfolders, which git ignores; they are safe to delete and are rebuilt automatically. The CO₂-bug notebooks can run again (mask path fixed). Rule in `CLAUDE.md`.</span>
>
> <span style="color:#008080">**Land-only equilibrium notebook (21:35):** regions are now modified cells, global land and tropics; the only old run shown is FUT_LCC_old. FUT_CTRL was hidden behind FUT_LCC (they are identical outside the modified cells); it is now drawn as a thin line on top. Rerun; verdict unchanged (all three runs in equilibrium).</span>
>
> <span style="color:#008080">**Vegetation-state notebook (14:50):** now shows only three regions: global land, modified cells, all unmodified land. Rerun; conclusions unchanged.</span>
>
> <span style="color:#AAAAAA">**Status 16:20:** running: PD CTRL land-only 12c, coupled spin-ups 13b, 23b, 23c (all since 15:15). **The BVOC-climatology jobs submitted at 16:12 (CTRL_PD and CTRL_FUT, all 19 species) all failed at once:** the compute nodes can't find the Python on NIRD.</span>
>
> <span style="color:#AAAAAA">**Status 21:20:** 12c at year 40 of 100 (done around 03:30). 13b/23b/23c running. **New since 17:11:** all-species fBVOC runs 14c (LCC_PD_fBVOCctrlPD), 24c (LCC_FUT_fBVOCctrlPD), 24d (LCC_FUT_fBVOCctrlFUT) are running; their 1-day tests passed.</span>
>
> <span style="color:#62733B">**BVOC climatologies (22:45):** done; all 76 files are in the shared folder, and the duplicate copies in the work folder have been deleted (29 GB freed). From now on the scripts **move** each finished file to the shared folder. **Processed files:** no rename. When the current fBVOC runs (14c/24c/24d, for the meeting) are postprocessed, the existing 2001–2009 files first move to `postprocessing/2001-2009-pre-co2-fix/`; after the CO₂ fix the 2001–2014 files will go to `2001-2014-pre-co2-fix/`.</span>
>
> <span style="background:#CC0000;color:#FFFFFF;padding:0 4px;border-radius:3px">**WAITING ON YOU**</span> <span style="color:#CC0000">**Waiting on you:** the go for one commit (CLAUDE.md, a comment in `forcing_maps.py`, the two logs, `run_nb_inplace.py`). **Automatic launches (since 22:57):** a watcher on login-3 starts 13c when 12c finishes (~03:30, 26 Oct), and each nudged run (13a, 14a, 23a, 24a) as soon as its coupled spin-up finishes, after copying the spin-up to NIRD and pointing the script at it. If a run stops early, that branch halts and the log says so. Check: `bash cases-scripts/auto_launch_new_chain.sh --check`. The fBVOC runs on the new chain are not automated yet.</span>
>
> <span style="color:#A84300">**New analysis notebooks (00:16):** `analysis/forcing_maps.ipynb` is split into `radiative_forcing.ipynb` (Ghan decomposition: 12 annual + 12 seasonal figures), `bvoc-soa-cloud-interactions.ipynb` and `biogeophysical-hydro.ipynb` (hydrology, snow/albedo, surface energy, sunlight at the surface, water budget). New figures in `results/figures/` (old ones in `first-round/`, reproduced exactly). Runoff and water storage were added to the processed data (new HYDRO files, 2001–2009). Present day north of 45°N: LCC − CTRL warms by **+0.24 W m⁻²**, mostly through the clear-sky term (albedo, +0.37), partly offset by clouds (−0.11). **Update (00:0x):** the LCC−CTRL grids now have a 4th row, CTRL_FUT − CTRL_PD (the climate change alone). The water budget now closes everywhere (< 1 mm/yr) after adding ice runoff from glaciers. **Attribution notebook (00:40):** `analysis/pd-fut-attribution.ipynb` explains the PD/FUT flip. In FUT, almost all of it is clouds: the LCC runs emit far more BVOC than the fixed-emission runs (which get present-day emissions), giving more SOA, more droplets and brighter clouds (−0.7 W m⁻²); the same effect appears with the opposite sign in fixed-BVOC − CTRL (+0.97). So the FUT BVOC contrast mostly measures future vs present-day emissions. In PD, the lower SOA in LCC − fixed-BVOC shows up all year, also in winter, so it comes from the fixed-BVOC setup (probably the missing other MEGAN compounds), not from the forests. **fBVOC − CTRL grids (00:56):** every contrast-grid figure type (and the water budget) now also exists for fixed-BVOC − CTRL. Not committed.</span>
>
> <span style="color:#E58AA5">**Shared colour scales (26 Oct, 10:25):** the six-panel forcing summaries now also come in two versions with shared colourbars: `_shared6` (all six maps on −6…+6 W m⁻²) and `_split6-2` (albedo + total on −6…+6, the four BVOC maps on −2…+2). Section 1b of `radiative_forcing.ipynb`, PD and FUT × NET/SW/LW (12 figures). The old version (own colourbar per map) is unchanged.</span>

One block per working window (a new block starts after more than 1 hour without prompts, or in a new session). Newest first.

---

<div style="color:#999999">

## 2026-11-26 · 14:57 → 15:12 (15 min) · session 5b362f0a

**Goal:** commit all open work by topic; gitignore the local archive folders.

**Done:** commits for vegetation regions, sandbox, archives out of git, new analyses, draft Methods+SI; 2001–2025 / design-B / pre-CO₂-fix archive folders added to `.gitignore`; VS Code backup moved to `/cluster/work` to free space.

**Found:** the home folder was over its quota (20.2 of 20 GiB, and too many files), which blocked every git write.

**Open-next:** commit the 2001–2040 rerun once ~1 GB more is free; push when you say.

**Files changed:** `.gitignore`

</div>

<div style="color:#E58AA5">

## 2026-11-26 · 14:02 → 14:52 (50 min) · session 9576fddd

**Goal:** forcing tree (5 rows): less vertical space, text spread over the tree.

**Done:** layout code changed; one shared colourbar for rows 3–5, section labels placed; test figure drawn (FUT case); 4 paper figures redrawn after your OK; second round: row 2 beside TOTAL, closure note centred, 'other' on two lines, unit label closer, * footnote back; third/fourth round: 'other' grey italic, closure-text rename tried and undone, "(δ not drawn)" removed, * footnote restyled for all figures.

**Open-next:** other map figures get the new footnote style only when their notebooks are rerun. Deck with process chips next to each map (`results/pptx/build_forcing_tree_processes_pptx.py`) being built. Nothing committed.

**Files changed:** `analysis/radiative_forcing_tree_5rows.py`, `sandbox/test_forcing_tree_5rows.py`, `src/boreal_forest_expansion/plotting/forcing_maps.py` (footnote)

</div>

<div style="color:#999999">

## 2026-11-25 · 19:40 → 19:51 (11 min) · session 9261baaa

**Goal:** remove `sandbox/test_vegetation_*.py` scripts that no longer reproduce a saved figure.

**Done:** removed 5 scripts: 4 whose figures are gone (coast_edge, dash_density, line_style_final, red_cells) and `siberia_closed` (its input file is lost). `left_out` now reads `vegetation_map_lines.json`; rerun gives an identical figure and table. Kept 11, all import fine.

**Found:** two line files (`_siberia_closed`, `_before_siberia`) had disappeared after 19:26 (not in git). `siberia_gap_closed.png` stays in the outputs folder without a script.

**Open-next:** commit the removal.

**Files changed:** 5 scripts removed (git rm), `sandbox/test_vegetation_left_out.py` (one path).

</div>

<div style="color:#CC0000">

## 2026-11-25 · 19:42 → 19:44 (2 min) · session a03fb91c
**Goal:** why is the 5-row forcing-tree figure folder empty?
**Done:** checked: the folder was created empty at 19:00; the redraw waits for the cloud-masking notebook (running since 18:28) and starts by itself after it.
**Found:** the waiting job is alive; nothing broken.
**Open-next:** look at the 4 new 5-row figures once they appear.
**Files changed:** none (logs only).

<div style="color:#E58AA5">

## 2026-11-25 · 19:41 → 19:58 (17 min) · session aa1522f0

**Goal:** region names back to broadleaf exp. / needleleaf exp., redraw straight in results/, fix the draft SI.

**Done:** names changed back in the plotting code, region file (cells identical: 266 / 576 / 319), CLAUDE.md and 3 notebook texts; footnote keeps the short definitions. Redrawn: forcing decomposition (13 figures), MEGAN attribution (8). Land-temperature and cloud-masking notebooks stopped and restarted (19:54) so they use the old names. Draft: SI section S1 (text, list, table, captions), one Methods line, SI figure redrawn; compiled, table fits.

**Open-next:** look at the land-temperature and cloud-masking figures when they finish (hours). The 4 old 4-row forcing-tree figures go away when the 5-row tree is drawn.

**Files changed:** forcing_maps.py, megan_maps.py, build_vegetation_regions.py + vegetation_regions.nc, si_region_map.py, si_vegetation_classes.py, CLAUDE.md, 3 notebooks (text), draft supplementary-material.tex, methods-claude.tex, figures/vegetation_regions_by_class.png.

</div>

## 2026-11-25 · 19:37 → 19:40 (3 min) · session aa1522f0

**Goal:** check that all figures say broadleaf exp. / needleleaf exp., not replacement / net tree gain.

**Done:** checked code and figure dates; viewed 3 new figures. Nothing changed.

**Found:** 25 figures + the SI figure made after 17:40 say replacement / net tree gain; older ones say broadleaf/needleleaf exp. The code, the SI text and CLAUDE.md all follow option A.

**Open-next:** you confirm the revert → change names back in the code, SI legend and draft, redraw the 25 figures + SI figure.

**Files changed:** logs only.

</div>

<div style="color:#999999">

## 2026-11-25 · 19:25 → 20:08 (43 min) · session eab501a1

**Goal:** clean the sandbox; move the vegetation-region scripts to diagnostics.

**Done:** deleted `vegetation_map_lines_before_estonia_trim.json` and `region_cells_outputs/region_monoterpene.csv` (neither used by any script). Moved `region_cells_outputs/` + 4 scripts to `diagnostics/lcc-modified-cells/`, fixed their paths, reran all 4 (OK). Merged the sandbox helpers they need into one `vegetation_helpers.py` there; figures pixel-identical. Folded `si_region_map.py` into `si_vegetation_classes.py` (your OK), deleted it; SI figure identical, it prints the SI table numbers.

**Found:** `vegetation_map_lines.json` and `_siberia_closed.json` are identical to the live file in `diagnostics/lcc-modified-cells/`; both are still read by sandbox scripts, as is `_before_siberia.json`.

**Open-next:** commit. The sandbox helper originals stay (10 other sandbox tests use them).

**Files changed:** 2 sandbox files deleted; 4 scripts + 1 folder moved to `diagnostics/lcc-modified-cells/` (paths edited); new `vegetation_helpers.py`; `si_region_map.py` deleted.

</div>

<div style="color:#A84300">

## 2026-11-25 · 18:02 → 18:33 (31 min) · session b631a2eb

**Goal:** explain the APRP method; turn it into a function; show how each mapped term is calculated under the figure titles.

**Done:**
- Explained APRP and its variables (in chat).
- New function `aprp()` (+ `aprp_parameters()`) in `src/.../analysis/aprp.py`; checked on LCC_PD − CTRL_PD 2001–2002: identical to the notebook (difference 0).
- Sandbox test figures with formulas under the panel titles, written with the model output variables (your correction 18:28): masking, APRP split, cloud variables ([LCC − CTRL]_PD).

**Found:** nothing new about the science.

**Open-next:**
- Your OK on the formula design → add it to `analysis/cloud-masking-aprp.ipynb` after its 2001–2040 run ends (ask before rerun).

**Files changed:** `src/boreal_forest_expansion/analysis/aprp.py` (new), `src/boreal_forest_expansion/analysis/__init__.py`, `sandbox/test_aprp_module.py`, `sandbox/test_aprp_formula_titles.py` (+ outputs).

</div>

<div style="color:#A84300">

## 2026-11-25 · 17:39 → 19:29 (110 min) · session 47db7f49

**Goal:** settle the names of the two vegetation regions (broadleaf vs needleleaf expansion).

**Done:**
- Region names decided: option A, "replacement" / "net tree gain" (open since 2026-11-24, 17:33).
- Test maps redrawn in the sandbox (7 kinds), new labels and footnote fit.
- One-row context grid for [LCC − CTRL]_FUT only (isoprene … evapotranspiration): `sandbox/vegetation_regions/src_maps_outputs/contrast_grid_context_context_LCC-CTRL_FUT_2001_2025.png`.
- Dominant-PFT map (CTRL, LCC, change): `sandbox/vegetation_regions/src_maps_outputs/dominant_pft_change.png`.
- Copy of the vegetation-classes figure with the two lines: `sandbox/test_vegetation_outlines_outputs/vegetation_classes_with_lines.png` (original unchanged); kept as reference.
- New SI figure (tree-cover change of broadleaf and needleleaf + the region map): `sandbox/vegetation_regions/region_cells_outputs/si_vegetation_classes.png`, now in the draft.
- SI legend reframed around needleleaf, in the order teal / light teal / orange: "Needleleaf expansion (net tree gain)", "No needleleaf loss, but broadleaf gains (net tree gain)", "Needleleaf decrease, replaced by broadleaf (replacement)", "Little tree gain (≤ 1 pp, left out from regional means)". Both SI figures redrawn.
- Draft S1: the 3-panel figure replaces the single map; class list and table rewritten in the same order and wording; compiled and checked.
- Renamed everywhere: map labels, subtitle, line legend and footnote; the region file (rebuilt, same 266 / 576 / 319 cells); the SI section S1, its table and figure; one sentence in the methods draft; text in 3 notebooks.

**Found:** the methods sentence speaks of an "increase" in the net-tree-gain cells, but PD isoprene there changes by −0.53 (log 25 Nov, 16:06). Worth a look. The dominant plant type changes in only 188 of 1161 modified cells (17 % of their area), mostly arctic grass → needleleaf trees or shrubs; broadleaf becomes dominant in just 7 cells, so in the replacement region broadleaf is added as a minority type. Raising the 1 pp threshold does not remove the light-teal cells (broadleaf gain median +6 pp): it moves replacement cells into them (47 → 63 cells at 3–5 pp).

**Open-next:** the Δ formula in S1 runs past the right margin (was already so); rerun the analysis notebooks so `results/figures` get the new names (ask first).

**Files changed:** `src/.../plotting/forcing_maps.py`, `megan_maps.py`, `diagnostics/lcc-modified-cells/build_vegetation_regions.py` + `vegetation_regions.nc`, `sandbox/vegetation_regions/si_region_map.py`, `region_cells.py`, draft `supplementary-material.tex`, `methods-claude.tex`, `figures/vegetation_regions_by_class.png`, 3 `analysis/` notebooks (text only), `CLAUDE.md`

</div>

<div style="color:#E58AA5">

## 2026-11-25 · 18:26 → 19:00 (34 min) · session cdb1451a

**Goal:** get the 5th-row test figure drawn, then put it in the paper figures.

**Done:** test figure drawn and checked (`sandbox/test_forcing_tree_5rows_outputs/`). Non-BVOC (≥45°N): −0.065 = +0.16 real − 0.23 masking; BVOC −0.020 ≈ real cloud change. Scale kept shared (you). Renamed 4rows → 5rows (script, results folders, tables, cache, README, watcher script). Automatic redraw of the 2001–2040 figures set up.

**Found:** first test job was killed with the old session. The 2001–2040 rerun had stopped at 16:04 but another session restarted it at 18:28; its 4-row tree ran at 18:33 without row 5 (cloud-masking caches not ready yet).

**Open-next:** look at the four 2001–2040 five-row figures when the redraw is done (log `/cluster/work/users/adelez/analysis-2001-2040/tree5/run.log`).

**Files changed:** `analysis/radiative_forcing_tree_5rows.py` (was `_4rows`), `analysis/README.md`, `cases-scripts/run_when_done/analysis_2001-2040_when_done.sh`, `sandbox/test_forcing_tree_5rows.py`, `results/tables/radiative-forcing-tree-5rows/`

</div>

<div style="color:#E58AA5">

## 2026-11-25 · 17:00 → 17:20 (20 min) · session cdb1451a

**Goal:** add a 5th row to the 4-row forcing tree: cloud SW = real cloud change + masking.

**Done:** code added to `analysis/radiative_forcing_tree_4rows.py`; sandbox test script `sandbox/test_forcing_tree_5rows.py`.

**Open-next:** look at the test figure; redraw the paper figures (2001–2040) once the cloud-masking notebook run has finished (ask first).

**Files changed:** `analysis/radiative_forcing_tree_4rows.py`, `sandbox/test_forcing_tree_5rows.py`

</div>

<div style="color:#A84300">

## 2026-11-25 · 15:10 → 15:10 (0 min) · session ba876485

**Goal:** check whether cloud vertical profiles exist for the non-artefact contrasts.

**Found:** yes, for interactive, fBVOC and non-BVOC (annual + JJA, 2001–2040) in `results/figures/bvoc-soa-cloud-interactions/`.

**Files changed:** none.

</div>

<div style="color:#A84300">

## 2026-11-25 · 20:24 → 20:30 · session 499a01f9

**Goal:** finish the 2001–2040 reruns and put the land-temperature numbers in the draft.

**Done:** land-temperature notebook done; draft M5b filled with its numbers. Cloud-masking rerun relaunched with the missing cloud fields; 5-row tree redraw chained to it. Land-temperature figure flaws (doubled "K K", overlapping bar labels) fixed in the notebook code and tested in the sandbox.

**Found:** over the modified cells the forest warms land air 0.11 K (FUT) vs 7.4 K for climate = 1.5 % (spring 3.4 %, winter 0.4 %); warming comes from the needleleaf-expansion cells, broadleaf cells ~0 and cooler in winter; no warming outside the modified cells. Cloud masking failed 4× because my staged copy had only total cloud.

**Open-next:** OK to redraw the land-temperature figures; cloud-masking numbers into the draft; delete the staging copy afterwards.

**Files changed:** `analysis/climate-vs-lcc-land-temperature.ipynb` (cells 5–6), `sandbox/test_land_temp_ratio.py`, draft `methods-claude.tex`.

</div>

<div style="color:#A84300">

## 2026-11-25 · 15:01 → 19:04 (~4 h) · session 499a01f9

**Goal:** rerun the 3 missing items for 2001–2040; only 2001–2040 in `results/figures/`; add them to the automatic chain; MEGAN maps with leaf area in row 1; update the draft (numbers, MEGAN grouping, forest-vs-climate note); land temperature comparison.

**Done:** 334 figures for 2001–2025 deleted from `results/figures/`. `results/tables/forcing-tree*` → `radiative-forcing-tree*`. Automatic chain: + 3 items + the new land-temperature notebook, 3 tries each. Draft `methods-claude.tex`: 2001–2040 numbers, significance shares, MEGAN grouping + safeguard notes, new section M5b. MEGAN sandbox figures with leaf area in row 1. Fixed: vegetation-region numbers missing on cropped maps (MEGAN).

**Found:** correction: forest vs climate differ at TOA because of longwave (climate −7 W m⁻², forest −0.1), not cloud masking (clouds hide ~half of the surface darkening in both). MEGAN soil-moisture factor is always 1 in CLM. 2001–2040 numbers move ≤ 0.01 W m⁻², intervals 15–30 % narrower; significant cells up for every forest contrast. MEGAN safeguard = CLM sets emission to 0 when γ < 0, caused by a negative isoprene leaf-age factor in fast spring leaf-out; ≤ +0.03 isoprene, 0 monoterpenes. PD isoprene: broadleaf cells gain through leaf area, needleleaf cells through temperature. NIRD unstable all afternoon.

**Open-next:** the 3 reruns and the land-temperature notebook (running); land-temperature number box in the draft; rerun the MEGAN notebook (your OK) and choose its layout; check the citations in M5b; equilibrium and autocorrelation still on 25 years; you review `diagnostics/background-aerosol/`; `results/tables/` still has both periods.

**Files changed:** `src/.../plotting/forcing_maps.py`, `analysis/radiative_forcing_tree{,_4rows}.py`, `radiative-forcing-decomposition.ipynb`, `cloud-masking-aprp.ipynb`, `climate-vs-lcc-land-temperature.ipynb` (new), `analysis/README.md`, `cases-scripts/run_when_done/analysis_2001-2040_when_done.sh`, `sandbox/test_megan_lmdi_lai_row1.py`, `sandbox/significance_2025_vs_2040/`, draft `methods-claude.tex`; `results/figures/` (deletions), `results/tables/` (rename).

</div>

<div style="color:#AAAAAA">

## 2026-11-25 · 14:58 → 14:58 (0 min) · session 499a01f9

**Goal:** status of analysis and runs. All runs done; 2001–2040 analysis finished without errors at 00:08. Read-only.

</div>

<div style="color:#A84300">

## 2026-11-24 · 17:23 → 17:33 (10 min) · session dbee06ab

**Goal:** move the forcing-tree scripts from the sandbox to `analysis/`, outputs in `results/`.

**Done:** scripts moved and renamed (`forcing_tree.py`, `forcing_tree_4rows.py`); 16 figures and 4 tables written to `results/{figures,tables}/forcing-tree{,-4rows}/`; tables identical to the sandbox ones; README row added.

**Open-next:** delete the old copies `analysis/test_forcing_tree*_outputs/`; commit.

**Files changed:** `analysis/forcing_tree.py`, `analysis/forcing_tree_4rows.py` (moved), `analysis/README.md`, `results/figures/forcing-tree*/`, `results/tables/forcing-tree*/`.

</div>

<div style="color:#CC0000">

## 2026-11-24 · 17:13 → 17:33 (20 min) · session 4e079785

**Goal:** understand the light-teal class in `si_region_classes.png` and why it counts as needleleaf region.

**Done:** explained it from the code: the regions split "broadleaf replaces needleleaf" from "any other tree gain", so broadleaf gain without replacement lands in the second group.

**Found:** light-teal cells (47): broadleaf +6.2 pp, needleleaf +1.7 pp (medians); needleleaf also grows > 1 pp in 55 % of them.

**Open-next:** **WAITING ON YOU:** choose legend/region names A, B or C (A recommended; see box above). Then apply to `si_region_map.py`, the SI text, and the map subtitles/labels in `forcing_maps` and `megan_maps`.

**Files changed:** none (logs only).

</div>

<div style="color:#999999">

## 2026-11-24 · 17:09 → 17:12 (3 min) · session 40b2b6a1

**Goal:** commit the open work by topic.

**Done:** 7 commits in the project repo, 1 in the draft repo, not pushed. Includes MEGAN, background aerosol and Tang/LPJ-GUESS (left out on 21 Nov, open since 2026-11-21).

**Open-next:** push when you want; the vegetation-regions session may still change its files after this snapshot.

**Files changed:** only the two logs.

</div>

<div style="color:#E58AA5">

## 2026-11-24 · 16:40 → 17:42 (62 min) · session 4cd451a7

**Goal:** Try a 4-row forcing tree: Ghan terms of both branches, then SW/LW of each, no physical labels.

**Done:** new script and folder `sandbox/test_forcing_tree_4rows*`; 4 figures (one per case). Checked: Ghan terms add up to each branch, SW + LW = NET (errors < 1e-5 W m⁻²). Rows 3–4 of each branch share one colour scale.

**Found:** `LCC_FUT − CTRL_PD`, ≥45°N: non-BVOC clean-clear-sky +3.96 = SW +10.12, LW −6.16; BVOC cloud −1.10, almost all SW (−1.12).

**Also:** row-4 titles now say NON-BVOC / BVOC; explained which processes each SW/LW Ghan map contains.

**Cloud masking (APRP), done:** new notebook `analysis/cloud-masking-aprp.ipynb` (figures and tables in `results/*/cloud-masking-aprp/`). The negative SW cloud term of the land-cover (non-BVOC) part is masking: clouds hide part of the darker surface. The clouds themselves reflect slightly less (present day ≥45°N: cloud term −0.07 = real cloud change +0.16 + masking −0.23 W m⁻²). For BVOC there is no masking: the cloud term is a real brightening of clouds.

**Open / next:** choose layout 3-row or 4-row; read the APRP findings (§5 of the notebook).

**Files changed:** `sandbox/test_forcing_tree_4rows.py` (new), `analysis/cloud-masking-aprp.ipynb` (new), `analysis/README.md`, `results/{figures,tables}/cloud-masking-aprp/` (new), `sandbox/test_forcing_tree_4rows_outputs/` (4 PNG + 2 CSV), cache `/cluster/work/users/adelez/boreal-caches/forcing-tree-4rows/`

</div>

---

<div style="color:#E58AA5">

## 2026-11-24 · 16:13 → 16:31 (18 min) · session 4cd451a7

**Goal:** Forcing decomposition tree: colourbars on rows 1–2, usual albedo name, add LW.

**Done:** each map of rows 1–2 (total, non-BVOC, BVOC) has its own colourbar; albedo panel = "ALBEDO / SW CLEAR-SKY FORCING"; LW figures drawn without the albedo/rest split. 12 figures redrawn (sandbox only).

**Found:** LW, ≥45°N: same-climate cases are small (total ±0.4 W m⁻² scale); with climate change total ≈ −6.8 W m⁻² (`LCC_FUT − CTRL_PD`), BVOC +0.21, mostly the chemistry/residual term (+0.19).

**Open / next:** your OK on the design, then move it to `analysis/`.

**Files changed:** `sandbox/test_forcing_tree.py`, `sandbox/test_forcing_tree_outputs/*` (12 PNG + 2 CSV), cache `/cluster/work/users/adelez/boreal-caches/forcing-tree/`

</div>

---

<div style="color:#555555">

## 2026-11-24 · 16:15 → 16:30 (15 min) · session ee15eedf

**Goal:** Check the runs and get the last one postprocessed.

**Found:** all 12 nudged runs are finished and copied to NIRD. Postprocessing of `LCC_PD_fBVOClccPD` failed twice overnight on NIRD read/write errors, so the 2001–2040 analysis had not started (open since 23 Nov).

**Done:** removed the 19 broken partial files and restarted postprocessing with fewer parallel jobs. It starts the 2001–2040 analysis by itself when it succeeds.

**Open / next:** check that postprocessing reaches 19/19 and the analysis starts.

**Files changed:** `/cluster/work/users/adelez/met-nudg-2040/recover2_LCC_PD_fBVOClccPD.sh` (new), `docs/CLAUDE_log.md`, `docs/CLAUDE_log_human.md`

</div>

---

<div style="color:#A84300">

## 2026-11-24 · 16:03 → 17:47 (104 min) · session 560cc914

**Goal:** finish the vegetation-region numbers (broadleaf vs needleleaf expansion) and choose how to show them on the maps.

**Done:**
- Answered: "little tree gain" = largest tree gain (broadleaf or needleleaf) ≤ 1 percentage point of the cell. 319 cells, 19 % of the modified area, median gain 0.
- New sandbox test `sandbox/vegetation_regions/test_region_numbers.py`: regional means added to the real Ghan figure and context grid in 3 layouts, all checked by eye.
- Two extra lines under each map: clean in both figures. One line: values run into each other. Side block: runs into the next map and makes the figure very wide.
- You chose: regions by cell class (lines only for display), two-line layout, subtitle A with an asterisk and a footnote at the bottom. Both test figures redrawn with it and checked.
- Applied to all result maps (you, 17:12): region file + lines file in `diagnostics/lcc-modified-cells/`, shared plotting code (`forcing_maps.py`, `megan_maps.py`) and the two MEGAN LMDI notebooks. Checked on 7 kinds of figure drawn directly from the new code; colourbars moved a little lower so their ×10ⁿ label does not touch the numbers.
- 12 notebooks with maps rerunning in the background (started 17:29, `/cluster/work/users/adelez/veg-regions-rerun/run.log`).
- Draft: Supplementary numbering S1, S2, Table S1, Fig. S1 (compiled).
- Fixed (you, 17:35): white lines on the dark MEGAN maps; gamma-map colourbars closer to the maps; **snow persistence** (open since 2026-10-28) now = snow-season length (longest continuous snow cover in the year, ≤ 365 d). The old value (−18,900 days) came from CLM's counter, which never resets under permanent snow. Now LCC_FUT − CTRL_PD ≈ −47 days of snow season over 45–90°N; LCC − CTRL ≈ −0.5 to −0.8 days.
- Draft: new Supplementary section "Vegetation regions used for the regional means" (definitions, class table, how the means are computed, lines are display only) + region figure; compiles. Not committed.

**Found:** Ghan NET [LCC − CTRL]_FUT: broadleaf exp. −0.58 ± 0.05, needleleaf exp. +1.31 ± 0.04 W m⁻², against +0.22 over 45–90°N. Cloud term reverses sign between the two regions (+1.03 vs −0.76).

**Open-next:** check the reruns when they finish. The "needleleaf exp." region also contains 47 cells where broadleaf gains without replacing needleleaf (5 % of the area).

**Files changed:** `src/.../plotting/forcing_maps.py`, `megan_maps.py`; `diagnostics/lcc-modified-cells/build_vegetation_regions.py`, `vegetation_regions.nc`, `vegetation_map_lines.json` (new); `analysis/megan-lmdi-attribution-maps.ipynb`, `megan-lmdi-vs-approx.ipynb`; `CLAUDE.md`; `docs/PLOTTED_VARIABLES.md`; sandbox test scripts + outputs; draft `supplementary-material.tex`, `main.tex`, `figures/vegetation_regions_by_class.png`. Results figures being regenerated.

</div>

<div style="color:#E58AA5">

## 2026-11-23 · 21:32 → 21:50 (18 min) · session 9f4eadd9

**Goal:** draw the three-row forcing decomposition for all existing cases.

**Done:** 8 figures (4 cases, NET and SW) in the sandbox, with δ quantified on each. Mapping and albedo choice confirmed (open since 21:10 today).

**Found:** δ is at most 0.021 W m⁻² in NET at ≥45°N and within its uncertainty in every case. When climate is included, albedo (about +10) and rest (about −8) largely cancel in NET.

**Open-next:** user decides if the design is final, and whether LW is needed. `results/figures` not touched.

**Files changed:** `sandbox/test_forcing_tree.py`, `sandbox/test_forcing_tree_outputs/`, these logs.

</div>

<div style="color:#E58AA5">

## 2026-11-23 · 21:45 → 21:55 (10 min) · session 0fee2434

**Goal:** separate colour scale per row on the MEGAN attribution maps; explain the CLM safeguard; judge whether more years are needed.

**Done:** 8 sandbox figures with one colour scale per row (row 2 at ±10).

**Found:** the CLM safeguard sets the emission to zero when the total activity factor is outside 0 to 100. Its effect is tiny (+0.03 for PD isoprene in JJA). LAI drives the activity change (+3.3 of +4.0). Temperature, light and leaf age are small, and more years would narrow their uncertainty without making them larger.

**Open-next:** user chooses the LAI scale, then the notebook can be updated.

**Files changed:** `sandbox/test_megan_lmdi_row_scales.py` (new).

</div>

<div style="color:#555555">

## 2026-11-23 · 21:33 → 21:52 (19 min) · session bb091224
**Goal:** Fix the stalled watcher and restart the 2001–2040 chain.

**Done:**
- Watcher stall fixed and watcher restarted (open since 23 Nov, 21:23). A dry run first confirmed it would act only on `LCC_PD_fBVOClccPD`.

- Automatic retry of the NIRD copy started, followed by postprocessing of that run.

**Found:** The first copy of that run failed on NIRD input/output errors. One sea-ice file and two restart files were missing on NIRD afterwards; the originals are safe in the work archive.

**Open / next:** Check the retry result. Then the 2001–2040 analysis starts by itself.

**Files changed:** `cases-scripts/run_when_done/met_nudg_2026-2040_when_done.sh`, `docs/CLAUDE_log.md`, `docs/CLAUDE_log_human.md`

---

</div>

<div style="color:#CC0000">

## 2026-11-23 · 21:20 → 21:23 (3 min) · session bb091224
**Goal:** Check how the runs are going.

**Found:**
- All 12 nudged runs reached 2041 and are archived. The queue is empty.
- The automatic watcher stalled on 22 Nov: it read the empty queue as a queue error and kept waiting for the last run.
- Because of this, `LCC_PD_fBVOClccPD` has no NIRD copy past 2014 and no postprocessing (209 of 228 files), and the 2001–2040 analysis has not started.

**Open / next:** OK to fix the watcher and restart it.

**Files changed:** `docs/CLAUDE_log.md`, `docs/CLAUDE_log_human.md`

---

</div>

<div style="color:#CC0000">

## 2026-11-23 · 21:05 → 21:10 (5 min) · session 9f4eadd9

**Goal:** plan a three-row radiative forcing decomposition figure and confirm it before drawing.

**Done:** proposed the panels and the simulations behind each one. Checked that the non-BVOC runs have the fields needed.

**Found:** total = non-BVOC + BVOC + a small artefact term (≥45°N NET: PD −0.002, FUT +0.014 W m⁻²).

**Open-next:** user confirms the mapping, the albedo definition, and PD + FUT. Then draw in the sandbox only.

**Files changed:** these logs.

</div>

<div style="color:#CC0000">

## 2026-11-22 · 17:10 → 17:14 (4 min) · session 8f7da9d1

**Goal:** record the new paper story and discuss it.

**Done:** story recorded in memory and logs.

**Found:** in the changed cells, forest expansion is 18 % of the climate signal in net TOA radiation and 7 % in the albedo term. Climate change reduces the albedo effect of the forest by 23 %. BVOC effects are small (−0.04 PD, −0.07 W/m² FUT).

**Open-next:** choose the framing. Fixed ocean and nudged winds favour climate in this comparison, so the wording must account for that.

**Files changed:** `docs/CLAUDE_log.md`, `docs/CLAUDE_log_human.md`.

</div>

<div style="color:#E58AA5">

## 2026-11-23 · 21:02 → 21:58 (56 min) · session c88bbb02

**Goal:** finish the line edits and subtitle, then test region maps and regional numbers.

**Done:** removed the coastal piece, added your subtitle and a little more title space. Created `sandbox/vegetation_regions/` with a region map and a monoterpene table.

**Found:** the whole-area monoterpene mean hides two opposite signals: in FUT, −1.49 Tg/yr in the broadleaf region and +1.35 Tg/yr in the other tree-gain region. Adding the 319 little-gain cells to a region lowers its mean, but barely changes its total.

**Open-next:** choose the region definition and number layout, then decide on applying to paper figures. Snow persistence still to check. Coastline white-edge test not reviewed.

**Files changed:** `sandbox/vegetation_regions/region_cells.py` and its outputs, `sandbox/test_vegetation_siberia_closed.py`, `sandbox/test_vegetation_real_figures.py`, `sandbox/test_vegetation_outlines_outputs/vegetation_map_lines.json` (backup `vegetation_map_lines_before_estonia_trim.json`), test figures.

</div>

<div style="color:#E58AA5">

## 2026-11-22 · 16:30 → 17:27 (57 min) · session c88bbb02

**Goal:** finish the two map lines: land-only modified line, smoother Siberia closure, west Alaska, Estonia and Sweden.

**Done:** all line edits saved as the fixed file, with a backup. The four real test figures are redrawn with it and checked.

**Found:** dashed border 17,620 km. Modified-cell line on land: 17,088 km drawn, 5,751 km removed. A 140 km opening stays in west Alaska.

**Open-next:** apply to paper figures, subtitle or caption, snow persistence. Coastline white-edge test not reviewed.

**Files changed:** `sandbox/test_vegetation_left_out.py`, `sandbox/test_vegetation_siberia_closed.py`, `sandbox/test_vegetation_outlines_outputs/vegetation_map_lines.json` (backup `vegetation_map_lines_before_siberia.json`), test figures.

</div>

<div style="color:#E58AA5">

## 2026-11-22 · 15:00 → 15:21 (21 min) · session c88bbb02

**Goal:** see whether the open dashed line in Russia can be closed.

**Done:** closed the central Siberia gap along your sketched route (710 km, 499 km of it new). Updated the left-out figure and table.

**Found:** the final line is 17,543 km and leaves out 1,689 km of small pieces. The Far East gap has no vegetation border to follow, and Kola stays open as you asked.

**Open-next:** keep the route or not. Coastline white-edge test was stopped and not reviewed. Earlier open items stay: apply to paper figures, subtitle or caption, snow persistence.

**Files changed:** `sandbox/test_vegetation_russia_gap.py`, `sandbox/test_vegetation_siberia_closed.py`, `sandbox/test_vegetation_left_out.py`, `sandbox/test_vegetation_coast_edge.py`, test outputs in `sandbox/test_vegetation_outlines_outputs/`.

</div>

<div style="color:#E58AA5">

## 2026-11-22 · 01:39 → 01:49 (10 min) · session c88bbb02

**Goal:** test the final vegetation lines on the real figures, in the sandbox.

**Done:** all four test figures drawn with both lines and checked. Test-script bug fixed.

**Found:** nothing was written to `results/`. The snow persistence panel shows about −18,900 days for FUT − PD, which cannot be a yearly length (already there before the lines, cause not checked).

**Open-next:** user decides on applying to paper figures and on subtitle or caption. Check snow persistence.

**Files changed:** `sandbox/test_vegetation_real_figures.py`, `sandbox/test_vegetation_outlines_outputs/real_figures/`.

</div>

<div style="color:#CC0000">

## 2026-11-21 · 23:07 → 00:18 (71 min) · session c88bbb02

**Goal:** finish the candidate lines for the result maps and test their style on other variables.

**Done:** mostly-land modified-cell line chosen (open since 16:47 block). West Alaska border parts restored and Kola link removed. Modified-cell line removed inside the 2 marked boxes. Black lines with a 30 % transparent white edge chosen and drawn on forcing, 2 m temperature, spring albedo, leaf area, SOA burden and liquid water path, for PD and FUT.

**Found:** the white edge keeps the black lines readable on the dark cells.

**Open-next:** check the real-figure test (running), then decide on applying the lines to the paper figures.

**Files changed:** `sandbox/test_vegetation_final_lines.py`, `sandbox/test_vegetation_line_colours.py`, `sandbox/test_vegetation_line_halo.py`, `sandbox/test_vegetation_line_style_final.py`, `sandbox/test_vegetation_outlines_outputs/`.

</div>

<div style="color:#008080">

## 2026-11-21 · 16:39 → 17:17 (38 min) · session 36563bcd

**Goal:** keep two background-aerosol notebooks (PD vs FUT, LCC vs CTRL) with the same merged analysis.

**Done:** both rebuilt and run with outputs. Numbers shared with the earlier versions are unchanged. Earlier versions are saved in each `_outputs/previous-version-20261121/`.

**Found:** over the future forest area, FUT has about 3 times more SOA than PD (+210 %) and 45 % less sulfate. The forest expansion itself does not significantly change SOA, sulfate or AOD there in FUT.

**Open-next:** keep or delete the extra combined notebook `background_aerosol_lcc_ctrl_pd_fut_online.ipynb`. Nothing is committed.

**Files changed:** `diagnostics/background-aerosol/background_aerosol_pd_fut_online.ipynb`, `background_aerosol_lcc_ctrl_fut_online.ipynb`, their outputs, `diagnostics/README.md`.

</div>

<div style="color:#CC0000">

## 2026-11-21 · 16:47 → 18:11 (84 min) · session c88bbb02

**Goal:** mark the modified cells and the border between broadleaf and needleleaf regions on the result maps, in a simple style.

**Done:** chose a dashed border, width 0.7, with the yellow cells in the needleleaf area. Mapped everything the line leaves out. Tested a modified-cell line drawn only against unmodified land. Checked the red cells outside the needleleaf area.

**Found:** the border leaves out about 4,700 of 18,700 km: 3 small Alaska/Yukon loops, the pieces in the marked boxes and 7 short fragments. Keeping the modified line only against mostly-land cells cuts it from about 74,000 to 23,000 km and removes the coast tracing.

**Open-next:** confirm the modified-line version and the left-out parts, then save one fixed border and test on other figures.

**Files changed:** `sandbox/test_vegetation_*.py`, `sandbox/test_vegetation_outlines_outputs/`.

</div>

<div style="color:#CC0000">

## 2026-11-21 · 16:29 → 16:42 (13 min) · session c88bbb02

**Goal:** mark on the result maps where broadleaf trees gain or replace needleleaf trees, and where needleleaf trees advance.

**Done:** sandbox test with a class map and 3 outline styles on the PD total forcing map.

**Found:** of the modified land area, broadleaf replaces needleleaf in 30 %, broadleaf gains most in 5 %, needleleaf gains most in 46 %, and 19 % has almost no tree gain.

**Open-next:** choose the style and confirm the rule, then test on the other figure types.

**Files changed:** `sandbox/test_vegetation_outlines.py`, `sandbox/test_vegetation_outlines_outputs/`.

</div>

<div style="color:#008080">

## 2026-11-21 · 16:23 → 16:27 (4 min) · session 36563bcd

**Goal:** same online background-aerosol analysis for LCC − CTRL in both PD and FUT climates.

**Done:** notebook written, run started.

**Open-next:** check the numbers, write the summary.

**Files changed:** `diagnostics/background-aerosol/background_aerosol_lcc_ctrl_pd_fut_online.ipynb` (new).

</div>

<div style="color:#A84300">

## 2026-11-21 · 16:24 → 16:26 (2 min) · session fff170e9

**Goal:** check whether row 2 of Fig. 1c wrongly repeats row 1.

**Done:** checked the contrast definitions and recomputed both rows from the processed files for isoprene, monoterpene and the two SOA burdens (2001–2025, 45–90°N).

**Found:** not a bug. The maps differ, but are very similar (pattern correlation 0.989–0.999). The difference is 14 % of the climate signal for isoprene, 12 % for monoterpene, and 1.5–3.6 % for SOA burdens.

**Open-next:** decide whether Fig. 1c should keep both rows or show the difference more prominently.

**Files changed:** logs only.

</div>

<div style="color:#A84300">

## 2026-11-21 · 16:02 → 16:21 (19 min) · session 6f761ff3

**Goal:** commit the work by topic; remove the 16 Nov pre-reorganisation figures and tables.

**Done:**
- Project repo, 6 commits: results layout and artefacts, MET 2026–2040, BVOC plots, isoprene diurnal cycle, equilibrium and autocorrelation, diagnostics index + runner + logs.
- Draft repo, 1 commit: Methods values, setup figure, LaTeX fixes. Nothing pushed.
- Deleted `results/figures-pre-reorg-20261116/` (331 files) and `results/tables-pre-reorg-20261116/` (17 files).

**Found:** all 348 deleted files were in git history and no code used them.

**Open-next:** commit MEGAN (after the maps notebook ends), background aerosol and Tang/LPJ-GUESS when you want; push.

**Files changed:** `.gitignore`, `CLAUDE.md`, `results/README.md`, both logs.

</div>

<div style="color:#AAAAAA">

## 2026-11-21 · 15:55 → 17:42 (107 min) · session d2e64b8d

**Goal:** resubmit the crashed run and rerun the maps notebook.

**Done:** `LCC_PD_fBVOClccPD` resubmitted from its intact 2036 restart (crash open since 21 Nov 15:55 block). Maps notebook rerun OK on attempt 6 (failed since 20 Nov). Last Methods number (LMDI FUT, open since 2 Nov) filled.

**Found:** restart files, met list and settings all checked OK before submitting. The run passed start-up. The maps notebook failed 3 times on NIRD import errors, so it is rerunning with a stability check. The watcher is alive: 3 runs picked up by 17:15.

**Open-next:** `main.tex` tables, `methods.tex` cleanup, corrected deck, commits.

**Files changed:** `methods-claude.tex`, maps notebook + its figures and tables, `docs/met-nudg-2026-2040.md`, logs; failure flag moved to `met-nudg-2040/retry-20261121/`.

</div>

## 2026-11-21 · 15:52 → 15:55 (3 min) · session d2e64b8d
- **Goal:** status and to-do list.
- **Found:** 11/12 nudged runs on track; PD `lcc_fBVOClccPD` crashed at start-up (surface file intact, likely bad read). MEGAN LMDI maps notebook still failed.
- **Open-next:** your OK to resubmit the run; rerun the maps notebook and fill the last Methods number.
- **Files changed:** logs only.

## 2026-11-20 · 16:45 → 16:50 (5 min) · session 4607124c

**Goal:** tidy the design A six-map forcing figures and update the slide deck.

**Done**
- Deleted the 6 out-of-date `_split6-2` figures (asked on 19 Nov).
- Dropped the duplicate case `LCCFUT-CTRLPD_fBVOCctrlPD` (identical to `LCCFUT_fBVOCctrlPD`) from the notebook and deck script; its 6 figures deleted (asked on 19 Nov).
- Deleted the 12 one-colourbar-per-map figures; the notebook now draws only the shared-scale version.
- Rebuilt `results/pptx/BOREAL_figures_2001-2025_CICERO.pptx`: 307 slides, 297 figures; section 5.2 has the 12 shared-scale figures.

**Open-next**
- Notebook code changed but not rerun (its saved outputs are still from before).
- Commit when you want.

**Files changed:** `analysis/radiative-forcing-decomposition.ipynb`, `results/pptx/build_figures_pptx.py`, `results/pptx/BOREAL_figures_2001-2025_CICERO.pptx`, figures folder above.

</div>

<div style="color:#A84300">

## 2026-11-19 · 16:28 → 16:51 (23 min) · session 21b50ffc

**Goal:** in the design A six-map figures for FUT with PD emissions, show LCC_FUT − LCC_PD (lccPD) and LCC_FUT − CTRL_PD (ctrlPD) in maps 1–2.

**Done:** `analysis/radiative-forcing-decomposition.ipynb` cases changed; colour scale ±40/±15/±2 (`split40-15-2`); deck builder entries updated (deck not rebuilt). 12 figures redrawn (script with retries, inputs copied to /cluster/work because of NIRD read errors). Notebook rerun failed on NIRD (HDF read errors, broken imports), so its figure cell shows an error.

**Found:** LCC_FUT − LCC_PD, ≥45°N, 98th percentile: albedo 38, total NET 12, SW 20, LW 12 W m⁻². Means ≥45°N NET: total +1.07 (vs LCC_PD) / +1.33 (vs CTRL_PD), albedo +9.7 / +10.2 W m⁻². The ctrlPD figure is now the same as the existing `LCCFUT-CTRLPD_fBVOCctrlPD` figure.

**Open-next:** rerun the notebook when NIRD is stable; old `_split6-2` files of these two cases are stale (delete?); drop the duplicate LCCFUT-CTRLPD case?

**Files changed:** `analysis/radiative-forcing-decomposition.ipynb`, `results/pptx/build_figures_pptx.py`, figures in `results/figures/radiative-forcing-decomposition/`.

</div>

<div style="color:#A84300">

## 2026-11-19 · 16:10 → 17:47 (97 min) · session 2ca075af

**Goal:** Tang comparison: outline the forest-change cells, add Tang's CanESM5 to the totals, and a figure like Tang Fig. 1b,f (then also with the vegetation-only differences, FUT and PD).

**Done:** thick outline of the modified cells in both Fig. 5 versions; CanESM5 bars (with the spread across scenarios) in the totals chart; new trend-map figure in Tang's unit (mgC m⁻² yr⁻²) with histograms, with three columns: total (lccFUT − ctrlPD), vegetation only in FUT (lccFUT − ctrlFUT) and in PD (lccPD − ctrlPD). Notebook rerun.

**Found:** Tang's present-day isoprene is ~12.5 TgC/yr, not ~14 as noted before (misread). Our emissions grow far more than Tang's in both models (ISO +211 % vs +18 / +64 %; MT +352 % vs −5 / +13 %). Our monoterpene change is positive almost everywhere; Tang's falls over much of the boreal zone (CO₂ inhibition, which our model lacks for monoterpenes). The vegetation change alone is small per year (forest-change cells: ISO +0.11 FUT / +0.07 PD, MT −0.04 / +0.01 mgC m⁻² yr⁻²) and goes both ways (about a third of the cells go down). Offline vs coupled: our PD→FUT increase = leaf temperature ×2.3–2.8 × leaf area ×2 (isoprene halved by CO₂, monoterpenes not); the coupled feedback of the new forest on its own leaf temperature (+0.3 K in summer) is worth only ~3–5 %. Correction: Tang's 2.4 / 2.8 °C warming is the mean over all 5 scenarios, so it is not comparable with our SSP5-8.5-only +6.6 K (land 46–82°N); Tang's Supp. Fig. 4a (you checked): SSP5-8.5 CanESM5 ~+12 K, GFDL ~+6–7 K, so GFDL warms like our runs. New LAI notebook: PD LAI agrees with LPJ-GUESS; by 2100 CLM's grows ×2.1 vs ×1.6. No notebook yet compares CLM's leaf area with LPJ-GUESS's.

**Open-next:** maybe drop "≈ OD550" from the Fig. 5 row labels and the side-by-side table (asked 15:11).  

**Files changed:** new `diagnostics/lai-clm-vs-lpjguess/clm_vs_lpjguess_lai.ipynb` + outputs, `diagnostics/README.md`; `diagnostics/tang2023-comparison/tang2023_comparison.ipynb`, its Fig. 5, totals and new `tang_fig1bf_trend_maps_2001_2025.png` + `fig1bf_trend_values_2001_2025.csv`.

</div>

<div style="color:#E58AA5">

## 2026-11-19 · 15:02 → 15:11 (9 min) · session 2ca075af

**Goal:** fix the colour of Tang's 2100 bar in the emission totals figure; in Fig. 5, keep Tang's ranges only for quantities that match.

**Done:** Tang's 2100 bar is now orange (= lccFUT, vegetation + climate), not red (ctrlFUT). In the Tang-range copy of Fig. 5, SOA burden and AOD vis keep our own scale (a burden is not an optical depth); the SOA burden bar goes to ±3 in both Fig. 5 versions. Notebook rerun.

**Found:** nothing new.

**Open-next:** maybe drop "≈ OD550" from the row labels and the side-by-side table (asked).

**Files changed:** `diagnostics/tang2023-comparison/tang2023_comparison.ipynb`, its emission-totals and 2 Fig. 5 PNGs.

</div>

<div style="color:#E58AA5">

## 2026-11-19 · 14:50 → 15:00 (10 min) · session 2ca075af

**Goal:** Tang comparison Fig. 5: colour bars like Tang's, plus a copy on Tang's ranges.

**Done:** discrete colour bars (4 steps per side, round numbers); copy with Tang's exact ranges (columns 1–2; column 3 keeps its own scale because Tang's third column is a different experiment). Notebook rerun, outputs saved.

**Found:** on Tang's ranges, our MT, SOA, AOD and CCN changes are past the end of the bar almost everywhere; ISO stays within it.

**Open-next:** none.

**Files changed:** `diagnostics/tang2023-comparison/tang2023_comparison.ipynb`, its 2 Fig. 5 PNGs.

</div>

<div style="color:#AAAAAA">

## 2026-11-19 · 14:12 → 14:47 (35 min) · session fff6dc27

**Goal:** fix the nudged 2026–2040 problems (your go); show where open science items 6–8 live; recap from 9 Nov; fill the Methods \NUM boxes; disk space; run timeline.

**Done:** LCC_FUT resubmitted (open since 13:55). MET copied to NIRD (open since 13:55). 3 false failure flags cleared (open since 13:55). Watcher queue check fixed and watcher restarted 14:19 (open since 13:55). Told you where items 6–8 are; recap since 9 Nov, newest first, with the reasons.

- Methods \NUM boxes filled (open since 4 Nov): FPC numbers (99.7 % BoNET expansion, densification < 5 % in every scenario), vegetation equilibrium PD + FUT on 2001–2025 (new notebook; outside the modified cells LCC and CTRL differ by ≤ 0.1 %), year-to-year independence on 25 years (rerun; radiation/temperature/cloud fine; PD LCC − CTRL SOA has real persistence: its significant cells drop 675 → 185 with an effective sample size). Only the FUT emission split is left. Both .tex files compile.

**Found:** the nn9188k project disk is a shared group quota: 954 of 1000 GiB; our part is ≈ 137 GB (restarts 86, input data 31, `_old` 20). The runs write to /cluster/work, so they are not at risk (inference). NIRD's whole disk is 99 % full.

**Open-next:** PD raw deletion, commits; science items 6–8 not investigated; FUT LMDI box after batch 2.

**Files changed:** `cases-scripts/run_when_done/met_nudg_2026-2040_when_done.sh` (queue check); `boreal-forest-expantion-draft/methods.tex` (3 macros), `methods-claude.tex` (5 boxes); new `diagnostics/0_check-simulation-equilibrium/check_LCC_vs_CTRL_vegetation_state_2001-2025.ipynb`; `diagnostics/yearly-difference-autocorrelation/yearly_difference_autocorrelation.ipynb` (2001–2025, old outputs kept in `_outputs_2001-2014/`). Not committed.

</div>

<div style="color:#AAAAAA">

## 2026-11-19 · 13:55 → 14:10 (15 min) · session fff6dc27

**Goal:** status check today, list of open topics, recap of recent sessions.

**Found:** the nudged 2026–2040 runs mostly started overnight (11 of 12 running). LCC_FUT crashed at start-up (segfault reading the restart, 09:53). The watcher marked 3 runs as failed that are actually running (false alarms from its queue check). The MET copy to NIRD failed (NIRD read error). Met build 3 done (met files reach 2041-01-02). FUT MEGAN batch 2 is running.

**Open-next:** your OK: resubmit LCC_FUT, clear the 3 false failure flags, retry the MET NIRD copy, fix the watcher's queue check.

**Files changed:** none (logs only).

</div>

<div style="color:#A84300">

## 2026-11-18 · 20:11 → 20:22 (11 min) · session af520c06

**Goal:** fix and relaunch the two stalled chains (your go).

**Done:** (1) Nudged runs 2026–2040: fixed the check that failed falsely (it allowed only spaces, but `atm_in` uses tabs) in `cases-scripts/cases-setup.sh` and the same check in `extend_nudg_runs_2026-2040.sh`. Old failure files moved to `/cluster/work/users/adelez/met-nudg-2040/falsefail-20261117/`. Dry run clean, watcher restarted 20:12. It submitted met build 2 and phase A of all 12 runs by 20:20, none failing (the restart files are now switched too). (2) FUT MEGAN batch 2 (2002, 2006, 2011) launched 20:15 (6 cases, 12 jobs); reduction watcher started.

**Found:** the 17 Nov failure was only the check, and no run was touched beyond `user_nl_cam`.

**Open-next:** 2026–2040 results expected ~22–23 Nov; FUT batch 2 done in ~11 h, then the maps waiter reruns the reducer and notebook; PD raw deletion and commits still wait for you.

**Files changed:** `cases-scripts/cases-setup.sh` (lines 210–211), `cases-scripts/extend_nudg_runs_2026-2040.sh` (line 83). Not committed.

</div>

<div style="color:#008080">

## 2026-11-18 · 19:40 → 19:50 (10 min) · session af520c06

**Goal:** status check: what is on the plate.

**Found:** two automatic chains stopped and nothing has run since. (1) FUT MEGAN batch 2 (2002, 2006, 2011) was never launched: at 20:11 on 16 Nov the waiter saw a from2000 job still queued and refused. (2) All 12 nudged 2026–2040 runs: phase A **false-failed** at 02:30 on 17 Nov. The met switch worked (user_nl_cam + atm_in show the 2000–2040 list), but the check greps `name *=` and atm_in uses tabs. The watcher exited, so the met folder only reaches 2031-12-31, although MET finished to 2041 (14:33 today). /cluster/projects is at 954 of 1000 GiB.

**Open-next:** your OK: fix the grep and resubmit the 12 runs + restart the watcher; relaunch FUT batch 2; PD raw deletion (~6.3 TB, purge ~mid Dec); commits (41 M, 457 D, 42 new).

**Files changed:** none (logs only).

</div>

<div style="color:#A84300">

## 2026-11-16 · 22:00 → 00:30 (150 min) · session 06c39ecc

**Goal:** compare our results with Tang et al. 2023 (Figs. 1, 2, 5), then make the same kind of maps for our runs.

**Done:** answered in chat first. Built and ran `diagnostics/tang2023-comparison/tang2023_comparison.ipynb`: Tang Fig. 5 layout (standard / noVegDym / vegetation effect), regional boxes, PFT cover change, emission totals vs Tang, side-by-side table, written reading (section 7).

**Found:** the vegetation effect has Tang's monoterpene pattern (−5 to −10 % in the southern boreal belt and Fennoscandia, +15 to +26 % in Alaska, N Canada, E Siberia) but over ≥45°N it changes SOA, AOD and CCN by only ~0.3 %, against +235 % SOA, +8 % AOD, +46 % CCN from the future climate on emissions. Isoprene drops in Fennoscandia/E Siberia, opposite to Tang. `AEROD_v` is empty in our files (use `AOD_VIS`). NIRD gave read errors all evening; files fine (BVOCOX too).

**Open-next:** check why isoprene falls where broadleaf trees expand (CLM-MEGAN emission factors?); commit the notebook if you want it.

**Files changed:** `diagnostics/tang2023-comparison/` (new notebook + `_outputs/`, cache symlink to /cluster/work).

</div>

<div style="color:#008080">

## 2026-11-16 · 22:08 → 22:29 (21 min) · session 79aa63f4

**Goal:** second figure in `plot_bvoc_means.ipynb` with all other BVOC seen by CAM.

**Done:** new section 4: the 17 other MEGAN species (`MEG_*`, biogenic only), mean ± 1σ over 2001–2025, LCC-modified cells, Gg/yr, one panel each, sorted by size. Yearly totals cached in `plot_bvoc_means_outputs/bvoc_other_yearly_totals_2001-2025.csv`.

**Found:** over the modified cells the forest effect on all 17 species is small and negative (PD −0.3 to −5 %, FUT −0.7 to −8 %; only acetaldehyde/ethanol +1 % in PD). Climate effect +345 to +621 % (β-caryophyllene largest). Several species change by exactly the same %, as MEGAN splits them from shared emission classes (inference).

**Open-next:** none; figure checked.

**Files changed:** `diagnostics/2_bvoc-emissions/plot_bvoc_means.ipynb`; new CSV + PNG in `plot_bvoc_means_outputs/`.

</div>

<div style="color:#008080">

## 2026-11-16 · 22:13 → 23:49 (96 min) · session 16ac98c9

**Goal:** say what `diagnostics/2_isoprene-diurnal-cycle` is for; then compare each fBVOC run with its own interactive source.

**Done:**
- Answered: the folder only partly did this (input files vs other MEGAN runs).
- New script `reduce_isoprene_fbvoc_vs_source.py` and notebook section 10 (checks, diurnal cycle, monthly 2001–2025, variability, summary).

**Found:** fBVOC runs = source average exactly, same daily cycle; they lack the weather-driven swings (summers ±7–9 %, days ±25–35 %); 2015–2025 PD sources ~2 % below the input. NIRD gives random read errors (~5 %), none from `/cluster/work`.

**Open-next:** commit when you want.

**Files changed:** new `reduce_isoprene_fbvoc_vs_source.py`, `isoprene_diurnal_cycle_fBVOC.ipynb` (+ section 10, + 3 figures, 3 tables), new files in `data/processed-data/isoprene-diurnal/`.

</div>

<div style="color:#008080">

## 2026-11-16 · 22:09 → 22:50 (41 min) · session 6722329d

**Goal:** give `plot_bvoc_emissions.ipynb` a figures folder.

**Done:**
- Each figure is saved as PNG in `diagnostics/2_bvoc-emissions/plot_bvoc_emissions_outputs/` (annual maps, LCC − CTRL maps, seasonal cycles, seasonal maps).

**Open-next:** commit when you want.

**Files changed:** `diagnostics/2_bvoc-emissions/plot_bvoc_emissions.ipynb`, new `plot_bvoc_emissions_outputs/`.

</div>

<div style="color:#008080">

## 2026-11-16 · 20:43 → 21:10 (27 min) · session 64634bba

**Goal:** repeat the isoprene diurnal-cycle notebook for the fixed-BVOC runs, and plot the whole time series hour by hour.

**Done:**
- New reducer `reduce_isoprene_fbvoc_and_timeseries.py`: daily-cycle averages of the 4 prescribed input files and of the 2 fBVOC test runs with 30-min output; 30-min regional totals for all runs (saved on NIRD, so they survive the /cluster/work purge).
- New notebook `isoprene_diurnal_cycle_fBVOC.ipynb`, run with outputs saved: seasons, LCC − CTRL, month × hour, latitude shape, summary, test runs, full hourly series + a July zoom.

**Found:**
- The model emits the file values as given (replay test = its source run to 0.05 %).
- The input's yearly totals are within 2.5 % of the interactive runs; daily shape and LCC − CTRL by hour are the same. Only the day-to-day weather signal is smoothed out.

**Open-next:** FUT 2002/2006/2011 after FUT batch 2: rerun the reducer, then the notebook.

**Files changed:** `diagnostics/2_isoprene-diurnal-cycle/{reduce_isoprene_fbvoc_and_timeseries.py, isoprene_diurnal_cycle_fBVOC.ipynb, isoprene_diurnal_cycle_fBVOC_outputs/}`; `data/processed-data/isoprene-diurnal/{fbvoc,timeseries}/`; logs.

</div>

<div style="color:#62733B">

## 2026-11-16 · 20:48 → 21:05 (17 min) · session e5c7a527

**Goal:** fix and restyle the BVOC means plot.

**Done:**
- Why the two LCC_FUT points did not overlap: I had shifted the open marker on purpose (same run, same value). Shift removed; the PD → FUT arrow ends on LCC_FUT.
- x labels VEG_CTRL / VEG_LCC; lines are arrows with the run names along them; colours in a legend; period as non-bold subtitle.

**Open-next:** none (error bars still ± 1 SD between years; standard error possible on request).

**Files changed:** `diagnostics/2_bvoc-emissions/plot_bvoc_means.ipynb` + its figure; logs.

</div>

<div style="color:#A84300">

## 2026-11-16 · 20:39 → 20:55 (16 min) · session e391bcc3

**Goal:** check that the reorganisation reruns finished.

**Done:**
- All 10 notebooks reran without errors (18:15–20:16): radiative-forcing-decomposition, artefact-corrected-split, radiative_forcing, bvoc-soa-cloud-interactions, land-carbon-water, biogeophysical-hydro, cumulative_radiative_decomposition, timeseries-responses, pd-fut-attribution, simulation-contrasts (open since 17:58).
- Slide-deck builders updated to the new folders (figures, land carbon/water, MEGAN; contrasts needed nothing). Test builds in the scratchpad: all 4 OK, every figure placed (main deck 325 slides / 315 figures, with a new section 5 "Forcing decomposition"; land 13, MEGAN 55, contrasts 12 slides). `fut-fbvoc-emission-source-choice` left as it is (you asked).
- 29 empty folders removed. Checked the new δ_FUT Ghan figure: δ is small and not significant (NET ≥45°N +0.014 ± 0.025 W m⁻²).

**Open-next:** rebuild the 4 decks in `results/pptx/` (your OK); commit (another session holds my changes, on your instruction).

**Files changed:** `results/pptx/build_figures_pptx.py`, `build_land_carbon_water_pptx.py`, `build_megan_pptx.py`; results (reruns, empty folders removed); logs.

</div>

<div style="color:#008080">

## 2026-11-16 · 18:20 → 19:14 (54 min) · session 8fca3854

**Goal:** diurnal cycle of isoprene from the saved 30-min output; move the `plot*` BVOC notebooks to diagnostics.

**Done:**
- `reduce_isoprene_diurnal.py` turns the 30-min isoprene/monoterpene output of the MEGAN split runs into monthly average days, saved on NIRD (`data/processed-data/isoprene-diurnal/`). PD: 2001–02, 2005–06, 2010–11. FUT: 2001, 2005, 2010.
- `isoprene_diurnal_cycle.ipynb` (outputs saved): cycle in local solar time by season, LCC − CTRL by hour, month × hour, shape by latitude, summary table.
- Moved `plot_bvoc_emissions`, `plot_bvoc_timeseries`, `plot_bvoc_means` (+ figure folders) to `diagnostics/2_bvoc-emissions/`. Paths fixed, not rerun.

**Found:**
- Peak at 12:45–13:15 local time; 3–5 % of the summer emission is at night (18–06).
- LCC − CTRL in summer over the expansion area: +6.5 % (PD), +4 % (FUT, only 3 years, not significant). Almost the same % at every hour.
- Further north the cycle is flatter (long days): summer peak 3.7 × the daily mean in the tropics, 2.7 × at 65–90°N.

**Open-next:** when FUT batch 2 (2002, 2006, 2011) is archived, rerun the script and the notebook. Nothing committed.

**Files changed:** `diagnostics/2_isoprene-diurnal-cycle/` (new), `diagnostics/2_bvoc-emissions/` (moved), `diagnostics/README.md`, `preprocess/bvoc-emissions/README.md`.

</div>

<div style="color:#555555">

## 2026-11-16 · 18:26 → 18:29 (3 min) · session 017a5cd2

**Goal:** know what keeps running without internet; restart the archive guard.

**Done:**
- Checked what runs where. Slurm jobs and detached scripts keep going without you. The Claude sessions in VS Code only last until the VS Code server gives up waiting for you to reconnect (about 3 h, not verified).
- Archive guard: found it alive on login-3 (its lock file is held), so no restart was needed.

**Found:** pgrep can't see login-3 from login-2. Checking the lock file works from any node.

**Open-next:** nothing.

**Files changed:** logs only.

</div>

<div style="color:#62733B">

## 2026-11-16 · 18:16 → 18:27 (11 min) · session e5c7a527

**Goal:** one plot condensing the BVOC time series into mean values (your sketch).

**Done:**
- New `preprocess/bvoc-emissions/plot_bvoc_means.ipynb` (run, outputs saved). Figure `plot_bvoc_means_outputs/bvoc_means_veg_x_climate_modified_2001-2025.png`: one panel each for ISOP and MTERP.

**Found:** (Tg/yr, LCC-modified cells, 2001–2025) ISOP 4.1 → 4.3 (PD), 12.6 → 12.9 (FUT); MTERP 4.9 → 5.0 (PD), 22.8 → 22.6 (FUT). Forest effect is small next to the climate effect.

**Open-next:** check that the open "PD → FUT" marker means what you meant (now = LCC_FUT, shifted right); error bars are ± 1 SD of yearly totals (could be standard error instead).

**Files changed:** `preprocess/bvoc-emissions/plot_bvoc_means.ipynb` + `plot_bvoc_means_outputs/` (new); logs.

</div>

<div style="color:#A84300">

## 2026-11-16 · 17:58 → 18:36 (38 min) · session e391bcc3

**Goal:** reorganise `results/` per notebook, use design A everywhere, new forcing-decomposition notebook, period wording in titles.

**Done:**
- `results/` reorganised as you asked (layout above); old 2001–2025 set archived in `results/figures-pre-reorg-20261116/` and `results/tables-pre-reorg-20261116/` (not in git). MEGAN figures and tables moved to their notebook folders (no rerun needed).
- art_LCC_P redefined as LCC_P − LCC_P_fBVOClccP (own emissions); δ_P added as an artefact contrast (open since 16:47).
- Titles: years removed, map subtitles say "Maps: 25-year mean" (open since 16:47; also answers the 13:43 period-wording item).
- New notebook `analysis/radiative-forcing-decomposition.ipynb`: six-map figures (design A, slide names, new colour scales, new file names) for PD, 3 FUT cases and LCC_FUT − CTRL_PD, plus the design-A split budget.
- `artefact-corrected-split.ipynb` now only design B (→ `artefacts/design-B/`) and the B-vs-A comparison.
- 9 other notebooks point to their new folders; `results/README.md` and `CLAUDE.md` updated.

- First rerun attempt failed at once: the notebook kernel took more than 60 s to start (slow NIRD disk). The runner now waits up to 10 min (`run_nb_inplace.py --startup-timeout`); reruns restarted 18:15. First new figures (PD, FUT ctrlFUT) look right: slide names, no years in the title, "Maps: 25-year mean" in the subtitle, BVOC maps on ±0.5 now show their pattern (PD NET ≥45°N: albedo +0.44, total +0.26, BVOC −0.020 ± 0.023 W m⁻², not significant).
- New decomposition notebook finished without errors (21 min): 30 six-map figures + the design-A budget; the split adds up exactly (1.6e-15). LCC_FUT − CTRL_PD (NET, ≥45°N): albedo +10.15, total +1.33, BVOC −1.00 ± 0.02 W m⁻² (cloud −1.10). The other 9 notebooks are running.

**Open-next:** check the reruns; slide-deck builders still expect the old folders (not changed yet); `fut-fbvoc-emission-source-choice` still writes to its own `_outputs/` folder.

**Files changed:** `src/.../plotting/forcing_maps.py`, `megan_maps.py`; `results/tables/logs/run_nb_inplace.py`; 12 notebooks in `analysis/` (1 new); `results/README.md`, `CLAUDE.md`, `.gitignore`; watcher comment in `cases-scripts/run_when_done/megan_lmdi_maps_when_FUT_done.sh`; logs.

</div>

<div style="color:#008080">

## 2026-11-16 · 18:03 → 18:33 (30 min) · session f7c9ff9e

**Goal:** split the background-aerosol PD/FUT notebook into a prescribed and an online notebook; rename the LCC notebook to `_online`; bar charts and time series also north of 40°N.

**Done:**
- Two new notebooks in `diagnostics/background-aerosol/`: `background_aerosol_pd_fut_prescribed.ipynb` and `background_aerosol_pd_fut_online.ipynb`, each with its own outputs folder.
- North of 40°N: emission totals (bars) and file time series in the prescribed notebook; online-source bars and time series in the online notebook (no lightning: it exists only as a global number).
- `background_aerosol_lcc_ctrl_fut_online.ipynb` (renamed, with its outputs folder; not rerun, only paths changed). `diagnostics/README.md` updated.

**Found:** north of 40°N, FUT vs PD: sulfur emissions 19.5 → 4.2 Tg S (−79 %), BC −46 %, OM +17 % (fires), NOx −34 %, NH₃ unchanged; MEGAN 56 → 191 Tg (×3.4), DMS flux 1.12 → 1.56 Tg S (+39 %), dust and sea salt about the same.

**Done (18:31):** both notebooks ran without errors (24 and 15 min; NIRD slow); 40°N figures checked; old `background_aerosol_pd_fut.ipynb` and its outputs folder deleted (still in git, commit 58de6c2).

**Open-next:** commit the split (not done).

**Files changed:** the notebooks above + outputs; `diagnostics/README.md`; logs.

</div>

<div style="color:#999999">

## 2026-11-16 · 17:58 → 18:08 (10 min) · session cf84836f

**Goal:** commit the open work by topic.

**Done:** 5 commits: MEGAN 2001–02 month fix + reruns; background aerosol 2001–2025 + Arctic maps; notes (`CLAUDE.md`, `NOTES.md`); sandbox tests; logs.

**Open-next:** split-figure labels commit held until the results-folder reorganisation is settled; background aerosol notebooks being rerun by another session → commit their new outputs after.

**Files changed:** logs only (plus git commits).

</div>

<div style="color:#999999">

## 2026-11-16 · 16:04 → 16:27 (23 min) · session 9b7c5f07

**Goal:** suggestions for `NOTES.md` in the same style as your notes.

**Done:** suggested new lines for "In cleaning process" (old figure sets, Python caches, test runs, old-chain runs, git size) and "Notes" (old spin-up mismatch, SF vs MEG, matched baseline, purge/quota, spin-up months). Rewrote the spin-up note more clearly: the code removes the first 12 time steps without looking at dates, so running it twice loses a real year.

**Found:** 17 notebook checkpoint folders, 15 Python cache folders, `.git` 4.2 GB, home 14 of 20 GB used.

**Done (later):** added the lines to `NOTES.md` and fixed the spin-up rule in `CLAUDE.md` (you asked).

**Open-next:** nothing.

**Files changed:** `NOTES.md`, `CLAUDE.md`, logs (not committed).

</div>

<div style="color:#555555">

## 2026-11-16 · 16:00 → 16:40 (40 min) · session 06b518ae

**Goal:** check why the MEGAN 2001/2002 month-fix logs looked silent, then finish the fix.

**Found:** the re-reduction had finished at 14:25 (logs were only buffered). The check before the swap failed on rounding-level differences (1e-16); results are fine.

**Done:** fixed 2001/2002 files swapped in at 16:34 (your "go"); old files in `data/processed-data/megan-lmdi/old-month-offset-20261115/`. Added to `NOTES.md`: the month fix and the nudging fix of the last met file (2015-01-01).

**Open-next:** 3 MEGAN notebooks rerunning (status in `results/tables/logs/run_monthfix_notebooks_20261116.status`). Deleting the PD raw files is no longer blocked, but needs your OK.

**Files changed:** `NOTES.md`; `analysis/megan-lmdi-vs-approx.ipynb` (stricter check, rerun); 2 more notebooks rerun; PD 2001/2002 LMDI files.

</div>

<div style="color:#008080">

## 2026-11-16 · 15:27 → 16:37 (70 min) · session f7c9ff9e

**Goal:** background-aerosol PD vs FUT notebook: 25 years, Arctic maps (global as appendix), online sources plotted like the prescribed emissions.

**Done:**
- `background_aerosol_pd_fut.ipynb` updated and run (0 errors): 2001–2025; all maps polar (north of 45°N, dashed Arctic Circle); global versions in an Appendix (`figures/appendix-global/`); new §9.1 bar chart (25-yr global mean ± 1 s.d., stacked by component) and yearly time series (CTRL_PD solid, CTRL_FUT dashed); summary table with an Arctic column. The LCC_FUT − CTRL_FUT notebook already used 2001–2025 and polar maps (unchanged).
- Old 2001–2014 figures and tables kept in `background_aerosol_pd_fut_outputs/2001-2014/`.
- Bar labels now plain numbers (2470, not 2.47e+03); FUT − PD colourbars: the bin around 0 is pure white, other colours unchanged (first rerun failed: Jupyter kernel did not start; second try failed too (the NIRD disk is slow, so Python takes > 2 min to start); third try with a longer start-up wait worked, 0 errors, figures checked).

**Found:** values change ≤ 2 % vs 2001–2014. Arctic (>66.5°N) FUT vs PD: sulfate −41 %, surface DMS +413 %, droplet column **+25 %** (global −9 %). A first run gave a wrong FUT dust (362 Tg) because of a grid mismatch in a reused cache; fixed, now 4.03 Pg as in the LCC notebook.

**Open-next:** why the Arctic droplet column rises (DMS / sea ice / clouds) is not checked.

**Files changed:** `diagnostics/background-aerosol/background_aerosol_pd_fut.ipynb` + outputs; logs.

</div>

<div style="color:#E58AA5">

## 2026-11-16 · 15:11 → 16:47 (96 min) · session e391bcc3

**Goal:** use the slide names (`simulations-interpretation.pptx`) in the six-map forcing figures, design A and B.

**Done:**
- The plotting function can now take a title name, a label over each group of maps (part of it in bold) and a note under the figure. Old figures look the same unless these are given.
- Test figures (NET, PD + 3 FUT cases, design A and B) in `sandbox/test_split_aliases_outputs/`; checked by eye.
- Added the case LCC_FUT − CTRL_PD (land cover + climate change together): left maps LCC_FUT − CTRL_PD (albedo +10.15, total +1.33 W m⁻² over 45–90°N, NET), right maps = the same BVOC maps as the FUT case with ctrlPD emissions. The ±6 colour scale is saturated on the left (snow loss from the climate change).

- You approved the names (design A brackets not bold) and a new file-name pattern; you asked to reorganise `results/` first (one folder per notebook, then interactive / fBVOC / non-BVOC; artefacts only in `artefacts/`; design A everywhere).
- Found: `radiative_forcing.ipynb` already uses prescribed − prescribed pairs for fBVOC (design A, real LCC_FUT_fBVOClccFUT since 11 Nov); the six-map decomposition figure is only in `artefact-corrected-split.ipynb` now.
- Explained the two MEGAN notebooks (plain EPS/GAMMA maps vs exact attribution maps).

- 16:35: layout agreed (see box). Computed the spread of every map of the decomposition figures (file `sandbox/test_split_aliases_outputs/decomposition_ranges_q98_designA_2001_2025.csv`) and proposed colour scales. Found that the current art_LCC (LCC − LCC_fBVOCctrl) still contains the BVOC effect, so it is not a pure artefact.

- 16:52: you confirmed `artefacts/d_artefacts/`, `artefacts/design-B/` and the colour scales. Explained the art_LCC question again with numbers; gave 3 options for the period in titles.

**Open-next:** art_LCC choice; title option. Then: move the files, fix the notebook paths, add the names to `analysis/artefact-corrected-split.ipynb` and redraw its split figures (all bands, both colour-scale versions).

**Files changed:** `src/boreal_forest_expansion/plotting/forcing_maps.py`; new `sandbox/test_split_aliases.py` + outputs; logs.

</div>

<div style="color:#999999">

## 2026-11-16 · 13:16 → 13:36 (20 min) · session ada6f70d

**Goal:** make the proposed commits, grouped by topic; fix `lake_fix_effect.ipynb`; commit the latest updates.

**Done:**
- 8 commits on `main`, not pushed: notes moved to `docs/`; design A split figures; MEGAN LMDI reruns; caches moved to `/cluster/work`; sandbox simulation-year script; simulation-contrasts figures moved to `results/` (work of another session); `lake_fix_effect` fix; logs. Commit proposal from 13:14 (session 90ef7026) done.
- `lake_fix_effect.ipynb`: now reads the old figures from `results/figures-2001-2014/`; rerun with no errors (open since 13:14, session 90ef7026).
- `analysis/simulation-contrasts` change: already committed in `1995c62` (notebook + figures moved to `results/figures/simulation-contrasts/`); nothing left to commit.
- Home folder was at its file limit (99 530 of 100 000), which blocked git and broke reruns. With your OK, 6 unused VS Code server copies were deleted: now 73 949 files.

**Open-next:** two new files from other sessions are not committed: `cases-scripts/run_when_done/megan_lmdi_maps_when_FUT_done.sh`, `sandbox/test_fut_minus_pd.py`. Keep an eye on the file count (`dusage`).

**Files changed:** `diagnostics/3_megan-exact-split-test/lake_fix_effect.ipynb` (+ outputs, run log); `~/.vscode-server/` (old copies removed); logs.

</div>

<div style="color:#999999">

## 2026-11-16 · 13:08 → 13:14 (6 min) · session 90ef7026

**Goal:** move the Markdown notes out of `analysis/` into `docs/`; suggest commits.

**Done:** 3 notes moved with git (`FBVOC_ARTEFACT.md`, `MEGAN_ATTRIBUTION.md`, `PLOTTED_VARIABLES.md`); all references updated. Commit plan written.

**Found:** two notebook reruns failed: `analysis/megan-lmdi-attribution-maps.ipynb` (NIRD HDF lock error; the committed version is fine) and `diagnostics/3_megan-exact-split-test/lake_fix_effect.ipynb` (looks for a figure in the old `results/figures/megan_factors/before_lake_fix/`).

**Open-next:** your go on commits A (housekeeping) and B (design A); fix + rerun the two notebooks; then the one leftover reference in `megan-lmdi-attribution-maps.ipynb`.

**Files changed:** the 3 notes (moved), ~25 files with updated references.

</div>

<div style="color:#999999">

## 2026-11-16 · 13:07 → 13:20 (13 min) · session d963b45a
**Goal:** put the simulation-contrasts figures in `results/` with the other figures.

**Done:** moved the 9 figures for 2001–2025 to `results/figures/simulation-contrasts/` and the 9 for 2001–2014 to `results/figures-2001-2014/simulation-contrasts/`. The notebook now saves there, and the deck script reads from there. Both READMEs are updated. (At first I had only added a note to the README; you meant a move.)

**Open / next:** nothing. The automatic 2001–2040 rerun will also write there.

**Files changed:** `analysis/simulation-contrasts.ipynb` (path only), `results/pptx/build_contrasts_pptx.py`, `analysis/README.md`, `results/README.md`, logs.

</div>

<div style="color:#999999">

## 2026-11-16 · 11:44 → 11:50 (6 min) · session 0706ae25
**Goal:** see whether the unfinished spin-up check and `_old/` hold anything worth keeping.

**Done:** checked both, changed nothing.

**Found:** the spin-up check was dropped because the NCO scripts were too slow, and its raw input is gone. The newer `0_check-simulation-equilibrium` covers it, except for the quick spin-up (LCC FUT) figures. `_old/`: all functions were moved to `src/`; the rest is notebooks from the earlier idealized setup.

**Open / next:** your OK to archive the spin-up folder (keeping its figures and small files) and to delete `_old/` (git keeps a copy).

**Files changed:** logs only.

</div>

<div style="color:#999999">

## 2026-11-16 · 11:39 → 11:44 (5 min) · session 4d122426
**Goal:** suggest and make commits for the uncommitted work.

**Done:** commits grouped by topic (your rule from now on: one commit per topic, not per folder). 4 made: MET + nudged runs 2026–2040, MEGAN exact split, design A, background aerosol.

**Open / next:** push when you want; the design-A commit message still mentions the folder rename (already in your own commit), reword if you like.

**Files changed:** logs only.

</div>

<div style="color:#008080">

## 2026-11-16 · 10:59 → 11:31 (32 min) · session 6ce7bd45

**Goal:** finish the background-aerosol work: methane values, a table of what each compound does, a section on the natural sources, a new LCC_FUT − CTRL_FUT notebook, and why the cleaner FUT background matters.

**Done:**
- PD/FUT notebook: roles table; methane 1778 → 2415 ppb (+36 %), N₂O +24 %, CO₂ ×3.1; natural sources section (MEGAN, dust, sea salt, DMS, lightning NOx); longer summary.
- Checked NH₃ in the model code: no ammonium particles, but NH₃ makes cloud water less acidic, which speeds up sulfate formation in clouds (the earlier "gas only" answer was incomplete).
- New notebook `background_aerosol_lcc_ctrl_fut.ipynb` (2001–2025, significance tested).
- "Add CH₄ values and roles table" done (open since 2026-11-15 19:17).

**Found:**
- PD → FUT: forests emit far more (isoprene +74 %, monoterpenes ×3.5); lightning NOx +36 %; DMS flux +43 % at 46–82°N because of less sea ice.
- LCC_FUT − CTRL_FUT in the expanded-forest cells: isoprene +2.8 %, monoterpenes −0.6 %, ozone +1.3 %, droplets −0.75 %; particles (SOA, sulfate, AOD) not significantly changed.

**Open-next:** add both notebooks to `diagnostics/README.md` (it still lists the old folder; the folders were moved at 11:27 outside this session); nothing committed.

**Files changed:** `diagnostics/background-aerosol/background_aerosol_pd_fut.ipynb` (+ outputs); new `diagnostics/background-aerosol/background_aerosol_lcc_ctrl_fut.ipynb` (+ outputs).

</div>

<div style="color:#E58AA5">

## 2026-11-16 · 11:22 → 13:43 (141 min) · session 89a5509c

**Goal:** finish the simulation-year plots; move all caches to the work disk (you asked).

**Done:** all `cache/` folders moved to `/cluster/work/users/adelez/boreal-caches/` (links left in place, ignored by git); year-1 files all made.

**Found:** the write errors came from a full home quota (my sandbox cache, 4.8 GB). Home also has nearly the maximum number of files (99,368 of 100,000).

**Done (2):** 6 drift figures (simulation-year axis) from the existing yearly table + year 1.

**Found (2):** FUT runs with present-day emissions: SOA settles only after ~3 years (mean changes by 0.5 %).

**Done (3):** title wording tried three ways (A/B/C) in `sandbox/test_period_wording_outputs/`.

**Open-next:** pick A/B/C wording; your feedback on the drift plots; seasonal figures when NIRD reads work.

**Files changed:** `.gitignore`, `CLAUDE.md` (cache location), `sandbox/test_fut_minus_pd_outputs/cache/run_2000_missing.sh`.

</div>

<div style="color:#E58AA5">

## 2026-11-16 · 11:00 → 11:13 (13 min) · session 89a5509c

**Goal:** plot the cyclical PD/FUT runs with simulation year on the x-axis; drift with the analysis period shaded; Jan–Dec seasonal cycle.

**Done:** script `sandbox/test_cyclical_sim_year.py` written.

**Found:** yesterday's year-2000 helper skipped the emission and evapotranspiration files (a script bug); being redone.

**Open-next:** run the script, check the figures.

**Files changed:** `sandbox/test_cyclical_sim_year.py`, `sandbox/test_fut_minus_pd_outputs/cache/run_2000_missing.sh` (new).

</div>

<div style="color:#555555">

## 2026-11-16 · 10:56 → 11:08 (12 min) · session 1b77ec0b

**Goal:** fix the 2001–2002 time shift, rerun the ANN-affected MEGAN notebooks, switch to exact attribution maps.

**Done:**
- 2001–2002 time shift: decided "fix" (open since 2026-11-15); reduction code fixed and tested.
- ANN rerun and exact maps: decided "yes" (open since 2026-11-15); approximate maps removed from `megan_factor_maps.ipynb`, the exact-map notebook is the reference.

**Found:** FUT 2005 already reduced, 2010 reducing; FUT 2001 runs until tonight, so it gets the fix directly.

**Open-next:** check the swap + reruns (~14:30); update the MEGAN slides; PD raw deletion still needs your OK.

**Files changed:** `postprocess/megan_lmdi/reduce_megan_lmdi.py`, `src/.../plotting/megan_maps.py`, `analysis/megan_factor_maps.ipynb`.

</div>

---

<div style="color:#7B2FBE">

## 2026-11-16 · 10:58 → 12:33 (95 min) · session e425a9ff

**Goal:** bring the slide decks in `results/pptx/` up to design A; make the design-A figures that were missing.

**Done:** 4 CICERO decks rebuilt (old copies in `/cluster/work/users/adelez/pptx-backup-20261116/`); new figures `design-A-split/radiative_budget_split_designA_NET_2001_2025.png` and `*_ghan*_artLCCown_*` (8); the notebook runner can now run only some cells (`--cells`); integrity check of all 7 decks and all 339 figures: nothing broken.

**Found:** artefact on LCC land with own emissions, FUT ≥45°N: +0.074 ± 0.027 W m⁻² (cloud +0.080). NIRD lost its file locks: most `RADIATIVE` files need `HDF5_USE_FILE_LOCKING=FALSE`; the Python env also gave I/O errors twice.

**Open-next:** `simulations-interpretation.pptx` and the old non-CICERO deck still show design B; commit when you want.

**Files changed:** `analysis/artefact-corrected-split.ipynb`, `results/tables/logs/run_nb_inplace.py`, `results/pptx/build_{figures,contrasts,megan,land_carbon_water}_pptx.py`, the 4 `*_CICERO.pptx`.

</div>

<div style="color:#AAAAAA">

## 2026-11-16 · 10:59 → 11:02 (3 min) · session fc06b4b6

**Goal:** status of the 2026–2040 runs.

**Done:** watcher started (it was not running; nothing was missed). Archive guard alive.

**Found:** MET runs 6.7 model years per day; job 1 ends ~19:00 today.

**Open-next:** gate check + met days after MET job 1 → the 12 runs start automatically (MET + nudged 2026–2040, open since 11 Nov).

**Files changed:** `docs/met-nudg-2026-2040.md` (job log).

</div>

<div style="color:#A84300">

## 2026-11-16 · 10:58 → 13:18 (140 min) · session ae435137

**Goal:** MEGAN attribution maps like the old PD ones, but from the exact LMDI split; when FUT ends.

**Done:** new notebook `analysis/megan-lmdi-attribution-maps.ipynb` (run, outputs saved) → 4 maps `results/figures/megan_factors/PD_{isoprene,MTERP}_attribution_LMDI_{ANN,JJA}_6yr.png` + table `results/tables/megan_factors/megan_lmdi_attribution_PD_45N.csv`. (Made 15 Nov 19:45.)

**Found:** ≥45°N, ANN, 6 years: isoprene +1.8 % = composition −2.2 % + activity +4.0 % (leaf area +3.3 %); monoterpenes −0.5 % = composition −4.5 % + activity +4.0 % (leaf area +3.7 %). Temperature only +0.5 % in both. FUT: 2000 + 2005 reduced, 2010 reducing, 2001 running.

**Open-next:** your feedback on the maps; FUT LMDI maps once all FUT years are in (~17 Nov evening).

**Found (11:55):** the 2001–2002 half-hour shift was already decided ("fix", 15 Nov 19:51) and is being fixed by another session; my new maps are redrawn automatically once the fixed PD 2001/2002 files are in place. FUT 2001/2002 use the fixed code. My earlier "still waiting on you" was wrong.

**Done (13:18):** the maps notebook now does PD and FUT; FUT is drawn automatically by `cases-scripts/run_when_done/megan_lmdi_maps_when_FUT_done.sh` (running) once all 6 FUT years are reduced (~17 Nov evening). PD results unchanged.

**Open-next (12:50):** nothing needed from you now. Later: MEGAN slides still show the old approximate maps; FUT numbers in the Methods; decide on deleting the MEGAN raw files (the work disk purges them ~mid-December anyway).

**Files changed:** `analysis/megan-lmdi-attribution-maps.ipynb` (new), 4 png + 1 csv (new).

</div>

<div style="color:#555555">

<div style="color:#E58AA5">

## 2026-11-15 · 19:15 → 19:24 (9 min) · session d8d4f4eb

**Goal:** how to plot the PD/FUT time-slice runs; sandbox figures of FUT − PD.

**Done:** advice (pair FUT and PD by nudging year, no 2000→2100 axis); new sandbox folder `test_fut_minus_pd_outputs/` with 4 figures + table.

**Found:** ≥45°N, 2001–2025: FUT − PD net TOA +1.1 W m⁻² (CTRL) vs +2.0 (fBVOC runs with the same emissions in both periods); the forest-expansion effect itself changes little from PD to FUT (−0.04 ± 0.03 W m⁻²).

**Open-next:** your feedback on the layout; a seasonal-cycle version needs the monthly files.

**Files changed:** `sandbox/test_fut_minus_pd.py` (new), `sandbox/test_fut_minus_pd_outputs/` (new).

</div>

## 2026-11-15 · 19:17 → 19:28 (11 min) · session 6ce7bd45

**Goal:** keep the 46–82°N band but explain it better; understand which compounds the background-aerosol notebook looks at and what DMS does.

**Done:** the notebook now says in §6 and §8 that 46–82°N is the forest-expansion band (where LCC land cover differs). Only text was changed; the results are unchanged.

**Found:** the compounds are simply every prescribed emission in the model setup. Some other background inputs are not shown: methane and other greenhouse gases, ocean organic particles, lightning NOx.

**Open-next:** reload the notebook in Jupyter before saving it. Optional: add the methane values and a short table on what each compound does.

**Files changed:** `diagnostics/background-aerosol-pd-fut/background_aerosol_pd_fut.ipynb` (text only).

## 2026-11-15 · 19:14 → 19:15 (1 min) · session 6ce7bd45

**Goal:** understand why the background-aerosol notebook averages over 46–82°N.

**Done:** answered only; nothing changed.

**Found:** 46–82°N is the band where the LCC land cover differs from CTRL (the forest-expansion area). The Arctic (>66.5°N) is already a separate region in the same notebook.

**Open-next:** add a 45–90°N region if you want it.

**Files changed:** none.

## 2026-11-15 · 19:00 → 19:05 (5 min) · session 91ef3258

**Goal:** a workflow picture of the MEGAN exact split (LMDI) that also explains the reasons for each step.

**Done:** new figure `docs/workflows/workflow_MEGAN_LMDI_logic.png` (10 steps, each with a "WHY" line) and its script `docs/workflows/draw_workflow_MEGAN_LMDI.py`.

**Found:** nothing new; the status box shows the state at 19:00 (PD finished, FUT batch 1 started).

**Open-next:** none from this block.

**Files changed:** `docs/workflows/workflow_MEGAN_LMDI_logic.png`, `docs/workflows/draw_workflow_MEGAN_LMDI.py` (both new).

</div>

<div style="color:#999999">

## 2026-11-15 · 18:41 → 18:56 (15 min) · session 6509e9d2

**Goal:** find what can safely be removed from the project folder (look only).

**Done:** size check of every folder; explained `results/*-designB-standin-20261111/`.

**Found:** caches ~1.7 GB (rebuilt on demand); old figure sets ~1.8 GB; git 3.8 GB. The design-B stand-in folders (573 MB, not in git) are the automatic copy of `results/figures` and `results/tables` made on 11 Nov just before the analysis switched to the real LCC_FUT_fBVOClccFUT run.

**Open-next:** delete or move anything only after your OK, and after the other session's notebook runs finish.

**Files changed:** only these logs.

</div>

<div style="color:#555555">

## 2026-11-15 · 18:53 → 19:41 (48 min) · session fc06b4b6

**Goal:** run MET and the 12 nudged runs on to 2040, automatically, then redo processing and analysis.

**Done:** plan approved (one met folder 2000–2040, user choice). Folder renamed, old name kept as a link; the folder check passed. Scripts for the folder build, the MET continuation, the 3 run phases, the watcher and the 2001–2040 analysis are written and checked (all 12 runs pass the phase-A check). Workflow record `docs/met-nudg-2026-2040.md`. **MET submitted 18:59** (jobs 1803953 / 1803954).

**Found:** 3 MET jobs of 5 yr would stop at 2041-01-01, one day short, so MET runs 3 × 6 yr instead. MET's bad-node list missed 2 nodes; fixed.

**Open-next:** **start the watcher (you; blocked for me)**, before MET job 1 ends (~21 h after it starts). Then CLAUDE.md / run list / README updates. MET + nudged runs 2026–2040 (open since 11 Nov) in progress.

**Files changed:** `cases-scripts/cases-setup.sh`, `extend_nudg_runs_2015-2025.sh`, `run_when_done/extend_24g_2015-2025_when_done.sh`, `preprocess/nudging/{regroup_met_ext_days,check_nudging_dir}.py`; new `cases-scripts/12e-NF2000norbc_tropstratchem_met_ext_2026-2040_f19_f19.sh`, `extend_nudg_runs_2026-2040.sh`, `run_when_done/{met_nudg_2026-2040,analysis_2001-2040}_when_done.sh`, `preprocess/nudging/build_met_folder.sh`, `build_met_2000-2040_job.sh`, `docs/met-nudg-2026-2040.md`; shared met folder renamed + link; MET case settings (backups `*.before_2026-2040`).

</div>

<div style="color:#999999">

## 2026-11-15 · 18:39 → 18:43 (4 min) · session 08562175
**Goal:** remove the old temporary folder `analysis-2001-2019/`.

**Found:** its 6 Nov preparation had failed, so it held no data or figures; nothing depended on it.

**Done:** folder deleted (your OK); mentions removed from `.gitignore`, `CLAUDE.md`, `analysis/README.md`, `postprocess/run_all_parallel.sh`.

**Open / next:** commit the deletion.

**Files changed:** the four files above; `analysis-2001-2019/` removed.

</div>

<div style="color:#999999">

## 2026-11-15 · 17:54 → 18:56 (62 min) · session 7559c0c6

**Goal:** suggest commits for the ~600 uncommitted changes, then make them.

**Done:**
- 11 commits on `main` (not pushed): 2 code fixes, `.gitignore`, analysis reruns, results 2001–2014 → 2001–2025, 2 diagnostics, watcher scripts, pptx builders, docs (commits open since 2026-11-09 16:46).
- `.gitignore`: the 2001–2014 and design-B archive folders (~1.2 GB) stay local; `cicero_template.pptx` is now in git.

**Found:** another session is rerunning `artefact-corrected-split` and `cumulative_radiative_decomposition` and started `megan-lmdi-vs-approx.ipynb`, so those were left out.

**Found (push):** GitHub refused the push: `analysis/radiative_forcing.ipynb` is 112 MB (130 embedded figures; limit 100 MB). It is the only file over the limit. Re-encoding the embedded figures as 256-colour PNGs brings it to ~42 MB; quality check done: no visible difference (average change < 1 % of a colour step range, side-by-side crop identical by eye).

**Done (push fix):** you chose “shrink + keep it small”. New `results/tables/logs/shrink_nb_images.py`; `run_nb_inplace.py` now shrinks notebooks over 20 MB after each run. 10 notebooks shrunk (radiative_forcing 112 → 42 MB, others now 8–17 MB). Commit `3e643af` rewritten with the 3 shrunk analysis notebooks (now `fccaeb8`; later commits, incl. your “final palette”, re-hashed, content unchanged); the other 7 in a new commit. No file over 50 MB left in the push.

- Held-back notebooks committed after their runs finished: `artefact-corrected-split` + `cumulative_radiative_decomposition` (design A and B side by side) with outputs; `artefact-corrected-split` shrunk 68 → 26 MB.
- `analysis-2001-2019/` removal (done by another session with your OK) committed.
- **Pushed to GitHub** (`origin/main` = `9ce308c`).

**Open-next:** other sessions' uncommitted work stays out (MET 2026–2040 scripts, nudging scripts, `megan_maps.py`, `megan-lmdi-vs-approx.ipynb`, `check_reduced_vs_raw.py`).

**Files changed:** `.gitignore`, git history, these logs.

</div>

---

<div style="color:#AAAAAA">

## 2026-11-15 · 16:57 → 19:51 (174 min) · session 1b77ec0b

**Goal:** status; then design A/B notebooks, Methods update, MEGAN questions.

**Done:**
- Switch to design A finished (open since 2026-11-11 12:33).
- Design A and B side by side in `artefact-corrected-split` and `cumulative_radiative_decomposition` (design-B notebooks open since 2026-11-11 12:33); running.
- Exact vs approximate MEGAN comparison done (open since 2026-11-03).
- MEGAN raw files checked (open since 2026-11-07): all 6 PD years match the reduced files exactly, and re-reducing July 2005 from the raw files gives a bit-identical result.
- FUT MEGAN batches launched (open since 2026-11-07).
- LMDI vs approximate comparison done (open since 2026-11-07).
- ANN season bug in `megan_maps` fixed. LMDI-vs-approx notebook written (LMDI comparison open since 2026-11-07); running.
- Methods outline rewritten (open since 2026-11-11, plan #29); "main FUT emission source" and journal no longer on hold (open since 2026-11-02).
- Ghan figure title bug fixed.

**Found:** NIRD read errors since ~17:10 (files fine, mount flaky). FUT runs keep restarts only at 2005/2010/2015, like PD.

**Open-next:** design-A notebook results → δ intervals in the Methods; your OK for: MEGAN raw deletion, LMDI comparison notebook, FUT MEGAN batches; runs 2026–2040 → plan in another session; `main.tex` tables.

**Files changed:** `analysis/artefact-corrected-split.ipynb`, `analysis/cumulative_radiative_decomposition.ipynb`, `analysis/megan-lmdi-vs-approx.ipynb` (new), `postprocess/megan_lmdi/check_reduced_vs_raw.py` (new), `src/.../plotting/forcing_maps.py`, `boreal-forest-expantion-draft/methods-claude.tex`, these logs.

</div>

---

<div style="color:#7B2FBE">


<div style="color:#999999">

## 2026-11-15 · 16:55 → 16:57 (2 min) · session 111565e9

**Goal:** confirm which colour palette was chosen.

**Done:** checked `plotting/palette.py` and the 3 Nov log: it is option Q1. P was the same palette but with a paler red (`#C4524E`); Q uses `#BC423E`, with gold for totals.

**Files changed:** none (logs only).

</div>

<div style="color:#999999">

## 2026-11-11 · 15:41 → 15:54 (13 min) · session 0e06cada

**Goal:** order the plan files by date, mark what is on hold, keep it updated automatically.

**Done:**
- `~/.claude/plans/INDEX.md`: 31 plans by date with status.
- New hook `~/.claude/hooks/plans_index.py`: each time a plan is written, the list is re-sorted and new plans are added as "new, status not set".
- The top of `INDEX.md` now explains what updates by itself and what is set by hand.

**Found:** 3 plans still open: Methods rewrite (not started), MET + nudged runs 2026–2040 (not started), MEGAN comparison + FUT batches (raw deletion on hold).

**Open-next:** nothing new.

**Files changed:** `~/.claude/plans/INDEX.md`, `~/.claude/hooks/plans_index.py`, `~/.claude/settings.json` (outside the repo).

</div>

---

<div style="color:#555555">

## 2026-11-11 · 12:25 → 12:33 (8 min) · session d23b46ef

**Goal:** process LCC_FUT_fBVOClccFUT to 2025 and switch the analysis to design A; land carbon/water deck; artefact doc; answers on open items.

**Done:**
- Status check: MEGAN batch 2 reduced, all checks pass (open since 7 Nov). LCC_FUT_fBVOClccFUT reached 2025 on 10 Nov.
- `analysis/FBVOC_ARTEFACT.md`: H6 added (open since 9 Nov).
- New deck builder `results/pptx/build_land_carbon_water_pptx.py` (test build OK, 13 slides).

**Found:** the MEGAN comparison needs no raw files. The reduced MEGAN files exist only on NIRD (one copy). Raw MEGAN files on work: ~6.3 TB, purged around mid–late December. `analysis-2001-2019/` was never run and is superseded.

**Open-next:** check the design-A rerun and the deck; decide on the two design-B notebooks; contrasts deck to rebuild after the switch; delete old deck `BOREAL_figures_2001-2025.pptx`?; delete `analysis-2001-2019/`?; MEGAN headline unit.

**Files changed:** `analysis/FBVOC_ARTEFACT.md`, `cases-scripts/run_when_done/designA_24g_when_done.sh`, `cases-scripts/run_when_done/land_pptx_after_designA.sh`, `results/pptx/build_land_carbon_water_pptx.py`, docs logs.

</div>

## 2026-11-09 · 17:10 → 17:23 (13 min) · session cd28f708

**Goal:** conclusions from the C0102 run (weather link or wrong mean?).

**Done:** added a band check and a verdict to section H6 of `fbvoc_artefact_causes.ipynb`, plus an H6 row in the summary; notebook rerun without errors.

**Found:** extra SOA in the prescribed run: real fluxes 0.5 %, 2-year climatology 1.6 %, 14-year climatology 3.0 %. About 2.5 % is the lost weather link; the different mean of 2001–2014 adds ~0 globally (it only moves production between northern bands). The precursors are lifted more the more weather is averaged away (isoprene 0 / 10 / 16 hPa higher in the tropics).

**Open-next:** update `analysis/FBVOC_ARTEFACT.md` if you want.

**Files changed:** `fbvoc_artefact_causes.ipynb` (+ 2 tables in its `_outputs/tables/`), logs.

</div>

<div style="color:#008080">

## 2026-11-09 · 16:42 → 17:55 (73 min) · session c2b27a7c

**Goal:** what background aerosol the FUT runs have; notebook comparing PD and FUT aerosol, precursors and NOx.

**Done:** read the resolved namelists of CTRL_PD and CTRL_FUT; wrote and ran `diagnostics/background-aerosol-pd-fut/background_aerosol_pd_fut.ipynb` (20 figures, 5 tables; summary in its last section).

**Found:** PD = CMIP6 historical emissions of year 2000; FUT = SSP5-8.5 emissions of year 2100, both repeated every year. Fires are prescribed, not interactive. Stratospheric volcanic SO₂ is the same in both (0.53 Tg SO₂/yr). The DMS override in the CTRL_FUT `user_nl_cam` has no effect. Year read: SOx 70.6 → 29.7 Tg S, BC 7.5 → 3.3 Tg C, OM 55 → 42 Tg, NOx 48 → 37 Tg N, NH3 57 → 84 Tg. Model (2001–2014): sulfate burden −39 %, AOD +6 %, surface O₃ +3 %, CO +30 %.

**Open-next:** the AOD increase is not split by component (no extinction AOD per component in the output); other FUT cases' `user_nl_cam` not checked for the same DMS line.

**Files changed:** new `diagnostics/background-aerosol-pd-fut/` (notebook + outputs); `diagnostics/README.md` row. Not committed.

</div>

<div style="color:#CC0000">

## 2026-11-09 · 17:01 → 17:10 (9 min) · session 4eca6534

**Goal:** what to check before deleting the raw MEGAN output.

**Done:** checked the reduction logs and the raw-file sizes.

**Found:** 2001, 2002, 2005 and 2010 are reduced (with the driver swaps) and pass every check. The raw files total about 5 TB; /cluster/work purges them anyway around 18 Dec (batch 1) and 21 Dec (batch 2).

**Open-next:** your call: wait for 2006/2011, run the LMDI-vs-approximate comparison, confirm the monthly output covers every planned figure, then delete (maybe keep one year).

**Files changed:** none.

</div>

<div style="color:#CC0000">

## 2026-11-09 · 16:40 → 16:50 (10 min) · session 4eca6534

**Goal:** status of the runs.

**Done:** checked the queue, watchers and logs.

**Found:** LCC_FUT_fBVOClccFUT (24g) is at Oct 2019; the 2015–2019 piece ends ~18:00 today, then 2020–2025 runs automatically (~27 h, so ~21:00 Tuesday; close to the 30 h job limit). MEGAN batch 2 (2002/2006/2011) finished; 2002 is reduced and passes all checks, 2006 is reducing (~20:30), 2011 next (~2 am). The archive jobs timed out but everything was already archived. C0102 run, postprocessing and notebook are done.

**Open-next:** nothing to decide; raw-file deletion still on hold.

**Files changed:** none.

</div>

<div style="color:#CC0000">

## 2026-11-09 · 16:44 → 16:46 (2 min) · session f963f9be

**Goal:** suggest commits; check the new `results/pptx/` folder.

**Done:** 8-commit plan; checked the moved PowerPoint scripts still work (paths OK).

**Found:** `BOREAL_figures_2001-2025*.pptx` are 101 MB each, over GitHub's 100 MB limit.

**Open-next:** your go-ahead to commit; ignore the `.pptx` decks.

**Files changed:** none in the repo (only Claude's memory note).

</div>

<div style="color:#A84300">

## 2026-11-09 · 16:25 → 17:20 (55 min) · session a0599c5f

**Goal:** status of the land carbon/water notebook.

**Done:** confirmed it finished; final numbers re-checked, unchanged. Showed where plant CO₂ (plant respiration, AR) and the ET maps are. Outputs now go to `results/` (READMEs updated); rerun done, same numbers; old `_outputs/` folder removed.

**Open-next:** add the 9 figures to the PowerPoint builder; nicer titles?; next diagnostic.

**Files changed:** `analysis/land-carbon-water.ipynb`, `analysis/README.md`, `results/README.md`.

</div>

<div style="color:#A84300">

## 2026-11-09 · 13:29 → 13:37 (8 min) · session a0599c5f

**Goal:** finish and check the land carbon/water notebook.

**Done:** notebook restarted after the session ended, run OK; all figures and the regional table checked.

**Found:** LCC − CTRL over modified cells, 2001–2025: GPP −373 TgC/yr (PD, −3 %) / −1197 (FUT, −5 %); vegetation carbon +3.8 / +8.3 PgC; net CO₂ flux ≈ 0 (PD) / +50 TgC/yr source (FUT); ET +2.5 / +2.0 mm/yr, from ground evaporation. FUT runs are a net CO₂ source on their own (+61 CTRL, +111 LCC TgC/yr): land maybe not in equilibrium (to check).

**Open-next:** decide whether the figures go into `results/figures/`; pick extra diagnostics from the suggestions.

**Files changed:** `analysis/land-carbon-water.ipynb` (new) + `analysis/land-carbon-water_outputs/`.

</div>

<div style="color:#A84300">

## 2026-11-09 · 13:18 → 13:25 (7 min) · session a0599c5f

**Goal:** plot land variables (GPP, ET, CO₂ from vegetation) and suggest others.

**Done:** new notebook `analysis/land-carbon-water.ipynb` (carbon grid, ET-split grid, regional table, seasonal cycle), running.

**Open-next:** check the figures; decide whether they go into `results/figures/`.

**Files changed:** `analysis/land-carbon-water.ipynb` (new).

</div>

<div style="color:#A84300">

## 2026-11-09 · 08:55 → 09:38 (43 min) · session d7d2f7b6

**Goal:** the figures PowerPoint in your CICERO template; then separate ones for the MEGAN factors and for `simulation-contrasts.ipynb` (2001–2025).

**Done:** `results/BOREAL_figures_2001-2025_CICERO.pptx`: 269 slides with your template's layouts, colours, fonts, logo and page numbers; all 260 figures, including the 10 new artefact maps. `results/BOREAL_MEGAN_factors_2001-2014_CICERO.pptx`: 46 slides, all 38 MEGAN figures (factors, attribution, fields per run, lake-fix check). `results/BOREAL_simulation_contrasts_2001-2025_CICERO.pptx`: 12 slides, the 9 contrast figures with the row explanations. Scripts to rebuild: `results/build_contrasts_pptx.py`, `results/build_figures_pptx.py`, `results/build_megan_pptx.py` (shared template code in `results/cicero_pptx.py`).

**Found:** the template's chapter page has very large text (50 pt), so the section intros are set to 20 pt. The MEGAN factor maps exist only for 2001–2014. `simulation-contrasts.ipynb` was already on 2001–2025 (run 05:41–06:04, inputs unchanged since), so it was not rerun.

**Open-next:** can the old deck (`results/BOREAL_figures_2001-2025.pptx`, own colours, 250 figures) be deleted? Run `megan_factor_maps.ipynb` on 2001–2025 if you want the MEGAN deck on the longer period.

**Files changed:** `results/BOREAL_figures_2001-2025_CICERO.pptx`, `results/BOREAL_MEGAN_factors_2001-2014_CICERO.pptx`, `results/build_figures_pptx.py`, `results/build_megan_pptx.py`, `results/BOREAL_simulation_contrasts_2001-2025_CICERO.pptx`, `results/build_contrasts_pptx.py`, `results/cicero_pptx.py` (all new); `results/cicero_template.pptx` (yours, uploaded).

</div>

<div style="color:#A84300">

## 2026-11-09 · 08:08 → 08:20 (12 min) · session d7d2f7b6

**Goal:** a PowerPoint with all figures, ordered as a story, to download.

**Done:** `results/BOREAL_figures_2001-2025.pptx`: 259 slides, all 250 figures in `results/figures/`, 6 sections with subsections (PowerPoint sections), file path on every slide. Script to rebuild: `results/build_figures_pptx.py`.

**Found:** —

**Open-next:** rebuild the deck after the `artefact-corrected-split` rerun (new FUT maps).

**Files changed:** `results/BOREAL_figures_2001-2025.pptx` (new), `results/build_figures_pptx.py` (new).

</div>

<div style="color:#7B2FBE">

## 2026-11-09 · 07:31 → 08:50 (79 min) · session daa384fc
**Goal:** find the forcing-decomposition maps after the reorganisation; make them also for FUT with PD emissions (ctrlPD, lccPD), 2001–2014 and 2001–2025; split them by colour scale.

**Done:**
- 24 new maps: FUT with ctrlPD and lccPD emissions, NET/SW/LW, two colour scales, 2001–2014 and 2001–2025.
- All forcing-decomposition maps now in `design-B-split/individual-scale/` and `design-B-split/split6-2/` (in `results/figures/artefacts/` for 2001–2025 and `results/figures-2001-2014/artefacts/` for 2001–2014). `artefact-corrected-split.ipynb` writes there from now on (code changed, not rerun); `results/README.md` updated.

**Found:** FUT, 45–90°N, NET: corrected BVOC effect −1.00 W m⁻² (ctrlPD) and −0.99 (lccPD) for 2001–2014; −0.98 (lccPD) for 2001–2025. Both mostly measure FUT vs PD emissions, not the forest expansion.

**Done (you OK'd 08:06):** ctrlPD/lccPD added back to `artefact-corrected-split.ipynb`; rerun 2001–2025 OK (new Ghan + context maps, table columns). FUT, 45–90°N, NET, 2001–2025: −0.98 W m⁻² (ctrlPD and lccPD) vs −0.03 (ctrlFUT).

**Open-next:** 2001–2014 Ghan/context maps and tables for ctrlPD/lccPD not made (only the forcing maps).

**Files changed:** `analysis/artefact-corrected-split.ipynb` (cells 7–8), `results/README.md`.

</div>

---

<div style="color:#AAAAAA">

## 2026-11-09 · 07:29 → 07:31 (2 min) · session 58a36ed1
- You asked to split results by period. Done: `figures/`, `tables/` = 2001–2025; `figures-2001-2014/`, `tables-2001-2014/` = 2001–2014. README updated.

---

## 2026-11-09 · 07:26 → 07:50 (24 min) · session 880cb2fa
**Goal:** Status check, then rerun the 2 failed 2001–2025 notebooks.

**Done:**
- Checked runs and overnight jobs.
- Fixed `timeseries-responses` (it now picks the longest processed file when the 2001–2014 and 2001–2025 files are both there).
- Reran both, one after the other: both OK (07:31, 07:48). All 9 analysis notebooks now cover 2001–2025.

**Found:** at ≥45°N the total is +1.32 ± 0.17 W m⁻² over 2001–2025 (it was +1.19 over 2001–2014). The corrected BVOC step is smaller, −0.03 ± 0.03 (it was −0.06 ± 0.05).

**Open / next:** commit the fix; update the notebook text to the 2001–2025 numbers.

**Files changed:** `analysis/timeseries-responses.ipynb`, both logs

---

</div>

<div style="color:#E58AA5">

## 2026-11-09 · 01:20 → 02:11 (51 min) · session e02674e3

**Goal:** compare rows of the contrast grids: same colour scale in each column.

**Done:** new option in the grid code: one scale per column (largest row), reduced by the smallest 2/5/10… step only where a row would show nothing, marked "scale ÷N". Default unchanged.

**Found:** works on all 4 context grids; the big rows (LCC_FUT − CTRL_PD, CTRL_[FUT − PD], LCC_[FUT − PD]) now share one scale and look alike, the LCC − CTRL rows are ÷2 to ÷50.

**Done:** your OK; row-uniform ÷N added; overnight job launched to make it the default (plus a cap so noisy panels aren't over-amplified), rerun the 4 grid notebooks and snapshot the 2001–2014 figures.

**Open-next:** check `/cluster/work/users/adelez/colscale-rerun/run.log` in the morning (4 × rc=0, ALL DONE), then commit.

**Files changed:** `src/boreal_forest_expansion/plotting/forcing_maps.py`, new `sandbox/test_column_scale.py`.

</div>

<div style="color:#5B2A86">

## 2026-11-09 · 00:28 → 01:16 (48 min) · session 650b1073

**Goal:** commit the results reorganisation; then fix the refused push.

**Done:** reorganisation files staged (you committed them as 1f91e79). The push failed because `radiative_forcing.ipynb` was 109 MB (GitHub limit 100 MB). Its inline figures are now stored as 256-colour PNGs: same look, file now 43 MB. Backup of the original in the session scratchpad.

**Open-next:** you run `git add analysis/radiative_forcing.ipynb && git commit --amend --no-edit && git push` (I am not allowed to amend). The 2001–2025 rerun will make this notebook big again: decide whether to shrink it automatically.

**Files changed:** `analysis/radiative_forcing.ipynb` (inline images only), logs.

</div>

<div style="color:#008080">

## 2026-11-08 · 23:55 → 01:42 (108 min) · session 6fa0a97f

**Goal:** check and explain `diagnostics/fbvoc-prescription-artefact/fbvoc_artefact_causes.ipynb`; fix its caption; add a figure on how the SOA lifetime gets longer.

**Done:**
- Notebook confirmed up to date (last run 7 Nov).
- Caption corrected (replay result added, convection idea marked untested).
- Sign checked with the raw numbers: prescribed 2.512 vs interactive 2.438 mg m⁻² SOA; figure labels now say which run has more.
- New run `CTRL_PD_fBVOCctrlPD_C0102` set up and launching automatically (opened in this block); notebook section H6 ready for it.
- New section + figure `mechanism_soa_lifetime.png` (4 panels: tropical profiles, height shift, SOA by band and layer, cause chain); notebook rerun, no errors.

**Found:** the interactive run has 3 % less SOA than the prescribed one (A = −3.03 %). Same emissions and production; in the prescribed run precursors sit higher (tropics: isoprene mean height +16 hPa higher, +18 % at 400–100 hPa), SOA forms higher and lives longer (7.02 → 7.24 days). OH and O₃ unchanged; replay run ≈ CTRL_PD. Why the precursors go up (convection on cloudy days) is still a guess.

**Open-next:** C0102 run → results in H6 (automatic); commit notebook, `14f` script, watcher, docs.

**Files changed:** `fbvoc_artefact_causes.ipynb` (caption, mechanism section, H6), its `_outputs/`, `cases-scripts/14f-…C0102….sh`, `run_when_done/run_C0102_when_done.sh`, `run_aliases.csv`, `cases-scripts/README.md`, `CLAUDE.md`, logs; new emission files `ems_<CTRL_PD>_2001-2002_*` (shared inputdata).

</div>

<div style="color:#A84300">

## 2026-11-08 · 21:59 → 23:05 (66 min) · session 2e8818ca

**Goal:** correct the contrast pairs in `analysis/simulation-contrasts.ipynb` to the user's list.

**Done:**
- Artefacts on LCC land now LCC_P − LCC_P_fBVOCctrlP; CTRL ones unchanged.
- Fig. 3b row 2 → LCC_FUT_fBVOCctrlPD − CTRL_PD_fBVOCctrlPD.
- CTRL_FUT_fBVOCctrlPD question closed: no longer needed in this notebook (open since 2026-11-07).
- Fig. 2: LCC_FUT_fBVOClccFUT replaced by design B (LCC_FUT − CTRL_FUT + CTRL_FUT_fBVOCctrlFUT) until 24g is processed; switches by itself after.

- Rerun done: all 9 figures, no errors.
- Row names on the left in short form (your list); Fig. 3b third row = row 2 − row 1 (same as Fig. 3a row 1).

- **Reorganisation (22:36):** 4 categories (interactive, fBVOC, non-BVOC, artefacts) as the only contrasts; shared definition in `forcing_maps.CONTRASTS`; old results archived; topic notebooks rewritten and rerunning.

- All other notebooks switched (cumulative, PD–FUT attribution, FUT emission source, artefact split, simulation contrasts); READMEs and CLAUDE.md updated.

**Found:** cumulative decomposition with the artefact removed: ≥45°N non-BVOC +0.26 ± 0.04 W m⁻² (was +0.17), corrected BVOC −0.06 ± 0.05 (was +0.03).

**Open-next:** check the reruns (errors, figures); texts/findings of PD–FUT attribution, FUT emission source and artefact split still describe the old contrasts; replace the design-B stand-in when LCC_FUT_fBVOClccFUT is processed (`LCC_FUT_FBVOCLCCFUT_DESIGN_B = False`).

**Files changed:** `analysis/*.ipynb`, `src/boreal_forest_expansion/plotting/forcing_maps.py`, `results/` (archived + new category folders).

</div>

<div style="color:#7B2FBE">

## 2026-11-08 · 21:57 → 22:30 (33 min) · session 4a626602

**Goal:** split the uncommitted work into commits and commit it.

**Done:** 6 commits in BOREAL-FOREST-EXPANSION (artefact sign flip, simulation-contrasts notebook, 2001–2019 set, BVOC emission plots, D1 far-field check, docs) and 1 in the draft repo (`methods-claude.tex`). Nothing pushed.

**Open-next:** `git push` in both repos (your call). New since 22:03: contrasts-notebook pair fix and BVOC plots, both rerunning → commit when done.

**Files changed:** none (commits only; these logs).

</div>

<div style="color:#62733B">

## 2026-11-08 · 21:46 → 23:23 (97 min) · session c46e88fa

**Goal:** time series of ISOP and MTERP emissions for each pair of runs in your list.

**Done:** new notebook `preprocess/bvoc-emissions/plot_bvoc_timeseries.ipynb`, run, outputs saved. After your corrections: LCC-modified cells only, pairs fixed (section 3 last pair, art_LCC_PD/art_LCC_FUT now against the ctrl emissions), one vertical scale for all panels. 2 figures (ISOP, MTERP), 19 pairs in 4 rows, plus a table. New colours: red/navy for LCC or *lcc* emissions, orange/teal for CTRL or *ctrl* emissions (FUT red/orange, PD navy/teal), fixed BVOC dashed. Figures saved as PNG in `plot_bvoc_timeseries_outputs/`.

**Found (modified cells):** non-BVOC pairs have identical emissions (Δ = 0, same prescribed file). art_LCC_PD ISOP +0.24 Tg/yr (+5.9 %), art_LCC_FUT +0.37 Tg/yr (+3.0 %): this is the LCC − CTRL emission change, since those prescribed runs use CTRL emissions. art_CTRL_PD and art_CTRL_FUT: +0.05 %. CTRL_FUT − CTRL_PD ISOP +8.4 Tg/yr (+203 %).

**Open-next:** switch LCC_FUT_fBVOClccFUT to its processed file when 24g is done and postprocessed, then rerun.

**Files changed:** `preprocess/bvoc-emissions/plot_bvoc_timeseries.ipynb` (new), `preprocess/bvoc-emissions/plot_bvoc_timeseries_outputs/` (new, 2 PNG).

</div>

<div style="color:#62733B">

## 2026-11-08 · 21:47 → 23:09 (82 min) · session da0cb87f

**Goal:** bring the BVOC emission plotting notebook to the new simulations (your OK: yes to all).

**Found:** it still read the old-chain CTRL emissions (`-20261023`).

**Done:** the notebook now reads CTRL_PD `-20261029`, CTRL_FUT, LCC_PD and LCC_FUT `-20261028`; new section with LCC − CTRL maps north of 45°N; seasonal plots show all four sources. The totals table gains the LCC columns and the % change LCC vs CTRL; the species notebook and the folder README follow.

**Found (new totals, ≥45°N, LCC vs CTRL):** isoprene +3.1 % PD / +1.7 % FUT; monoterpenes +0.7 % / −0.3 %. In the changed cells, the light alkenes, CO and similar species drop by about 5 % (PD) and 8 % (FUT). The new CTRL totals are within 1.4 % of the old-chain ones.

**Done (23:09):** both notebooks reran without errors.

**Open-next:** commit when you want.

**Files changed:** `plot_bvoc_emissions.ipynb`, `bvoc_species_processes.ipynb`, `bvoc_totals_tg_per_yr.csv` (by the rerun), `README.md` in `preprocess/bvoc-emissions/`; the two logs.

</div>

<div style="color:#999999">

## 2026-11-08 · 22:34 → 23:04 (30 min) · session 4f89c2b2

**Goal:** confirm batch 2 started; are all runs done to 2025? Then process the 11 nudged runs for the analysis (your request).

**Done:** batch 2 is running (all 6 jobs since about 21:10). The 11 nudged runs are being processed for **2001–2025** (all 19 categories, same code as for 2001–2014), started 22:40, expected to take 3–4 hours. Files go to a staging folder on NIRD: `data/processed-data/postprocessing-2001-2025-staging/`.

**Found:** all 11 runs have the complete raw output (Jan 2000 – Dec 2025). LCC_FUT_fBVOClccFUT is at Aug 2014 and should reach 2026 around 11 Nov.

**Open-next:** when processing ends, check it against the 2001–2014 files and move the new files next to them (the 2001–2014 files stay). then, automatically: switch 9 analysis notebooks to 2001–2025 (your decision, 22:58: early 2001–2014, late 2015–2025; LCC_FUT_fBVOClccFUT = design B) and rerun them overnight, after the reorganisation reruns. Script `cases-scripts/run_when_done/analysis_2001-2025_when_done.sh`; result in `/cluster/work/users/adelez/analysis-2001-2025/SUMMARY.txt`. Afterwards: the notebooks' written conclusions still quote 2001–2014 numbers. The reorganisation window confirmed (23:04) that the plan fits its changes and that it starts no more runs.

**Files changed:** the two logs; new staging folder on NIRD; new script `cases-scripts/run_when_done/analysis_2001-2025_when_done.sh` (uncommitted). Overnight it will change the year lines of 9 notebooks and `forcing_maps.py`.

</div>

<div style="color:#999999">

## 2026-11-08 · 21:04 → 21:04 (0 min) · session 4f89c2b2

**Goal:** start MEGAN batch 2 (your request).

**Done:** the plan check passed, and batch 2 (2002, 2006, 2011, raw files kept) was relaunched at 21:05 with the same launcher as batch 1.

**Open-next:** (done 22:37) jobs queued, watcher started. Each year then takes about 14 h of model time, plus the reduction.

**Files changed:** the two logs; new launch log in the work folder.

</div>

<div style="color:#999999">

## 2026-11-08 · 12:51 → 12:55 (4 min) · session 4f89c2b2

**Goal:** status of the runs and what is open.

**Done:** checked every chain. Nothing changed.

**Found:** MEGAN batch 1 is fully reduced (2001, 2005, 2010 + swaps). **Batch 2 did not start:** on 7 Nov at 09:09 the auto-launcher saw a CTRL 2005 archive job still in the queue, refused, and stopped without retrying. It would pass now. The 11 nudged runs reached 2026 and are archived. LCC_FUT_fBVOClccFUT is at Sep 2011 (segment 2011→2016, ends ~03:00 Monday), then it extends by itself to 2026.

<span style="background:#CC0000;color:#FFFFFF;padding:0 4px;border-radius:3px">**WAITING ON YOU**</span> <span style="color:#CC0000">**Open / next:** relaunch MEGAN batch 2 (2002, 2006, 2011)? On hold: deleting the batch-1 raw files, main FUT fBVOC source, journal, location for the 2001–2019 analysis.</span>

**Files changed:** the two logs.

</div>

<div style="color:#7B2FBE">

## 2026-11-07 · 00:33 → 01:30 (57 min) · session cb4be630

**Goal:** use one sign everywhere: artefact = interactive − prescribed.

**Done:** docs, Methods outline, code comments and notebook text/code updated; the BVOC values stay the same.

**Then:** you OK'd the reruns and deleting old files; old-chain cause notebooks flipped too; all 7 reruns OK, old files deleted.

</div>

<div style="color:#A84300">

## 2026-11-07 · 00:13 → 01:08 (55 min) · session eff577b5

**Goal:** one notebook with all simulation contrasts, one figure per question.

**Done:** `analysis/simulation-contrasts.ipynb` (9 map grids, same layout as the FUT artefact notebook without liquid water path); missing rows now shown as PENDING instead of being dropped (your remark on Fig. 2); third row = row 2 − row 1 in Figs. 1b, 1c, 3a, 4b, with its own colours.

**Found:** CTRL_FUT_fBVOCctrlPD does not exist; LCC_FUT_fBVOClccFUT still running.

**Open-next:** decide on CTRL_FUT_fBVOCctrlPD; check artefact definitions; rerun when LCC_FUT_fBVOClccFUT is processed.

**Files changed:** `analysis/simulation-contrasts.ipynb`, `analysis/simulation-contrasts_outputs/`, `analysis/README.md`.

</div>

<div style="color:#A84300">

## 2026-11-07 · 00:10 → 00:25 (15 min) · session 83498e52

**Goal:** speed up the FUT emissions notebook and D1 (your OK), hatch non-significant cells in D1 maps (your OK), finish the FUT rerun and write its conclusions.

**Done:** D1 dots → hatching of non-significant cells (open since 6 Nov 20:40). Loader speed-up in both notebooks (open since 6 Nov 21:25): FUT ~5 min, D1 ~4 min, D1 numbers unchanged. FUT emissions notebook runs to the end; conclusion text of §10 and §14–17 rewritten with the new numbers (open since 3 Nov).

**Found:** the FUT notebook's last section kept failing because of a too-strict tolerance for cloud droplet numbers (~10¹⁰), not the float32 issue. Forest expansion ≥45°N in FUT: isoprene +0.39 Tg/yr, monoterpenes −0.09 (not significant); corrected radiative effect −0.06 W m⁻² (not significant); artefact as large as the expansion effect for SOA and CDNUMC.

**Open-next:** nothing on these three items.

**Files changed:** `diagnostics/2_FUT-fBVOC-background-lcc-effect-decomposition/bvoc_emissions_decomposition-after-co2-fix.ipynb` (cells 1, 5, 25, 32, 40, 41), `diagnostics/2_other-BVOC-emission-magnitude/D1_farfield_check.ipynb` (cells 1, 6, 16, 23), logs.

</div>

<div style="color:#A84300">

## 2026-11-07 · 00:07 → 00:12 (5 min) · session dc82b504

**Goal:** list what is waiting on your decision; act on your answers.

**Done:** listed the open decisions. MEGAN batch 2 OK (open since 2026-11-06 17:55): set to launch by itself once batch 1 is reduced.

**Found:** batch 1 still running (2001 both runs, CTRL 2005); 2010 re-reduced with the swaps, all checks pass.

**Open-next:** batch 2 starts automatically (estimate Saturday midday). On hold: raw-file deletion, main FUT fBVOC emission source, target journal. Later: LMDI vs approximate split.

**Files changed:** the two logs; new waiter script in the work folder (not in the repo).

</div>

<div style="color:#999999">

## 2026-11-06 · 21:54 → 22:30 (36 min) · session fa133924

**Goal:** decide what to commit.

**Done:** proposed 8 grouped commits; explained which edits are only renamed paths in text and which are code; picked the 6 ready now; you committed them, I committed the last 3 (images, `run_all_parallel.sh`, `CLAUDE.md` + `.gitignore`), then undid them at your request (changes kept).

**Open-next:** your choice of commits.

**Files changed:** the two logs only (`CLAUDE_log.md` restored after being emptied).

</div>

<div style="color:#A84300">

## 2026-11-06 · 21:21 → 21:24 (3 min) · session a3a096fb

**Goal:** write the swaps, explain them, list the unit options.

**Done:** swaps were already done and validated by the other window (21:15); `MEGAN_ATTRIBUTION.md` updated (status, unit table); explanation given.

**Open-next:** your pick of headline unit; batch 2 OK; later delete batch-1 raw files. 2010 re-reduction ends ~01 h.

**Files changed:** `analysis/MEGAN_ATTRIBUTION.md`.

</div>

<div style="color:#CC0000">

## 2026-11-06 · 20:33 → 22:05 (92 min) · session e28a984f

**Goal:** what is `analysis/radiative_forcing_2001-2019.ipynb`; then prepare the 2001–2019 analysis in one folder you can delete.

**Found:** the notebook was a half-finished copy from 5 Nov. All 11 nudged runs have 2000–2019 archived. The notebook shows BVOC effects **without** artefact correction. Its LCC_FUT_fBVOClccFUT row would show LCC_FUT − LCC_FUT_fBVOClccFUT = the artefact on LCC land, not a BVOC effect.

**Done:** `analysis-2001-2019/` (README, run list, `prepare.sh`, notebook moved in and updated). Started 21:23; **failed ~21:55: processed files on home filled the home quota** (my mistake). Stopped and cleaned, home 14.6 GB.

**Open-next:** where to put the processed files (work proposed); design B copy for 2001–2019; fix the design A row; then restart.

**Files changed:** new `analysis-2001-2019/` (all); `analysis/radiative_forcing_2001-2019.ipynb` moved into it; logs.

</div>

<div style="color:#999999">

## 2026-11-06 · 20:32 → 22:40 (128 min) · session 83498e52

**Goal:** status of 7 open items; rerun FUT emissions notebook; zonal-plot colours; fix D1; why the FUT notebook is slow.

**Done:** status check (already done earlier: LCC_PD_fBVOClccPD start-up (open since 3 Nov), radiative_forcing labels (done 4 Nov), push of `main` (open since 3 Nov), design A vs hybrid (decided 4 Nov)). Zonal-mean colours navy / teal / red / orange applied and rerun (open since 3 Nov). D1 duplicate-label error fixed, D1 rerun without errors (open since 3 Nov).

**Found:** FUT notebook slowness = ~2,900 one-by-one opens of raw 104 MB files (0.5–1 s each), same runs reloaded in several cells; D1 loading took 75 min for the same reason. Notebook runs started from a Claude window die when that window closes (3 runs lost). The runner rewrites the whole notebook after every cell, so edits made during a run are lost (this is why one run used old code).

**Open-next:** FUT notebook running in tmux `futnb` since 22:42 → then rewrite its conclusion; faster loader (your OK); D1 maps still mark significance with dots (project rule: hatch non-significant), your call.

**Files changed:** `diagnostics/how-warmer-future-climate-is/how_warmer_future_climate_is.ipynb` (cell 18 colours), `diagnostics/2_other-BVOC-emission-magnitude/D1_farfield_check.ipynb` (cells 3, 16), logs.

</div>

<div style="color:#7B2FBE">

## 2026-11-06 · 20:19 → 21:37 (78 min) · session 28813a15
**Goal:** FUT emission-source notebook: retire the old one, corrected results only, and a separate uncorrected-vs-corrected view.

**Done:**
- Old `analysis/fut-fbvoc-emission-source.ipynb` was uncorrected by design. Its two missing parts (Ghan maps; the `fBVOCctrlFUT − fBVOCctrlPD` row) were ported to `-choice`, then it was moved to `analysis/_old/`; README, 5 notebook links, 2 code comments and CLAUDE.md now point to `-choice`.
- `-choice` now shows **only artefact-corrected** contrasts in every section (emissions, budget, maps, Ghan maps, seasonal chain), plus the emissions-only row (needs no correction) and art_FUT itself.
- New `diagnostics/fbvoc-prescription-artefact/how_big_artefact_is_FUT.ipynb`: the map grid with each **uncorrected row followed by its corrected one**, then emissions-only and art_FUT. When design A is processed it adds its pair automatically (its corrected row = FUT test of the design-B assumption).
- Small code change: monthly regional differences now accept the corrected (combined) reference; checked it equals uncorrected + art_FUT exactly.

- `how_big_artefact_is_FUT.ipynb` ran; figure checked. Example (≥45°N SOA burden): source CTRL_FUT −0.086 → +0.015 mg m⁻² after correction; source CTRL_PD 2.57 → 2.67.
- `-choice` seasonal-chain figure crashed on the corrected reference; fixed in the code.

- `-choice` rerun finished without errors; map grid and seasonal chain regenerated and checked.

**Open-next:** section 6 ("Reading for the decision") of `-choice` is still empty. Nothing committed.

**Files changed:** `analysis/fut-fbvoc-emission-source-choice.ipynb`, new `diagnostics/fbvoc-prescription-artefact/how_big_artefact_is_FUT.ipynb`, `analysis/_old/fut-fbvoc-emission-source.ipynb` (moved), `src/.../plotting/forcing_maps.py`, `analysis/README.md`, `CLAUDE.md`, markdown links in 5 analysis notebooks.

</div>

<div style="color:#999999">

## 2026-11-06 · 20:26 → 21:58 (92 min) · session a54817a0
**Goal:** recap of Wed–Fri; then (your yes, 20:32) write the MEGAN driver swaps into the reduction and test them on the 60-day pair.

**Done:**
- Recap of 4–6 Nov given in chat (from this log).
- MEGAN swap choices: **decided 6 Nov 17:55** (open since 5 Nov 18:27), never written here; box corrected.
- **Swaps written** (open since 4 Nov): new `postprocess/megan_lmdi/megan_swaps.py` + a new version of the reduction (`reduce_megan_lmdi.new.py`; the live script is not touched until the test passes, so the batch-1 watcher keeps using the old one).
- First test, 3 days of the 60-day pair: replayed MEGAN = CLM to 10⁻¹⁵, rebuilt light = CLM to 10⁻¹³, terms add up exactly. Only the very first step of a run cannot be replayed (its previous step is not on the tape): 0.6 % of the change over 3 days, ≈ 0.03 % over 60 days.
- **July 2010 test (3 days) passed every check**, nothing flagged (carry-over from 30 June works). Plausible: plant cover ≈ LMDI composition, leaf temperature ≈ γT, canopy ≈ γL + γA (isoprene +2.90 vs +2.89).
- **60-day test passed every check** (replay = CLM to 10⁻¹⁵; only the first step of the run is flagged, 0.03 % of the change). The LMDI part is bit-identical to the earlier file.
- **New reduction now live** (21:15); the 60-day output rewritten with the swaps. Batch-1 years reduced from now on (2001, 2005) get the swaps automatically.
- **2010 re-reduction started** from its kept raw files (login-3, ≈ 3.5 h, nothing deleted); at 21:24 day 16 of 365, ends ≈ 00:45. How to check it: commands given in chat (log progress, PASS lines, quick totals). Whole reduction chain explained in chat (scripts, files, current plan).
- Docs: `postprocess/megan_lmdi/README.md` (method, output, tests), status in `analysis/MEGAN_ATTRIBUTION.md`.

**Open / next:** check the 2010 re-reduction (~00:45); then batch 2 (2002, 2006, 2011) **needs your OK**; deleting batch-1 raw files after re-reduction: your call.

**Files changed:** new `postprocess/megan_lmdi/megan_swaps.py`; `reduce_megan_lmdi.py` (swaps added), `postprocess/megan_lmdi/README.md`, `analysis/MEGAN_ATTRIBUTION.md`; `data/processed-data/megan-lmdi/megan_lmdi_PD_test60d.nc` (rewritten); both logs.

---

</div>

<div style="color:#7B2FBE">

## 2026-11-06 · 20:16 → 20:17 (1 min) · session 28813a15
**Goal:** add the artefact-corrected (design B) contrasts to the maps in the FUT fBVOC emission source notebook.

**Done:**
- Checked: in `analysis/fut-fbvoc-emission-source-choice.ipynb` only section 2 (radiative budget) was corrected; the maps (section 3), emissions (section 1) and seasonal chain (section 4) are uncorrected.
- Section 3 figure now has three blocks of rows: uncorrected per source, **corrected per source (design B: uncorrected + art_FUT)**, then art_FUT. When design A (`LCC_FUT_fBVOClccFUT`) is processed it adds its own two rows automatically; its corrected row tests the design-B assumption.
- Notebook re-running so the new figure is saved in it.

</div>

<div style="color:#999999">

## 2026-11-06 · 18:02 → 20:46 (164 min) · session ffd2d7c5
**Goal:** MEGAN case names; your OK to resubmit CTRL_PD 2005 and fix the LCC_FUT_fBVOClccFUT climatology.

**Done:**
- Listed the MEGAN case names. Renaming the LCC 2010 case to 20261105: possible in principle but not worth it (it has already run and been reduced; the scripts store the pairs by full name).
- **CTRL_PD 2005 resubmitted** (job 1791950, ~15 h + queue), avoiding the node where it failed.
- **Climatology fix: left to another session** that was already doing it (it is re-cutting pieces 2–3 to the CTRL convention, 1,300 of 1,825 files done at 18:10). I sent it what it needs to restart LCC_FUT_fBVOClccFUT. One of the two open windows replied that it is not that session; the other (adelez-d4 = last night's session 570e9150) confirmed it owns the fix and took the notes.
- Explained what went wrong in the climatology: pieces 1 and 2–3 cut the days of half-hourly data 30 min apart; the script refuses to average years cut differently. My fix would have re-cut piece 1; the other session re-cuts pieces 2–3 to match the CTRL runs, which is the better choice.
- Checked: every other run whose emissions are prescribed is one continuous run started in 2000 and cuts days 00:00–23:30. Only the two branch pieces of the LCC_FUT rerun differ.
- Why the rerun was split in 3 (decided 4 Nov night, your OK): to finish ~2 days faster, and LCC_FUT only kept restart files for 2005 and 2010. In hindsight the two branch pieces caused two setbacks (a crash at start, ~13 h, and this climatology failure, ~1 day), so no time was gained.
- Your call: keep splitting reruns into parallel pieces. The two pitfalls (each branch piece needs its own nudging start file; branch pieces cut days differently and must be re-cut before the climatology) are saved in my memory for next time.

- 19:44 status: the other session stopped after the re-cut; the re-merge, the 8-species rerun and the watcher restart are still to do.

- LCC_FUT_fBVOClccFUT climatology fix finished by me (re-merge, 8 species resubmitted, watchers restarted).
- `run_aliases.csv` updated (18 rows corrected, 9 added).
- FUT emissions notebook: crash in its last section fixed, rerun started.
- New notebook comparing the three FUT emission sources, running.
- Methods draft: 5 number boxes filled (land-cover change, capped cells, mask, artefact test, artefact size).
- Explained step by step how LCC_FUT_fBVOClccFUT and the MEGAN runs are produced (scripts, file moves, checks).
- New notebook `analysis/fut-fbvoc-emission-source-choice.ipynb` finished; its reading is written (below). The FUT emissions notebook is now rerun and concluded by another session, at your request.
- Drew both workflows as diagrams: `docs/workflows/workflow_LCC_FUT_fBVOClccFUT.png`, `docs/workflows/workflow_MEGAN_LMDI.png`.

**Found (FUT emission source, 2001–2014, ≥45°N, net TOA):** with CTRL_PD or LCC_PD emissions the "BVOC effect" is ≈ −1 W m⁻² but is almost all the future-climate emission increase (+14 Tg isoprene); with CTRL_FUT emissions (forest expansion only) it is ≈ 0 uncorrected and −0.06 ± 0.05 corrected, the same size as the prescription artefact (−0.09). LCC_FUT_fBVOClccFUT will test that artefact on LCC land.

**Open / next:** choose the main FUT emission source (still on hold); 5 number boxes still wait for results (colonisation share, PD vegetation check, PD autocorrelation, MEGAN split closure).

**Files changed:** both logs only.

---

</div>

<div style="color:#CC0000">

## 2026-11-06 · 17:40 → 18:16 (36 min) · session ffd2d7c5
**Goal:** status of the runs and what is open.

**Found:**
- Nudged runs: all 11 reached 2020; 8 already continue to 2026, the other 3 follow when their archives finish.
- MEGAN batch 1: 2000 and 2010 done and reduced; 2001 running (~03 h tonight); **2005 CTRL failed at launch** (Slurm timeout), LCC 2005 done.
- **LCC_FUT_fBVOClccFUT not started**: the emission climatology failed on a time-grouping mismatch between piece 1 and pieces 2–3.

- 18:12: CTRL 2005 has been resubmitted by another session (your OK 18:08), queued as job 1791950. The LCC_FUT_fBVOClccFUT fix is being done by another session too (`rephase_branch_h1.sh`); this session leaves it alone.
- 18:14: two other sessions (0d and d4) each assumed this session runs the rephase script. None of the three does, and its log doesn't say which session started it. **Resolved 18:16:** the owner is session 570e9150 (the 5 Nov conversation, running in parallel); it is doing the whole fix.

**Open / next:** the 4 MEGAN swap choices (open since 5 Nov 18:27).

**Files changed:** both logs only.

---

</div>

<div style="color:#AAAAAA">

<div style="color:#CC0000">

## 2026-11-05 · 17:25 → 18:42 (77 min) · session 570e9150
<div style="color:#555555">

**Goal:** your answers: fix the archives (and automatically from now on), extend the nudged runs to 2025, MEGAN batch 1; then (18:12) LCC_PD_fBVOClccPD extension, LCC_FUT_fBVOClccFUT, batch 1 with raw files kept, decide the swaps.

**Done:**
- Failed archives fixed (open since 5 Nov 15:10): automatic archive guard (`cases-scripts/archive_guard.sh`); all 3 LCC_FUT half-hourly pieces archived, MEGAN test resumed (CTRL job 2 running, LCC being archived). Bad nodes b5203/b5204 excluded everywhere.
- MET extension finished and archived; its watcher bug fixed; the 2000–2025 folder is being built (at Jul 2015, 18:25).
- Nudged extension to 2025 (open since 3 Nov 23:30): automatic, now 11 runs (+ LCC_PD_fBVOClccPD, your OK 18:12); all checked OK.
- LCC_PD_fBVOClccPD to 2014 finished, postprocessed, notebook rerun (16:23).
- LCC_FUT_HRBVOC done and identical to LCC_FUT (open since 4 Nov 01:31); emission climatology running; LCC_FUT_fBVOClccFUT (new script 24g) starts automatically after the checks.
- MEGAN batch 1: starts automatically when the test passes, raw files kept (`--keep-raw`).
- LCC_FUT_fBVOClccFUT also extended to 2025 (your OK 18:34), automatic after its 2000–2014 run.

**Open-next:** your 4 swap choices (saved for later; see the box); then I write the swaps. Batch 2 must also keep raw files unless the swaps are ready.

**Files changed:** new `cases-scripts/archive_guard.sh`, `cases-scripts/24g-…lcc_fBVOClccFUT….sh`, `cases-scripts/run_when_done/{extend_nudg_2015-2025_when_done,run_24g_when_done,extend_24g_2015-2025_when_done,megan_batch1_when_test_ok}.sh`; edited `cases-scripts/extend_nudg_runs_2015-2025.sh`, `megan-lmdi/launch_megan_lmdi.sh`, `megan-lmdi/watch_megan_lmdi.sh`, `preprocess/nudging/met_ext_watch_and_build.sh`, `CLAUDE.md`.

</div>

## 2026-11-05 · 15:05 → 15:10 (5 min) · session 570e9150
<span style="color:#AAAAAA">**Run status check.** Archive jobs fail on node b5204 (6 runs not archived, MEGAN test stuck after 30 days). LCC_PD_fBVOClccPD 2008–2014 finished and archived 15:05. MET piece 2 at Dec 2025. Nothing changed.</span>

## 2026-11-04 · 14:50 → 16:21 (91 min) · session e60507d0
**Goal:** MEGAN exact split: write the production branch script and the batch launcher (your YES, 14:50).

**Done:**
- Branch script, launcher (gated batches), watcher (reduces each year when it is archived, copies the result to NIRD), identity check, per-year reduction job (`cases-scripts/megan-lmdi/`, `postprocess/megan_lmdi/`). Production-script part of "write the code for the per-plant reruns" (open since 3 Nov).
- Tested without running the model: identity check on the old 5-day test, 30-min emissions identical to the parent (6.6 million values, 0 differ); reduction of one year on the 5-day pair, all checks pass; case setup checked against the parent for CTRL_PD (32-day test) and LCC_FUT (2010 chain): same model, only the output differs. Launcher refuses wrong year lists and unfinished earlier batches.

**Found:**
- The four new-chain runs kept restarts only for 2005, 2010 and 2015. Your decisions: don't touch the running LCC_FUT rerun; **change the years to 2005–2008 + 2010–2012**; 32-day test from **2005-01-01**.
- The parent was built with an extra build flag (`CAM_AEROCOM`); the script now copies it, otherwise the branch would not be the same model.
- Your follow-ups (15:56): **restarts** are kept at the end of every year (so of every batch) and now also copied to the NIRD archive (work deletes after 42 days); **2015–2017** added as a third chain from the 2015 restart. It needs the new met data (MET run at mid-2019 now) and, for the identity check, the parents' 2015–2025 extension; the watcher waits for both.
- Your clarification (16:04): the restart at the end of each batch is kept and the next batch continues from it (e.g. a 2005–2006 batch ends with the 2007-01-01 restart). **2000–2003 instead of 2015–2017:** a third chain that starts exactly like the parent runs (from their spin-up); 2000 is only checked and then deleted. Now **10 years: 2001–2003, 2005–2008, 2010–2012**; setup checked against CTRL_PD, same model.
- Test length (16:15): **2 jobs × 30 days** (2 months + 1 day) instead of 32 days, so it also tests continuing a run from its restart, as every production chain does.
- The `preproc` queue is broken today: even trivial jobs hang at start. So the per-year reduction runs on the login node, one year at a time, ≈ 3 h per year. The whole chain was tested there: start, failure, copy to NIRD.

**Done (16:19):** production test started with your OK (2 × 30 days; relaunched 16:18 after my mistake at 16:16); years reduced to 6 (2001–02, 2005–06, 2010–11). **Open-next:** check the test when it ends (status: `bash cases-scripts/megan-lmdi/watch_megan_lmdi.sh PD --check`; it runs detached on login-3, safe to close VS Code); Then the driver swaps (option 1b) before batch 1. After PD batch 1: compare with the current maps for 2005, 2006, 2010.

**Files changed:** new `cases-scripts/megan-lmdi/` (4 files), `postprocess/megan_lmdi/check_identity.py`, `reduce_year_job.sh`; edited `reduce_megan_lmdi.py`, `postprocess/megan_lmdi/README.md`, `analysis/MEGAN_ATTRIBUTION.md`, `CLAUDE.md`.

</div>

<div style="color:#A84300">

## 2026-11-04 · 14:22 → 15:04 (42 min) · session 8e206b5a
**Goal:** add the FUT runs with present-day emissions (fBVOClccPD, fBVOCctrlPD) to the artefact-corrected split.

**Done:** both added, artefact-corrected, to every section of `analysis/artefact-corrected-split.ipynb`; rerun started 14:34; budget section done, closure checks pass.

**Found:** FUT, NET at top of atmosphere, global: corrected BVOC effect with PD emissions ≈ **−1.0 W m⁻²** (lccPD −1.01 ± 0.04, ctrlPD −1.04 ± 0.04), almost all cloud; vs −0.02 ± 0.04 with FUT emissions (ctrlFUT). So the big signal is the climate-driven emission rise, not the forest (lccPD vs ctrlPD differ by only 0.03).

**Open-next:** rest of the rerun (chain table, maps), check new figures; then add your note to the notebook intro: these FUT numbers change with design A (provisional).

**Files changed:** `analysis/artefact-corrected-split.ipynb` (+ outputs in `results/{figures,tables}/artefact-corrected-split/`).

</div>

## 2026-11-04 · 14:20 → 16:52 (152 min) · session ec98f95d

**Goal:** run status; act on your answers.

**Done:**
- LCC_FUT half-hourly pieces 2 and 3 resubmitted (14:30) with the nudging file of their own start date (open since 4 Nov 12:05).
- The run script now does this by itself for branch runs.
- BVOC_A outside the changed cells: **keep design A** (open since 3 Nov 21:00).
- LCC_PD_fBVOClccPD 2008 → 2014 submitted (job 1788254); 2003–2007 archived by hand (archive job died on a bad node) and being postprocessed.
- Contrast-label figures: rerun started, now with LCC_FUT_fBVOClccPD too (open since 3 Nov 19:03).
- Methods: LCC_PD emissions added as option 3 to the FUT-source table; the choice stays on hold.
- Contrast-label rerun finished without errors (15:01).
- LCC_PD_fBVOClccPD 2003–2007 postprocessed and artefact notebook rerun (15:02); 2008 job running.
- `results/` reorganised by contrast (new, 4 Nov 14:56).
- `run_when_done/` moved to `cases-scripts/` (new, 4 Nov 15:37; open since 3 Nov 23:25).
- Figure D in % and section 4f (why LCC_PD − CTRL_PD differ) added to `how_big_artefact_is_PD.ipynb` (new, 4 Nov 16:32).
- Rule for old-chain notebooks changed to "ask first"; two of them got the new watcher path (text only).

**Found:** the LCC_PD_fBVOClccPD extension ends 1 Jan 2008, not 2010.

**Open-next:**
- Check the `artefact-corrected-split.ipynb` rerun (my folder move broke another session's run).
- If the 2014 archive job also lands on a bad node: archive by hand and restart the watcher.
- Methods: FUT emission source (on hold) and journal.

**Files changed:** `cases-scripts/cases-setup.sh`, `cases-scripts/24f-…sh`, `cases-scripts/run_aliases.csv`; case dirs s2/s3 `user_nl_cam`; `analysis/radiative_forcing.ipynb`; `diagnostics/fbvoc-prescription-artefact/run_when_done/run_14e_{extension,to2014}_when_done.sh`; `boreal-forest-expantion-draft/methods-claude.tex`; `src/.../plotting/forcing_maps.py`; 6 analysis notebooks (paths only); `results/README.md`, `analysis/README.md`, `CLAUDE.md`.

</div>

<div style="color:#555555">

## 2026-11-04 · 11:58 → 12:05 (7 min) · session 233c5cc5

<span style="color:#AAAAAA">**Run status check.** Running: MET extension (at 2018-06), LCC_PD_fBVOClccPD extension (at 2007-03, to 2010, ~18 h left), LCC_FUT half-hourly piece 1 (at 2003-04, identical BVOC). Pieces 2 and 3 of the LCC_FUT rerun crashed at start: wrong nudging start file. Nothing resubmitted.</span>

## 2026-11-04 · 00:45 → 01:31 (46 min) · session 84967989

**Goal:** status of LCC_FUT_fBVOClccFUT; start the LCC_FUT rerun with half-hourly BVOC now.

**Found:** LCC_FUT_fBVOClccFUT is not set up. It is needed only if 14e shows that the artefact correction does not hold. LCC_FUT kept restart files only every 5 years (2005, 2010, 2015), so the rerun is split at those years.

**Done:** new script `24f` (alias LCC_FUT_HRBVOC). 3 pieces of 5 years run in parallel; output = the 8 half-hourly BVOC fields + 2 monthly fields to check that it is identical to LCC_FUT. Model and settings checked against LCC_FUT before building (only output and start settings differ). Submitted 01:29 (jobs 1787708, 1787710, 1787712). Merge script for the emission files written.

**Open-next:** after ~1–2 h, compare the first month with LCC_FUT (must be identical); when done, build the emission files. LCC_FUT_fBVOClccFUT itself waits for the 14e verdict.

**Files changed:** `cases-scripts/cases-setup.sh` (new output mode `HR_BVOC_ONLY`), new `cases-scripts/24f-…_lcc_HRBVOC_….sh`, new `preprocess/bvoc-emissions/merge_lcc_fut_hrbvoc.sh`, `run_bvoc_climatology_array.sh` (input folder option), `run_aliases.csv`, `cases-scripts/README.md`, `CLAUDE.md`.

</div>

<div style="color:#555555">

## 2026-11-03 · 23:30 → 01:00 (90 min) · session 9e6f4132

**Goal:** start the 11-year MET extension; check the test; fill the 2000–2025 folder after the first piece; prepare the extension of all nudged runs.

**Done:** MET extension running since 23:43 (job 1787584) (open since 3 Nov, 21:39). Test **PASS**: 40 six-hourly records bit-identical to the old MET (MET reproduction test, open since 3 Nov, 21:39). Folder build automated: watcher `preprocess/nudging/met_ext_watch_and_build.sh` runs on login-2 and fills the folder after each MET piece. Extension script for the 10 nudged runs ready and checked (all 10 can continue from 2015-01-01), **not submitted**.

**Found:** (1) the script set `BRNCH_RETAIN_CASENAME`, which this model version doesn't have; not needed, the model keeps the case name by itself. (2) The new MET files are cut 6 h later than the old ones, so they are regrouped into calendar days (checked value for value). The real 2015-01-01 replaces the patched one. (3) Each nudged run's restart remembers the exact path of the old met file. The extension rewrites that path (1 byte changes) and the namelist, otherwise the run would use the patched 2015-01-01 file and then crash. (4) The b5… compute nodes are faulty since 3 Nov; the small `preproc` nodes (b5201–5206), where archive jobs run, fail at random. The runs avoid the b5 block; the watcher redoes a failed MET archive. LCC_PD_fBVOClccPD's archive job also sits on those nodes.

**Open-next:** your OK to submit nudged part 1 (2015–2019, ~17 h, 10 runs; total ≈ 190 000 core-h for 2015–2025), after the folder fill (~22–23 h today). Decide on LCC_PD_fBVOClccPD. After MET ends (~5 Nov evening): final fill, then part 2 (2020–2025). Update CLAUDE.md (met data now to 2026).

**Files changed:** `cases-scripts/12d-…met_ext…sh`, `cases-scripts/cases-setup.sh` (`extend_case` options, new `switch_case_to_met_2000_2025`), new `cases-scripts/extend_nudg_runs_2015-2025.sh`, `preprocess/nudging/` (new `regroup_met_ext_days.py`, `met_ext_watch_and_build.sh`, `build_met_2000-2025_job.sh`; rewritten `copy-…-2000-2025.sh`, `check_met_reproduction.py`), `cases-scripts/README.md`, `run_aliases.csv`.

</div>

<div style="color:#555555">

## 2026-11-03 · 23:25 · session 70247179
**Goal:** plan the commits; decide where `run_when_done/` should live. **Done:** 7-commit plan proposed. **Found:** the 14e watcher is running with hard-coded paths into that folder. **Open-next:** your go-ahead for the commits; move the folder only after the watcher finishes. **Files changed:** logs only.

## 2026-11-03 · 21:01 → 21:49 (49 min) · session 8672845b

**Goal:** extend MET by 11 years (2015–2025) so the nudged runs can later run to 2025.

**Done:** plan agreed with you (same case name, small h0, 10-day test first, one folder for all met files). Wrote the run script `cases-scripts/12d-…met_ext…sh` (modes `test` and `production`; it checks that build and namelists match the original MET and stops if not), the test checker, the folder-building script and its checker. Checkers tested on the existing files: the old 2000–2015 folder is complete (every day, 4 records, no time gaps).

**Found:** MET kept restarts only for 2005, 2010, 2015, so the test starts from 2010. Code is unchanged since MET ran. 11 years ≈ 20 000 core-hours, ~1.7 days.

**Open-next:** 10-day test building/submitting since 21:49 (detached; log `/cluster/work/users/adelez/met-ext/`); when done, compare with MET → then the 11-year run → then build the `_6h_2000-2025` folder (in /cluster/shared, your OK). Later: how to extend the nudged runs.

**Files changed:** `cases-scripts/12d-NF2000norbc_tropstratchem_met_ext_f19_f19.sh` (new), `cases-scripts/cases-setup.sh` (4 new functions), `preprocess/nudging/check_met_reproduction.py`, `check_nudging_dir.py`, `copy-nudging-data-to-inputForNudging-directory-2000-2025.sh` (new), `cases-scripts/README.md`, `cases-scripts/run_aliases.csv`.

</div>

<div style="color:#999999">

## 2026-11-03 · 21:40 → 21:41 (1 min) · session b157c5d7

**Goal:** list what we worked on today.

**Done:** summary from today's log blocks. No files changed.

**Files changed:** logs only.

</div>

<div style="color:#008080">

## 2026-11-03 · 20:11 → 21:23 (72 min) · session bc4585e4

**Goal:** move the two FUT BVOC decomposition notebooks to the new runs, palette and map style.

**Done:** two new `-after-co2-fix` notebooks (2001–2014, new runs incl. all 3 fBVOC FUT runs and the FUT artefact run), both run; hatched non-significant cells; palette colours; note on the old notebooks; results text of the interaction notebook rewritten.

**Found:** expansion effect on emissions ≥45°N is now small and positive for isoprene (+0.29 PD, +0.39 FUT Tg/yr), ~0 for monoterpenes; the old FUT decrease (−2.6 / −3.9) is gone, likely because it came from the CO₂-bug spin-up.

**Open-next:** rewrite the conclusion text of the emissions notebook (§10, §14–17 findings) with the new numbers; check its fixed-emission and atmospheric-response outputs.

**Files changed:** the 2 new notebooks (+ output folders), 1-line note in the 2 old ones.

</div>

<div style="color:#008080">

## 2026-11-03 · 19:52 → 20:38 (46 min) · session 69fd7b68

**Goal:** maps of the three groups of contrasts you defined (LCC effect per background, FUT emission source, PD → FUT), without the artefact correction.

**Done:** notebook `diagnostics/lcc-bvoc-background-contrast-maps/contrast_maps_uncorrected.ipynb`; 9 map grids (3 questions × radiation / BVOC→SOA→cloud / surface) in `contrast_maps_uncorrected_outputs/figures/`; a table says which rows contain the artefact.

**Found:** Q2: isoprene ≥45°N changes by +0.01 mg m⁻² d⁻¹ with the LCC-driven emission change, +0.52 with the PD → FUT emission change; SOA −0.001 vs +2.65 mg m⁻²; net radiation −0.01 vs −0.94 W m⁻². Total land-cover effect (≥45°N): +0.24 W m⁻² PD, +0.20 FUT.

**Done (same block):** regional-mean table + additivity check (first run broke because the modified-cells mask moved during the run; rerun OK).

**Open-next:** artefact-corrected version of the same maps if you want it.

**Files changed:** new notebook + outputs; `diagnostics/README.md`.

</div>

<div style="color:#999999">

## 2026-11-03 · 20:15 → 20:20 (5 min) · session d09b520e

**Goal:** move `lcc-modified-cells/` up to `diagnostics/` and fix the paths.

**Done:** folder moved; paths fixed in 11 equilibrium notebooks, 13 other notebooks, `forcing_maps.py`, `megan_maps.py`, `build_modified_cells.py` (import of `equilibrium.py`), `CLAUDE.md`, `PLOTTED_VARIABLES.md`. All paths checked.

**Open-next:** none.

**Files changed:** the files above, both logs

</div>

<div style="color:#008080">

## 2026-11-03 · 20:10 → 20:43 (33 min) · session db60df4e

**Goal:** update the nudging-on-land notebook to the new runs and the plotting choices.

**Done:** notebook switched to the new runs (CTRL_PD, LCC_PD, CTRL_FUT, LCC_FUT and their new coupled spin-ups; 2001–2014), run, summary written. The jump split now removes the land spin-up effect. Palette, Cantarell font, more colourbar ticks, dark-grey outline of the modified cells. Old outputs moved to `pre_co2_fix/`. Then: maps hatch the cells that are not significant (instead of dots), and a new figure shows MET, CTRL_PD, LCC_PD, CTRL_FUT and LCC_FUT on the same years.

**Found:** the nudging effect is the same as before (global land: sun −4.6 W m⁻², soil at 1 m −0.24 K, much stronger in the tropics). Land spin-up effect small on average, but up to ~1 K cooler over Siberia. FUT jump bigger than PD (wetter boreal soils). CTRL and LCC jump alike. The drift difference flags drop from 9 to 4 of 96 (chance level); the old water/snow difference north of 45°N is gone. Cell-by-cell, the LCC − CTRL trend is significant over 18–26 % of land (5 % expected by chance), but that test is not strict.

**Open-next:** optional stricter test (autocorrelation + multiple testing) on the drift maps, if you want it.

**Files changed:** `diagnostics/impact-of-nudging-on-land/impact_of_nudging_on_land.ipynb` (+ outputs folder), `diagnostics/README.md`, both logs

</div>

<div style="color:#A84300">

## 2026-11-03 · 19:45 → 21:03 (78 min) · session 83846750

**Goal:** time series of the context-map variables and the Ghan forcing, global vs regional.

**Done:** `analysis/timeseries-responses.ipynb` (run, outputs saved); 6 difference figures + 4 absolute-value figures (all nudged runs) in `results/figures/timeseries/`; tables `results/tables/timeseries_{regional_means,absolute}_2001_2014.csv`; line in `analysis/README.md`. Path fix in `src/` for the moved modified-cells file (later superseded: another session moved it again and updated the code).

**Found:** NET TOA, ≥45°N: total +0.24 (PD) / +0.20 (FUT) W m⁻²; corrected BVOC −0.03 (PD) / −0.06 (FUT, CTRL_FUT emissions) W m⁻². The FUT BVOC row with CTRL_PD emissions (−1.0 W m⁻²) is dominated by the 2100 background, as expected.

**Open-next:** nothing from this request.

**Files changed:** `analysis/timeseries-responses.ipynb` (new), `analysis/README.md`, `src/.../plotting/forcing_maps.py`, `src/.../plotting/megan_maps.py` (path only; since changed again by another session).

</div>

<div style="color:#7B2FBE">

## 2026-11-03 · 19:43 → 21:46 (123 min) · session ca3050fb

**Goal:** show with maps whether the PD artefact depends on the land, how much, and decide on the extension of LCC_PD_fBVOClccPD.

**Done:** `how_big_artefact_is_PD.ipynb`: global + Arctic maps in three figures (A1 artefacts, A2 the three BVOC estimates C / BVOC_B / BVOC_A, B why δ_PD is tropical), definitions in the titles, LCC − CTRL time series, region table, verdict sections 3b (LCC cells) and 3c (north of 45°N). Rerun with outputs saved.

**Found:** the global δ_PD (+1.0 % SOA) is a tropical vegetation offset of 2001–2002, not the boreal land. Over the LCC cells: isoprene ratio 0.12 (small), monoterpene 0.60 (moderate, same sign both years), SOA not resolved. The three differences between the BVOC estimates are exactly the artefact maps: BVOC_B − C = art_CTRL, BVOC_A − C = art_LCC, BVOC_A − BVOC_B = δ_PD. Dropping 2001–2002 from the main analysis is not needed (≤0.2 percentage points).

**Done (cont.):** your choice on the extension (open since 20:25): LCC_PD_fBVOClccPD continued for 2003–2007, submitted 20:48; a watcher postprocesses it, reruns the notebook and updates CLAUDE.md when it ends.

**Found (cont.):** BVOC_A is not 0 outside the changed cells because the LCC_PD and CTRL_PD emission climatologies differ there too: in the tropics mostly noise and slowly diverging vegetation (net ≈ 0 after 2002), next to the changed cells a real response (33–63 % of emitting cells significant). New notebook section 4e shows this with significance maps (Figure D) and a table.

**Done (cont.):** extension running since 21:33 after two failed starts on 4 faulty compute nodes (resubmitted avoiding them).

**Open-next:** read the new verdicts (2001–2007) when the watcher finishes (~1 day). Decide whether to keep design A as is or use a hybrid emission file (LCC emissions only north of 45°N); the hybrid needs a new run.

**Files changed:** `diagnostics/fbvoc-prescription-artefact/how_big_artefact_is_PD.ipynb` + `_outputs/` (7 figures, 6 tables); new `run_when_done/run_14e_extension_when_done.sh`; section 4e (Figure D, hatching = not significant, + `lcc_minus_ctrl_emission_significance.csv`).

</div>

<div style="color:#555555">

## 2026-11-03 · 19:38 → 20:27 (49 min) · session c650bace

**Goal:** keep LCC − CTRL results, move only the fixed-BVOC ones aside.

**Done:** 69 figures (incl. 10 mixed ones that also show an uncorrected fixed-BVOC contrast), the cumulative-decomposition folder and all 8 tables of 2001–2014 → `pre-artefact-correction/`. Your OK to move (open since 19:33) answered.

**Open-next:** notebook 1 running (started 20:26); then fill its findings and do notebook 3.

**Files changed:** `results/README.md`, `analysis/README.md`, new `analysis/artefact-corrected-split.ipynb`, files moved in `results/`.

</div>

<div style="color:#A84300">

## 2026-11-03 · 19:14 → 19:33 (19 min) · session c650bace

**Goal:** decide what to analyse now that all new fixed-BVOC runs are done.

**Done:** plan with 4 analyses, each with its own notebook and results folders; shared code for corrected contrasts ("virtual run") written and tested: total = non-BVOC + corrected BVOC exactly.

**Found:** none of the paper notebooks use the artefact correction yet. The surface-albedo proxy is not exactly additive (small, expected).

**Open-next:** your OK to move the uncorrected results aside; then notebook 1 (corrected split).

**Files changed:** `src/boreal_forest_expansion/plotting/forcing_maps.py`.

</div>

<div style="color:#CC0000">

## 2026-11-03 · 18:54 → 19:13 (19 min) · session d34b64e4

**Goal:** show which runs are subtracted in the forcing-decomposition figures.

**Done:** one label line with a bracket over the four BVOC panels (e.g. "LCC_FUT − LCC_FUT_fBVOCctrlFUT"); applies to every forcing-decomposition figure. Test versions of all 27 figures made in the sandbox.

**Open-next:** your OK to rerun `analysis/radiative_forcing.ipynb`.

**Files changed:** `src/boreal_forest_expansion/plotting/forcing_maps.py`, `sandbox/test_group_label.py` (new).

</div>

<div style="color:#999999">

## 2026-11-03 · 17:30 → 18:40 (70 min) · session a2e7f46d

**Goal:** find out why conda files showed up as new files in git and why so many files were staged; prepare clean commits.

**Done:** `~/.condarc` now uses absolute paths: packages go to `/nird/datapeak/NS9188K/adelez/.conda/pkgs`, environments to `.../envs` (backup in `~/.condarc.bak`). The 1.1 GB cache `docs/nird/.conda/` is unstaged and deleted. Staged files went from 3,345 to 322.

**Found:** the setting used a relative path (`nird/.conda/pkgs`), so conda put its cache wherever it was run, here `docs/` on 2 Nov 16:31. The staging came from **VS Code on 2 Nov at 19:00**. Its log shows `git add -A -- .` (127 s), then two commits stopped because the message was empty. That is what VS Code does when you commit with nothing staged: it stages all changes first. Neither Claude nor the terminal ran it.

**Done (later):** VS Code no longer stages everything without asking (`git.enableSmartCommit` off). The index was emptied at 17:35, so nothing is staged now. `.gitignore` now skips the old pre-CO₂-fix figures (`results/figures-2001-2014-all-bvoc-pre-co2-fix/`, 239 MB), watcher pid files, sandbox run logs and `commit_messages.md`. Created `commit_messages.md` with 9 commits covering all 346 changed files: housekeeping, case scripts, pre/postprocessing, plotting library, 2 diagnostics commits, analysis + tables, new figures (271 MB, kept separate), sandbox scripts.

- Commit messages file done (opened 17:45 in this block): you committed most of it yourself (18 commits, 17:45–18:29) and deleted the file. Then 4 more commits from me: `2f2e672` diagnostics palette (16 files, notebooks not rerun, so their saved figures keep the old colours), `a51c46d` diagnostics README, `684be41` D2 MEGAN budget on the new chain (notebook + 13 outputs), `615a07e` palette rerun of `cumulative_radiative_decomposition` + `fut-fbvoc-emission-source` (+ 3 figures, log).

**Open-next:** push to GitHub when you say so (`main` is 10 ahead). D1 new-chain notebook: fix the ValueError in `plot_contributions`, rerun, commit. `megan_patch_branch_5day_test.ipynb`: discard the re-save (`git restore`) or commit it.

**Files changed:** `~/.condarc` and new `~/.vscode-server/data/Machine/settings.json` (both outside the repo); `.gitignore`; new `commit_messages.md` (gitignored); `docs/nird/` deleted.

</div>

<div style="color:#E58AA5">

## 2026-11-03 · 17:24 → 17:26 (2 min) · session 5372bf34

<div style="color:#008080">

**Done:** explained in plain words what `diagnostics/megan-exact-split-test/gamma_eff_vs_GAMMA_check.ipynb` shows (why γ_eff ≠ GAMMA even in cells dominated by one plant type). No files changed.

</div>

## 2026-11-03 · 17:07 → 17:11 (4 min) · session e2025936

**Goal:** try palette O on the zonal-mean ΔT plot.

**Done:** sandbox script redraws it from the notebook cache in two colour mappings.

**Open-next:** pick P1 or P2; then update the notebook cell and rerun it (with your OK).

**Files changed:** `sandbox/test_zonal_mean_palette_O.py` (new), 2 PNGs in `sandbox/test_palette_picture_outputs/`.

</div>

<div style="color:#E58AA5">

## 2026-11-03 · 15:50 → 17:35 (105 min) · session c238acfa

**Goal:** put the picture palette in colour order on the charts; lighter navy.

**Done:** three orders tried (picture order, hue wheel, your teal → navy → plum → red → orange → gold); navy lightened to `#36449A`. Radiative and water budget checked by eye.

**Found:** lighter navy separates better from the dark-grey total, but gets closer to plum for protan readers.

**Found (16:06):** Paul Tol's scheme you pasted: a solid, colour-blind-tested source; its 'muted' set is the same family as your picture. In your order it is not better than J by our check; its blue-red map is the same as the one we use now.

**Done (16:13–16:30):** tried your 12-colour set (K by meaning, L in order) and Tol muted (M); total in grey (J2) or gold (J3) instead of black; albedo proxy hatched in the F_rest colour.

**Done (16:31–16:59):** tuned your order: navy `#2C3990`, plum `#A8559A`, gold `#EBC45C`, light grey `#CCCCCC` for total and residual. Found that the mid-grey total looked like teal to colour-blind readers; fixed.

**Done (17:01–17:21):** red softened (tried `#C4524E`, too pastel → `#BC423E`); plum back to dark but pinker (`#9A4A84`); total in gold (Q1) or orange (Q2).

**Done (17:22–17:35):** you chose Q1 (gold total). Palette saved in `plotting/palette.py`, used by default in all plots, in the analysis notebooks and in all diagnostics notebooks; rule added to `CLAUDE.md`. Analysis rerun started.

**Open-next:** check the rerun result; decide whether to rerun the diagnostics notebooks too (old-chain ones need the archived data); then move it into `forcing_maps.py` (and the hard-coded colours in `pd-fut-attribution.ipynb`).

**Files changed:** `sandbox/test_palette_picture.py`; `src/.../plotting/{palette,style,forcing_maps}.py`; 4 analysis + 24 diagnostics notebooks (code only); `diagnostics/check-simulation-equilibrium/equilibrium.py`; `CLAUDE.md`; new `results/tables/logs/rerun_palette_20261103.sh`.

</div>

<div style="color:#E58AA5">

## 2026-11-03 · 15:33 → 15:43 (10 min) · session c238acfa

**Goal:** try the palette of your reference picture (+ orange, red) on existing charts.

**Done:** `sandbox/test_palette_picture.py` → `sandbox/test_palette_picture_outputs/` (radiative budget, water budget, paired years, emission origin; current vs picture palette; swatch with colour-blind simulation; `cvd.csv`).

**Found:** colours are easy to tell apart, also for colour-blind readers, except navy vs the dark-grey total bar (tritan) and teal vs grey residual (deutan).

**Open-next:** your verdict; then maybe a lighter/black total, then move the palette into `forcing_maps.py`.

**Files changed:** `sandbox/test_palette_picture.py` (new).

</div>

<div style="color:#008080">

## 2026-11-03 · 15:23 → 15:28 (5 min) · session d8575a33

**Goal:** keep one version of the "how warmer is FUT" notebook, on the latest runs.

**Done:**
- `how_warmer_future_climate_is.ipynb` now uses the new-chain CTRL runs and was rerun; the text is updated. Old-run notebook, the `-after-co2-fix` copy and the old outputs deleted.
- Rerun on the new chain done (open since 2026-10-30).

**Found:** results unchanged to 0.1 K (global +3.5, Arctic +8.9, forest cells +7.5, vs pre-industrial +3.9).

**Files changed:** `diagnostics/how-warmer-future-climate-is/` (notebook, outputs), `diagnostics/README.md`.

</div>

<div style="color:#A84300">

## 2026-11-03 · 15:16 → 15:50 (34 min) · session 903fd5f7

**Goal:** understand `FUT_isoprene_attribution_ANN_2001_2014.png`; fix the lake bug; discuss the exact split.

**Done:**
- Explained the figure; checked it uses the new runs.
- Lake fix in the MEGAN maps (waiting since 2 Nov 17:52, your OK today); old figures saved as `_before_lake_fix`; before/after notebook done.
- Removed the out-of-date "different land spin-ups" note from FUT figures.

**Found:**
- Total +0.3 % = vegetation mix +13.8 − activity 13.5; activity = LAI −5.4, temperature +2.7, light −0.6, rest −10.2 (mostly weighting −8.5).
- Lake fix: negligible (0.05–0.07 moved from activity to composition; up to ~10 only in 12 tundra cells).

- MEGAN exact split: 32-day test approved; batch 1 = 2002, 2008, 2014 (recorded in `analysis/MEGAN_ATTRIBUTION.md`).

**Open-next:** write the code for the per-plant reruns (branch script, swaps, identity check, launcher), then the 32-day test; later: after PD batch 1, compare exact vs current split for 2002/2008/2014, then FUT.

**Files changed:** `src/.../plotting/megan_maps.py`, `analysis/megan_factor_maps.ipynb` (rerun), new `diagnostics/megan-exact-split-test/lake_fix_effect.ipynb`, figures in `results/figures/megan_factors/`, `analysis/MEGAN_ATTRIBUTION.md`.

</div>

<div style="color:#999999">

## 2026-11-03 · 15:15 → 15:17 (2 min) · session a5cffa92

**Goal:** check whether the 2 Nov rerun overwrote the old figures.

**Found:** `results/figures/` (118 files, all 2 Nov) = new; `results/figures-2001-2014-all-bvoc-pre-co2-fix/` (118 files, 28–29 Oct) = old, kept. D1/D2 old outputs are in `*_outputs_pre_co2_fix/` (21–22 Oct). `how_warmer_future_climate_is.ipynb` is the old-chain version on purpose (reads -20261023); the new-chain one is `-after-co2-fix.ipynb`. Overwritten: `how_big_artefact_is_PD_outputs/` (old = stand-in "pending" version) and `fbvoc_prescription_artefact_outputs/` (rerun on the same old data, so the same numbers).

**Open-next:** same as 14:34.

**Files changed:** logs only.

</div>

---

<div style="color:#AAAAAA">

## 2026-11-03 · 14:34 → 14:36 (2 min) · session a5cffa92

**Goal:** status of runs and the to-do list.

**Done:** checked Slurm, the rerun log and the artefact notebook outputs.

**Found:** queue empty; every fixed-BVOC run finished on 2 Nov. Rerun log `results/tables/logs/rerun_new_chain_20261102.log` is "all done" 00:09, with one FAIL (`D1_farfield_check.ipynb`: "cannot reindex on an axis with duplicate labels" in `plot_contributions`). `how_big_artefact_is_PD.ipynb`: SOA burden δ_PD +1.06 % global (R = 0.81), −0.22 % at ≥45°N (R = 2.98, but the two years have opposite signs) → "design A in FUT is worth it".

**Open-next:** design A decision; γ_eff lake fix OK; MEGAN 32-day test OK; fix D1; update `run_aliases.csv`; ONHOLD items (FUT emission source, journal).

**Files changed:** logs only.

</div>

---

<div style="color:#999999">

## 2026-11-02 · 18:33 → 18:50 (17 min) · session 6aedb215

**Goal:** move logs and pids in `diagnostics/fbvoc-prescription-artefact/` out of the main folder.

**Done:** everything from the watchers (2 scripts, 12 logs, 2 pids) moved to `run_when_done/` (`logs/`, `pids/`); paths in the scripts and the script names mentioned in the two notebooks updated.

**Found:** the notebooks never read the logs/pids themselves, so no notebook code changed and no rerun was needed.

**Open-next:** nothing.

**Files changed:** `diagnostics/fbvoc-prescription-artefact/run_when_done/*.sh`, `fbvoc_prescription_artefact.ipynb`, `fbvoc_artefact_causes.ipynb` (text only).

</div>

<div style="color:#CC0000">

## 2026-11-02 · 17:20 → 18:10 (50 min) · session 8901a50d

**Goal:** list of runs after the CO₂ fix (status, artefact runs, γ attribution runs); recap of Friday 30 Oct; what the "stray Jupyter server" is; what the γ_eff ≠ GAMMA question means.

**Done:** status table given in chat; Friday recap from this log; explained the Jupyter server; explained γ_eff vs GAMMA; then **tested the causes** with the 5-day patch-level output (γ_eff ≠ GAMMA, open since 2026-10-30); the test is now a notebook: `diagnostics/megan-exact-split-test/gamma_eff_vs_GAMMA_check.ipynb` (run, outputs saved).

**Found:** γ_eff ≠ GAMMA is mostly expected: the "one plant type" cells still have small patches that can dominate the emission (e.g. leafless dominant forest). Cells with exactly one patch give exactly 1. But there is **one real bug**: `megan_maps.py` counts lakes in the area used for γ_eff, while CLM leaves lakes out. In ~1 in 4 land cells north of 45°N γ_eff is >5 % too low (up to 6× in lake cells). Total emission change is not affected, only its split into composition vs activity. The CLM cutoff (γ ≥ 100 not stored) is a minor effect (isoprene only, mostly crops; 1 cell north of 45°N). `run_aliases.csv` status column out of date; 5 `CTRL_PD_fBVOCctrlPD_HR_*` files in the current processed folder although they were moved earlier.

**Open-next:** update `run_aliases.csv`; check where the HR files came from; Jupyter server pid 1758272 on login-2 still running since 30 Oct (no password): stop it if it's not yours (`kill 1758272`); <span style="background:#CC0000;color:#FFFFFF;padding:0 4px;border-radius:3px">**WAITING ON YOU**</span> OK to fix the lake bug in `megan_maps.py` and rerun `megan_factor_maps.ipynb`.

**Files changed:** `diagnostics/megan-exact-split-test/gamma_eff_vs_GAMMA_check.ipynb` + `…_outputs/` (new), `diagnostics/README.md`.

</div>

<div style="color:#7B2FBE">

## 2026-11-02 · 17:41 → 18:47 (66 min) · session 634a8b84

**Goal:** summarise the two ways to remove the artefact (A and B) and collect the whole artefact discussion in one document.

**Done:** summary in words and formulas (chat). New `analysis/FBVOC_ARTEFACT.md`: the problem, its cause, the two designs with formulas, the decision, the runs, first new-chain numbers, caveats.

**Found:** the 30 Oct plan for fixed-BVOC CTRL twins was only partly carried out: of its three FUT twins only CTRL_FUT_fBVOCctrlFUT was made; CTRL_FUT_fBVOCctrlPD and CTRL_FUT_fBVOClccPD were dropped by the later decision the same day. Careful: that plan's "option A" is what the new document calls design B.

**Open-next:** add δ_PD and the verdict once CTRL_PD_fBVOCctrlPD is postprocessed (running now). CTRL_FUT_fBVOCctrlPD is not needed after all: the artefact belongs to the run that is replaced (the interactive one), not to the emissions that are prescribed, so one FUT baseline corrects every FUT contrast (my earlier suggestion withdrawn).

**Files changed:** `analysis/FBVOC_ARTEFACT.md` (new), `analysis/README.md`.

</div>

<div style="color:#7B2FBE">

## 2026-11-02 · 16:38 → 16:43 (5 min) · session 634a8b84

**Goal:** check the two artefact runs set up on 30 Oct.

**Done:** both ran and were postprocessed automatically: LCC_PD_fBVOClccPD (3 yr, 31 Oct) and CTRL_FUT_fBVOCctrlFUT (15 yr, 2 Nov) (open since 2026-10-30). LCC_PD_fBVOCctrlPD finished today 16:23.

**Found:** SOA burden artefact on LCC land (PD, 2001–02) +3.6 %; FUT artefact +2.8 % on average but larger in the first years (~+5 % in 2001–03), so 2-year averages of the artefact are not representative.

**Open-next:** when CTRL_PD_fBVOCctrlPD is archived and postprocessed (~tonight), rerun `how_big_artefact_is_PD.ipynb`; check whether the PD artefact on CTRL land also is larger in the first years.

</div>

<div style="color:#008080">

## 2026-11-02 · 16:13 → 16:32 (19 min) · session d2a9b8a9

**Goal:** check the year-to-year autocorrelation of the yearly differences, so the methods can say the 14 years are independent samples.

**Done:** notebook `diagnostics/yearly-difference-autocorrelation/yearly_difference_autocorrelation.ipynb` (run, outputs saved). It covers 4 contrasts × 10 fields, regional and cell by cell, and checks the FDR stippling with a reduced sample size.

**Found:** radiation, temperature, cloud droplets and LWP behave like random noise (about 5 % of cells outside the noise range, as expected), so independence holds. BVOC emissions and SOA burden show positive autocorrelation from slow trends (PD monoterpene LCC effect fades from 2001 to 2014; FUT SOA BVOC effect grows 13 % per decade). With the reduced sample size, the small PD LCC − CTRL SOA signal loses its significant cells.

**Open-next:** rerun once LCC_PD_fBVOCctrlPD is processed (PD BVOC contrast missing); look into the emission/SOA trends (drift?); put the sentence in the methods.

**Files changed:** new `diagnostics/yearly-difference-autocorrelation/` (notebook + `_outputs/`), `diagnostics/README.md`.

</div>

<div style="color:#CC0000">

## 2026-11-02 · 17:54 → 18:56 (62 min) · session 514734ef

**Goal:** finish the land-cover part of the Methods outline; bring in the artefact method.

**Done:** only GFDL-ESM4 named; found what drove LPJ-GUESS (1901–2014 observation-based CRU-NCEP climate; after 2015 GFDL-ESM4, bias-corrected to CRU-NCEP over 1985–2014), from the study's preprint; M4 rewritten from `analysis/FBVOC_ARTEFACT.md` (frozen not zero emissions, closed split equations, assumptions and test rule, artefact size and its decrease over the FUT run); new §8 "In the paper" in `FBVOC_ARTEFACT.md`; autocorrelation results (`diagnostics/yearly-difference-autocorrelation/`, checked against its tables) added to the statistics part, with the draft sentence; PDF viewer tools (poppler) added to `tex-env`; artefact-causes notebook (H1–H5): split undone on your request, one notebook kept on the old PD runs with a note at the top (CO₂ bug was in the FUT land spin-up); other old-chain notebooks left as they are; naming rule in CLAUDE.md (new-chain versions get `-after-co2-fix`); new `check_CTRL_FUT_vs_LCC_FUT_vegetation_state-after-co2-fix.ipynb` (new-chain lineage, 2001–2014, new section D: paired test + FDR outside the modified cells, old vs new). **Result: outside the modified cells the FUT members now have the same vegetation** (leaf area, vegetation and ecosystem carbon, GPP differ by ≤ 0.15 %; old chain −11 to −34 %). A few sparse cells (~1 %) differ by > 10 %, far from the forest: leftovers of the free coupled spin-ups. Methods number filled; outline compiles and was checked by eye.

**Found:** the artefact cause tests are old-chain: in the paper say so, or rerun the replay test on the new chain. With an effective sample size, the significant cells of the PD forest SOA-burden map drop from 291 to 0: the paper must say how SOA and emission maps are tested. FUT LCC − CTRL SOA has a negative autocorrelation (−0.18), unlike the other emission/SOA contrasts.

**Open-next:** confirm the preprint is the same study as Tang et al. 2023; decide the main FUT emission source and the journal; numbers when the runs are done.

**Files changed:** `boreal-forest-expantion-draft/methods-claude.tex`, `analysis/FBVOC_ARTEFACT.md` (§8 appended, notebook names), `diagnostics/fbvoc-prescription-artefact/fbvoc_artefact_causes.ipynb` (note at top), new `diagnostics/check-simulation-equilibrium/check_CTRL_FUT_vs_LCC_FUT_vegetation_state-after-co2-fix.ipynb`, `diagnostics/README.md`, `CLAUDE.md`.

</div>

<div style="color:#CC0000">

## 2026-11-02 · 16:22 → 16:36 (14 min) · session 514734ef

**Goal:** add your answers to the Methods outline; make LaTeX work on Betzy.

**Done:** NORBC described (sea surface from coupled NorESM2, not observations); LPJ-GUESS slice fixed to 2071–2100 minus 1971–2000; GCM = GFDL-ESM4 added; LMDI attribution now a main-text point; open decisions in orange, missing numbers in yellow; `xcolor` added to `main.tex`. Journal advice given in chat. **LaTeX installed:** Tectonic in a new conda env `tex-env` on NIRD; the outline and `main.tex` compile (line-overflow fixes in the outline).

**Found:** the LPJ-GUESS historical output is the same for the three GCMs: the paper must say what climate forced it. The third GCM is not named in our data folder.

**Open-next:** choose the main FUT fixed-BVOC emission source and the journal; fill the yellow numbers when the final runs are done.

**Files changed:** `boreal-forest-expantion-draft/methods-claude.tex`, `boreal-forest-expantion-draft/main.tex`; new env `/nird/datapeak/NS9188K/adelez/.conda/envs/tex-env`.

</div>

<div style="color:#A84300">

## 2026-11-02 · 16:00 → 16:10 (10 min) · session 514734ef

**Goal:** outline of the Methods section for the paper.

**Done:** new `boreal-forest-expantion-draft/methods-claude.tex`: sections Model, Land-cover change, Experimental design, Isolating the BVOC effect, Analysis, Data/code; each point tagged main/SI.

**Found:** points to check before writing: FUT runs are nudged to PD weather; DMS in FUT is kept at PD; meaning of `norbc`; LPJ-GUESS slice "2100" vs 2071–2100.

**Open-next:** user to choose the main FUT fBVOC emission source and the journal format.

**Files changed:** `boreal-forest-expantion-draft/methods-claude.tex` (new).

</div>

<div style="color:#7B2FBE">

<div style="color:#CC0000">

## 2026-11-02 · 17:53 → 19:15 (82 min) · session 4556636c

**Goal:** archive the two test runs under clear names; explain the stale light inputs.

**Done:** 2001–2002 test renamed `CTRL_PD_fBVOCctrlPD_test2yr` and kept in the archive folder; replay test moved there too (both open since 16:30 today); 3 artefact notebooks repointed (not rerun). Duplicate MEGAN reduction script removed; the MEGAN factor copy moved into `postprocess/megan_lmdi/`. New rule applied to the "how warm is FUT" notebook: the old version is restored as it was, the new-chain version is `how_warmer_future_climate_is-after-co2-fix.ipynb` (running). Swap design agreed (four groups + three-group headline, plant cover and CO₂ factor separate) and written into `analysis/MEGAN_ATTRIBUTION.md` (option 1b).

**Found:** stale light inputs ≥ 45°N = 0.02–0.04 % of steps, 0.001 % of emission, only C3 grass at 48°N; cause: isoprene leaf-age factor goes negative when LAI rises fast, so CLM skips isoprene there; they can be rebuilt exactly. The identity-check script of 29 Oct was not lost: on 29 Oct you asked to move all checks into `megan_patch_branch_5day_test.ipynb` (its §1), and the script was deleted then.

**Open-next:** (19:09) nothing external blocks MEGAN batch 1: yearly restarts exist. To do: branch-run script per year (~1 h), batch launcher (~2 h), swaps in the reduction (~½–1 day). Proposal: launch batch 1 once script + launcher are ready and keep its raw output until the swaps are ready — needs your OK. Rerun: D2 still running; PD notebooks after it. (19:14) Test proposed before batch 1: 32-day CTRL_PD + LCC_PD branches from 1 Jan 2002 with the production script and launcher (≈ 1,200 core-hours) — needs your OK.

**Files changed:** `postprocess/megan_lmdi/{README.md, megan_replay.py}`, removed `postprocess/megan-lmdi/`, `analysis/MEGAN_ATTRIBUTION.md` (status note; option 1b driver groups), `diagnostics/fbvoc-prescription-artefact/{fbvoc_artefact_causes, fbvoc_prescription_artefact, how_big_artefact_is_PD}.ipynb`.

</div>

<div style="color:#A84300">

## 2026-11-02 · 16:12 → 16:57 (45 min) · session 4556636c

**Goal:** see results from the new runs.

**Done:** old processed files of LCC_PD_fBVOCctrlPD, the CTRL_PD_fBVOCctrlPD test and the replay test moved to the archive folder (the rest had been moved by the launcher); old figures and tables archived; SOA burden switched to the model field; D1/D2 case names filled (open since 2026-10-28) and output folders fixed; how-warm notebook pointed at the new CTRL runs; rerun started. Replay test file moved back to the main folder (your request). MEGAN reduction script written and tested on the 5-day pair (exact); the Python MEGAN factors match CLM exactly.

**Found:** CLM updates leaf area and the 1-/10-day means after MEGAN, so the saved values are one step ahead; on crop patches the saved light fields are stale (7 % of steps).

**Open-next:** PD notebooks and D1 tonight after LCC_PD_fBVOCctrlPD; artefact notebook after CTRL_PD_fBVOCctrlPD; update the text in the notebooks to the new numbers; decide the name of the 2001–2002 test files; MEGAN: driver swaps, per-year check, batch launcher, then your OK.

**Files changed:** `src/.../plotting/forcing_maps.py`, `analysis/pd-fut-attribution.ipynb`, `analysis/fut-fbvoc-emission-source.ipynb`, D1/D2, how_warmer, fbvoc_artefact_causes notebooks, new `results/tables/logs/rerun_new_chain_20261102.sh`. New `postprocess/megan-lmdi/` (reduce_megan_lmdi.py, megan_replay.py, README.md); status note in `analysis/MEGAN_ATTRIBUTION.md`.

</div>

## 2026-11-02 · 15:51 → 15:58 (7 min) · session 4556636c
- Status check: where the runs are and what comes next. Nothing changed.

## 2026-10-30 · 15:53 → 16:48 (55 min) · session 634a8b84

**Goal:** decide how to measure the BVOC effect now that the prescription artefact is known, and set it up.

**Done:** compared two designs (A: LCC runs that both prescribe emissions; B: matched baseline = real LCC run + artefact measured on CTRL land). You chose B. New run scripts CTRL_FUT_fBVOCctrlFUT (15 yr) and LCC_PD_fBVOClccPD (3 yr), both added to the auto-launcher (restarted, running). New notebook `how_big_artefact_is_PD.ipynb` (pending until the runs exist; tested with a stand-in). CLAUDE.md, run list and READMEs updated.

**Found:** the fixed-BVOC runs are not "MEGAN off": they keep realistic, frozen emissions. Design B needs only one extra FUT run, not three. LCC_FUT does not save half-hourly emissions, so design A in FUT would need a rerun.

**Open-next:** when LCC_PD_fBVOClccPD is processed (~1–2 Nov), rerun the notebook. If the artefact depends on the land (R > 0.5), consider design A in FUT.

**Files changed:** `cases-scripts/14e-…`, `cases-scripts/24e-…` (new), `cases-scripts/auto_launch_new_chain.sh`, `diagnostics/fbvoc-prescription-artefact/how_big_artefact_is_PD.ipynb` (new), `CLAUDE.md`, `cases-scripts/run_aliases.csv`, `cases-scripts/README.md`, `diagnostics/README.md`.

</div>

<div style="color:#7B2FBE">

## 2026-10-30 · 15:49 → 15:52 (3 min) · session 634a8b84

**Goal:** what LCC_PD_fBVOCctrlPD − CTRL_PD_fBVOCctrlPD measures.

**Done:** explained: the forest effect with BVOC emissions held fixed; BVOC effect = total − that. Nothing changed.

</div>

<div style="color:#999999">

## 2026-10-30 · 13:34 → 13:45 (11 min) · session 9251b358

**Goal:** structured recap of the MEGAN γ residual; how its three terms are calculated.

**Done:** recap given in chat (source: `analysis/MEGAN_ATTRIBUTION.md`); explained how Δln γ_eff, Δln GAMMA and Σ Δln γ_i are computed (code: `megan_maps.py`). Nothing changed.

**Found:** in cells with a single plant type γ_eff and GAMMA should be equal but differ by up to ±10–14 %; cause not yet known.

**Open-next:** find why γ_eff ≠ GAMMA in single-plant-type cells (affects the composition vs γ_eff split and the weighting panel of the current figures, not the exact LMDI split).

</div>

<div style="color:#008080">

## 2026-10-30 · 11:15 → 12:10 (55 min) · session bdaee31b

**Goal:** answer "how much warmer are the FUT simulations?" with a notebook.

**Done:**
- New notebook `diagnostics/how-warmer-future-climate-is/how_warmer_future_climate_is.ipynb` (run, outputs saved; tables and figures in `how_warmer_future_climate_is_outputs/`). Listed in `diagnostics/README.md`.

**Found:**
- Explained (you asked): FUT does not simulate the ocean. It reads a 12-month sea-surface-temperature and sea-ice file (mean of 2090–2100 from a NorESM2 SSP5-8.5 run) and repeats it every year. So the ocean warming is an input, and the ocean cannot respond to the forest expansion.
- FUT − PD, 2-m air temperature, annual, 2001–2014: global **+3.5 K**, land +4.9, ocean +2.9, Arctic **+8.9** (winter +13.6, summer +4.6), land 46–82°N +6.6, forest-expansion cells **+7.4 K**. Every one of the 14 years gives 3.45–3.49 K globally.
- Cause: the FUT runs read the SSP5-8.5 2090–2100 ocean (SST +2.2 K, Arctic September sea ice 5.3 → 0 million km²) and CO₂ 1135 ppm (PD 369).
- Precipitation +3 % globally, +23 % on land 46–82°N.
- **Relative to pre-industrial** (you asked; new section in the notebook): about **+3.9 K** globally, +8.4 K where the forest expands. This adds NorESM2-LM's own warming from 1850–1900 to 1995–2005 (+0.4 K, from its CMIP6 historical runs). Check: the coupled NorESM2 run gives the same FUT − PD as ours (3.46 vs 3.48 K). NorESM2 warms less up to 2000 than observed (~0.4 vs ~0.8 K); with the observed value it would be ~4.2 K. The Arctic estimate (+10.5 K) is less reliable: our PD Arctic is 3.6 K colder than in the coupled model.

**Open-next:**
- Rerun on the new-chain CTRL runs when they are archived.
- Stop the Jupyter server I started by mistake on the login node: `kill 1758272` (I was not allowed to).

**Files changed:** `diagnostics/how-warmer-future-climate-is/how_warmer_future_climate_is.ipynb` (new), `diagnostics/README.md`.

</div>

<div style="color:#999999">

## 2026-10-30 · 10:56 → 11:19 (23 min) · session 421cf33f
**Goal:** status of runs and open items; then write the replay verdict, check the LCC MEGAN test, explain MEGAN batch 1 and the fixed-BVOC options.

**Done:**
- Status: the four nudged runs finish tonight (FUT ~21–22 h, LCC_PD ~00:30) and early 1 Nov (CTRL_PD).
- Replay verdict written in `fbvoc_artefact_causes.ipynb` (H5 + summary): the climatology causes the +3 % SOA; prescribing as such adds at most ~0.5 %.
- LCC 5-day MEGAN test checked (section 6 of `megan_patch_branch_5day_test.ipynb`): passed. One thing it cannot show: bit-identity with its parent (no half-hourly output in that parent).

**Open-next:** your choice for the fixed-BVOC runs (and whether to pause tonight's two launches); OK for MEGAN batch 1 once the scripts for it are written.

**Files changed:** `fbvoc_artefact_causes.ipynb` (text only), `megan_patch_branch_5day_test.ipynb` (new section 6, rerun), `diagnostics/README.md`, both logs.

</div>

<div style="color:#999999">

## 2026-10-29 · 14:10 → 14:12 (2 min) · session 4b5c7d6f
**Goal:** fix `analysis/cumulative_radiative_decomposition.ipynb`; explain the open decision on `sandbox/test_titles_outputs/`.

**Done:**
- Notebook: nothing to fix. It was rerun at 11:29; all 7 code cells have outputs, no errors, and no code it uses has changed since. The "needs a rerun" line in the summary was out of date (corrected).
- Figure titles: nothing to decide. The new titles are already in the paper figures, because the analysis rerun on 28 Oct (21:52–00:46) used the updated code. Checked two of them: "fsds_split: LCC − LCC_fBVOC (2001–2014)" and "Ghan decomposition, LW: LCC_PD − CTRL_PD (2001–2014)". The "waiting for your OK" line was out of date (corrected).

**Open-next:** nothing new.

**Files changed:** both logs.

</div>

<div style="color:#999999">

## 2026-10-29 · 13:57 → 13:58 (1 min) · session 4b5c7d6f
**Goal:** overview of what is open right now.

**Done:** read both logs and the job queue. Five runs are going: CTRL_PD, LCC_PD, CTRL_FUT, LCC_FUT (new chain) and the replay test `CTRL_PD_fBVOCctrlPD_HR`. No files changed.

**Open-next:** see the summary in the chat (waiting on the runs; commit; OKs for paper figures and the MEGAN test runs; rerun of `cumulative_radiative_decomposition.ipynb`).

**Files changed:** both logs.

</div>

<div style="color:#A84300">

## 2026-10-29 · 13:13 → 16:47 (214 min) · session 6cf483eb
**Goal:** show the residual split in the MEGAN attribution figures, then plan how to remove the residual, since the split by factor will be a paper result.

**Done:**
- Attribution figures redone with the residual split into weighting + co-variation (notebook rerun, no errors), then again with fixed colour scales: PD ±60, FUT ±100 (13:54).
- New `analysis/MEGAN_ATTRIBUTION.md`: what the figure shows, where the residual comes from (toy example, real grid cell), its two parts, all options with method, cost and verdict, the step-by-step workflow, the list of output fields, and the 5-day test.
- Decisions (yours): exact split (option 1) on **7 alternate years** (2002, 2004, …, 2014; the odd years can be added later if the uncertainty is too large): half the cost of all 14 (≈ 96,000 CPU hours for PD, ≈ 3 days); runs in **batches of 3 years**; sequential vs overlapping batches decided after the 5-day test.
- 5-day test: case script written (checks now in the notebook `diagnostics/megan-exact-split-test/megan_patch_branch_5day_test.ipynb`); first launch stopped by its own safety check (a harmless setting), fixed; the run then failed at start-up because the nudging reader started from the 2000 data file instead of 2005 (a setting copied from CTRL_PD that only works for a continuing run); fixed in the case and the script, **resubmitted (job 1784026)**. Proposed (waiting for your OK): a second 5-day test without the usual monthly outputs (only what the split and the checks need), as the production runs would be. You agreed (keep only MEGAN-related output); this is the setup for the production runs (no separate test needed: each year is checked against CTRL_PD anyway). **First result: the copy is identical to CTRL_PD, bit for bit** (emissions at every half hour of 1–4 January 2005), so it is the same run, not a new ensemble member. New notebook `diagnostics/megan-exact-split-test/megan_patch_branch_5day_test.ipynb` documents the whole test (all five checks): identical at all 240 half-hour steps of the 5 days. Other checks passed too (all fields there, the factors multiply exactly); but writing the extra output makes the model **4× slower**, so option 1 costs ≈ 191,000 CPU hours for PD (≈ 2 % of what is left; ≈ 4 % with FUT) and ≈ 5–6 days per experiment. The doc has the measured numbers. Why not restart the main runs with the new output instead: if the test shows the copies are identical to the originals (same numbers bit for bit), they are the same run, not a different ensemble member, and restarting would lose ≈ 30,000 CPU hours and delay everything; if they are not identical, we discuss restarting.

**Found:**
- The residual is not a model error: CLM multiplies the factors per plant type and half hour, but saves only monthly grid-cell averages. CLM can save the factors per plant type with output settings only, no code change.
- The exact split means rerunning 2001–2014 of CTRL and LCC (PD, later FUT) with one extra output tape: ≈ 48,000–72,000 CPU hours for PD (≈ 1 % of what the project has left). Options 2 and 3 would need the same runs, so they are not cheaper.
- CTRL and LCC have different lists of plant-type patches (LCC changes which plant types exist), so the split pairs them by grid cell + plant type.
- 14 years, not 15: the runs cover 2000–2014, but 2000 is spin-up and dropped.

**Open-next:** 5-day LCC_PD copy done (job 1784064) (to test the split code on a real CTRL + LCC pair); the split script (`postprocess/megan_lmdi/`) now **works on the real CTRL + LCC pair**: all checks pass and the factors add up exactly to the emission change, with no residual (it also found one rare case where CLM itself switches the emission off; that now has its own category); next: add the replay, then the batch scripts that shrinks the big daily files and computes the split, tested on the test output; then, with your OK, the 3-year batches once the new-chain CTRL_PD and LCC_PD are archived.

**Files changed:** `postprocess/megan_lmdi/reduce_megan_lmdi.py` + `README.md` (new), `cases-scripts/tests/14a-…-meganpatch-5day.sh` (new), `analysis/MEGAN_ATTRIBUTION.md` (new), `analysis/PLOTTED_VARIABLES.md`, `analysis/README.md`, `src/boreal_forest_expansion/plotting/megan_maps.py`, `analysis/megan_factor_maps.ipynb`, `results/figures/megan_factors/`, `cases-scripts/tests/13a-…-meganpatch-5day.sh` (new), `diagnostics/megan-exact-split-test/megan_patch_branch_5day_test.ipynb` (new), `diagnostics/README.md`, `cases-scripts/run_aliases.csv`.

</div>

<div style="color:#999999">

## 2026-10-29 · 12:03 → 12:57 (54 min) · session d5c587e4
**Goal:** make the log easier to read in the Markdown preview.

**Done:** blank lines between items (box and blocks); every entry coloured by topic, with a legend under the title (colours chosen by you: artefact purple, CO₂ fix golden, waiting on you red label, diagnostics teal, analysis dark orange, run status light grey, run setup / archiving / postprocessing dark grey, preprocessing olive, figure style rose, housekeeping light grey). Text unchanged (checked against a backup). Rules added to `CLAUDE.md`.

**Files changed:** `docs/CLAUDE_log_human.md`, `docs/CLAUDE_log.md`, `CLAUDE.md`.

</div>

<div style="color:#7B2FBE">

## 2026-10-29 · 11:58 → 13:22 (84 min) · session f3016b9d
**Goal:** prepare the 14-year fixed-BVOC control (the replay test is now with another session) and automate postprocessing of the new runs.

**Done:**
- 14c script set to the new chain, 15 years; the auto-launcher now starts it together with the other fixed-BVOC runs.
- Coupler check: disabling MEGAN only removes its 19 emission fields; nothing else changes. Now in the causes notebook (section H1e, by the session that owns it). The replay there uses one-year emission files, so no model code change is needed.
- Auto-launcher now also postprocesses every new-chain run when it finishes, one at a time. It first moves that run's old results to the archive folders: 2001–2009 files to `2001-2009-pre-co2-fix/`, the rest, incl. the old 2-year test, to `2001-2014-all-bvoc-pre-co2-fix/`. Tested on dummy files.
- Auto-launcher restarted twice (12:49, 13:02); the 12:45 copy crashed when its script was edited while it ran; nothing was launched or lost.
- Option to fix or work around the artefact chosen (open since 2026-10-29 11:52).
- Moving the old 2-year results before postprocessing made automatic (opened earlier in this block).

**Open / next:** until all runs of a comparison are redone, the results folder mixes old and new runs: don't compare across them. The analysis still has to be switched to the new runs by hand.

**Files changed:** `cases-scripts/14c-…ctrl_fBVOCctrlPD….sh`, `cases-scripts/auto_launch_new_chain.sh`, new `postprocess/postprocess_new_chain_run.sh`, `CLAUDE.md`, `cases-scripts/run_aliases.csv`, `cases-scripts/README.md`.

</div>

<div style="color:#7B2FBE">

## 2026-10-29 · 11:48 → 11:52 (4 min) · session f3016b9d
**Goal:** know the options to fix the fixed-BVOC artefact, and whether the cause is needed first.

**Found:** (1) compare LCC_fBVOC with the fixed-BVOC control run (needs no cause; longer control run would reduce noise); (2) also prescribe the LCC run's own emissions so both sides are prescribed (needs no cause, one new run); (3) prescribe the real time-varying emissions instead of the average year (depends on the cause; the test run also checks it); (4) change MEGAN in the land model (too much work).

<span style="background:#CC0000;color:#FFFFFF;padding:0 4px;border-radius:3px">**WAITING ON YOU**</span> <span style="color:#CC0000">**Open / next:** choose for the 13:00 meeting; OK needed for a 3-year replay test.</span>

**Files changed:** logs only.

</div>

<div style="color:#A84300">

## 2026-10-29 · 11:27 → 11:30 (3 min) · session ac14246f
**Goal:** restore the results of the cumulative radiative decomposition notebook.

**Done:** reran it in place: no errors, results saved inside it again. Table identical to last night's; the 2 figures were rewritten.

**Files changed:** `analysis/cumulative_radiative_decomposition.ipynb`, its 2 figures in `results/figures/cumulative-radiative-decomposition/`.

</div>

<div style="color:#999999">

## 2026-10-29 · 10:47 → 10:50 (3 min) · session ac14246f
**Goal:** check whether parallel sessions overwrote any notebook.

**Found:** all notebooks keep their cells and results, except `analysis/cumulative_radiative_decomposition.ipynb`. Its code is the right version, but it was run and saved at 10:22 while `derived.py` had stray null bytes. It now shows an import error and no results. Figures and CSV from 00:04 are untouched.

**Open / next:** rerun that notebook (waiting for OK).

**Files changed:** logs only.

</div>

<div style="color:#7B2FBE">

## 2026-10-29 · 10:22 → 13:40 (198 min) · session ed68c0d4
**Goal:** check the CTRL_PD_fBVOCctrlPD test run, find what in the emission prescription raises SOA, and start the replay test.

**Done:**
- Run finished (10:17) and archived. Postprocessed with 2000 dropped → 2001–2002 files (BVOC, SOA, CHEM, CLOUDPROP, RADIATIVE).
- Fixed two problems that stopped the automatic chain: files saved in the wrong folder (moved, script fixed); a damaged source file (`derived.py`, 2 stray null bytes at the end, removed).
- Artefact notebook rerun, no errors. Fixed-BVOC artefact test done (open since 2026-10-28).
- New notebook `fbvoc_artefact_causes.ipynb`: 3 causes tested (H1–H3), SOA budget (H4), replay section ready (H5), synthesis figure at the end.
- Test run decided and launched (open since this block, 12:00): replay run `CTRL_PD_fBVOCctrlPD_HR` (script 14d) with CTRL_PD's actual emissions of 2000, 2001, 2002. Its 57 emission files were made and checked; submitted at 13:20 (three 1-year jobs, ~1 day + queue); a watcher postprocesses it and reruns the notebook automatically.

**Found:**
- Prescribing the emissions alone raises SOA by ~3 % (global +3.0 %, ≥45°N +3.0 %), 62–74 % of the LCC − LCC_fBVOC SOA drop. Based on 2 years only.
- Not a missing species, not a timing shift. The missing day-to-day weather makes isoprene live 10–28 % longer north of 45°N.
- **SOA budget:** same SOA production (−0.02 %), but SOA lives 3 % longer; the extra SOA sits at 400–100 hPa everywhere. In the tropics the SOA-forming gas moves up (less at 850–700 hPa, more at 500–150 hPa). Likely cause (not proven): with an average emission, precursors are also emitted on convective days and lifted before they react, so SOA forms higher and is washed out more slowly.

<span style="background:#CC0000;color:#FFFFFF;padding:0 4px;border-radius:3px">**WAITING ON YOU**</span> <span style="color:#CC0000">**Open / next:** decide how to correct or present the fBVOC contrasts (still open). The replay result (expected tomorrow) will say whether the average emissions (climatology) or the prescription itself is the cause.</span>

**Files changed:** new `diagnostics/fbvoc-prescription-artefact/fbvoc_artefact_causes.ipynb` (+ `_outputs/`), `run_replay_when_done.sh`; new `cases-scripts/14d-NF2000norbc_tropstratchem_nudg_ctrl_fBVOCctrlPD_HR_f19_f19.sh`; `run_when_done.sh` (output path); `src/boreal_forest_expansion/postprocess/derived.py` (null bytes removed); `run_aliases.csv`, `cases-scripts/README.md`, `preprocess/bvoc-emissions/README.md`, `CLAUDE.md` (new run row); 57 new `ems_<CTRL_PD>_Y-Y_*` files in the shared bvoc_emissions folder.

</div>

<div style="color:#62733B">

## 2026-10-29 · 10:39 → 10:42 (3 min) · session d327ae8c
- Both notebooks have run; results are saved inside them.

</div>

<div style="color:#62733B">

## 2026-10-29 · 10:14 → 10:38 (24 min) · session d327ae8c
- Seasonal BVOC maps: zero flux is now white.
- New table of the 19 BVOC species: emissions, aerosol vs chemistry role, linear or not, warming or cooling (from the model code).

</div>

<div style="color:#A84300">

## 2026-10-28 · 23:45 → 00:06 (21 min) · session 94d8cfc5
**Goal:** fix and run the cumulative radiative notebook (supervisor's P1–P5 overview).

**Done:** notebook connected to the 4 real runs (2001–2014), checks added, uncertainty over years added, run with outputs saved; figures + table exported; README updated.

**Found:** ≥45°N net TOA: background +1.01 ± 0.18, forest biophysics +0.14 ± 0.05, BVOC +0.14 ± 0.04, total +1.29 ± 0.16 W m⁻² (old chain, CO₂-bug FUT land spin-up → provisional).

**Open-next:** discuss the rest of the P1–P5 chart: P3 needs LCC_FUT_fBVOClccPD (planned); CO₂ and O₃ steps have no runs.

**Files changed:** analysis/cumulative_radiative_decomposition.ipynb, analysis/README.md, results/figures/cumulative-radiative-decomposition/, results/tables/cumulative_radiative_decomposition_2001_2014.csv

</div>

<div style="color:#A84300">

## 2026-10-28 · 23:12 → 00:33 (81 min) · session 314da964
**Goal:** understand the PD BVOC maps (LCC_PD − LCC_PD_fBVOCctrlPD).

**Done:** compared the three PD runs by latitude band and season; wrote and launched the test run `CTRL_PD_fBVOCctrlPD` (script 14c, 3 years; first set to 2, back to 3 before the job started); notebook `fbvoc_prescription_artefact.ipynb` (tables, verdict, 3 figures), tested with a stand-in run; automatic postprocessing + rerun when the run is archived; added an evidence section (why we suspect an artefact) with two new figures.

**Found:** emissions match CTRL_PD within 0.05 %, but SOA is +2.9 % (global) in the fixed-BVOC run. LCC − fixed-BVOC SOA is −4.2 %, while LCC − CTRL is only −1.4 % (about −0.5 % north of 45°N).

**Open-next:** check around 12:00 that the notebook was rerun with the test run (`run_when_done.log`); postprocess it when done and compare with CTRL_PD for 2001–2002; then SOA budget, missing-species and diurnal-timing checks.

**Files changed:** `cases-scripts/14c-…ctrl_fBVOCctrlPD….sh` (new), `cases-scripts/run_aliases.csv`, `cases-scripts/README.md`, `CLAUDE.md`, `diagnostics/README.md`, new `diagnostics/fbvoc-prescription-artefact/`.

</div>

<div style="color:#A84300">

## 2026-10-28 · 23:30 → 00:48 (78 min) · session 7dc91df2
**Goal:** check the cloud-type figures; add the emission-source row to the LCC − fixed-BVOC grids; run the notebook.

**Done:** row `LCC_FUT_fBVOCctrlFUT − LCC_FUT_fBVOCctrlPD` added to every LCC − fixed-BVOC grid; `bvoc-soa-cloud-interactions.ipynb` run with outputs saved (no errors); 8 new figures in `results/figures/`. Cloud-type analysis done (open since 23:26).

**Found (summer, north of 45°N, old runs):** future BVOC effect: liquid water path +4.6 g m⁻², low cloud +0.33 %-points, mid +0.43, high −0.28. The emission-source row alone gives +5.2 g m⁻² and the same cloud pattern; LCC with its own future emissions gives −0.6 g m⁻². So the future BVOC cloud signal is the climate-driven emission increase, not the forest change. The rows add up (4.57 + 0.62 = 5.19 vs 5.18).

**Done:** vertical-profile figures: non-significant cells now hatched like the maps (tested in sandbox).

**Done:** cloud and biogeophysical-hydro notebooks rerun (00:46, no errors): profile figures hatched, hydro grids and water budget have the 4th row. In the modified cells the emission-source row also gives the drop in ET and rain (about −7 mm yr⁻¹), like the future BVOC row.

**Open / next:** nothing pending from this session.

**Files changed:** `forcing_maps.py`, `bvoc-soa-cloud-interactions.ipynb`, `PLOTTED_VARIABLES.md`, `analysis/README.md`, `sandbox/test_cloud_types.py`.

</div>

<div style="color:#A84300">

## 2026-10-28 · 23:10 → 23:26 (16 min) · session 7dc91df2
**Goal:** add an analysis of cloud types (low vs high clouds).

**Done:** new figures: maps of total/low/mid/high cloud + liquid and ice water path (annual and JJA), monthly cycles per cloud type, and latitude–height profiles of cloud fraction, liquid and ice. Added as section 3 of `bvoc-soa-cloud-interactions.ipynb`.

**Open / next:** look at the test figures; then run the notebook (needs OK).

**Files changed:** `src/.../plotting/forcing_maps.py`, `analysis/bvoc-soa-cloud-interactions.ipynb`, `analysis/PLOTTED_VARIABLES.md`, `analysis/README.md`, `sandbox/test_cloud_types.py`.

</div>

<div style="color:#A84300">

## 2026-10-28 · 23:17 → 00:34 (77 min) · session 75b1ee7c
**Goal:** understand the MEGAN attribution maps; complete and restyle the MEGAN figures.

**Found:** PD monoterpenes (LCC_PD vs CTRL_PD, annual): the +0.9 % change ≥45°N = +1.8 % from more/different trees (composition) − 0.9 % from lower per-leaf activity. Temperature +1.5 %, LAI −0.6 %; the −1.8 % residual comes from averaging, not from a process: −0.7 from weighting patches by area instead of by emission, −1.1 from factors that peak together (summer, midday) being averaged separately. Isoprene JJA: residual −9.4 = −7.8 + −1.6. Example cell (50°N 110°E): the four saved γ maps multiply to +22 %, the true activity changed +3 %, so the residual is −19. The `megan_factors/` set had only 2 of the 8 change/attribution figures.

**Done:** MEGAN maps restyled like the other maps; all 20 figures made (16 change/attribution + 4 field maps) in `results/figures/megan_factors/`.

**Done:** residual now split into weighting + co-variation (third row of the attribution maps); tested in the sandbox.

**Open / next:** rerun the MEGAN notebook with the split (waiting for OK). FUT MEGAN results wait for the new runs.

**Files changed:** `analysis/megan_factor_maps.ipynb`, `src/.../plotting/megan_maps.py`, `src/.../plotting/forcing_maps.py` (two optional arguments), `sandbox/test_megan_style.py`.

</div>

<div style="color:#A84300">

## 2026-10-28 · 21:09 → 23:58 (169 min) · session b74a1ef9
**Goal:** add the new output fields to the postprocessing; rerun the analysis on the 2001–2014 all-BVOC set.

**Done:** pd-fut-attribution findings rewritten for the 2001–2014 set; new fields + categories BVOCOX, AERSIZE, SURFEXCH; recommendation (open since 20:37) applied; 7 surface-exchange files made and checked. Analysis switched to 2001–2014 with the all-species fBVOC runs; fBVOC − CTRL dropped, CTRL_FUT − CTRL_PD added; new notebook `analysis/fut-fbvoc-emission-source.ipynb` (row 3 = fBVOCctrlFUT − fBVOCctrlPD).

**Found:** the 7 processed runs (old chain) have none of the new CAM fields and only RSSUN/RSSHA of the new CLM ones. The `pd-fut-attribution` findings text was written on the old 2001–2009 set and is now flagged as not revised.

**Open-next:** recheck these findings on the CO₂-fix chain; revise the findings text; process the new categories once the new-chain runs are archived.

**Files changed:** `src/.../postprocess/variables.py`, `postprocess/run_all_parallel.sh`, `docs/history-output/added_fields_20261028.csv`, `src/.../plotting/forcing_maps.py`, `megan_maps.py`, the 5 `analysis/*.ipynb` + new one, `analysis/README.md`, `PLOTTED_VARIABLES.md`, `CLAUDE.md`.

</div>

<div style="color:#555555">

## 2026-10-28 · 20:37 → 20:40 (3 min) · session b74a1ef9
**Goal:** decide which new output fields the postprocessing should keep.

**Done:** recommendation (see chat).

**Open-next:** your OK → edit `variables.py`, run on the new-chain runs once archived.

**Files changed:** logs only.

</div>

<div style="color:#555555">

## 2026-10-28 · 18:50 → 21:30 (160 min) · session 14b55ad1
**Goal:** status of the simulation versions in the archive; tidy it up.

**Done:** moved the 4 pre-all-BVOC runs (CTRL `-20260925` ×2, `_IM` fixed-BVOC `-20261008/09`) into `c-before-all-bvoc/`; dropped the _IM runs from postprocessing; the old ISOP/MTERP emission script now reads from the new location. Postprocessing of the 7 current pre-CO₂-fix runs started (2001–2014). 12 diagnostics notebooks point to the moved runs (same years, outputs unchanged); new `diagnostics/README.md`. D1/D2 copies for the CO₂-fix chain made (not run). Redrew 4 figures in the current style to check it (scratchpad only); found a few small style issues; new mean ± CI number format applied in `forcing_maps.py` (CI with 1 significant digit, e.g. +0.016 ± 0.002, +0.47 ± 0.02; zero-within-CI as 0.00 ± 0.01; small values (−2.4 ± 9.1) ×10⁻³; values ≥ 1 with 3 significant digits, +12.3 ± 1.6). Plot code + sandbox style-test notebooks committed (aa612b7, not pushed; output folders left out and now in `.gitignore`). Copied to NIRD (checked complete) 7 runs that were only on /cluster/work: LCC `-20261005` ×2 (years 2010–2014 were missing), CTRL `-20261023` ×2, fixed-BVOC `-20261025` ×3.

**Found:** 4 new-chain runs running. Test runs and an aborted land-only run (`I2000…-20260924`, stopped at year 51) left on /cluster/work only.

**Open-next:** OK to add automatic postprocessing to the launcher? Confirm with the other session what happens to the relaunched runs and the auto-launcher; check the postprocessing output; run the new D1/D2 and rerun the FUT-fBVOC decomposition on the new chain (fill in the TODO case names); move old-chain runs into `d-before-co2-fix/`? (your call).

**Files changed:** `postprocess/run_all_{parallel,postprocessing}.sh`, `preprocess/bvoc-emissions/prescribe-just-ISOP-MTERP/create_bvoc_emissions_climatology.sh`, `src/.../plotting/forcing_maps.py` (number format), 12 notebooks in `diagnostics/` (paths only), new `diagnostics/README.md`, `CLAUDE.md`, `.gitignore`, logs.

</div>

<div style="color:#E58AA5">

## 2026-10-28 · 18:44 → 21:02 (138 min) · session ff448ee2
**Goal:** recap plot settings; fix colourbar ticks.

**Done:** outer tick near the bar end; ×10ⁿ from 10⁻² (10⁻³ tried, reverted) and moved above the bar; bigger mean numbers under grid maps; wrong panel titles 'activated effective radius / droplet number' corrected to 'cloud droplet effective radius' / 'cloud droplet number concentration' (ACT = Average Cloud Top in CAM); grid column titles bigger (11.5 pt), long ones on two lines; 'aerosol number' → 'aerosol number concentration'. New docs: `postprocess/POSTPROCESSING.md` (what the postprocessing does) and `analysis/PLOTTED_VARIABLES.md` (what every figure panel shows and how it is calculated, now with the model long names). Ghan terms renamed everywhere: F_TOTAL, F_AEROSOL-DIRECT, F_CLOUD, F_REST (variables `*_toa`, `*_dir`, `*_cloud`, `*_rest`); old processed files still load.

**Open-next:** layout option choice; SNOW_PERSISTENCE bug; readable figure-title names (hydro, surface_energy); fsds_split: make it a surface version of the Ghan split?; add the missing SOA burden fields (cb_SOA_A1, cloud-borne SOA) to the runs not yet started?; paper figures wait for OK.

**Files changed:** `src/boreal_forest_expansion/plotting/forcing_maps.py`, `postprocess/POSTPROCESSING.md` (new), `postprocess/README.md`, `analysis/PLOTTED_VARIABLES.md` (new), `analysis/README.md`, `src/boreal_forest_expansion/postprocess/derived.py`, `CHANGES.md`, `analysis/pd-fut-attribution.ipynb` (code only, not rerun)

</div>

<div style="color:#E58AA5">

## 2026-10-28 · 15:45 → 17:10 (85 min) · session 88725d5f
- **Goal:** tidy map style and layout of all analysis figures; choose a font. All tested in the sandbox.
- **Done:** italic *Under the maps:*; tiny means as 8.2 × 10⁻⁴; colourbar numbers 10 pt, labels 8 pt; font Cantarell (`style.py`). Font comparison `sandbox/test_fonts.ipynb` (11 fonts). Map figures rebuilt on a fixed layout: same gap between all maps, more room between rows and under the title, each colourbar under its own map. New `sandbox/test_layout_all_figures.ipynb` draws one of each of the 18 analysis figure types (all checked; fixed: panel titles further from the maps and more vertical space, mean centred between map and colourbar, title closer to the maps, colourbars longer/thicker with 5 values and ×10ⁿ labels that don't overlap, crowded labels in the bar charts, ×10ⁿ axis numbers); `sandbox/test_layout_options.ipynb` shows 3 layouts (compact / current / airy) to choose from; `sandbox/test_palettes.ipynb` shows 6 colour palettes for the bar/line charts, with a colour-blindness check.
- **Found:** snow persistence differences look wrong (thousands of days, colour scale ±40 000 days): probably a bug in that derived variable, not checked yet. The automatic layout gave columns different gaps (sized by each column's longest text). Computer Modern font is broken here; Cantarell has no italic. Another session edits titles in the same file.
- **Open/next:** pick a layout (A/B/C or a mix) (chart palette: keep the current one, decided 17:05); check every figure from the layout notebook (line/bar charts too); then, when you say so, rerun the analysis notebooks (they first need to point to the archived 2001–2009 data).
- **Files changed:** `src/.../plotting/forcing_maps.py`, `src/.../plotting/style.py`, `sandbox/test_overall_map_mean.ipynb`, `sandbox/test_fonts.ipynb`, `sandbox/test_layout_all_figures.ipynb` (+ output folders), fonts in `~/.local/share/fonts/plot-tests/`, both logs.

</div>

<div style="color:#E58AA5">

## 2026-10-28 · 16:36 → 16:40 (4 min) · session dbf31f1f
**Goal:** your follow-up on the titles.

**Done:** title order is now figure first, then contrast and years; the hatching notes in the notebook intros are back.

**Open-next:** regenerate results/figures once you OK it (the notebooks must first read the archived 2001–2009 files; open since 16:08).

**Files changed:** `src/.../plotting/forcing_maps.py`, `sandbox/test_titles.ipynb`.

</div>

<div style="color:#E58AA5">

## 2026-10-28 · 15:58 → 16:08 (10 min) · session dbf31f1f
**Goal:** apply your comments on the figure texts.

**Done:** contrast names spelled out (LCC − LCC_fBVOC, LCC_fBVOC − CTRL); titles without "context"/"contrasts"; Ghan subtitles TOTAL / AEROSOL-DIRECT / CLOUD / REST; hatching sentence removed from 4 notebook intros. Two test figures in `sandbox/test_titles_outputs/`.

**Found:** "CRE" in the cloud panel = cloud radiative effect (Ghan cloud term), not an aerosol term.

**Open-next:** regenerate results/figures (4 analysis notebooks) once you OK it; they first need to read the archived 2001–2009 files.

**Files changed:** `src/.../plotting/forcing_maps.py`, `analysis/*.ipynb` (markdown only), `sandbox/test_titles.ipynb`.

</div>

<div style="color:#555555">

## 2026-10-28 · 15:17 → 17:25 (128 min) · session a7f48415
- **Goal:** settle the open decisions; automate the fixed-BVOC runs on the new chain; check the new runs; equilibrium check of the coupled spin-ups.
- **Decided (you):** LCC_FUT without half-hourly BVOC output; fixed-BVOC runs automated; isoprene/monoterpene-only runs (`_IM`) dropped; the 4 analysis notebooks wait for your go.
- **Done:** LCC_FUT BVOC output: nothing to change (open since 13:50 today). The launcher now also runs the fixed-BVOC part (open since 2026-10-25): when CTRL_PD, CTRL_FUT or LCC_PD finishes, it builds the emission files, checks them, and starts LCC_PD_fBVOCctrlPD + LCC_FUT_fBVOCctrlPD, LCC_FUT_fBVOCctrlFUT, LCC_FUT_fBVOClccPD. Tested on copies; swapped in at 15:49 without interrupting anything. CTRL_FUT and LCC_FUT checked: all new output fields requested, started from the new spin-ups, no errors (open since 13:50). LCC_PD started 15:37. Run tables updated in CLAUDE.md and `run_aliases.csv` (open since 13:50).
- **Found:** the "98 % full" is the NS9188K project space on NIRD (7.6 TB free), not the whole NIRD.
- **Found (spin-up equilibrium notebook):** the CTRL/LCC spin-up mismatch is gone. Away from the new forests, LCC − CTRL vegetation carbon is now +0.04 % (PD) and −0.06 % (FUT), against +14.5 % and −39 % in the old runs. The old CTRL spin-ups were still building up carbon. The new spin-ups still drift slowly (carbon pools 0.1–1 % per decade, water storage ±0.1 %), but CTRL and LCC drift together.
- **Done:** BVOC-emission plot notebook ran (open since 2026-10-25); it still shows the old CTRL emission files.
- **Found (16:20):** `check_CO2_bug_in_land_only.ipynb` (now in `check-CO2-bug-in-spinups/`) describes the old, superseded runs; everything in it except its written summary is repeated, with the new regions, in the six-variables notebook. Two files still point to the old folder name.
- **Done (17:25):** the CO₂-bug notebooks are now one: the six-variables notebook holds the full record of the old chain (its summary now also covers sections 1–7, with the current regions); the older notebook and its outputs are deleted (still in git history). The old D1 "Total" results are kept as a record in `D1_farfield_check_outputs/old-chain-with-Total_2026-10-21/` (open since 2026-10-21).
- **Found (17:25):** with the current regions, the old FUT recovery fit says vegetation carbon would never catch up with CTRL (the old summary said ~160 years).
- **Open/next:** rerun the equilibrium notebook after CTRL_PD's spin-up ends; recompute D1 Total on the new runs; ozone kernel: first check how much ozone changes; decide whether to keep the CO₂-bug notebook as a record or fold it into the six-variables one (~05:00 29 Oct; only 15 of 20 years now) and the plot notebook once the new emission files exist; switch postprocessing to each new run once it is archived
- **Files changed:** `cases-scripts/auto_launch_new_chain.sh`, `14b/24b/24c/24d` scripts (spin-up), `run_aliases.csv`, `CLAUDE.md`, `preprocess/bvoc-emissions/README.md` + `plot_bvoc_emissions.ipynb`, new `check-equilibrium-after-co2-fix/check_coupled_spinup_equilibrium_after_co2_fix.ipynb`, both logs.

</div>

<div style="color:#AAAAAA">

## 2026-10-28 · 14:05 → 15:25 (80 min) · session f67e4e59
**Goal:** status of the nudged runs; a table of all run aliases.

**Done:** status check (no run of the new chain is archived yet); new table `cases-scripts/run_aliases.csv`: every run (spin-ups, MET, nudged, fixed-BVOC) with its alias from the chain figure, old and new version, case name, years, status, parent runs (checked in each case's settings) and where the processed files are. The ISOP/MTERP-only run scripts (LCC_PD_fBVOCctrlPD_IM, LCC_FUT_fBVOCctrlPD_IM and their 2-day test) moved to `cases-scripts/just-ISOP-MTERP/`; paths fixed, README/CLAUDE.md updated. After your renumbering (all-species fixed-BVOC runs now 14b, 24b, 24c, 24d; quick spin-ups in `quick-spinups/`) the table, CLAUDE.md, the scripts README (run list rewritten with the figure names), the postprocessing comments and the emissions README all use the new numbers. The watcher is not affected.

**Decided:** the future fixed-BVOC run with LCC emissions is `LCC_FUT_fBVOClccPD` (present-day LCC emissions), as in the scripts; the figure label is wrong. The early preliminary nudged runs stay out of the table. Old processed files covering 2001–2014 go to `2001-2014-pre-co2-fix/` (written in CLAUDE.md).

**Open-next:** the 1-day test scripts in `tests/` still carry the old numbers (rename them?).

**Files changed:** `cases-scripts/run_aliases.csv` (new); `cases-scripts/just-ISOP-MTERP/` (3 moved scripts); `cases-scripts/README.md`; `CLAUDE.md`; `postprocess/run_all_*.sh` and `forcing_maps.py` (comments); `preprocess/bvoc-emissions/README.md`; `tests/*-1day.sh` (header line).

</div>

<div style="color:#AAAAAA">

## 2026-10-28 · 13:50 → 13:55 (5 min) · session a7f48415
- **Goal:** list what still has to be decided and checked, across open sessions and logs.
- **Done:** list given in chat. The launcher is running again and is setting up CTRL_FUT; LCC_FUT (24a) is next.
- **Open/next:** decide on 24a's BVOC output before it starts; update the run-versions table in CLAUDE.md.
- **Files changed:** both logs.

</div>

<div style="color:#E58AA5">

## 2026-10-28 · 13:10 → 14:01 (51 min) · session 88725d5f
- **Goal:** CI under the maps not bold; test notebooks to `sandbox/`; smaller maps and more white space in the forcing-decomposition figures.
- **Done:** only the mean is bold (e.g. **+0.24** ± 0.04 W m⁻²). Test notebooks + outputs moved to `sandbox/`. Forcing-decomposition figure height 5.2 → 4.4 in (maps smaller, wider gaps, text same size). All checked in the sandbox notebook.
- **Mistake, undone:** I reran `analysis/radiative_forcing.ipynb`, which overwrote 41 figures in `results/figures/`; stopped and restored from the last commit (nothing of yours lost).
- **Found:** the 2001–2009 processed data are now only in `2001-2009-pre-co2-fix/`, so the analysis notebooks fail until they are pointed there; the sandbox notebook already is.
- **Open/next:** decide when to apply the new style to `results/figures/`; point the analysis code to the archive folder (or wait for new data). Commit when you say so.
- **Files changed:** `src/boreal_forest_expansion/plotting/forcing_maps.py`, `analysis/README.md`, `sandbox/test_*` (+ outputs), both logs.

</div>

<div style="color:#555555">

## 2026-10-28 · 13:04 → 14:30 (86 min) · session 273bbdcb
- **Goal:** decide which extra output fields go into the new 15-year runs, and add them before the launcher starts them.
- **Done:** fields added to `cases-setup.sh`: CAM 262 fields (+79), CLM base list 91 (+35). All checked against the field lists of existing runs (PD, FUT, fixed-BVOC). Launcher stopped at 13:15, just before it started CTRL_FUT; restarted 13:49. CTRL_FUT started 14:00 with all 262 CAM fields, land list accepted. CLAUDE.md: name runs by alias (CTRL_PD, LCC_FUT_fBVOCctrlFUT…), not by script number.
- **Found:** 7 of the suggested CLM fields don't exist in our model version, and CLM stops the run on an unknown name. Snow albedo can be computed after all (snow radiation fields exist in CLM). A CTRL nudged run is 57 GB (half-hourly BVOC tape 34 GB, monthly atmosphere 11 GB), an LCC run ~30 GB.
- **Done too:** tables of all output fields with units and descriptions in `docs/history-output/` (CAM 292, CLM 599 variables; 114 added), made from CTRL_FUT's first month.
- **Open-next:** the postprocessing does not know the new CAM fields yet (decide which to add); LCC_FUT, LCC_PD, CTRL_PD launch automatically; when the new runs finish, update run names (version checklist); NIRD is 98 % full.
- **Files changed:** `cases-scripts/cases-setup.sh`, `CLAUDE.md`, both logs.

</div>

<div style="color:#E58AA5">

## 2026-10-27 · 16:58 → 17:10 (12 min) · session 88725d5f
- **Goal:** make the ≥45°N means under the maps readable, and say in a subtitle what they are.
- **Done:** numbers 7.8 → 13 pt, only value ± CI under each map; subtitle under every map-figure title: "Numbers under the maps: area-weighted mean over 45–90°N ± 95 % CI of the yearly means". Test notebook with 4 figure types, all look fine.
- **Found:** an explicit title position made the title overlap the panels; fixed.
- **Open/next:** rerun `radiative_forcing`, `bvoc-soa-cloud-interactions`, `biogeophysical-hydro`, `pd-fut-attribution` to update `results/figures/`. Commit when you say so.
- **Files changed:** `src/boreal_forest_expansion/plotting/forcing_maps.py`, new `analysis/test_overall_map_mean.ipynb` + `analysis/test_overall_map_mean_outputs/`, both logs.

</div>

<div style="color:#008080">

## 2026-10-27 · 16:53 → 16:59 (6 min) · session 23a9fcf4
- **Goal:** show modified cells, all unmodified cells and global land in the plots of two equilibrium notebooks.
- **Done:** `check_land_only_equilibrium_after_co2_fix` (tropics replaced by unmodified land) and `check_CO2_bug_in_land_only_six_variables` (>45°N unmodified and tropics replaced by unmodified land + global land). Both reran without errors; written summaries updated with the new numbers.
- **Found:** land-only runs still all in equilibrium (largest drift ratio 0.17). FUT_LCC and FUT_CTRL are identical on unmodified land. In the old (buggy) FUT runs, LCC − CTRL on unmodified land: TWS +16 mm, soil temperature +0.30 K (5 × the year-to-year noise).
- **Open/next:** the companion notebook `check_CO2_bug_in_land_only.ipynb` still uses the old regions — switch too? Commit when you say so.
- **Files changed:** the two notebooks (+ their output figures/CSVs), both logs.

</div>

<div style="color:#555555">

## 2026-10-28 · 13:59 → 14:02 (3 min) · session 42e247bf
- **Goal:** archive the old processed files, postprocess 14c/24c/24d, explain the aliases.
- **Done:** old 2001–2009 files moved to `2001-2009-pre-co2-fix/` (open since 2026-10-25). Postprocessing scripts now list the three new runs and also make the HYDRO files. New rule recorded: archive the old files each time a run from the new spin-ups is archived.
- **Found:** 14c/24c/24d are only on Betzy (work disk, deleted after 42 days), not on NIRD yet.
- **Open/next:** your OK to postprocess (~20 min). Should CTRL and LCC also be redone on 2001–2014? Which archive folder holds the 2001–2014 files later? Copy 14c/24c/24d to NIRD.
- **Files changed:** `postprocess/run_all_parallel.sh`, `postprocess/run_all_postprocessing.sh`, `CLAUDE.md`, both logs.

</div>

<div style="color:#AAAAAA">

## 2026-10-28 · 12:47 → 12:47 (0 min) · session 42e247bf
- **Goal:** status of the runs.
- **Done:** the fixed-BVOC runs 14c/24c/24d are finished and archived, 2000–2014 complete (open since 2026-10-25).
- **Found:** the spin-ups are going faster than estimated yesterday (about 16 h per 5 years). 23c, 23b and 13b finish today; 13c finishes tomorrow ~05:00.
- **Open/next:** move the old 2001–2009 processed files to `2001-2009-pre-co2-fix/`, then postprocess 14c/24c/24d. Check that the watcher launches 23a/24a/14a today.
- **Files changed:** both logs.

</div>

<div style="color:#AAAAAA">

## 2026-10-27 · 13:31 → 13:31 (0 min) · session 42e247bf
- **Goal:** status of the runs; a diagram of what has been rerun, is rerunning and still has to be rerun, and what depends on what.
- **Done:** status table and dependency diagram (in chat).
- **Found:** all 7 runs are healthy. The running fixed-BVOC runs start from the old LCC spin-up, so they will have to be redone on the new chain. The new LCC_FUT script (24a) does not save the all-species BVOC output (only matters if LCC_FUT emissions are ever needed).
- **Open/next:** after the new CTRL_PD/CTRL_FUT/LCC_PD runs: rebuild the emission climatologies, then redo 14c/24c/24d (+24e). Decide whether to automate this. Decide whether the isoprene/monoterpene-only runs (14b/24b) are ever redone.
- **Files changed:** both logs.

</div>

<div style="color:#E58AA5">

## 2026-10-26 · 10:03 → 10:25 (22 min) · session 18cd48f1
- **Goal:** six-panel forcing maps with shared colourbars.
- **Done:** two new versions per period and band: all six maps on −6…+6 (`_shared6`), or albedo + total on −6…+6 and the BVOC maps on −2…+2 (`_split6-2`).
- **Found:** on the −6…+6 scale the PD BVOC maps are almost blank (their values are ~0.1 W m⁻²); the split version shows their pattern. Notebook reran without errors.
- **Open/next:** commit when you say so.
- **Files changed:** `src/.../plotting/forcing_maps.py`, `analysis/radiative_forcing.ipynb`.

</div>

<div style="color:#A84300">

## 2026-10-25 · 22:47 → 00:56 (129 min) · session 7648e6ae
- **Goal:** more radiative-forcing maps (Ghan split per contrast), maps with one row per contrast, and the processes behind the forcing (hydrology, snow, surface energy, sunlight at the surface).
- **Done:** 12 Ghan figures + 12 seasonal ones; 10 contrast-grid figures; water-budget table and 2 charts. Three notebooks replace `forcing_maps.ipynb`; all run with outputs saved. New runoff/water-storage data for all 6 runs.
- **Found:** PD, north of 45°N: forest expansion +0.24 W m⁻² (clear-sky/albedo +0.37, clouds −0.11, aerosol ~0). The BVOC part in PD is +0.13 (clouds +0.07, clear-sky +0.05). In FUT the BVOC contrast is strongly negative in summer (−2.3 W m⁻² SW, clouds). The water budget closes over the changed cells, not over the other northern land (+28 mm/yr).
- **Done:** water-budget gap closed by adding ice runoff (opened and closed in this block); 4th row CTRL_FUT − CTRL_PD in all LCC−CTRL figures.
- **Done:** attribution notebook `pd-fut-attribution.ipynb` (6 analyses, 8 figures, 4 tables) and fixed-BVOC − CTRL Ghan maps; fixed-BVOC − CTRL contrast-grid figures (5) and water-budget chart.
- **Found (attribution):** FUT BVOC contrast ≈ future vs present-day emissions acting through clouds; PD SOA/aerosol deficit is a setup offset (present in winter too).
- **Open/next:** all results are provisional (old CTRL version); commit when you say so.
- **Files changed:** `src/.../plotting/forcing_maps.py`, `src/.../postprocess/variables.py`, `postprocess/run_postprocess.py` (docstring), `CLAUDE.md`, `analysis/README.md`, new `analysis/{radiative_forcing,bvoc-soa-cloud-interactions,biogeophysical-hydro}.ipynb`, removed `analysis/forcing_maps.ipynb`; new `analysis/pd-fut-attribution.ipynb`; new data `*_lnd_HYDRO_2001-2009.nc`, `results/tables/water_budget_2001_2009.csv`.

</div>

<div style="color:#62733B">

## 2026-10-25 · 21:53 → 23:05 (72 min) · session 3b25e01e
- **Goal:** where are the BVOC climatologies? Which files would the fBVOC rename touch? Make the scripts move files instead of copying them.
- **Done:** the climatologies are finished and in the shared folder. The scripts now delete the work copy once the shared copy has been checked as identical.
- **Found:** the 19 future-run emission files with year-2000 dates were missing from the shared folder (now copied). The rename is dropped: old processed files will move to `2001-2009-pre-co2-fix/` instead.
- **Done:** automatic launcher started for 13c and the nudged runs 13a/14a/23a/24a on the new spin-up chain.
- **Open/next:** decide whether the fBVOC runs on the new chain should also be automated. When 14c/24c/24d finish: move the old processed files to `2001-2009-pre-co2-fix/`, then postprocess 14c/24c/24d when they finish.
- **Files changed:** `preprocess/bvoc-emissions/{run_bvoc_climatology_array.sh, create_bvoc_emissions_climatology.sh, check_bvoc_climatology.py, create_bvoc_emissions_climatology_staged.py (comment), README.md}`, `cases-scripts/24e*.sh` (comments), `CLAUDE.md`, `forcing_maps.py` (comment only), new `cases-scripts/auto_launch_new_chain.sh`, `cases-scripts/README.md`.

</div>

<div style="color:#008080">

## 2026-10-25 · 21:28 → 21:35 (7 min) · session af52cc01
**Goal:** clearer plots in the land-only equilibrium notebook.

**Done:** regions changed to modified cells / global land / tropics; PD_LCC_old dropped, only FUT_LCC_old kept as reference; FUT_CTRL made visible; rerun with outputs saved; summary updated.

**Found:** FUT_CTRL was missing from plots because it is identical to FUT_LCC everywhere except the modified cells.

**Open / next:** nothing new.

**Files changed:** `diagnostics/check-simulation-equilibrium/check-land-only-equilibrium-after-co2-fix/check_land_only_equilibrium_after_co2_fix.ipynb` (+ its outputs).

</div>

<div style="color:#999999">

## 2026-10-25 · 16:15 → 16:16 (1 min) · session dc6addbf
**Goal:** Understand a git warning when staging the equilibrium notebooks.

**Done:** Checked: everything was staged except `__pycache__`, which git ignores on purpose. 200 files staged in total, not committed yet.

**Found:** The warning is harmless.

**Open / next:** Commit when ready.

**Files changed:** both logs.

</div>

<div style="color:#AAAAAA">

## 2026-10-25 · 21:17 → 21:25 (8 min) · session dc9990de
**Goal:** Table of the previous round of runs, in the same format as the running ones.

**Done:** Tables of the previous round (23–25 Oct, all finished) and of the current queue.

**Found:** The queue has changed since 16:12. 12c is at year 40/100. Three new all-species fBVOC runs (14c, 24c, 24d) were started at 17:11–17:30.

**Open / next:** nothing new.

**Files changed:** both logs.

</div>

<div style="color:#AAAAAA">

## 2026-10-25 · 16:12 → 16:20 (8 min) · session dc9990de
**Goal:** Which runs are going, and what was started in the last round.

**Done:** Checked the queue. Running since 15:15: 12c (PD CTRL land-only, ~7 h), 13b, 23b, 23c (coupled spin-ups, 20 yr).

**Found:** The 19-species BVOC climatology jobs (CTRL_PD and CTRL_FUT, submitted 16:12) all failed within 10 s: the Python on NIRD is not found on the preproc nodes.

**Open / next:** Fix the Python path in `run_bvoc_climatology_array.sh` and resubmit (whoever submitted it).

**Files changed:** both logs.

</div>

<div style="color:#555555">

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

</div>

<div style="color:#008080">

## 2026-10-25 · 14:45 → 14:50 (5 min) · session af52cc01
**Goal:** simpler region set in the CTRL_FUT vs LCC_FUT vegetation-state notebook.

**Done:** regions reduced to global land, modified cells and all unmodified land; notebook rerun with outputs saved; summary tables updated.

**Open / next:** nothing new.

</div>

<div style="color:#999999">

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

</div>

<div style="color:#AAAAAA">

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

</div>

<div style="color:#E58AA5">

## 2026-10-23 · 18:44 → 18:55 (11 min) · session 0ec901d3
**Goal:** make the weak present-day expansion pattern visible on the maps.

**Done:** PD panels get their own colour scale; FUT and Interaction share one; extreme 2 % of cells clipped. Notebook rerun with outputs saved.

**Found:** PD expansion raises emissions over western Canada, Alaska and eastern Siberia, with lower emissions along the southern edge of the changed area.

**Open / next:** old map PNGs with the previous names are still in the output folder (can be deleted).

**Files changed:** `diagnostics/FUT-fBVOC-background-lcc-effect-decomposition/bvoc_expansion_PD_FUT_interaction.ipynb`, its map PNGs, logs.

</div>

<div style="color:#E58AA5">

## 2026-10-23 · 18:30 → 18:35 (5 min) · session 0ec901d3
**Goal:** use the hatching style in the CTRL_FUT vs LCC_FUT vegetation-state maps.

**Done:** dots replaced by grey hatching on non-significant cells (p ≥ 0.05); notebook rerun with outputs saved.

**Found:** nothing new; numbers unchanged.

**Open / next:** none.

**Files changed:** `diagnostics/check-simulation-equilibrium/check_CTRL_FUT_vs_LCC_FUT_vegetation_state.ipynb`, its `B_delta_maps.png`, logs.

</div>

<div style="color:#008080">

## 2026-10-23 · 17:43 → 18:46 (63 min) · session e2a259e9
**Goal:** one notebook instead of three duplicates; run the PD-vs-FUT interaction notebook.

**Done:** merged into `bvoc_emissions_decomposition.ipynb` (all sections + maps + conclusions), deleted the other two and their output folders; ran both notebooks with outputs saved (set the LCC_PD path, which was missing).

**Found:** expansion effect on emissions (≥45°N, Tg/yr, isoprene / monoterpenes): PD +0.43 / +0.18, FUT −2.61 / −3.85. The sign flips every year. 92 % / 69 % of the future drop is in cells whose vegetation did **not** change.

**Then:** switched on the last sections (temperature, light, leaf area, plant-type changes, check of the fixed-emission run, cloud/radiation response); they were off only because their file paths had never been filled in. Small fix so land-model fields line up with the atmosphere grid. Re-ran: everything works (18:45).

**Found too:** in the future runs with LCC, leaf area is lower than in CTRL nearly everywhere north of 45°N, all year round, even where vegetation did not change. Temperature and sunlight go *up*, so the drop in emissions follows the lost leaf area. This most likely comes from the low-CO₂ land spin-up bug, not from the new forests (not proven). The fixed-emission run gets the right emissions (within 0.05 %).

**Open / next:** look at the new plots; the future fixed-emission run (`LCC_FUT_fBVOC_FUT`) does not exist yet, so the clean cloud/radiation comparison is still missing.

**Files changed:** `diagnostics/FUT-fBVOC-background-lcc-effect-decomposition/` (2 notebooks + output folders), logs.

</div>

<div style="color:#B8860B">

## 2026-10-23 · 16:33 → 17:42 (69 min) · session 035c87f8
**Goal:** are we ready to start the coupled LCC spin-ups (PD and FUT)?

**Done:** checked the three new land-only runs: settings, progress, and the CO₂ CLM actually sees.

**Found:** CO₂ is correct now. But the runs are not finished: each stopped when the archiving step hit a filesystem read/write error, which also stops the automatic resubmission. The PD CTRL land-only run (12c) does not exist. The coupled scripts still point to the old land runs.

**Restarted (16:37):** the three runs are running again. Cause of the stops: temporary filesystem errors during archiving.

**Found too:** the FUT LCC extension crashed at 31 Dec 2014 because the nudging data stop at 1 Jan 2015 00:00. The other nudged runs ending in 2014 will crash the same way.

**Fixed:** the nudging data now go past 1 Jan 2015 (3 records copied from 31 Dec; script `preprocess/nudging/extend_last_met_file.py`, original backed up in `data/nudging-met-backup/`). Year 2014 of LCC_PD and LCC_FUT resubmitted.

**Open / next:** check the 2014 reruns finish and archive; decide on 12c; when the runs reach year 100, copy them to NIRD and update `LAND_CASE` in 13b/23b (and 13c/23c).

**Files changed:** new `preprocess/nudging/extend_last_met_file.py`, `data/nudging-met-backup/` (backup + README); patched met file in `/cluster/shared/…/inputForNudging/AZ/…_6h_2000-2015/`; logs.

</div>

<div style="color:#AAAAAA">

## 2026-10-23 · 01:40 → 01:45 (5 min) · session 78f6d842
**Goal:** how to check there is room for the hourly output; finish the 1-day test checks.

**Done:** checked the quotas on Betzy (`dusage`). The project area is at 920 GB of 1 TB. The model archive (`/cluster/work`) holds 178 GB. The NIRD disk as a whole is 98 % full. The present-day 1-day test passed all checks (check open since 01:36). The future test is now archived too (open since 01:36).

**Found:** the hourly output is about **28 GB per 15-year run** once archived (compressed), not 116 GB as said at 01:38. The 116 GB came from measuring the uncompressed file before archiving.

**Open / next:** check the NIRD project quota from a NIRD login (`dusage -p NS9188K`) before moving ~60 GB of new hourly output there.

**Files changed:** logs only.

</div>

<div style="color:#AAAAAA">

## 2026-10-23 · 01:36 → 01:39 (3 min) · session 78f6d842
**Goal:** check the status of the runs just submitted and of the 1-day tests.

**Done:** checked the queue and CaseStatus. All production runs are running (CTRL_PD, CTRL_FUT, the LCC_PD/FUT extensions, three land-only spin-ups). The future 1-day test passes every output check.

**Found:** the archiving of the future test failed on a filesystem read/write error (it looks temporary); its output is safe in the run folder. The new hourly output is larger than estimated: about 116 GB for 15 years, not about 30 GB.

**Open / next:** check the present-day test when it finishes; re-archive the future test; decide whether 116 GB of hourly output is acceptable.

**Files changed:** logs only.

</div>

<div style="color:#E58AA5">

## 2026-10-23 · 01:24 → 02:00 (36 min) · session 339178f2
**Goal:** notebooks should always keep their outputs; lighter significance marks.

**Done:**
- Significance test: ocean no longer faded; now compares thin dense grey hatching (`////`, `/////`) and fading the non-significant cells (two strengths). Outline dropped.
- New standing rule (Claude memory + `CLAUDE.md`): notebooks are run with `run_nb_inplace.py`, which saves outputs and figures in the notebook. The significance test notebook was re-run this way.
- Significance style chosen (opened this block): thin grey hatching `/////` on non-significant cells is now the default in the forcing maps; ocean no longer faded by default.
- Forcing maps use the current fBVOC file names; `forcing_maps.ipynb` re-run with all figures (opened this block).

**Open / next:** if the fBVOC files are renamed later, switch the forcing maps back to the `_PD_IM` names.

**Files changed:** `CLAUDE.md`, `analysis/test_significance_marking.ipynb`, `analysis/forcing_maps.ipynb`, `src/.../plotting/forcing_maps.py`.

</div>

<div style="color:#E58AA5">

## 2026-10-23 · 01:10 → 01:22 (12 min) · session 339178f2
**Goal:** see whether to mark significant or non-significant cells on the forcing maps.

**Done:** test notebook `analysis/test_significance_marking.ipynb` with 4 styles × 3 panels, PD and FUT. Figures in `results/figures/tests/`.

**Found:** PD BVOC panels: almost nothing significant (0 %); FUT BVOC: ~90 % significant; Total: ~25–28 %. So no style is sparse everywhere.

**Open / next:** choose the style; then add it as an option to the forcing-map functions.

**Files changed:** `analysis/test_significance_marking.ipynb` (new), `results/figures/tests/*.png`.

</div>

<div style="color:#B8860B">

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

</div>

<div style="color:#62733B">

## 2026-10-23 · 00:29 → 00:30 (1 min) · session 0042d825
**Goal:** decide whether the fixed isoprene/monoterpene files should come from SF* or MEG_*.

**Found:** use **SF*** (total emissions). The fBVOC runs already remove the fire emissions of these two species and apply no extra diurnal cycle, so the prescribed file must contain everything. MEG_* would leave out the fire part.

**Open / next:** none from this question.

**Files changed:** none.

</div>

<div style="color:#62733B">

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

</div>

<div style="color:#555555">

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

</div>

<div style="color:#008080">

## 2026-10-23 · 00:05 → 00:13 (8 min) · session bd6c4048
**Goal:** Move the D1/D2 figures and tables out of `results/` into the diagnostics folder.

**Done:**
- 18 figures and 8 tables moved to `diagnostics/other-BVOC-emission-magnitude/D1_farfield/` and `D2_megan_budget/` (each with `figures/` and `tables/`).
- The run logs `D1.log` and `D2.log` moved too, into a `logs/` folder in each.
- The two notebooks now save there; CLAUDE.md paths updated.

**Open-next:** commit (the move shows in git as deleted files under `results/`).

**Files changed:** the two notebooks, `CLAUDE.md`, moved PNG/CSV files.

---

</div>

<div style="color:#B8860B">

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

</div>

<div style="color:#008080">

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

</div>

<div style="color:#999999">

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

</div>

<div style="color:#999999">

## 2026-10-22 · 19:26 → 19:30 (4 min) · session 1f288034
**Goal:** Check that automatic logging works in a new session; keep a record of solved items.

**Done:**
- The logging script is switched on and works in a new session (open since 2026-10-22 19:07).
- New rule: earlier Open items are never deleted from this log. When one is done, it goes under **Done** in the current block, with the date it was opened.

**Open / next:** Nothing for the logs. Science: check the D2 tables; decide on the CTRL re-spin-up.

**Files changed:** `docs/CLAUDE_log_human.md`, `docs/CLAUDE_log.md`

---

</div>

<div style="color:#999999">

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

</div>

<div style="color:#008080">

## 2026-10-21 (later): D1 results and MEGAN maps
**Found:**
- **D1:** the fBVOC runs change the forcing far from the modified area (tropics +0.05 W m⁻² in PD, −0.44 W m⁻² in FUT), which is more than the local effect.
- PD Total is clean. FUT Total has a +0.25 W m⁻² tropical offset from the spin-up mismatch.
- **MEGAN:** the PD summer monoterpene increase north of 45°N (+1.6 %) comes from vegetation composition, not from weather or the activity factor (γ).

**Done:** maps of the MEGAN emission factors (ε, γ); smaller significance dots on the maps.

**Open / next:** check the D2 tables.

</div>

<div style="color:#008080">

## 2026-10-21: forcing maps rebuilt, spin-up problem found
**Found:**
- **CTRL and LCC use different land spin-ups.** LCC had an extra 100-year spin-up. In FUT, tropical vegetation in LCC is 31 % lower than in CTRL. This contaminates LCC − CTRL.
- fBVOC lacks the other BVOC compounds, which causes a chemistry artifact.

**Done:** rewrote the forcing-map code (fixed a bug: FUT Total now uses CTRL_FUT); imported the D1/D2 diagnostics.

**Open / next:** decide on a CTRL re-spin-up; get the ozone kernel; commit the code.

</div>

<div style="color:#555555">

## 2026-10-20/21 (night): postprocessing sped up
**Done:** all 90 processed files were produced in ~26 min (before: hours). Fixed a bug that stopped land files from ever being processed.

</div>
