# Claude log

Working memory across Claude Code sessions. **Read NOW first; read older blocks only if needed.**

**Evidence tags:** **(a)** verified in source, scripts, files or output · **(b)** inference · **(c)** unverified.

User preferences: short labelled sections, tables, bold key terms, worked examples; be critical, separate facts from inference; never assume variables that look alike are equivalent.

Protocol: hook `~/.claude/hooks/boreal_log.py` injects NEW/CONTINUE BLOCK each prompt. NOW = overwritten every turn.

Blocks = one per prompt-cache window (new session or >60 min gap), newest first, rewritten in place within the window.

Human twin: `docs/CLAUDE_log_human.md`.

---

## NOW (overwrite every turn)
- 16:21 21 Nov session 6f761ff3 (block 16:02): user OK commits except proposal #3 MEGAN, #4 background aerosol, #7 Tang/LPJ. Committed on main, NOT pushed (a): 9d8be8e results layout/artefacts, 40c6aed MET 2026-2040, f9be173 BVOC plots, 8ddb633 isoprene diurnal, 6e86c49 equilibrium/autocorrelation, then diagnostics index + runner + logs; draft repo methods commit (not pushed). diagnostics/README.md committed whole, so it already lists the uncommitted background-aerosol/Tang/LPJ files. STILL UNCOMMITTED by user choice: MEGAN files (nb, megan_maps.py, build_megan_pptx.py, waiter, megan figures/tables), diagnostics/background-aerosol/, tang2023-comparison/, lai-clm-vs-lpjguess/; run_megan_lmdi_maps_FUT.status left out. MEGAN waiter pid 2738837 status RUNNING attempt 2 since 16:08:50. Deleted results/{figures,tables}-pre-reorg-20261116 (348 files, all blobs in git history, no code refs (a)). KEPT *-pre-reorg-20261108.
- 15:58 21 Nov session d2e64b8d (block 15:55), user OK: LCC_PD_fBVOClccPD phase C resubmitted by direct case.submit (same exclude list): case.run 1812398 PENDING, st_archive 1812399. extend script --check refuses because last CaseStatus line is the crash, so checked by hand (a): 6 rpointers 2036-01-01, archive rest/2036 present (.gz), run-dir restarts present, cam.r met path = _6h_2000-2040, list ends 2041-01-02, STOP 5 yr, RESUBMIT 0. phaseC .failed moved to met-nudg-2040/retry-20261121/ so watcher counts the run again; watcher liveness still unverified from login-3 (c). If it is dead, done/postprocessing will not start: check watch.log for 'at 2041-01-01' lines tonight. Maps: megan_lmdi_maps_when_FUT_done.sh restarted 15:57 login-3 (pid 2738837, 3 attempts), status results/tables/logs/run_megan_lmdi_maps_FUT.status = RUNNING; background wait b4h0xvhps. NEXT: read notebook result, then LMDI FUT \NUM in methods-claude.tex (not filled yet). If 1812398 crashes the same way: stop and investigate, no blind retry.
- 15:55 21 Nov session d2e64b8d, status check (read-only except logs). 11/12 nudged runs in phase C (2036->2041): 10 at 2040-05..12, LCC_FUT 1811849 at 2038-10, ETA ~23:00 (b). FAILED: NF2000 nudg_lcc_fBVOClccPD_20261031 job 1811597 02:12 at init, surfrd_veg_all wt_nat_patch sum 0.99882 at nl=5664; fsurdat PCT_NAT_PFT intact (all cells 100, nl 5664 = 100) and same file used by sibling runs -> transient bad read likely (b), rpointer 2036-01-01, phaseC_<case>.failed set. NEXT, needs user OK: resubmit phase C; it blocks 2001-2040 postprocessing/analysis (watcher step 5 needs all 12). Watcher not visible from login-3 (last action 06:50, probably login-2), liveness unverified. analysis/megan-lmdi-attribution-maps.ipynb still has NetCDF HDF error in cell 0 -> rerun, then fill last LMDI FUT \NUM in methods-claude.tex. nn9188k 954 GiB/1 TiB. git 561 paths uncommitted. archive_guard lock HELD.
- 16:50 20 Nov session 4607124c (block 16:45): user → (1) deleted 6 stale LCCFUT_fBVOC{lccPD,ctrlPD}_*_split6-2_designA.png; (2) dropped duplicate tag LCCFUT-CTRLPD_fBVOCctrlPD (md5-identical to LCCFUT_fBVOCctrlPD) from analysis/radiative-forcing-decomposition.ipynb cell 1 + build_figures_pptx.py DECOMP, its 6 PNGs deleted; (3) per-map-colourbar (no-scale-suffix) design A six-map PNGs deleted (12), nb cell 3 now draws only family scale (cells 0,2 md updated), deck 5.2 = 'Six-map decomposition' (12 figs, shared scales only). Folder now 12 six-map PNGs + budget split (a). Nb NOT rerun (code edit only; outputs still old/cell 3 error). Design B (artefacts/design-B, deck 7.8/7.9) untouched. Deck rebuilt → results/pptx/BOREAL_figures_2001-2025_CICERO.pptx 307 slides / 297 figs, all placed (a); python-pptx venv in scratchpad 4607124c/venv (lcc-env --system-site-packages + pip python-pptx 1.0.2). Backups nb/script .bak in scratchpad. Title slide date still hard-coded '16 November 2026'. Not committed.
- 20 Nov status check (read-only, no files changed): 12 nudged runs phase A done, phase B running (11 R since ~04–06 h; LCC_FUT phase B started 14:07, behind by ~9 h); 12 PD after-jobs queued. FUT MEGAN batch 2 DONE (2002/2006/2011 .ok+.copied, last 04:12) (a). megan_lmdi_maps_when_FUT_done → analysis/megan-lmdi-attribution-maps.ipynb FAILED 3× 04:20–04:58 (lcc-env ImportError platformdirs.unix = NIRD conda flakiness), status file FAILED (a) → rerun by hand. archive_guard lock held (alive), last fix 19 Nov 23:52 (a). git: ~560 uncommitted paths.
- 16:51 19 Nov session 21b50ffc (block 16:28): design A nb analysis/radiative-forcing-decomposition.ipynb cell 1 CASES: LCCFUT_fBVOClccPD ctrl=LCC_PD, LCCFUT_fBVOCctrlPD ctrl=CTRL_PD (title 'LCC_FUT − <ref>'), scale split6-2 → split40-15-2 (98th pct LCC_FUT−LCC_PD ≥45°N albedo 38.1, total NET 12.2/SW 19.5/LW 11.9 (a)). Cell 0 md + build_figures_pptx.py DECOMP l.178-179 updated (deck not rebuilt). 12 figs (2 tags × {split40-15-2, per-map} × NET/SW/LW) redrawn OK by scratchpad 21b50ffc/redraw_rfd.py (execs nb cell 1, fm.POSTPROCESSED_DIR → /cluster/work/users/adelez/boreal-caches/rfd-staging, 6 RADIATIVE files md5-checked copies; delete after). NET ≥45°N: LCC_FUT−LCC_PD total +1.07±0.17, albedo +9.71; −CTRL_PD +1.33±0.17, +10.15 (a). In-place nb run FAILED cell 3 (NIRD HDF error; env imports also flaky; must run from repo root: analysis/html shadows stdlib html with -c/cwd) → nb cell 3 shows error, cells 5-6 old outputs (unaffected). TODO: rerun nb when NIRD stable. Stale *_split6-2_designA.png for these 2 tags (ask delete). LCCFUT_fBVOCctrlPD now = LCCFUT-CTRLPD_fBVOCctrlPD (duplicate, ask drop). Nb backup scratchpad .bak (nb untracked).
- 16:44 19 Nov session 2ca075af (block 16:10): diagnostics/tang2023-comparison/tang2023_comparison.ipynb (22 cells, rerun OK (a)). Fig5 (both PNGs): discrete RdBu_r bars; Tang-range copy only ISO/MT/SOAs/CCN (TANG_LIMITS), SOAb ±3 (OWN_LIMITS) + AOD own scale; thick black outline of modified cells (outline_modified, cell 8). Totals bar chart (cell 16): + Tang CanESM5; TANG_TOT by eye from Fig1d,h (5-SSP mean, min–max error bars): hist ISO 12.5 MT 4.85; GFDL ~2100 ISO 14.7 (13.4–16.2) MT 4.6 (3.6–5.3); CanESM5 ISO 20.5 (19–24) MT 5.5 (5.0–6.0). Old note 'ISO ≈14→15, MT 5→4.5' was misread → text corrected (cells 15, 21). NEW §5b cells 17-18: Fig1b,f analogue (lccFUT − ctrlPD)/100 yr in mgC m-2 yr-2, TwoSlopeNorm ISO (−8,18), MT ±6 (Tang bars by eye) + histograms → tang_fig1bf_trend_maps_2001_2025.png, fig1bf_trend_values_2001_2025.csv: ISO +2.62 land≥45N/+2.64 modified, MT +4.92/+5.30; decreasing cells 9 % ISO, 7 % MT (Tang SSP585 MT mostly negative in boreal Eurasia/Canada). NIRD flaky: cell 1 scipy ImportError twice, retry OK. 16:44: §5b now 2×3: + vegFUT LCC_FUT_fBVOClccFUT−LCC_FUT_fBVOCctrlFUT, vegPD LCC_PD_fBVOClccPD−LCC_PD_fBVOCctrlPD (added to RUNS via EXTRA_RUNS, cache built), all /100 yr on Tang ranges; histograms over modified cells. Modified-cell means ISO std +2.64, vegFUT +0.11, vegPD +0.07; MT +5.30, −0.04, +0.01 mgC m-2 yr-2; cells decreasing 29–39 % (veg) vs 9–10 % (std). Offered, not done: drop '≈ OD550' labels + side-by-side rows. Not committed. 17:23: Q offline LPJ-GUESS vs coupled CLM-MEGAN (answer only, no files). Modified cells, CTRL_FUT/CTRL_PD 2001-25 (scratchpad q/pdfut_gamma.py, lcc_dT.py): ISO ×3.09 = γT ×2.82 · γL ×2.01 (TLAI 1.15→2.53) · γC ×0.47; MT(apin+bpin+car3) ×4.87 = γT ×2.26 · γL ×1.99, no γC; γP, γA, EPS ≈1 (area-mean γ, PD-emission weighted (b)). TV +7.5 K. Coupling feedback: LCC−CTRL TV JJA +0.31 PD / +0.36 FUT K, TLAI JJA −0.11/−0.38 (a) → ~+3–5 % emissions (b), same size as whole veg effect on totals (ISO +3 %, MT −0.5 % FUT). NIRD HDF errors again (retries). 17:29: sources checked: ours TREFHT ANN modified +7.46 K / land 46–82N +6.62 K (how_warmer_future_climate_is_outputs/tables/fut_minus_pd_by_region.csv); Tang 2.4 GFDL / 2.8 MRI °C = mean over 5 SSPs, study region (main text, Results); SSP585 per GCM only in Supp Fig 4 (supp PDF in scratchpad tang/supp.pdf, not readable: no PDF tools, pip install denied). Earlier answer compared SSP585-only (ours) with 5-SSP means (Tang): not like for like. No notebook compares CLM LAI with LPJ-GUESS LAI; LPJ LAI only in preprocess/edit-surfdatafile/fpc-to-pft-processing/lai_fpc_area_expansion_vs_densification.ipynb + sandbox/lai_fpc_analysis.ipynb. Offered to build one. 17:47: user (Tang Supp Fig 4a): Tang SSP585 2100 warming CanESM5 ~+12 K, GFDL ~+6–7 K → our +6.6 K (land 46–82N) ≈ GFDL SSP585: warming does NOT explain MT gap. NEW diagnostics/lai-clm-vs-lpjguess/clm_vs_lpjguess_lai.ipynb (run OK (a); outputs clm_vs_lpjguess_lai_outputs/: lai_means_*.csv, lai_change_*.csv, seasonal cycle + JJA maps PNG): LPJ annual file = annual peak (r .998 vs monthly max); LPJ 0.5° → CLM grid cos-lat binning, common cells cover ≥50 % (857; 844 of 1161 modified). Modified cells JJA: LPJ 1.84→2.88 (×1.57, +1.04); CLM CTRL_PD→LCC_FUT 1.77→3.66 (×2.07, +1.89); CTRL_PD→CTRL_FUT ×2.30; LCC_FUT−CTRL_FUT −0.41. PD agrees (annual 1.15 vs 1.15). LPJ greens earlier. Implication (b) up to ~25–30 % more FUT emission from LAI. diagnostics/README.md section added. Not committed.
- 14:45 19 Nov session fff6dc27 (block 14:12). DONE this turn (a): (1) Methods \NUM: methods.tex macros \areaPct=100 \bonetArea=99.7 \densMax=5 (lines ~121-127, source lai_fpc_area_expansion_vs_densification.ipynb cell 8 + §7; densMax = max over 3 scenarios 4.9 aC3 permissive; primary max 1.9 BoNET); methods-claude.tex boxes FPC, equilibrium (NEW diagnostics/0_check-simulation-equilibrium/check_LCC_vs_CTRL_vegetation_state_2001-2025.ipynb from processed lnd LAND/BIOGEOCHEM files, run OK, FUT 2001-14 = raw nb to 1.7e-16; unmodified land PD TLAI −0.10±0.08 %, TOTVEGC −0.06±0.01, TOTECOSYSC −0.03±0.002, GPP −0.10±0.06; FUT +0.06±0.07, −0.01±0.004, −0.02±0.002, −0.01±0.03; old text '+0.35 %/dec drift' replaced: PD +0.21/+0.23, FUT +0.39/+0.39), r1/FDR (yearly_difference_autocorrelation.ipynb rerun 2001-2025, old outputs → _outputs_2001-2014/; conclusions cell rewritten; PD LCC−CTRL cbSOA r1 +0.38, detrended +0.36 = persistence, FDR 675→185 with n_eff). Only LMDI FUT \NUM left (status text updated). Both methods-claude (wrapper) and main.tex compile with tectonic (scratchpad methods-build/). (2) Space: /cluster/projects/nn9188k 954.3/1000 GiB (shared group quota, 710k/1M files); adelez share ≈137 GB (restart 86, noresm-inputdata 31, _old 20); our runs write to /cluster/work (b). NIRD datapeak fs 99 % (266/270 T, whole fs). (3) Timeline: nudged 33.5 s/model day = 3.4 h/yr = 17 h per 5-yr phase; phase A ends 20 Nov ~02:30-05:30 (LCC_FUT +17 h after it starts; job 1809562 PD); phase A queue wait was 13 h. FUT MEGAN batch 2 at mid-June, ~110 s/day → model end ~20:45 today. Uncommitted: methods.tex/methods-claude.tex (Overleaf repo), new eq nb, autocorr nb, watcher fix, 18 Nov grep fixes.
- **Logging:** rules in repo `CLAUDE.md` § Session logs; hook `~/.claude/hooks/boreal_log.py`.

---

## 2026-11-21 · 16:02 → 16:21 (19 min) · session 6f761ff3
Deleted results/{figures,tables}-pre-reorg-20261116 (348 files, all in git history (a), no code refs). 6 BOREAL topic commits + 1 draft commit, not pushed. MEGAN, background aerosol, Tang/LPJ left uncommitted (user). 20261108 backups kept.

## 2026-11-21 · 15:55 → 15:58 (3 min) · session d2e64b8d
- User OK: crashed LCC_PD_fBVOClccPD resubmitted (1812398), maps notebook rerun started. Details in NOW.

## 2026-11-21 · 15:52 → 15:55 (3 min) · session d2e64b8d
- Status check. One nudged run failed at init (likely bad read), awaiting user OK to resubmit. Details in NOW.

## 2026-11-20 · 16:45 → 16:50 (5 min) · session 4607124c
- Design A six-map figures: split6-2 leftovers, duplicate LCCFUT-CTRLPD tag and per-map-colourbar versions removed; nb + deck script updated; figures deck rebuilt (307 slides). Details in NOW.

## 2026-11-20 · status check · session ee0260fc
- Status + open-analysis recap (read-only). Details in NOW.

## 2026-11-19 · 16:28 → 16:51 (23 min) · session 21b50ffc
- Design A FUT-with-PD-emission figures: maps 1–2 now LCC_FUT − LCC_PD / LCC_FUT − CTRL_PD, scale split40-15-2. Details in NOW.

## 2026-11-19 · 16:10 → 17:47 (97 min) · session 2ca075af
- Tang comparison: modified-cell outline on Fig. 5; CanESM5 (and corrected Tang historical) bars in emission totals; new Fig. 1b,f trend-map analogue (mgC m-2 yr-2), with vegetation-only FUT and PD columns. Rerun OK. Q answered: offline vs coupled BVOC (factor split PD→FUT, LCC feedback ΔT). New nb diagnostics/lai-clm-vs-lpjguess (CLM LAI ×2.07 vs LPJ ×1.57 PD→FUT JJA).

## 2026-11-19 · 15:02 → 15:11 (9 min) · session 2ca075af
- Tang emission-totals bar chart: Tang ~2100 bar red → orange (= lccFUT). Fig5 Tang-range copy: SOA burden + AOD_VIS off Tang's ranges; SOA burden bar ±3 in both. Reruns OK.

## 2026-11-19 · 14:50 → 15:00 (10 min) · session 2ca075af
- Tang Fig. 5 layout: discrete colour bars like Tang + copy on Tang's colour-bar ranges (new cells 9-10). Notebook rerun OK.

## 2026-11-19 · 14:12 → 14:47 (35 min) · session fff6dc27
- Item 1 DONE (LCC_FUT resubmitted, MET NIRD OK, watcher fixed + restarted login-2). Methods \NUM filled except LMDI FUT (FPC macros, new PD/FUT equilibrium nb 2001-2025, autocorr rerun 25 yr). Space nn9188k 954/1000 GiB explained; run timeline; recap in markdown.

## 2026-11-19 · 13:55 → 14:10 (15 min) · session fff6dc27
- Status + recap. met-nudg: 11/12 running; lcc FUT segfault at init (resubmit); 3 false phaseA .failed (pending jobs missed by queued()); MET NIRD rsync failed. No changes.

## 2026-11-18 · 20:11 → 20:22 (11 min) · session af520c06
- Fixed tab/space grep (cases-setup.sh:210-211, extend_nudg_runs_2026-2040.sh:83); met-nudg watcher restarted 20:12, phase A submitting 12 runs, build 2 job 1808597. FUT batch 2 (2002/2006/2011) launched 20:15 + watcher. Not committed.

## 2026-11-18 · 19:40 → 19:50 (10 min) · session af520c06
- Status check. FUT batch 2 stalled (waiter race 16 Nov 20:11); 12 nudged 2026-2040 runs blocked by tab-vs-space grep false-fail in cases-setup.sh:210 (17 Nov 02:30); met folder only to 2031. Awaiting user OK to fix/relaunch.

## 2026-11-16 · 22:08 → 22:29 (21 min) · session 79aa63f4
- plot_bvoc_means.ipynb: added fig 2 = 17 other MEGAN species (MEG_*, CAM h0 raw, work archive), Gg/yr, cached CSV; plotting refactored to interaction_figure(). Run done (a). Forest effect −0.3…−8 % on all 17 (vs ISOP +5.8 % PD); climate +345…+621 %.

## 2026-11-16 · 22:13 → 23:49 (96 min) · session 16ac98c9
- 22:15 Q answered: folder purpose (only partly fBVOC vs interactive).
- 22:26– fBVOC run vs own source: reducer reduce_isoprene_fbvoc_vs_source.py, nb section 10 (results + fixes in NOW), NIRD read flakiness.

## 2026-11-16 · 22:08 → 22:13 (5 min) · session c2410794
- 22:13 16 Nov session c2410794: USER 'rebuild the 4 decks in results/pptx/' → DONE (a): all 4 builders run (v312 venv in scratchpad d7d2f7b6), built to scratchpad then mv over old: figures_2001-2025_CICERO 325 slides/315 figs (134 MB, was 146 MB), land_carbon_water 13/9, MEGAN_factors_2001-2014 55/46, simulation_contrasts 12/9. All asserts passed (every PNG placed). Old own-theme BOREAL_figures_2001-2025.pptx + simulations-interpretation.pptx untouched.

## 2026-11-16 · 22:33 → 00:30 (117 min) · session 06c39ecc
- User OK: `diagnostics/tang2023-comparison/tang2023_comparison.ipynb` DONE, executed with outputs (00:25). Columns = fBVOC FUT contrasts lccFUT−ctrlPD ("standard"), ctrlFUT−ctrlPD ("noVegDym"), lccFUT−ctrlFUT (veg, own scale). Rows ISO/MT (mgC m-2 yr-1, no test: climatology, interannual std ~1e-11 (a)), SOA_surf, SOA burden (≈OD550soa), AOD_VIS (≈OD550aer), CCN7 (S 1.0 % = Tang CCN1.0). §7 = reading. Outputs `tang2023_comparison_outputs/` (fig5 png, pft_group_cover_change.png, emission_totals_vs_tang png, 4 csv).
- Results (a, ≥45°N ratios std/noveg/veg): SOA_surf +2.36/+2.35/+0.002; SOA burden +2.03/+2.03/−0.0002; AOD_VIS +0.082/+0.078/+0.003; CCN1.0 +0.46/+0.46/+0.003. MT veg-effect boxes: S boreal Canada −10 %, Fennoscandia+W Russia −7 %, W Sib −5 %; Alaska +26 %, N Canada +19 %, E Sib +15 % = Tang dipole. ISO veg: Fennoscandia −8 %, E Sib −11 % (opposite to Tang, cause unchecked). Modified-cell totals ctrlPD→ctrlFUT: ISO 3.6→11.0, MT 4.4→19.9 TgC/yr (Tang GFDL ≈14→15, 5→4.5 by eye).
- (a) `AEROD_v` is all fill (1e36) in our AEROPT files: OsloAero doesn't write it → use AOD_VIS. Worth noting for any other code using AEROD_v (grep found only variables.py listing).
- (a) NIRD flaky 22:05–00:15: random HDF read errors on big SOA files, Errno 5 in conda env, kernel deaths. BVOCOX file fine. Cache cell (retrying netCDF4 reads) → `_outputs/cache` → `/cluster/work/users/adelez/boreal-caches/diagnostics/tang2023-comparison/…`; auto-rebuilds if a variable is missing. Mask lat ≠ model lat by 1.7e-13 → assign model coords.
- Generator `make_tang_nb.py` (scratchpad) used for the first versions; later edits made directly in the .ipynb (CLAUDE.md: no generators).
- Not committed.

## 2026-11-16 · 22:00 → 22:12 (12 min) · session 06c39ecc
- Read-only comparison with Tang et al. 2023 (npj Clim Atmos Sci 6:147) Figs 1+5, asked by user. No files changed except logs.
- Mapping (b): Tang standard ≈ fBVOC_FUT_lccFUT-ctrlPD; noVegDym ≈ fBVOC_FUT_ctrlFUT-ctrlPD; veg effect (std − noVegDym) ≈ fBVOC_FUT_lccFUT-ctrlFUT.
- Numbers (a, `results/tables/timeseries-responses/timeseries_{absolute,regional_means}_2001_2025.csv`, 25-yr means): CTRL FUT−PD modified cells SFISOP +208 %, SFMTERP +361 %; cbSOA ≥45°N +199 %. lccFUT−ctrlFUT: SFISOP +0.034, SFMTERP −0.011 mg m-2 d-1 (modified cells), cbSOA ≥45°N −0.001 mg m-2, NET_toa ≥45°N −0.048 W m-2; ctrlFUT−ctrlPD NET_toa ≥45°N −0.95 W m-2.
- (a) CLM MEGAN CO₂ inhibition is isoprene-only (`components/clm/src/biogeochem/VOCEmissionMod.F90:435`); LPJ-GUESS applies it to MT too → Tang GFDL SSP585 MT decreases, ours +361 %.

## 2026-11-16 · 22:09 → 22:50 (41 min) · session 6722329d
- plot_bvoc_emissions.ipynb now saves its 12 figures to plot_bvoc_emissions_outputs/ (a). Details in NOW.

## 2026-11-16 · 20:43 → 21:10 (27 min) · session 64634bba
- Isoprene diurnal cycle for fBVOC (prescribed input + HR/C0102 test runs) + hourly full time series; new reducer + notebook (a). Details in NOW.

## 2026-11-16 · 20:48 → 21:05 (17 min) · session e5c7a527
- plot_bvoc_means.ipynb (now diagnostics/2_bvoc-emissions/): dodge removed, VEG_CTRL/VEG_LCC, arrows + on-line run labels, legend, subtitle (a). Details in NOW.

## 2026-11-16 · 18:20 → 19:14 (54 min) · session 8fca3854
- USER: diurnal cycle of isoprene from the saved 30-min output, new notebook + folder in diagnostics; then move preprocess/bvoc-emissions/plot* → diagnostics/2_bvoc-emissions.
- Source (a): `cam.h1` of the MEGAN exact-split branches (`/cluster/work/users/adelez/archive/*_meganpatch_*-from{2000,2005,2010}`), 48 rec/day, SFISOP+SFMTERP gridded, **avgflag 'I'** (user_nl_cam nhtfrq=0,1; avgflag_pertape='A','I'); clm2.h1 = per-patch (heavier, not used). 2000-chain files start 00:00, branch files 00:30 → script assigns stamp t to t−15 min (00:00 → previous day/year; reads Y+1-01-01 file).
- `diagnostics/2_isoprene-diurnal-cycle/reduce_isoprene_diurnal.py` (12 procs, ~8 s/yr, login-2) → NIRD `data/processed-data/isoprene-diurnal/diurnal_<ALIAS>_<YEAR>.nc` (+ reduce_*.log); checks every (day, step) present, no duplicates. FUT 2002/2006/2011 not archived yet → skipped; rerun the script when batch 2 is done, then rerun nb.
- `isoprene_diurnal_cycle.ipynb` (self-contained; nb built by scratchpad build_nb.py, not kept): LST = UTC + round(lon/7.5) steps; regional totals Mg h⁻¹ (flux × cell area); regions LCC-modified cells + ≥45°N; figs by season, LCC−CTRL (paired yearly Δ, 95 % t-CI; abs + %), month×hour, JJA shape by lat band (75–90°N has ~no isoprene → band 65–90°N), tables annual totals + summary.
- Results (a, outputs): ≥45°N CTRL_PD 8.3–10.2 Tg/yr, CTRL_FUT 23–24; modified cells CTRL_PD 3.7–4.4, LCC_PD +0.12–0.35. Peak 12:45–13:15 LST, JJA peak/mean ≈ 3.0 (PD) / 2.85 (FUT), night (18–06 LST) share 3–5 % JJA. LCC−CTRL JJA modified cells ≈ +6.5 % PD (CI ~4.5–8.5) / +4 % FUT (n=3, CI incl. ~0), ~flat across the day except a dip after 17 LST → LCC scales amplitude, not timing. Shape flattens northward (JJA peak/mean 3.75 tropics → 2.7 at 65–90°N).
- Gotchas: run_nb_inplace `%matplotlib inline` 60 s timeout failed once under load (retry OK); `pkill -f <pattern>` inside a bash -c that contains the pattern kills its own shell.
- Move (a): git mv plot_bvoc_emissions.ipynb, plot_bvoc_timeseries.ipynb, plot_bvoc_timeseries_outputs/; mv plot_bvoc_means.ipynb + _outputs (untracked). Patched code: plot_bvoc_emissions PREPROC=preprocess/bvoc-emissions (sys.path for create_bvoc_emissions_climatology_staged; totals CSV written there, read by bvoc_species_processes.ipynb which stays); means/timeseries OUTDIR → diagnostics/2_bvoc-emissions/…_outputs. Not rerun. prescribe-just-ISOP-MTERP/plot_bvoc_emissions.ipynb (legacy subfolder) NOT moved. README: preprocess/bvoc-emissions (2 refs), diagnostics (2 sections).

## 2026-11-16 · 18:26 → 18:29 (3 min) · session 017a5cd2
- Q: does losing laptop internet stop sessions? Process tree (a): all claude procs are children of vscode-server extension host on login-2; Slurm jobs 1803953 R, 1803954 PD dep, 1804319/1804323 R; run_reorg.sh detached (ppid 1). Answer (b): survives grace period only.
- archive_guard: lock held → alive on login-3; no restart (a 2nd guard on login-2 would exit on the lock anyway). No repo files changed.

## 2026-11-16 · 18:16 → 18:27 (11 min) · session e5c7a527
- USER sketch (VEG_PD/VEG_FUT × PD/FUT climate, PD→FUT diagonal) → new plot_bvoc_means.ipynb in preprocess/bvoc-emissions/ condensing plot_bvoc_timeseries to means ± SD (a). Built via scratchpad make_nb.py (not in repo), executed with nbconvert lcc-env kernel startup_timeout 900. Numbers in NOW.

## 2026-11-16 · 18:03 → 18:33 (30 min) · session f7c9ff9e
- USER: split pd_fut nb → _prescribed + _online; lcc nb → _online; bars + time series also north of 40°N. Done + both run, 0 errors (a); old nb + outputs deleted (in git 58de6c2). Not committed.

## 2026-11-16 · 17:58 → 18:08 (10 min) · session cf84836f
- USER: which commits to recommend? → proposed 6 topic commits. USER: hold #3 (split-alias forcing summaries), commit rest → 7441a42, 58de6c2, 11832ae, 76acbb5 + logs (a). Background-aerosol nbs being split/rerun by f7c9ff9e at commit time.

## 2026-11-16 · 16:04 → 16:27 (23 min) · session 9b7c5f07
- Q&A: suggestions for NOTES.md (user's personal notes) in the same style. Facts checked (a): restart-archive exists, 17 .ipynb_checkpoints, 15 __pycache__, results/ snapshot dirs listed, .git 4.2G, pptx 287M, /cluster quota 14/20G. Nothing edited. 16:14 clearer spin-up note: drop = first N records by position (fileio.drop_spinup; open_cam_monthly lives in D1/D2 notebooks, not analysis/loading — CLAUDE.md path stale). 16:24 USER OK: CLAUDE.md:151 fixed; NOTES.md filled (user lines kept, typo fixed, MEGAN month line omitted until swap). Uncommitted.

## 2026-11-16 · 16:00 → 16:40 (40 min) · session 06b518ae
- PD 2001/2002 month fix: verify false-fail (exact == on float sums, 1 ulp) → user GO → swapped 16:34 via /cluster/work/users/adelez/megan-lmdi/monthfix/finish_monthfix_20261116.sh (scratchpads wiped); 3 MEGAN nbs rerunning. NOTES.md: nudging last-file patch + monthfix notes.

## 2026-11-16 · 15:27 → 16:37 (70 min) · session f7c9ff9e
- USER: background-aerosol nb 25 yr; Arctic maps, global as appendix; online sources bars + time series as for prescribed.
- pd_fut nb edited + run OK (a); dust cache coord bug found + fixed (a); summary refreshed. Arctic CDNUMC +25 % unexplained (b).

## 2026-11-16 · 20:39 → 20:55 (16 min) · session e391bcc3
- 20:44 USER: update pptx builders (not fut-fbvoc-source nb) → done + test builds OK.
- USER "finished?" → reruns all EXIT 0; empty dirs removed; δ figure checked.

## 2026-11-16 · 17:58 → 18:36 (38 min) · session e391bcc3
- USER: art_LCC_P → own emissions; titles option 1; earlier answers: results/figures/<nb>/{a_,b_,c_}/, artefacts/d_artefacts, artefacts/design-B, new nb radiative-forcing-decomposition, scale families, naming. Implemented + archived old set + reruns launched (see NOW).

## 2026-11-16 · 15:11 → 16:47 (96 min) · session e391bcc3
- 16:47 USER: artefacts/d_artefacts/, artefacts/design-B/, scales OK; art_LCC re-explained; title options.
- 16:23 USER answered layout Qs; ranges computed; art_LCC not pure artefact flagged; scale proposal.
- 15:57 USER approved names + file pattern; wants results/ reorg first (per notebook → a_interactive/b_fBVOC/c_non-BVOC; artefacts only proper; design A). Questions asked; megan nb difference explained.
- 15:40 USER: add LCC_FUT − CTRL_PD case → done in sandbox (a); questions on scale + art_PD vs art_FUT open.
- USER (annotated png of FUT_fBVOCctrlFUTdesignA split6-2 NET): suptitle + left group "[LCC − CTRL] _FUT", right "LCC_FUT_fBVOC [lccFUT − ctrlFUT]" (bracket bold), aliases from simulations-interpretation.pptx slide 2/3 "third column"; design B: keep "LCC_FUT − LCC_FUT_fBVOCctrlFUT*", footnote "* = artefact corrected".
- forcing_maps.py kwargs title/group_labels/footnote (a, ran). Sandbox outputs (a, viewed). Not yet in analysis nb (memory rule: ask before rerunning analysis/results figures).

## 2026-11-16 · 13:16 → 13:36 (20 min) · session ada6f70d
13:33 16 Nov session ada6f70d (block 13:16): USER 'yes' to commit plan → COMMITTED on main, not pushed (a): 3742cf6 notes analysis/→docs/ + refs; 7e8b906 design A figs; 127dfd9 MEGAN LMDI reruns; 9a8fb05 caches → /cluster/work; d1830f2 sandbox/test_cyclical_sim_year.py; 3351b6b logs. USER 'yes' fix lake_fix_effect → FIG_DIR = results/figures-2001-2014/megan_factors (cell 1 + md cell 0); rerun failed twice: HOME FILE QUOTA (99 530/100 000 files; also broke git + conda imports, looked like NIRD HDF errors). USER OK → deleted 6 unused ~/.vscode-server/cli/servers/Stable-* (kept 69047191 in use) + 4 old code-* binaries → 73 949 files (a). Rerun HDF5_USE_FILE_LOCKING=FALSE: all 6 code cells OK, 0 errors (a) → b5608cc. USER 'commit last updates' → 1995c62 simulation-contrasts figs move (session d963b45a work, done 13:20). Left untracked (other sessions): cases-scripts/run_when_done/megan_lmdi_maps_when_FUT_done.sh, sandbox/test_fut_minus_pd.py. GOTCHA: home file quota near limit again ⇒ git 'Disk quota exceeded' / random Errno 5 I/O errors; check `dusage`. 13:35 USER 'commit analysis/simulation-contrasts change' → ALREADY in 1995c62 (nb + 9 png deleted from analysis/simulation-contrasts_outputs/ + 9 *_2001_2025 png added in results/figures/simulation-contrasts/; 9 *_2001_2014 copies in results/figures-2001-2014/simulation-contrasts/, gitignored .gitignore:52 as for all figures-2001-2014) (a); working tree clean except 2 untracked files of other sessions.

## 2026-11-16 · 13:08 → 13:14 (6 min) · session 90ef7026
13:14 16 Nov session 90ef7026 (block 13:08): (1) USER: move analysis/*.md → docs/. DONE (a): git mv FBVOC_ARTEFACT.md, MEGAN_ATTRIBUTION.md, PLOTTED_VARIABLES.md → docs/ (analysis/README.md kept); refs rewritten to docs/<name>.md in ~25 files. (2) USER: commits to suggest? PROPOSED (not done, waiting): A housekeeping = md move + refs + .gitignore **/cache + CLAUDE.md cache note + results/README.md contrast-figs note; B design A = analysis/artefact-corrected-split.ipynb + 9 new png results/figures/artefacts/design-A-split/ + designA_figs{,2} logs; leave out sandbox/*.py + logs (user rule 11:44). DO NOT COMMIT (a): analysis/megan-lmdi-attribution-maps.ipynb rerun at ~13:10 FAILED cell 2 'NetCDF: HDF error' (NIRD lock → rerun with HDF5_USE_FILE_LOCKING=FALSE; committed 60e3b5c version is good; still has old ref analysis/MEGAN_ATTRIBUTION.md); diagnostics/3_megan-exact-split-test/lake_fix_effect.ipynb ANN rerun FAILED 3× cell 11 FileNotFoundError results/figures/megan_factors/before_lake_fix/FUT_isoprene_attribution_ANN_2001_2014_before_lake_fix.png (figures reorg; now likely in results/figures-2001-2014/ (b)) → restore from HEAD or fix path + rerun. Path-only nbs in commit A: cumulative_radiative_decomposition, megan-lmdi-vs-approx, fbvoc_artefact_causes, gamma_eff_vs_GAMMA_check, megan_patch_branch_5day_test.

## 2026-11-16 · 13:07 → 13:20 (13 min) · session d963b45a
- simulation-contrasts figs moved analysis/simulation-contrasts_outputs/figures → results/figures[-2001-2014]/simulation-contrasts/; nb FIGDIR, pptx builder, both READMEs updated. Not rerun, not committed.

## 2026-11-16 · 11:44 → 11:50 (6 min) · session 0706ae25
- READ-ONLY. Reviewed diagnostics/0_check-spinup-equilibrium-uncomplete (abandoned, superseded by 0_check-simulation-equilibrium/equilibrium.py; unique = quick spin-up LCC FUT figs + MET global-mean nc) and _old/ (all utils ported to src/; nothing needed). Plan file written, not approved. No files changed besides logs.

## 2026-11-16 · 11:39 → 11:44 (5 min) · session 4d122426
Commit suggestions regrouped by topic (user rule); 4 commits made 785f809, 60e3b5c, e30ac19, d940ad8 (see NOW 11:44). Sandbox scripts + logs left uncommitted on request.

## 2026-11-16 · 10:59 → 11:31 (32 min) · session 6ce7bd45
- Background-aerosol nbs: PD/FUT §8 GHG + §9 online sources + roles table; NEW LCC_FUT−CTRL_FUT nb; details NOW.

## 2026-11-16 · 11:22 → 13:43 (141 min) · session 89a5509c
- Caches moved to /cluster/work (home quota full); 6 sim-year drift figs done without NIRD; seasonal pending (NIRD); FUT SOA spin-up ~3 yr in PD-emission runs.

## 2026-11-16 · 11:00 → 11:13 (13 min) · session 89a5509c
- Cyclical PD/FUT plots on a simulation-year axis (sandbox/test_cyclical_sim_year.py); year-2000 cache gaps (BVOC atm, ET lnd) being filled by cache/run_2000_missing.sh (run_2000.sh shift bug).

## 2026-11-16 · 10:56 → 11:08 (12 min) · session 1b77ec0b
- User: fix 2001–02 month offset; rerun ANN MEGAN nbs; exact LMDI maps replace approximate ones. Details NOW 11:06.

## 2026-11-16 · 10:58 → 12:33 (95 min) · session e425a9ff
- pptx integrity check OK (all decks + 339 png); pptx decks rebuilt for design A + 2 missing design-A figure sets (budget split A, art_LCC_own Ghan maps); NIRD HDF-lock gotcha; details NOW.

## 2026-11-16 · 10:59 → 11:02 (3 min) · session fc06b4b6
Status + watcher start: MET job 1 running (2029-10, ends ~19:00); watcher started 11:00 (had not been running); timing estimate given. Details NOW.

## 2026-11-16 · 10:58 → 13:18 (140 min) · session ae435137
- (15 Nov 19:40–19:45, logged now) LMDI attribution maps PD: analysis/megan-lmdi-attribution-maps.ipynb → results/figures/megan_factors/PD_*_attribution_LMDI_*_6yr.png (4) + table megan_lmdi_attribution_PD_45N.csv; numbers in NOW. FUT batch status + ETA in NOW. 11:55 confirmed month-offset FIX already decided/in progress (1b77ec0b); my maps auto-rerun after swap.

## 2026-11-15 · 19:15 → 19:24 (9 min) · session d8d4f4eb
- Q&A: plotting cyclical (time-slice) PD/FUT runs → paired FUT−PD by nudging year, seasonal cycle, no continuous 2000–2100 axis.
- NEW sandbox/test_fut_minus_pd.py + _outputs/ (fut_minus_pd_{global,regional}_2001_2025.png, forest_effect_change_{global,regional}_2001_2025.png, fut_minus_pd_2001_2025.csv). Input = absolute table from timeseries-responses.ipynb §3 (a). Not committed.

## 2026-11-15 · 19:00 → 19:05 (5 min) · session 91ef3258
- 19:05 15 Nov session 91ef3258 (block 19:00): USER asked MEGAN_LMDI workflow with logic + motivation → NEW docs/workflows/workflow_MEGAN_LMDI_logic.png (10 steps + side boxes, each 'WHY ▸' line; status box = 15 Nov 19:00: PD 6 yrs reduced, FUT batch 1 jobs 1803926/28 running, 1803949-52 queued, 2010 chain building) + NEW docs/workflows/draw_workflow_MEGAN_LMDI.py (matplotlib, regenerable: $PY docs/workflows/draw_workflow_MEGAN_LMDI.py; nxt() spaces rows by tallest box). Old workflow_MEGAN_LMDI.png (6 Nov snapshot) kept, untouched. Sources: MEGAN_ATTRIBUTION.md, megan-lmdi READMEs, this log. Not committed.

## 2026-11-15 · 18:41 → 18:56 (15 min) · session 6509e9d2
Read-only cleanup audit (see NOW). No files changed except logs. designB-standin = pre-design-A snapshot of 11 Nov (designA_24g_when_done.sh:84-91).

## 2026-11-15 · 18:53 → 19:41 (48 min) · session fc06b4b6
MET+nudged 2026-2040 implementation (plan approved; work 18:00-18:50 before the session restart). Folder renamed to _6h_2000-2040 + symlink; build/regroup/check scripts; one switch function; 12e MET continuation + nudged phase script; watcher + 2001-2040 analysis script; record docs/met-nudg-2026-2040.md. MET submitted 18:59 (1803953/1803954). Watcher start blocked by permission check -> user. Details in NOW.

## 2026-11-15 · 18:39 → 18:43 (4 min) · session 08562175
- Q: delete analysis-2001-2019? Checked failed/empty temp set → user OK → deleted + refs cleaned, uncommitted. Details NOW 18:43.

## 2026-11-15 · 16:55 → 16:57 (2 min) · session 111565e9
- User asked which palette was decided / is it P → Q1 (sandbox/test_palette_picture.py PICTURE_Q; P differs only in red #C4524E vs #BC423E). No changes.

## 2026-11-15 · 16:57 → 19:51 (174 min) · session 1b77ec0b
- 16:57 status check. 17:03 user: design A+B nbs, Methods update, answers on MEGAN raw/LMDI/FUT, 2026-2040 → other session. Details NOW 17:35.

## 2026-11-11 · 15:41 → 15:54 (13 min) · session 0e06cada
- Plans index ~/.claude/plans/INDEX.md + auto-sort hook plans_index.py (PostToolUse Write|Edit); header explains auto vs by-hand. See NOW 15:54.

## 2026-11-11 · 12:25 → 12:33 (8 min) · session d23b46ef
- User OKs: 24g 2001-2025 pp + design-A switch (running, waiter), land carbon/water deck (auto after switch), FBVOC_ARTEFACT.md H6 (done). See NOW 12:33.

## 2026-11-11 · status check · session d23b46ef
- Status check, see NOW 11 Nov.

## 2026-11-09 · 17:10 → 17:23 (13 min) · session cd28f708
H6 conclusions in fbvoc_artefact_causes.ipynb (cells 61–63 + summary), rerun EXIT 0: artefact = weather link (~2.5/3.0 %), 2-yr clim still half, wrong mean only regional P.

## 2026-11-09 · 16:42 → 17:55 (73 min) · session c2b27a7c
FUT background aerosol explained (all prescribed emissions = SSP585 yr 2100, cyclical; strat volc identical PD/FUT; DMS ocean + SST 2090–2100); user_nl_cam DMS override in CTRL_FUT ignored (group syntax). New nb diagnostics/background-aerosol-pd-fut/background_aerosol_pd_fut.ipynb DONE: SOx 70.6→29.7 Tg S, BC −56 %, NOx −23 %, NH3 +48 %, fires ±20 %; model sulfate −39 %, AOD +6 %.

## 2026-11-09 · 17:01 → 17:10 (9 min) · session 4eca6534
Raw-deletion checklist proposed (no changes): 4/6 years reduced all PASS; ~5 TB raw; need 2006/2011, LMDI-vs-approx, output-coverage OK from user, NIRD copy.

## 2026-11-09 · 16:40 → 16:50 (10 min) · session 4eca6534
Status check only (no changes): 24g phase1 ends ~18:00, phase2 → ~21:00 10 Nov; MEGAN PD_2002 reduced OK, 2006 reducing, 2011 next; batch-2 archive TIMEOUTs harmless; C0102 done.

## 2026-11-09 · 16:44 → 16:46 (2 min) · session f963f9be
Commit plan (8 commits, none made) for 592 uncommitted paths since 12c1e2d. pptx moved by user to results/pptx/: paths verified (a); 2 decks >100 MB → gitignore. Memory path updated.

## 2026-11-09 · 16:25 → 17:20 (55 min) · session a0599c5f
- Status check: land-carbon-water nb done, numbers re-verified from final csv (see NOW 16:27). Outputs moved to results/ (see NOW 17:03).

## 2026-11-09 · 13:29 → 13:37 (8 min) · session a0599c5f
- nb run killed at previous session end → relaunched detached (see NOW 13:31); interactive carbon grid numbers in NOW.

## 2026-11-09 · 13:18 → 13:25 (7 min) · session a0599c5f
- Land carbon/water plots requested → new nb analysis/land-carbon-water.ipynb (see NOW 13:25). Files ready: <ALIAS>_lnd_{BIOGEOCHEM,ET,LAND}_2001-2025.nc for all 11 runs (a). ET total was already in HYDRO_PANELS; GPP/NEE etc. plotted nowhere before (a, grep).

## 2026-11-09 · 08:55 → 09:38 (43 min) · session d7d2f7b6
- Q: deck in user's own theme → results/BOREAL_figures_2001-2025_CICERO.pptx on results/cicero_template.pptx (269 slides, 260 figs). Old own-theme deck kept (ask before deleting).
- Q: separate MEGAN factors deck → results/BOREAL_MEGAN_factors_2001-2014_CICERO.pptx (46 slides, 38 figs; 2001–2014 only, nb not run on 2001–2025). Shared helpers results/cicero_pptx.py; generators build_figures_pptx.py (refactored, identical output) + build_megan_pptx.py.
- Q: simulation-contrasts.ipynb to 2001–2025 + pptx → nb already 2001–2025 (run 05:41–06:04, inputs unchanged since; not rerun) → results/BOREAL_simulation_contrasts_2001-2025_CICERO.pptx (12 slides, 9 figs), build_contrasts_pptx.py. validate PASSED.

## 2026-11-09 · 08:08 → 08:20 (12 min) · session d7d2f7b6
- Task: user asked for a downloadable PowerPoint of results/figures/ organised in sections/subsections as a story.
- Output (a): results/BOREAL_figures_2001-2025.pptx; generator results/build_figures_pptx.py. 16:9, images JPEG q88 at 200 px/in of displayed size (white behind RGBA), file path in footer + notes.
- Story: 1 Experiment & runs (contrast table, absolute timeseries) → 2 interactive → 3 non-BVOC → 4 fBVOC (clouds before surface) → 5 PD vs FUT attribution → 6 artefacts (+ design-B split, individual-scale, split6-2). Subsections per category: budget, annual Ghan, seasonal Ghan, timeseries+paired years, surface/snow/water, BVOC/aerosol/clouds.
- No node/soffice on Betzy: python-pptx in scratchpad venv; QA by own PIL render of 6 slides (b: Liberation Sans proxy, conservative) + validate.py (needs py≥3.10 + defusedxml).

## 2026-11-09 · 07:31 → 08:50 (79 min) · session daa384fc
- USER Q: where is the forcing-decomposition plot after the reorg → artefacts/design-B-split/.
- USER: same figure for FUT_fBVOCctrlPD + FUT_fBVOClccPD (2014 + 2025) → 24 figs done; then subfolders individual-scale/ + split6-2/ (nb cell 8 + README). See NOW.
- USER OK 08:06: ctrlPD/lccPD back in nb + rerun done OK 08:49 (see NOW).

---

## 2026-11-09 · 07:29 → 07:31 (2 min) · session 58a36ed1
- USER: figures/ + tables/ = 2001–2025 only; 2001–2014 → figures-2001-2014/, tables-2001-2014/. Done + verified (a), see NOW.

---

## 2026-11-09 · 07:26 → 07:50 (24 min) · session 880cb2fa
- Status check (07:28), then user OK → rerun 2 failed nbs; timeseries-responses run_span fix; both rerun OK 07:48. See NOW 07:50.

---

## 2026-11-09 · 01:20 → 02:11 (51 min) · session e02674e3
- Column-shared colour scale for contrast grids (scale='column' opt-in, tiered reductions); sandbox test done, waiting user OK; details NOW 02:11.

## 2026-11-08 · 23:55 → 01:42 (108 min) · session 6fa0a97f
- 23:57 fbvoc_artefact_causes.ipynb up to date (a): rerun 7 Nov 00:44 after sign flip, 0 errors, A −3.03 %, committed ec86b83.
- 00:10 explained: replay → climatology not prescription path (a); (i) weather link vs (ii) mean mismatch not separated (b); convection = guess.
- 00:30 user sign Q answered: A −3.03 % = interactive has less SOA than prescribed.
- 00:47 DONE (a, user OK 00:23): fbvoc_artefact_causes.ipynb (old-chain) → caption cell 54 fixed + NEW section cells 56–58 'Mechanism figure' (fig fbvoc_artefact_causes_outputs/figures/mechanism_soa_lifetime.png; tables mechanism_A_R_by_band_layer.csv, mechanism_tropical_mean_pressure_shift.csv); full rerun run_nb_inplace EXIT 0, 0 errors (log results/tables/logs/run_fbvoc_artefact_causes_20261109_mechanism.log); uncommitted; backup scratchpad nb_backup/. Findings tropics 30S–30N, 2001–2002, Δp-weighted: prescribed run ISOP +18 % / MTERP +12 % at 400–100 hPa, ISOP −18 % at 850–700 hPa; mass-weighted mean p shift ISOP −16.4, MTERP −9.5, SOA_LV −8.4, SOA aer −6.6 hPa (replay ≤ 0.4); OH/O3 |A| ≤ 0.8 % all bands/layers; SOA aer A −3.6…−5.6 % at 400–100 hPa all bands (R ≤ 0.8). Convection premise UNTESTED (h1 has only SFISOP/SFMTERP/MEG_*; no daily convection). WAITING USER: 2001–2002-climatology run to split weather-link vs mean-mismatch (not set up). Not done: FBVOC_ARTEFACT.md not updated with these numbers.

- 01:40 USER OK 01:16 → CTRL_PD_fBVOCctrlPD_C0102 (old chain, 2001–2002 climatology of CTRL_PD -20261023, 3 yr) SET UP (a): clim job 1795283 COMPLETED (19 files in shared bvoc_emissions/ ems_<CTRL_PD>_2001-2002_*; check_bvoc_climatology OK 01:29); NEW cases-scripts/14f-…C0102….sh (copy of 14d without replay_prerun); watcher run_when_done/run_C0102_when_done.sh PID 1898963 login-2 (log run_when_done/logs/run_C0102_when_done.log) → SUBMITTED 01:42 jobs 1795302(RUNNING) 1795303(PENDING)  → wait rest 2003-01-01 → postprocess BVOC SOA CHEM CLOUDPROP RADIATIVE into 2001-2014-all-bvoc-pre-co2-fix/ alias CTRL_PD_fBVOCctrlPD_C0102 → rerun fbvoc_artefact_causes.ipynb (H6 cell 60, dry-run tested with replay as stand-in OK). Registered: run_aliases.csv, cases-scripts/README.md, CLAUDE.md table. USER sign confusion: raw global SOA_cb 2001–02 (a): CTRL_PD 2.4375, fBVOCctrlPD 2.5115, replay 2.4494 mg m-2 → prescribed MORE; figure now states 'A < 0 = more in prescribed' + raw burdens (cell 57; nb rerun EXIT 0). Uncommitted: nb, 14f, watcher, docs.
## 2026-11-08 · 21:59 → 23:05 (66 min) · session 2e8818ca
- 23:05 REORG code done for ALL nbs (a): cumulative (D1 CTRL_[FUT−PD], D2 nonBVOC FUT, D3 art_LCC_FUT − art_CTRL_FUT; RAN EXIT 0: ≥45N D2 +0.257±0.039 (was +0.170), D3 −0.056±0.045 (was +0.031), D1 +0.984, T +1.185 W m-2; figs results/figures/interactive/, table results/tables/), artefact-corrected-split (labels [LCC − CTRL] / [LCC − CTRL]_fBVOCctrl / art_LCC / art_CTRL / art_LCC − art_CTRL; EXTRA_SOURCES dropped; out results/{figures,tables}/artefacts/[design-B-split]), fut-fbvoc-emission-source-choice (rows = fBVOC FUT contrasts via design-B stand-in = same numbers as old corrected rows; old outputs → its _outputs/pre-reorg-20261108/), pd-fut-attribution (GROUPS PD/FUT of category contrasts; figs results/figures/pd-fut-attribution/; md findings NOT updated, note added), simulation-contrasts (uses fm.LCC_FUT_FBVOCLCCFUT). src: baseline_table(contrasts=), make_percent_change_figure(rows=). READMEs analysis/ + results/ rewritten, CLAUDE.md results row + "Analysis contrasts" bullet. RUNNING tmux login-3: reorgA radiative_forcing (cell 3 budget at 23:01), reorgB bvoc→hydro→timeseries (bvoc cell 3), reorgD artefact-split→fut-fbvoc→pd-fut→simulation-contrasts; logs results/tables/logs/run_<nb>_20261108_reorg.log. Checked fig: interactive context grid OK. PEER 4f89c2b2: scheduled auto switch to 2001-2025 (cases-scripts/run_when_done/analysis_2001-2025_when_done.sh pid 749822) waits for my run_nb processes, then patches START/END_YEAR + EARLY/LATE in 9 nbs/forcing_maps and reruns; patterns verified compatible, replied; I start NO further analysis runs. NEXT: check EXIT lines + figures of each nb; markdown findings of pd-fut-attribution/fut-fbvoc/artefact-split still old.
- 22:57 USER REORG (22:36 + answers 22:44): only 19 contrasts in 4 categories interactive / fBVOC / non-BVOC / artefacts; topic nbs loop categories; other nbs kept but switched; old results archived then regenerated; LCC_FUT_fBVOClccFUT = design B "TO BE REPLACED LATER". DONE (a): src forcing_maps.py (backup scratchpad forcing_maps.before_categories.py): CATEGORIES, FIG_CATEGORY/TABLE_CATEGORY (results/{figures,tables}/<cat>/), LCC_FUT_FBVOCLCCFUT_DESIGN_B=True + LCC_FUT_FBVOCLCCFUT VirtualRun, Contrast dataclass (key/label/one_line/row_label/design_b), CONTRASTS, contrast(key), budget_groups(), tick_label(), category_aliases(); make_contrast_grid_figure(category) rows+labels+folder; make_ghan_contrast_figure (tested on design-B row, closure 1e-5); radiative_budget_table/make_radiative_budget_figure/make_paired_years_figure/make_emission_origin_figure groups= ; water_budget_table sets= (+VirtualRun); zonal_profile_difference VirtualRun + profile labels; figure_path mkdir. Legacy API kept (diagnostics/yearly-difference-autocorrelation, analysis-2001-2019 use it). ARCHIVED: results/figures/{LCC-CTRL,CTRL_FUT-CTRL_PD,fBVOC,timeseries} → results/figures-pre-reorg-20261108/; results/tables/{artefact-design-B,pre-artefact-correction,*.csv} → results/tables-pre-reorg-20261108/ (logs/ stays; megan_factors/ stays). Rewritten: radiative_forcing (budget per category + paired years + Ghan annual/seasonal per contrast; 6-panel summaries DROPPED), bvoc-soa-cloud (grids/cloud types/seasonal lines/profiles per category; per-period context maps DROPPED), biogeophysical-hydro, timeseries-responses. nb backups scratchpad nb_backup_reorg/. RUNNING tmux login-3: reorgA radiative_forcing, reorgB bvoc→hydro→timeseries; logs results/tables/logs/run_<nb>_20261108_reorg.log (EXIT line). TODO: cumulative (D1 CTRL_[FUT−PD], D2 nonBVOC FUT, D3 art_LCC_FUT − art_CTRL_FUT), pd-fut-attribution, fut-fbvoc-emission-source-choice, artefact-corrected-split, simulation-contrasts → registry; READMEs (analysis, results), CLAUDE.md layout row.
- USER corrected pairs of analysis/simulation-contrasts.ipynb (a, edited via scratchpad fix_pairs.py; backup scratchpad simulation-contrasts.before_pairs_fix.ipynb): ARTEFACT art_LCC_PD = LCC_PD − LCC_PD_fBVOCctrlPD, art_LCC_FUT = LCC_FUT − LCC_FUT_fBVOCctrlFUT (USER def; CTRL arts unchanged own-emission); Fig 3b row 2 = LCC_FUT_fBVOCctrlPD − CTRL_PD_fBVOCctrlPD (CTRL_FUT_fBVOCctrlPD dropped, no longer needed anywhere in nb); Fig 2 rows 2–4 use design-B stand-in VirtualRun 'LCC_FUT_fBVOClccFUT[design B]' = LCC_FUT − CTRL_FUT + CTRL_FUT_fBVOCctrlFUT, auto-switch to real 24g when processed. diff rows now flagged v.diff_row=True (DIFF_CMAP/line keyed on that, not isinstance VirtualRun). Markdown header, §2, §3b, §4a, §4b updated. RERUN DONE 22:14, all 9 figs, 0 cell errors (a; harmless logging traceback at kernel shutdown). Checked figs 2/3b/4a: 3b rows ~equal (CC dominates, LCC part small); 4a ≥45N SOA PD −0.028±0.015, FUT −0.086±0.041 mg m-2. Uncommitted.

## 2026-11-08 · 21:57 → 22:30 (33 min) · session 4a626602
- Commit plan given (a): 1 sign flip, 2 simulation-contrasts, 3 analysis-2001-2019, 4 preprocess BVOC new chain, 5 D1 far-field + decomposition logs, 6 docs; draft repo: methods-claude.tex.
- All committed (a), not pushed: ec86b83, 82ac2ca, 45b8bfb, 5aa5f88, bd06467 + docs commit; draft repo 1 commit. CLAUDE.md split: 2 sign hunks in ec86b83 (git apply --cached --unidiff-zero), rest in docs commit.
- 22:30 status: new edits by other sessions (contrasts pair fix + 2 running nbs) → wait, then 2 more commits.

---

## 2026-11-08 · 21:46 → 23:23 (97 min) · session c46e88fa
- NEW preprocess/bvoc-emissions/plot_bvoc_timeseries.ipynb (a): yearly SFISOP/SFMTERP Tg/yr, modified cells, 19 contrast pairs (user list, corrected 22:07), 12 runs, one shared y-range; 24g from raw h0 2001–2009. Non-BVOC Δ = 0; art_LCC_* (vs ctrl emissions) = LCC−CTRL emission change; art_CTRL_* +0.05 %. Colours: LCC/lcc red-navy, CTRL/ctrl orange-teal (FUT warm, PD cool), fixed BVOC dashed. Figures saved in plot_bvoc_timeseries_outputs/.

## 2026-11-08 · 21:47 → 23:09 (82 min) · session da0cb87f
- plot_bvoc_emissions.ipynb was old-chain CTRL -20261023 → user OK → updated to 4 new-chain sources + LCC−CTRL maps; species nb + README adapted; both nbs rerunning in tmux bvocplots (see NOW 21:56).

## 2026-11-08 · 22:34 → 23:04 (30 min) · session 4f89c2b2
- Batch 2 verified submitted/running; answered 'all runs to 2025?' (no: 24g still at 2014). See NOW 22:37.
- User: process the 11 nudged runs for analysis → 2001-2025 postprocessing launched to NIRD staging (see NOW 22:45).
- Early/late split: user chose 2001–2014 / 2015–2025. Unattended analysis switch + rerun script launched (NOW 23:02).

## 2026-11-08 · 21:04 → 21:04 (0 min) · session 4f89c2b2
- User: fix batch 2 → relaunched by hand with the same launcher (see NOW 21:06). Submission check pending.

## 2026-11-08 · 12:51 → 12:55 (4 min) · session 4f89c2b2
- Status check (see NOW 12:55). Found batch-2 waiter exited on a transient 'jobs queued' refusal 07/11 09:09; plan-only passes now; asked user to relaunch. Nothing changed.

## 2026-11-07 · 00:33 → 01:30 (57 min) · session cb4be630
- User: artefact sign convention → interactive − prescribed (art = CTRL_P − CTRL_P_fBVOCctrlP; corrected = uncorr − art) everywhere, incl. old-chain cause nbs (user 00:40). Source/docs done; 7 reruns EXIT 0, numbers checked, stale files deleted (see NOW 01:30).

## 2026-11-07 · 00:13 → 01:08 (55 min) · session eff577b5
- New analysis/simulation-contrasts.ipynb (user): contrast grids per question, CONTEXT_PANELS minus lwp, FIGURES dict (1a…4b), AVAILABLE check of BVOC/SOA/CLOUDPROP atm + ET lnd files; pending rows drawn empty with label. Generator (not in repo): scratchpad make_nb.py. analysis/README row added. Runs in tmux (simcontrasts, simcontrasts2).
- 00:51 user: row 3 = row2 − row1 in 1b/1c/3a/4b, line above it, orange–blue-teal colours on row 3 only (VirtualRun + _plot_panel wrap).
- (a) CTRL_FUT_fBVOCctrlPD: no script/run/alias. LCC_FUT_fBVOClccFUT: 24g running.
- Uncommitted: analysis/simulation-contrasts.ipynb, analysis/simulation-contrasts_outputs/, analysis/README.md.

## 2026-11-07 · 00:10 → 00:25 (15 min) · session 83498e52
- Loader speed-up (FUT decomposition + D1), D1 hatching, FUT identity-check tolerance fix; both reruns OK; FUT conclusions (§10, §14–17) written (see NOW).

## 2026-11-07 · 00:07 → 00:12 (5 min) · session dc82b504
- Listed pending decisions (memory + methods-claude.tex ONHOLD: FUT fBVOC source, journal). User: batch 2 YES, raw deletion on hold, LMDI comparison no rush. Batch 1 still running → batch-2 waiter in tmux megan_b2 (see NOW). Memory boreal-megan-swaps-pending updated.

## 2026-11-06 · 21:54 → 22:30 (36 min) · session fa133924
- Commit proposal (8 groups) + clarified forcing_maps.py (VirtualRun code, not only renames); "commit now" = 6 groups, hold running nbs + 2001-2019 (AERSIZE failed 11/11). Log file emptied 21:55, restored from 21:29 snapshot (see NOW). User committed most groups; I committed 9c1f5bc, c99974a, 60a05a5 (22:26), then undid them on request (reset --mixed, changes kept, 22:30).

## 2026-11-06 · 21:21 → 21:24 (3 min) · session a3a096fb
- Swaps already implemented (a54817a0); explained groups/caveats; unit options table + status into MEGAN_ATTRIBUTION.md (NOW 21:24).

## 2026-11-06 · 20:33 → 22:05 (92 min) · session e28a984f
- Q: what is radiative_forcing_2001-2019.ipynb → orphan of 570e9150. Built self-contained analysis-2001-2019/ (nb moved in + repointed, cases.txt, prepare.sh, README). Duplicate debug run killed. prepare.sh then filled HOME quota (processed/ on home) → AERSIZE failed, killed, .part removed; awaiting user on data location (work proposed), design-B copy, design-A row fix.

## 2026-11-06 · 20:32 → 22:40 (128 min) · session 83498e52
- 22:46: D1 + zonal done; FUT nb failed/killed again → tmux relaunch 22:42 (see NOW).
- 22:06: D1 + how_warmer reruns complete OK; FUT nb cell 40 failed (old code ran) → relaunched 22:05.
- 21:25: FUT nb slowness diagnosed (serial raw h0 reads, ~2,900 opens); reruns died with session, restarted setsid.
- Status check of 7 items; FUT emissions nb killed + restarted; zonal colours applied + rerun; D1 dup-label fix + path fix + rerun (see NOW).

## 2026-11-06 · 20:26 → 21:58 (92 min) · session a54817a0
- Recap; swaps decided 17:55 (never logged, fixed). USER YES 20:32 → swaps implemented + validated (test60d 60 d + jul2010 3 d ALL PASS), live 21:15; test60d output rewritten; PD_2010 re-reduction running (NOW 21:17).

## 2026-11-06 · 20:19 → 21:13 (54 min) · session 28813a15
- Q: old fut-fbvoc-emission-source nb corrected? No. User: port missing parts (Ghan maps, ctrlFUT−ctrlPD row) + retire it → done (git mv to analysis/_old). Then user: -choice corrected only + new how_big_artefact_is_FUT.ipynb (uncorrected/corrected interleaved grid) → done; monthly_difference VirtualRun-aware; both nbs running (NOW 20:55).

## 2026-11-06 · 20:16 → 20:17 (1 min) · session 28813a15
- Q: are §3 contrasts in fut-fbvoc-emission-source-choice corrected? No (only §2). Added design-B corrected rows to §3 grid via fm.corrected_fbvoc; nb rerun (NOW 20:17).

## 2026-11-06 · 18:02 → 20:46 (164 min) · session ffd2d7c5
- Q: MEGAN case names → answered (NOW 18:03). Rename LCC 2010 date: advised no.
- User OK 18:08: CTRL_PD 2005 resubmitted (1791950/1791951). Climatology fix left to the other session already running rephase_branch_h1.sh; peers messaged (NOW 18:15); adelez-23 is not the owner → confirmed adelez-d4 = 570e9150 owns it, notes accepted.
- Explained the climatology failure + my alternative fix to the user (NOW 18:22). Verified all other prescription sources are phase 0 hybrid runs; LCC_FUT branch pieces are the only exception (NOW 18:31).
- Why 3 pieces: speed, restarts only at 2005/2010; in hindsight no net gain (NOW 18:36). User keeps splitting as the approach; pitfalls saved to memory (NOW 18:51).
- 19:44 status: 24g fix stalled after rephase (other session idle); offered to finish; analysis options asked (NOW 19:50).
- 19:51 user OK: finished 24g fix (merge, array 1792015, watchers restarted); run_aliases.csv updated; FUT emissions nb §17 crash fixed + rerun; new analysis/fut-fbvoc-emission-source-choice.ipynb running; 5 methods NUM boxes filled (NOW 20:05).
- 20:08 explained the full 24g + MEGAN action sequence (NOW 20:12).
- 20:40 workflow diagrams → docs/workflows/*.png (NOW 20:47).
- 20:45 source-choice nb §5 reading written; decomposition nb conclusions handed to session 83498e52 (NOW 20:46).

## 2026-11-06 · 17:40 → 18:16 (36 min) · session ffd2d7c5
- Status check (see NOW 17:55). Found: 24g climatology phase mismatch s1 vs s2/s3 (24g not started); MEGAN CTRL 2005 Slurm launch failure. Nothing changed; fixes proposed to user. 18:12: peer msg misaddressed (24g fix is another session's: rephase_branch_h1.sh); CTRL 2005 resubmitted by peer (1791950). Replied, nothing changed.

## 2026-11-05 · 17:25 → 18:42 (77 min) · session 570e9150
- 17:25 user OK: archive fix + auto-fix rule, nudged extension, MEGAN batch 1 → archive_guard.sh, extension watcher, MET watcher bug fixed, folder build. 18:12 user: + LCC_PD_fBVOClccPD extension, LCC_FUT_fBVOClccFUT (24g, automated), batch 1 keep-raw auto on test pass, swap decision asked (see NOW 18:27). 18:34 user: 24g to 2026 too (extend_24g watcher); left, swaps to decide later.

## 2026-11-05 · 15:05 → 15:10 (5 min) · session 570e9150
- Status check (see NOW 15:10). No files changed except logs.

## 2026-11-04 · 14:50 → 16:21 (91 min) · session e60507d0
- Q: MEGAN gamma runs on hold? → no hold; not started, scripts missing (a). User: YES write production script + launcher.
- FOUND (a): parents' rest/ only 2005, 2010, 2015 (20 files each; LCC_FUT 19); 24f run dirs have yearly restarts 2001–04 (s1) but DOUT_S_SAVE_INTERIM_RESTART_FILES=FALSE. User: leave 24f; change years; test 2005-01-01.
- Design: branch_meganpatch.sh RUN START [--days N] [--check-only] (parent user_nl verbatim, slim hist as 13a 5-day template, met_data_file → start date, CAM_AEROCOM from parent, compare_xml/compare_namelists vs parent, build only). Launcher: test PD | batch PD|FUT YEARS; gate = PD_test32d.ok + all earlier plan lines .ok; chains 2005–09 / 2010–14 contiguous; new chain → RESUBMIT=n−1; existing → rest must be y0-01-01 + nothing queued → CONTINUE_RUN=TRUE; submit via env -i bash -l case.submit --batch-args=--exclude=b5165,b5175,b5179,b5180; plan.txt/chains.txt in /cluster/work/users/adelez/megan-lmdi/<P>/. Watcher: 365 (test 32) tape-2 files of YEAR in both archives → sbatch reduce_year_job.sh (preproc, module netcdf4-python since /nird not on compute) → .ok → cp -n+cmp to data/processed-data/megan-lmdi/. Job: identity CTRL+LCC → (test: megan_replay on Jan31+Feb1) → reduce --year (delete yes/dry/no).
- Gotchas (a): /tmp scratchpad not visible from compute nodes. preproc 15:26–15:38: jobs 1788302 (b5203), 1788307 (b5204, with --exclude), env tests 1788310/11 (direct + env -i, b5203) all hang after `lmod/init/bash: Invalid argument` → all cancelled; b5203 kept in BAD_NODES; watcher default = login mode. Editing a running watcher script is unsafe (old watcher submitted 1788305 after state reset; killed). Don't `pkill -f` a pattern that matches the own shell (exit 144).
- 15:56 user: keep restarts per batch (→ watcher NIRD copy) + run 2015–2017 (→ chain 2015, extended met, waits for parents' extension output). Tested plan-only + restart copy (a).
- 16:04: user: restart = end-of-batch restart for continuing (already so); chain 2000–2003 (hybrid from spin-up, 2000 deleted) instead of 2015–17. Done + check-only tested (a).

## 2026-11-04 · 14:22 → 15:04 (42 min) · session 8e206b5a
- user: include fBVOClccPD + fBVOCctrlPD in analysis/artefact-corrected-split.ipynb → FUT extra corrected contrasts 'BVOC corr (lccPD)', 'BVOC corr (ctrlPD)' (EXTRA_SOURCES, pairs_for) in §1–§5 + md cell 0 (a). Rerun 14:34, log results/tables/logs/run_artefact_corrected_split_20261104.log; cell 1 ok 38 s (a). Backup /tmp/claude-204914/-cluster-home-adelez/8e206b5a-3f2e-4a64-a318-79b19ede1448/scratchpad/artefact-corrected-split.before.ipynb, edit script edit_nb.py same folder. Uncommitted: notebook.

## 2026-11-04 · 14:20 → 16:52 (152 min) · session ec98f95d
- Status check (14:25): s1 2003-12, 14e 2007-11 (ends 2008-01-01, not 2010), MET 2019-01. Watcher liveness not verifiable from login-3 (no ssh to other login nodes).
- User answers 14:28: resubmit 24f s2/s3 YES (done: 1788236/1788238, met_data_file fix + script fix in cases-setup.sh/24f); plan 14e to 2014 (plan in NOW, not submitted); keep design A (BVOC_A, closed); contrast label: where to see (sandbox/test_group_label_outputs/); Methods ONHOLD: explained.
- User 14:37: 14e to 2014 (submitted 1788254 via new watcher; 1787435 archive failed → manual st_archive + old watcher manual mode); rerun radiative_forcing (running, + FUT_fBVOClccPD); FUT source stays on hold, plot all 3, Opt 3 added to methods-claude.tex table.
- User 14:56: results/ reorganised by contrast (figures) + tables renames; forcing_maps.figure_path routing; broke 8e206b5a's artefact-corrected-split run (rerun by me 15:07).
- User 15:37: run_when_done/ moved to cases-scripts/ (watcher restarted on 1788254/1788255).
- User 15:44: old-chain notebook rule → ask first; 2 old-chain nbs path text updated with OK.
- User 16:32: how_big nb + Figure D in % + section 4f (drivers of LCC_PD − CTRL_PD), run OK.

## 2026-11-04 · 11:58 → 12:05 (7 min) · session 233c5cc5
- Status check; found 24f s2/s3 met_data_file crash; s1 identity OK (a). No files changed except logs.

## 2026-11-04 · 00:45 → 01:31 (46 min) · session 84967989
Status LCC_FUT_fBVOClccFUT: not set up; only the design-A fallback if 14e fails (CLAUDE.md:84). 24d/24e figure label "lccFUT" was wrong (24d = lccPD). User chose to prebuild the LCC_FUT HR_BVOC rerun now: 24f LCC_FUT_HRBVOC, 3 segments (see NOW). Plan said yearly restarts → WRONG, only 2005/2010/2015 exist (a) → s1 hybrid 2000-04. Gate passed, built (~9 min each), submitted 01:29 (1787708/10/12). Merge script + NORESM_ARCHIVE passthrough written, not run.

## 2026-11-03 · 23:30 → 01:00 (90 min) · session 9e6f4132
MET 11-yr extension RUNNING (1787584; fixed 12d BRNCH_RETAIN_CASENAME, --batch-args=, b5 exclude); repro test PASS. Branch h1 files shifted (-21600) → new regroup_met_ext_days.py + rewritten 2000-2025 build script; watcher met_ext_watch_and_build.sh (PID 4038629) builds the folder after each MET segment, reruns a failed st_archive on login (preproc b52xx flaky). Nudged extension prepared: extend_nudg_runs_2015-2025.sh phase1/phase2 + switch_case_to_met_2000_2025 (restart stores the met file FULL PATH → ncatted on run-dir restart). Not submitted.

## 2026-11-03 · 23:25 → 23:30 (5 min) · session 70247179
Git commit plan (7 topic commits, none made). run_when_done move: advised to wait for 14e watcher (hard-coded paths, running); no files changed except logs.

## 2026-11-03 · 21:01 → 21:49 (49 min) · session 8672845b
**MET extension 2015–2025 prepared (scripts only, nothing submitted) (a).** See NOW line 21:46 for files, decisions, facts and next steps. User decisions 2026-11-03: years 2015–2025 (stop 2026-01-02, no patching); keep MET case name; minimal h0 like spin-ups; 10-day repro test (branch 2010-01-01, only 2005/2010/2015 restarts exist); one nudging folder `<MET>_6h_2000-2025` with all data, old `_6h_2000-2015` left untouched.

## 2026-11-03 · 21:40 → 21:41 (1 min) · session b157c5d7
- User asked for a point list of today's work; answered from human log. No files changed.

## 2026-11-03 · 20:11 → 21:23 (72 min) · session bc4585e4
- User: update FUT-fBVOC decomposition nbs to new runs + palette + hatching. Done as -after-co2-fix copies (CLAUDE.md old-chain rule), both run OK; nb2 results text rewritten, nb1 text pending; user interrupted, waiting. See NOW (a).

## 2026-11-03 · 19:52 → 20:38 (46 min) · session 69fd7b68
- Built `diagnostics/lcc-bvoc-background-contrast-maps/contrast_maps_uncorrected.ipynb` (+ `_outputs/{figures,tables}`): map grids for Q1/Q2/Q3 contrasts (user tables copied into markdown), artefact table: int−int none (Q1 r1,r4; Q3), int−presc yes (Q1 r2,3,5,6; Q2 r3,4), presc−presc largely cancels (b) (Q2 r1,2). All 9 aliases new chain 2001–2014 (a). Generator was a scratchpad script only (not in repo).
- Q2 (a numbers, b reading): FUT emission source dominated by PD→FUT environment, not by LCC (≥45°N row1 ISOP +0.011 vs row2 +0.52 mg m-2 d-1; SOA −0.0008 vs +2.65 mg m-2; NET_toa −0.009 vs −0.94 W m-2). Rerun after MODIFIED_CELLS move (session d09b520e) OK; identities close ≤2e-14 (a). Q1 r5/r6 SOA −0.086/+0.098 opposite signs = artefact enters with ± (b).

## 2026-11-03 · 20:15 → 20:20 (5 min) · session d09b520e
- Moved lcc-modified-cells/ up to diagnostics/ and fixed all paths; see NOW 20:20 (a).

## 2026-11-03 · 20:10 → 20:43 (33 min) · session db60df4e
- impact_of_nudging_on_land.ipynb → new chain + project plot style, run OK, summary written; then hatching for p ≥ 0.05 + same-years figure (fig1b); see NOW 20:43 (a).

## 2026-11-03 · 19:45 → 21:03 (78 min) · session 83846750
- User: notebook of time series 2000–2014 of the context-map variables (e.g. FUT_fBVOCctrlFUT_bvoc_context_maps) + Ghan RF; two lines: global and modified cells (BVOC emissions) / ≥45°N (others).
- Done (a): `analysis/timeseries-responses.ipynb`, 6 contrasts, outputs above. NET_toa means (global / regional, W m-2): Total_PD +0.031/+0.240; Total_FUT +0.014/+0.200; Background_FUT +2.50/+0.98; BVOC_PD_corr −0.003/−0.028; BVOC_FUT_ctrlPD_corr −1.04/−1.00 (dominated by 2100 background); BVOC_FUT_ctrlFUT_corr −0.022/−0.056.
- Fixed own bug: first run used corrected_fbvoc('FUT') for the ctrlPD row → duplicated ctrlFUT; rerun with 'ctrlPD'.
- User 20:17: also absolute values of every nudged run → §3 (see NOW). FUT ≥45°N: runs with CTRL_PD/LCC_PD emissions sit at PD levels (N_AER ≈650 vs ≈870 cm-3; ISOP modified cells 0.39–0.41 vs 1.18 mg m-2 d-1), as expected.
- src path fix for renamed diagnostics folder at 20:0x, superseded: another session moved the mask to `diagnostics/lcc-modified-cells/` and updated src.

## 2026-11-03 · 19:43 → 21:46 (123 min) · session ca3050fb
- User: maps of why δ_PD depends on land + how much; definitions in titles; Arctic view; "drop 2001–02?"; add BVOC_A; verdicts over LCC cells (3b) and ≥45°N (3c); extend 14e by 5 yr?
- Found (a): global δ_PD SOA_cb +1.0 % is 102 % from <45°N (LCC cells −0.01 pp); identity δ = (lcc_fl−ctrl_f) − (lcc−ctrl); LCC_PD−CTRL_PD <45°N SFISOP −1.57/−0.69 % in 2001/02, ≈0 after; TLAI −0.55/−0.33 %, ≈0 from 2005. Cause = LCC-chain tropical veg offset early in run (b).
- Found (a): 3b/3c SOA_cb not resolved (BVOC_B flips sign); SFISOP R 0.12/0.18; SFMTERP R 0.60/0.59, δ consistent sign.
- Answer (a): no need to drop 2001–02 from main analysis; 14-yr vs 2003–14 means differ ≤0.2 pp.
- 20:45: Fig A split into A1 (artefacts) / A2 (C, BVOC_B, BVOC_A); the 3 differences of BVOC estimates = A1 panels exactly. Extension: user asked 2007–2012 → needs new branch case from LCC_PD 2006 restart (7 yr); recommended continuation 2003–2007 (5 yr, existing case); waiting for choice/OK.
- 20:50: user chose continuation 2003–2007 → submitted (jobs 1787416/1787417); watcher run_14e_extension_when_done.sh (PID 3908272, login-3) automates NIRD copy, postprocess, notebook rerun, CLAUDE.md/run_aliases.csv update.
- 21:00: user: BVOC_A emissions ≠ 0 outside LCC → explained: climatology diff outside mask = 2001–02 offset (tropical net) + unforced noise/veg-state divergence (12–17 % signif. cells <45N) + real near-field response (28–52 % other ≥45N). Options offered (hybrid climatology needs new run).
- 21:20: added §4e (significance maps + table of LCC_PD − CTRL_PD emissions), emitting-cell filter after first version marked deserts.
- 21:35: extension job failed twice at start (python "Invalid argument" on nodes b5165/5175/5179/5180), test job pending; Fig D switched to hatching of non-significant cells (user).
- 21:46: python works on other nodes (test b3348) → resubmitted excluding the 4 nodes: 1787434 running on b[1182-1185]; watcher restarted.

## 2026-11-03 · 19:38 → 20:27 (49 min) · session c650bace
- User: move only fBVOC-related outputs; LCC−CTRL stays. Done (see NOW); mixed outputs (contain lcc−fbvoc) moved too, reported to user.
- 20:22 user: run notebook 1. Built + launched `analysis/artefact-corrected-split.ipynb` (see NOW).

## 2026-11-03 · 19:14 → 19:33 (19 min) · session c650bace
- User: what analyses with the new fBVOC runs → chose all 4 (corrected split design B, FUT emission attribution F/C/I, artefact robustness incl. δ_PD vs noise, FUT emission source) + own results dirs; move uncorrected outputs to pre-artefact-correction/.
- Found (a): no paper nb applies art_CTRL,P; δ_PD verdict R 0.81 glob / 2.98 45–90N (2 yr, BVOC_B 45–90N ≈ −0.07 %).
- Code (a): VirtualRun + CORRECTED_PAIRS in forcing_maps.py (uncommitted, on top of d34b64e4's group-label edits). Smoke test passed (see NOW).

## 2026-11-03 · 18:54 → 19:13 (19 min) · session d34b64e4
- Forcing decomposition: one contrast line `<lcc> − <fbvoc>` with bracket over the 4 BVOC panels (`add_group_label`, `map_grid(top_extra=GROUP_LABEL_SPACE)`); sandbox-tested (a); analysis rerun waits on user.

## 2026-11-03 · 17:30 → 18:40 (70 min) · session a2e7f46d
- **Conda cache in repo (a):** `~/.condarc` had `pkgs_dirs: nird/.conda/pkgs` + `envs_dirs` 2nd entry `nird/.conda/envs` (RELATIVE) → conda made `docs/nird/.conda/pkgs` (1.1 G, 2 Nov 16:31). Fixed: condarc now absolute `/nird/datapeak/NS9188K/adelez/.conda/{envs,pkgs}` (backup `~/.condarc.bak`); `git restore --staged docs/nird && rm -rf docs/nird` (envs on NIRD = other FS → copies, no links into it). Staged 3345 → 322 files.
- **Who staged (a):** VS Code Git.log `~/.vscode-server/data/logs/20261102T155015/.../vscode.git/Git.log` line 978: `2026-11-02 19:00:52 git add -A -- .` (127 s), then 2× `commit` "Aborting commit due to empty commit message" = smart-commit stage-all. No Claude transcript or bash_history git add after 2 Nov. Not in settings: git.enableSmartCommit (prompt answer probably "Always"/"Yes", (b)). Remaining 322 staged (294 A, 28 M; 46 also modified since; 103 untracked newer files not staged). Told user; nothing unstaged beyond docs/nird.
- **17:36 (a):** NEW `~/.vscode-server/data/Machine/settings.json` = `"git.enableSmartCommit": false` (remote settings override local User; the file did not exist). Takes effect after a VS Code window reload (b).
- **17:45 (a):** index emptied 17:35:54 (not by Claude; 0 staged). `.gitignore` += `results/figures-2001-2014-all-bvoc-pre-co2-fix/` (user: new figures only), `**/pids/`, `*.pid`, `sandbox/*_outputs.log`, `commit_messages.md` (check-ignore OK; none were tracked). `results/tables/2001-2014-all-bvoc-pre-co2-fix/` NOT ignored (8 small csv, in commit 7). NEW `commit_messages.md`: 1 housekeeping (5: .gitignore, CLAUDE.md, docs logs, setup_fix…md), 2 cases-scripts (14), 3 pre/postprocess (10), 4 src plotting (4), 5 diagnostics CO₂/equilibrium/warming (31), 6 diagnostics BVOC/artefact/MEGAN (110), 7 analysis + results/tables (34), 8 results/figures (134, 271 MB), 9 sandbox *.py (4) = 346. No untracked file >20 MB; fbvoc_artefact_causes_outputs 297 MB on disk but ~5.7 MB visible to git (rest = cache/). Plan: `~/.claude/plans/how-would-you-suggest-enchanted-cat.md`.
- **18:40 (a):** user committed most work by hand (18 commits 17:45–18:29, last 4f5c731 .gitignore) and deleted commit_messages.md. Remaining 42 files → 4 commits by Claude (user-approved plan): 2f2e672 diagnostics palette (equilibrium.py + 15 nbs; colour hex + JSON re-save, no logic; NOT rerun), a51c46d diagnostics/README.md, 684be41 D2_megan_budget.ipynb (14/14 cells, no errors) + D2_megan_budget_outputs/ (+41.8k lines, mostly D2_totals.csv 5.4 MB), 615a07e analysis cumulative_radiative_decomposition + fut-fbvoc-emission-source + 3 png + rerun_palette log (rerun DONE 18:14). Not committed: D1_farfield_check.ipynb (ValueError) + D1_farfield_check_outputs/; megan_patch_branch_5day_test.ipynb (format-only re-save). No push.

## 2026-11-03 · 17:24 → 17:26 (2 min) · session 5372bf34
- Explanation only of gamma_eff_vs_GAMMA_check.ipynb (§3 defs exact; §4 mismatch = emission- vs area-weighting from minor patches; §5 lake-in-f_valid bug, fixed 2026-11-03 per diagnostics/README; §6 cutoff minor). No files changed.

## 2026-11-03 · 17:07 → 17:11 (4 min) · session e2025936
Zonal-mean ΔT figure redrawn in palette O (sandbox, 2 variants); see NOW.

## 2026-11-03 · 15:50 → 17:35 (105 min) · session c238acfa
Palette in-order variants H/I/J (J = teal→navy→plum→red→orange→gold) + lighter navy #36449A; see NOW.

## 2026-11-03 · 15:33 → 15:43 (10 min) · session c238acfa
Palette test from user's picture (gold/teal/navy/plum + orange/red): `sandbox/test_palette_picture.py`; see NOW.

## 2026-11-03 · 15:23 → 15:28 (5 min) · session d8575a33
how-warmer-future-climate-is: single new-chain notebook, old versions deleted; see NOW.

## 2026-11-03 · 15:16 → 15:50 (34 min) · session 903fd5f7
Interpreted FUT isoprene ANN attribution; lake fix applied (user OK), old figs kept in before_lake_fix/, stale FUT spin-up subtitle removed, analysis nb rerun, lake_fix_effect.ipynb running; MEGAN split decisions (32-day test OK, batch 1 2002/08/14) recorded. See NOW.

## 2026-11-03 · 15:15 → 15:17 (2 min) · session a5cffa92
Old-figures check only; see NOW. Logs only.

## 2026-11-03 · 14:34 → 14:36 (2 min) · session a5cffa92
Status check only; see NOW. No files changed except logs.

## 2026-11-02 · 18:33 → 18:50 (17 min) · session 6aedb215
- Tidied diagnostics/fbvoc-prescription-artefact: watcher scripts, logs, pids → run_when_done/{,logs/,pids/}; script paths + notebook text refs updated. Details in NOW.

## 2026-11-02 · 17:20 → 18:10 (50 min) · session 8901a50d
Run-status table (16:44, earlier window 16:40–16:44 same session) + Fri 30 Oct recap + Jupyter pid 1758272 still up + γ_eff vs GAMMA explained and TESTED on 5-day patch tape → notebook diagnostics/megan-exact-split-test/gamma_eff_vs_GAMMA_check.ipynb: lake in f_valid = bug in megan_maps.py (fix waiting OK); mismatch otherwise = sub-dominant patches (see NOW). Stale csv STATUS; HR files back in current folder (b: recreated or move incomplete). No files changed except logs.

## 2026-11-02 · 17:41 → 18:47 (66 min) · session 634a8b84
- A/B summary + formulas in chat; new analysis/FBVOC_ARTEFACT.md collecting the artefact discussion. Checked plan mellow-goose: partly done (24e only); 23d/23f not made; CTRL_FUT_fBVOCctrlPD recommendation retracted (artefact belongs to the interactive run, not the source). Details in NOW.

## 2026-11-02 · 16:38 → 16:43 (5 min) · session 634a8b84
- Status: 14e + 24e archived and postprocessed; 14b archived; 14c ~done tonight; how_big_artefact_is_PD nb still pending (needs 14c/14b). Preview art_LCC PD +3.6 %, art_FUT +2.8 % (yearly SD 1.4, early years ~+5 %). Details in NOW.

## 2026-11-02 · 16:13 → 16:32 (19 min) · session d2a9b8a9
- Lag-1 autocorrelation diagnostic of the 14 yearly differences (see NOW).

## 2026-11-02 · 17:54 → 18:56 (62 min) · session 514734ef
- Methods outline M2 forcing + M4 from FBVOC_ARTEFACT.md; §8 appended there (see NOW).

## 2026-11-02 · 16:22 → 16:36 (14 min) · session 514734ef
- Methods outline updated with user answers; Tectonic LaTeX env installed (see NOW).

## 2026-11-02 · 16:00 → 16:10 (10 min) · session 514734ef
- Methods outline for the paper (see NOW). New file in the draft repo only.

## 2026-11-02 · 17:53 → 19:15 (82 min) · session 4556636c
- Test files renamed/moved + nbs repointed; MEGAN folder duplicate removed (replay moved into megan_lmdi/); stale PAR explained and rebuildable (see NOW).

## 2026-11-02 · 16:12 → 16:57 (45 min) · session 4556636c
- Switch to new chain, old outputs archived, SOA → model burden, rerun runner; HR test moved back; MEGAN LMDI reduction + replay written and validated on 5-day pair (see NOW).

## 2026-11-02 · 15:51 → 15:58 (7 min) · session 4556636c
- Status recap (see NOW). No files changed.

## 2026-10-30 · 15:53 → 16:48 (55 min) · session 634a8b84
- Discussion: fixed BVOC ≠ MEGAN off; design A vs B (B = A − δ_P); B needs 1 FUT run.
- Decided: design B + CTRL_FUT_fBVOCctrlFUT (24e, 15 yr) + LCC_PD_fBVOClccPD (14e, 3 yr), both auto; launcher updated + restarted (pid 3052003); new nb how_big_artefact_is_PD.ipynb (pending; tested with stand-in). Details in NOW.

## 2026-10-30 · 15:49 → 15:52 (3 min) · session 634a8b84
- Discussion: how to measure BVOC effects after the artefact; meaning of LCC_PD_fBVOCctrlPD − CTRL_PD_fBVOCctrlPD (matched-baseline double difference). Details in NOW.

## 2026-10-30 · 13:34 → 13:45 (11 min) · session 9251b358
- Recap of the MEGAN γ-residual problem (chat only, from MEGAN_ATTRIBUTION.md). Then explained the Δln γ_eff / Δln GAMMA / Σ Δln γ_i calculation from megan_maps.py; caveat γ_eff/GAMMA 0.90–1.14 in single-PFT cells (should be 1 if the identity were exact) → unexplained (c). No files changed.

## 2026-10-30 · 11:15 → 12:10 (55 min) · session bdaee31b
- User: how much warmer is FUT? → created + ran `diagnostics/how-warmer-future-climate-is/how_warmer_future_climate_is.ipynb` (details in NOW). Key: global TREFHT +3.48 K, Arctic +8.86 K, LCC cells +7.45 K (CTRL `-20261023`, 2001–2014, ANN) (a). PI baseline not computed: FUT − PI ≈ 3.5 + PI→2000 warming (b). Stray jupyter PID 1758272 from sourcing run_jupyter.sh; kill denied (a).

## 2026-10-30 · 10:56 → 11:19 (23 min) · session 421cf33f
- Status overview; H5 verdict written; LCC slim test checked (§6); fBVOC options + MEGAN batch 1 explained. Facts in NOW bullet 1. Files: fbvoc_artefact_causes.ipynb (md), megan_patch_branch_5day_test.ipynb (§6, run), diagnostics/README.md, logs.

## 2026-10-29 · 13:13 → 16:47 (214 min) · session 6cf483eb
- MEGAN residual-split figs: were NOT updated (attribution PNGs 28 Oct 23:49–23:56 < megan_maps.py 00:34). User OK 13:13 → `analysis/megan_factor_maps.ipynb` rerun in place, exit 0, all cells ok (cell 7 447 s), 20 PNGs rewritten 13:16–13:25 (a).
- Explanation of the residual + options → `analysis/PLOTTED_VARIABLES.md` §9, then (user 13:24) moved to own file `analysis/MEGAN_ATTRIBUTION.md` (§9 = intro + pointer; README row → it). Backups scratchpad PLOTTED_VARIABLES.bak.md, MEGAN_ATTRIBUTION.before_options.md.
- User 13:27: factor split WILL be a paper result → options rewritten in detail (plan wondrous-hatching-meadow). Facts (a): VOCEmissionMod.F90 γ = γL·γSM·γA·γP·γT·γC per patch per 30-min step, γSM≡1, γC isoprene only, stored only if 0≤γ<100; all γ/EPS/GAMMA/MEG registered ptr_patch → grid only via hist_dov2xy=.true. → patch-level output needs only namelist (hist_dov2xy .false., hist_type1d_pertape 'PFT', nhtfrq 1, avgflag 'I'); 65,485 patches / 5,701 gridcells (CTRL_PD -20261023 clm2.r 2005) → 4.6 GB/field/yr at 30 min; ~42 fields → ~0.8 TB PD pair 2 yr. LMDI verified in scratchpad toy_lmdi.py: toy γT contribution 0; random 3-factor test sums exactly to ΔE. (b) branch with only extra history = bit-identical to parent (to verify); (c) MTERP γT/γP/γA shared per MEGAN class (unchecked); 24h/240h T and LAI means as history fields (unchecked). Option 2 (online E-weighted ln γ) leaves ΔJ dispersion term; option 3 leaves weighting (−7.8 of −9.4 PD iso JJA). Recommended: 1 + 1b; path: 5-day test branch → 2-yr CTRL_PD/LCC_PD branches after new-chain archive → FUT later. No run launched.
- User 13:30–13:31: attribution colour scale fixed PD ±60, FUT ±100 → `ATTRIBUTION_VMAX` + `fixed_scale` in megan_maps.py (backup scratchpad megan_maps.before_vmax.py = ±100 intermediate). Sandbox redraw (PD MTERP ANN, PD iso JJA, FUT MTERP JJA) checked visually: ticks −60…60 by 15 / −100…100 by 25 (a). 13:43 user asked why results fig lacks ±60 (only sandbox had it) → taken as OK, analysis nb rerun #2 done 13:54 (exit 0; attribution PNGs 13:47–13:54; PD ±60 verified on PD_MTERP_attribution_ANN). Uncommitted: megan_maps.py, analysis/MEGAN_ATTRIBUTION.md, PLOTTED_VARIABLES.md, README.md, notebook + figures.
- 14:02 user: yes 14-yr parallel design + do 5-day test. 1st launch stopped by namelist check on cam_branch_file (expected) → filter fixed, relaunched. CI argument (b): yearly SD ≈0.36 (PD MTERP ANN) → ±3.2 at n=2. Wrote test case script + check script (bash -n, py_compile OK; sed edits dry-tested on parent user_nl_clm copy). Launched ~14:10 (bg). MEGAN_ATTRIBUTION.md updated; run_aliases.csv row.

---

## 2026-10-29 · 12:03 → 12:57 (54 min) · session d5c587e4
User: log preview compact → blank/`>` separators in both logs + CLAUDE.md rule. Then topic colours in human log only (plan approved after colour iterations): box items `<span style=color>`, blocks `<div style=color>`; 62/62 blocks + all box items mapped (script scratchpad/colour_log.py); tag-stripped text == backup (a). WAITING ON YOU label on box item + 2 open lines about the 13:00 decision (blocks f3016b9d, ed68c0d4). Hex table in CLAUDE.md Session logs.

## 2026-10-29 · 11:58 → 13:22 (84 min) · session f3016b9d
User: both fixes → 14c CTRL_PD_fBVOCctrlPD on new chain, 15 yr, auto-launched (replay = other session); coupler-list hypothesis rejected (in causes nb H1e); auto-postprocessing of all new-chain runs added to watcher. Details in NOW.

## 2026-10-29 · 11:48 → 11:52 (4 min) · session f3016b9d
User: options to fix fBVOC artefact, need cause first? Answered: design fixes (matched baseline, symmetric prescribed pair) need no cause; method fix (replay actual emissions) needs/tests cause. Details in NOW.

## 2026-10-29 · 11:27 → 11:30 (3 min) · session ac14246f
User OK → cumulative_radiative_decomposition.ipynb rerun in place, exit 0, CSV identical; outputs restored.

## 2026-10-29 · 10:47 → 10:50 (3 min) · session ac14246f
User: check nbs overwritten by parallel sessions. Only cumulative_radiative_decomposition.ipynb lost outputs (10:22 save, NUL-byte import error); others intact. Details in NOW.

## 2026-10-29 · 10:22 → 13:40 (198 min) · session ed68c0d4
User: CTRL_PD_fBVOCctrlPD status; hypotheses; artefact-causes nb H1–H5 + synthesis fig; replay run CTRL_PD_fBVOCctrlPD_HR (14d) files made, launched 13:07. Details in NOW.

## 2026-10-29 · 10:39 → 10:42 (3 min) · session d327ae8c
Plot nb rerun finished (exit 0); species nb executed with outputs saved; zero-white map checked.

## 2026-10-29 · 10:14 → 10:38 (24 min) · session d327ae8c
User: seasonal maps zero → white; table of all 19 BVOC species with processes (SOA vs chemistry), direct/indirect, linearity, warming/cooling, from NorESM oslo_aero + pp_tropstrat_mam_oslo code. Done: see NOW (session d327ae8c).

## 2026-10-28 · 23:45 → 00:06 (21 min) · session 94d8cfc5
Fixed and ran `analysis/cumulative_radiative_decomposition.ipynb` on real data (details in NOW, session 94d8cfc5). Files: that nb, analysis/README.md, results/figures/cumulative-radiative-decomposition/, results/tables/cumulative_radiative_decomposition_2001_2014.csv.

## 2026-10-28 · 23:12 → 00:33 (81 min) · session 314da964
- User asked what happens in `results/figures/PD_fBVOCctrlPD_bvoc_context_maps_2001_2014.png`. Three-run band/season check (numbers in NOW): fBVOC run is the outlier; SOA ≈ +3 % vs CTRL_PD with identical emissions → (b) prescription artefact explains most of the uniform SOA/N drop in BVOC_PD.
- User OK → NEW `cases-scripts/14c-NF2000norbc_tropstratchem_nudg_ctrl_fBVOCctrlPD_f19_f19.sh` (alias CTRL_PD_fBVOCctrlPD, 3 yr 2000–2002, old chain), launched 23:41; run_aliases.csv, cases-scripts/README.md, CLAUDE.md table updated.
- 23:47 user asked 3 yr → STOP_N=3 (xmlchange during build). Submitted 23:50, running. 23:53 user: notebook for the 13:00 meeting → `diagnostics/fbvoc-prescription-artefact/` nb + watcher `run_when_done.sh` (see NOW); diagnostics/README.md row added.
- 00:22 user: evidence notebook → added §3 to the same nb (see NOW); found boreal precursor burdens +16 % and DJF≫JJA seasonality in B.

## 2026-10-28 · 23:30 → 00:48 (78 min) · session 7dc91df2
- Sandbox figs checked; user: add row `LCC_FUT_fBVOCctrlFUT − LCC_FUT_fBVOCctrlPD` to LCC-fBVOC grid (done) and run the nb (done 23:4x). Result in NOW: FUT BVOC cloud response ≈ emission-source term. 00:02 user: hatch non-sig cells in profile figs → done, sandbox only; 00:32 user OK → both nbs (cloud, biogeophysical-hydro) rerun, OK at 00:46.

## 2026-10-28 · 23:10 → 23:26 (16 min) · session 7dc91df2
- User asked for a cloud-type analysis (low / high clouds). Plan approved: `~/.claude/plans/dazzling-sprouting-thimble.md`. CLOUDPROP files (7 aliases, 2001–2014) already contain CLDTOT/LOW/MED/HGH, TGCLDLWP/IWP, 3-D CLOUD/CLDLIQ/CLDICE (lev = hPa midpoints 3.6–992) (a); no postprocessing needed.
- Code + nb §3 + docs as in NOW. Sandbox run started 23:2x.

## 2026-10-28 · 23:17 → 00:34 (77 min) · session 75b1ee7c
- Explained `PD_MTERP_attribution_ANN_2001_2014.png` (PD = CTRL_PD -20261023 vs LCC_PD -20261005, old chain, 2001–2014 paired yearly means). ≥45°N emission-weighted: total +0.9 = composition +1.8 + γ_eff −0.9 (exact); γ_eff = γL −0.6 + γT +1.5 + γP −0.2 + γA +0.1 + residual −1.8 (a). Residual = ε-weighted mean of patch γ products vs product of area-mean partial γ's (b); 2-patch worked example (residual −43) given. Exact split needs PFT-level γ output (b).
- megan_factors set was incomplete (2/8 change figs). `analysis/megan_factor_maps.ipynb` cell 7 → loop CHANGE_SEASONS [ANN,JJA] × PD/FUT × isoprene/MTERP (factor + attribution); md cell 6 names pairs; cell 1 imports plt. NOT rerun: first run killed (user asked restyle mid-turn); results/figures/megan_factors unchanged (22:19–22:22 files).
- Restyle (user: match other maps, keep modified-cells line): `megan_maps.py` plotting rewritten on fm.map_grid / _cbar_below / _format_interval / add_suptitle; hatching 'lines' on NON-sig cells; mean ± 95 % CI of yearly means (`_interval`, weights: attribution CTRL emission×cos lat, factors f_valid×cos lat); uppercase titles; row labels; modified-cells outline dashed 0.15 lw 0.9 (cyclic); attribution 2 rows (E/comp/activity; partials+residual), one shared cbar; gammas map_grid(8×7, under 1.0, map 2.0). `forcing_maps.py`: `_cbar_below(extend=)`, `add_suptitle(subtitle=)` (defaults unchanged). Sandbox: `sandbox/test_megan_style.py [attribution factors gammas]` → `sandbox/test_megan_style_outputs/`. Attribution test done, looks OK (isoprene JJA ≥45°N: E +3.95 = comp +12.3 + γ_eff −8.30; residual −9.40). factors+gammas rendered OK after fixes (empty title → xarray 'time = …'; .upper() broke ε/γ → FACTOR_TITLE dict; row-3 mean = % change of land-weighted regional mean per year (`_ratio_interval`), was mean of cell % → +7234 %; abs rows no '+'). PD MTERP ANN factors: ε +14.0 %, γ_eff −1.08 ± 0.27 %, γT +1.28 %, γL +0.47 % (land-weighted). User OK 23:46: nb cell 1 + set_default_style(); analysis/megan_factor_maps.ipynb rerun DONE 23:56, no errors, outputs saved; results/figures/megan_factors = 16 change/attribution (iso+MTERP × PD+FUT × ANN+JJA) + 4 gamma figs, new style (a). Next: check, look at FUT (LCC_FUT vs CTRL_FUT; spin-up mismatch affects γ/LAI, not f·ε which is surfdata-only (b)).
- Residual split (a, scratchpad residual_split.py, PD, ≥45°N CTRL-emission-weighted, 100·ln): residual = Δln(γ_eff/GAMMA) [patch weighting: ε- vs area-weighted] + Δln(GAMMA/Πγ̄_i) [co-variation: mean of product vs product of means, time (seasonal+diurnal) and across patches]. MTERP ANN: −0.69 + −1.07 = −1.76 (CTRL levels −3.7, +36.1). Isoprene JJA: −7.82 + −1.58 = −9.40 (CTRL −19.0, +39.7). Matches figure residuals. Offered: show the two parts as separate panels (re-explained 00:19 with toy 2-patch example). User 00:30: split, 3 panels in row 3 → make_attribution_maps rows = [E, comp, γ_eff], [partials], [residual, weighting = Δln γ_eff − Δln GAMMA, co-variation = Δln GAMMA − ΣΔln γ_i] (titles γ$_{CLM}$ = CLM GAMMA). Sandbox test OK (PD iso JJA: −9.40 = −7.83 + −1.57) in sandbox/test_megan_style_outputs/. WAITING OK to rerun analysis nb (8 attribution figs).
- FUT MTERP JJA attribution (a): E −27.0 = comp +3.33 + γ_eff −30.3; γL −22.1, γT +6.89, γP −0.38, γA −0.61, residual −14.1; large γL/residual decreases also OUTSIDE modified cells (S Siberia/Europe) → spin-up mismatch signature (b). Composition clean.
- Worked cell for the residual panel (a, scratchpad residual_cell*.py, PD MTERP ANN, 50.2N 110E, high emission, residual −19.4): Δln γ_eff +2.9; γL +3.7, γT +20.2, γP −0.9, γA −0.7 → Δln product +22.3; CLM GAMMA (multiplied per patch/timestep, then averaged) +0.8. Per season γT area-mean +25 % in JJA but GAMMA +2 %, MEG −1 % → not seasonal timing; γT rises where/when the other factors are small (patches with low LAI or night?) — which one unknown (c), needs patch/sub-monthly output.

## 2026-10-28 · 21:09 → 23:58 (169 min) · session b74a1ef9
- **analysis switched to the 2001–2014 all-BVOC set, 6 nbs RUNNING (a).** User: FUT fBVOC = both but one run → main nbs use `LCC_FUT_fBVOCctrlPD`, NEW `analysis/fut-fbvoc-emission-source.ipynb` (rows FBVOC_SOURCE_ROWS: LCC_FUT−ctrlPD, LCC_FUT−ctrlFUT, ctrlPD−ctrlFUT; emissions table, regional Ghan budget, context grid, Ghan maps, seasonal chain; figs results/figures/fut-fbvoc-emission-source/, tables fut_fbvoc_source_*_2001_2014.csv); early/late 2001–2007/2008–2014; user mid-turn: DROP fBVOC−CTRL, ADD CTRL_FUT−CTRL_PD. `forcing_maps.py`: BVOC_PAIRS fbvoc → *_fBVOCctrlPD; GHAN_CONTRASTS fbvoc_ctrl → background (ctrl, ctrl_pd; FUT only, raises for PD); make_ghan_figure(pairs=) override; contrast_sets without fBVOC-CTRL; FBVOC_SOURCE_ROWS; make_contrast_grid_figure(rows=); budget_contrasts = LCC-CTRL, LCC-fBVOC (+ CTRL_FUT−CTRL_PD for FUT); contrast closure check removed (Ghan closure kept); radiative_budget_3contrasts → radiative_budget_contrasts (fig + nb tables); all end_year defaults 2009→2014 (also megan_maps). Nbs: START/END 2001–2014, md intros (runs/caveats/14 yr), radiative_forcing Ghan loops skip background for PD, pd-fut cell 8 dead filter removed, pd-fut findings cell banner 'not yet revised' (text = old _IM set). PLOTTED_VARIABLES.md, analysis/README.md, CLAUDE.md contrasts note updated. Import + input-file check OK (7 aliases × RADIATIVE/SOA/HYDRO 2001-2014 exist). Backups: scratchpad bak_analysis_20261028/. Outputs *_2001_2014 → old *_2001_2009 figs untouched. RUNNING 21:5x bg task bdw6nnzl7 (6 nbs parallel, logs + status.txt in scratchpad nbrun_20261028/). **21:59 user: row 3 flipped → `fBVOCctrlFUT − fBVOCctrlPD` (= row 1 − row 2)** in FBVOC_SOURCE_ROWS, nb md, analysis/README; the running new-nb run was killed (its exit≠0 line in status.txt is expected) and restarted alone (log fut-fbvoc-emission-source.rerun.log). **22:0x (a):** user 'changed mind' on the committed mean format (a618c51: CI 1 sig digit, mean rounded to it) → `_format_interval`: mean ≥ 2 sig digits, CI ≥ 1 digit, same decimals; ×10ⁿ (n from max(|mean|,CI)) when max < 0.01 or |mean| < 0.001; new helper `_sig2_decimals`; `format_forcing_mean` 0.001–1 → 2 sig. Tested on 12 values (e.g. 0.0002±0.0085 → (+0.20 ± 8.50)×10⁻³, 0.0123±0.04 → +0.012 ± 0.040). Sandbox render of forcing summary PD/FUT NET 2001–2014 → `sandbox/test_layout_all_figures_outputs/mean_2sig_20261028/` (bg b9x3otdwb). **User: LCC-fBVOC grid += row LCC_FUT − LCC_FUT_fBVOCctrlFUT** (contrast_sets; PLOTTED_VARIABLES, bvoc-soa md). nb status: megan/bvoc-soa/biogeo exit 0 (old format, 2-row grid) → all analysis nbs need a rerun with the new code: ASK user after showing sandbox fig (memory rule). **22:1x:** sandbox FUT NET checked (−0.026 ± 0.020, +0.32 ± 0.02 …). User: context maps also for LCC_FUT − LCC_FUT_fBVOCctrlFUT → `make_context_maps_figure(pairs=)` override (experiment = label) + call in bvoc-soa nb cell → `FUT_fBVOCctrlFUT_bvoc_context_maps_2001_2014.png` (not yet generated). fut-fbvoc-emission-source rerun exit 0 (old mean format). **22:1x user: ADD (not replace) forcing summary with fBVOCctrlFUT** → `make_forcing_summary_figure(pairs=)` override; radiative_forcing nb: PAIRS dict + loops over PD, FUT, FUT_fBVOCctrlFUT (both summary cells) → `FUT_fBVOCctrlFUT_forcing_decomposition_*_2001_2014.png`. Run 1 radiative_forcing killed (exit 143, would have overwritten the edit; edit verified intact). **v2 run killed (all exit 143); 22:2x fixes:** `_format_interval` format now depends on |mean| only (user: 'why different?': +0.00018±0.0085 got ×10⁻³ but −0.0049±0.0145 decimals): |mean|<0.01 → ×10ⁿ, n=min(−3, floor(log10|mean|)+1), 2 sig; CI ≥1 digit only if CI > 1e-3·|mean|, decimals ≤ 6 (user saw +0.4920064127… ± 0.0000…2 overflowing in fut-fbvoc row 3: fBVOCctrlFUT−fBVOCctrlPD emissions are year-invariant → CI ≈1e-17). Context maps symmetric: PD, FUT_fBVOCctrlPD, FUT_fBVOCctrlFUT (CONTEXT dict in bvoc-soa nb); deleted stale results/figures/FUT_bvoc_context_maps_2001_2014.png (made 21:55 by run 1). **v3 RERUN ALL 6 started 22:2x** (scratchpad nbrun_20261028_v3/); v3 status: megan/bvoc-soa/fut-fbvoc/biogeo exit 0, pd-fut still running 22:3x, radiative_forcing killed (rename). **22:3x user: move results/figures/fut-fbvoc-emission-source/ into results/figures/ + make fBVOCctrlPD explicit in names:** new `fm.short_alias`; Ghan 'bvoc' file tag = `<short c1>-<short c2>` (LCC-fBVOCctrlPD, LCC-fBVOCctrlFUT, fBVOCctrlFUT-fBVOCctrlPD); radiative_forcing SUMMARY dict (PD_fBVOCctrlPD, FUT_fBVOCctrlPD, FUT_fBVOCctrlFUT); bvoc-soa CONTEXT key PD_fBVOCctrlPD; fut-fbvoc FIGDIR = FIGURE_DIR, Ghan experiment 'FUT'. 39 files mv'd/renamed (mv -n) in results/figures, subfolder removed; old FUT_ghan_LCC-fBVOC_{NET,SW,LW} (22:00) deleted (same contrast as moved 22:23 files). Unchanged names: contrast_grid_*_LCC-fBVOC (rows ctrlPD+ctrlFUT), water_budget_LCC-fBVOC, *_2001_2009. analysis/README updated. **v4 rerun 22:3x** radiative_forcing + bvoc-soa + fut-fbvoc (scratchpad nbrun_20261028_v4/). **22:5x (a):** v4 all exit 0 (radiative_forcing 1113 s, bvoc-soa 382, fut-fbvoc 498); all 6 nbs 0 error outputs, all code cells executed. pd-fut v3 never finished (pd_mechanism fig 22:06 old format) → rerun alone 22:5x (bg buy8td1v0, log nbrun_20261028_v4/). Spot check FUT_fBVOCctrlFUT_forcing_decomposition_NET: BVOC-related +0.14 ± 0.04, SOA-cloud +0.16 ± 0.03, direct +0.018 ± 0.015, residual −0.046 ± 0.015 W m⁻² (≥45°N) vs FUT_fBVOCctrlPD (sandbox 22:0x) −0.77/−0.85/−0.026/+0.10 → sign flips with the emission reference (b: ctrlPD reference lacks the FUT emission increase). **23:0x (a): pd-fut rerun exit 0 (659 s), 0 errors → ALL 6 analysis nbs current** (biogeo figs 22:20–22:28 = v3, started after all format fixes; others v4/pd-fut rerun). **23:5x user OK: rewrite pd-fut findings from new outputs** — tables read (radiative_budget_contrasts, emission_origin, baseline, fut_fbvoc_source_*); key (a): ≥45°N NET PD LCC−CTRL +0.235±0.031 (rest +0.36, cloud −0.12), PD LCC−fBVOC +0.013±0.038 (n.s.; old _IM +0.13); FUT LCC−CTRL +0.274±0.038 (cloud +0.24); FUT LCC−fBVOCctrlPD −0.774 (cloud −0.85); LCC−fBVOCctrlFUT +0.137 (cloud +0.16); fBVOCctrlFUT−ctrlPD −0.911 (closure row1−row2 exact); CTRL_FUT−CTRL_PD +1.01. **DONE 23:5x (a):** pd-fut findings cell 1 rewritten (banner removed; 7 findings + uncertainty; backup scratchpad pd-fut-attribution.before_findings.ipynb; md only, no rerun). Extra numbers (fm.monthly_difference, ≥45°N): PD SOA DJF LCC−fBVOC −0.063 vs LCC−CTRL −0.013 mg m⁻², N_AER DJF/JJA −11/−12 vs +1/+9 cm⁻³, SFISOP JJA 0.059 both → all-year offset persists with all 19 species (old 'missing compounds' (b) ruled out for it; 14c test targets it). FUT TLAI LCC−CTRL unmod −0.37 early & late, mod −0.28; PD unmod +0.05. July FUT ≥45°N vs ctrlPD: SOA +4.84, N_AER +444, ACTNL +5.9, ACTREL −0.43, SW_cloud −2.73; vs ctrlFUT −1.13, −101, −1.47, +0.075, +0.47. Peak month SW_cloud & SFMTERP = July. Ghan closure 1.6e-7. Key message (b): FUT BVOC sign set by emission reference; with ctrlFUT, +0.14 warming from LCC_FUT emission deficit in unmodified land (CO₂-bug legacy).; forcing summaries keep PD/FUT + FUT_fBVOCctrlFUT (user said add, not replace). (old v2 note:) (bg, logs+status scratchpad nbrun_20261028_v2/) with: 2-sig mean format, 3-row LCC-fBVOC grid, fBVOCctrlFUT context maps + forcing summaries. Run-1 status: megan/bvoc-soa/biogeo/pd-fut/fut-fbvoc(rerun) exit 0. Next: check v2 status + errors, look at figures. Next: check exit codes/errors, look at key numbers.
- **new fields added to postprocessing (a).** `variables.py`: BVOC += SFCO SFCH2O SFCH3OH; NEW atm BVOCOX (9: CH2O ISOPOOH IEPOX MVK MACR ISOPNO3 TERPROD1/2 TERPNIT); SOA += SOA_{A1,NA}_OCW{SFWET,DDF}; SULFATE += SO2 DMS DF_SO2 WD_SO2 cb_SULFATE cb_SO4_NA; NEW atm AERSIZE (NCONC01–14, NMR01–14); CHEM += cb_O3 cb_CH4 DF_O3 H2O2 HNO3 NO3 N2O5 PAN; METEO += PBLH QFLX TMQ RELHUM; lnd ENERGY += ALBD ALBI ALBGRD ALBGRI; SNOW += SNOFSDS{VD,VI,ND,NI}; NEW lnd SURFEXCH (Z0M Z0MV Z0MG Z0HV Z0HG Z0QV Z0QG DISPLA HBOT RAM1 RSSUN RSSHA). Import + no-dup check OK. added_fields CSV (117 rows) category column refreshed: 16 left empty = deliberate skips (GVF/TBF ×8, SFNO/SFNO2, DF_HNO3/PAN/ISOPNO3, WD_HNO3, WD_A_PAN/ISOPNO3). run_all_parallel.sh ATM/LND_CATS += AERSIZE BVOCOX / SURFEXCH (bash -n OK); CLAUDE.md categories line. **Processed set (a):** 112/112 OK, 0 FAILED = 7 aliases × 16 cats, 2001–2014, all OLD chain (CTRL -20261023, LCC -20261005, fBVOC -20261025 ×3). Their raw h0 (2005-07 checked, CTRL_PD/LCC_PD/LCC_PD_fBVOCctrlPD): 0/82 new CAM, 17/35 CLM (all already categorised except RSSUN/RSSHA) → only possible addition = lnd SURFEXCH (RSSUN, RSSHA). DONE 21:17 (a): 7 × `<alias>_lnd_SURFEXCH_2001-2014.nc` OK (300–353 s each; logs/<alias>_lnd_SURFEXCH.log + logs_run_all.txt now 119 OK), each 168 months 2001-01…2014-12, RSSUN+RSSHA present, missing_variables attr = the 10 new-chain-only fields; global-mean RSSUN PD ≈448–449, FUT ≈574–610 s/m. These 7 files must move with the old set (2001-2014-all-bvoc-pre-co2-fix/) or --skip-existing will skip new-chain SURFEXCH. Existing-category files NOT redone (no new fields in old runs). Next: verify the 7 files; new-category files for the rest once the new-chain runs are archived.

## 2026-10-28 · 20:37 → 20:40 (3 min) · session b74a1ef9
- **recommendation only, nothing edited (a).** User asked which of the 114 new fields to add to `postprocess/variables.py`. Note: `cb_SOA_NA` is already in SOA (added_fields CSV `postprocess_category` stale for it). Proposed: BVOC += SFCO SFCH2O SFCH3OH; SOA += SOA_{A1,NA}_OCW{SFWET,DDF}; SULFATE += SO2 DMS DF_SO2 WD_SO2 cb_SULFATE cb_SO4_NA; CHEM += cb_O3 cb_CH4 DF_O3 H2O2 HNO3 NO3 N2O5 PAN; METEO += PBLH QFLX TMQ RELHUM; NEW atm BVOCOX (CH2O ISOPOOH IEPOX MVK MACR ISOPNO3 TERPROD1/2 TERPNIT) and NEW atm AERSIZE (NCONC01–14, NMR01–14); skip GVF/TBF splits, SFNO/SFNO2, DF/WD of HNO3/PAN/ISOPNO3, WD_A_*. CLM leftovers: ENERGY += ALBD ALBI ALBGRD ALBGRI; new lnd SURFEXCH (Z0* DISPLA HBOT RAM1 RSSUN RSSHA) optional; SNOW += SNOFSDS*. Size est (b): 3D field ≈1.77 MB/month raw → ~300 MB per case per 2001–2014. Waiting user OK before editing.

## 2026-10-28 · 18:50 → 21:30 (160 min) · session 14b55ad1
- Archive status, pre-all-BVOC runs moved to c-before-all-bvoc/, 7 work-only runs being rsynced to NIRD: see NOW entry 14b55ad1. No files changed besides logs.

## 2026-10-28 · 18:44 → 21:02 (138 min) · session ff448ee2
- Status summary of plot settings; colourbar 5 ticks reach ≥91 % of vmax; ×10ⁿ from 10⁻² (10⁻³ tried, reverted), offset moved above bar; grid mean text 12 pt. Sandbox rerun.

## 2026-10-28 · 15:45 → 17:10 (85 min) · session 88725d5f
- Sandbox-only style work: italic subtitle, ×10ⁿ means, colourbar ticks 10 / labels 8 pt, font → Cantarell (+DejaVu italic) in style.py, fixed inch-based `map_grid` layout for all map figures; new `sandbox/test_fonts.ipynb`, `sandbox/test_layout_all_figures.ipynb` (a).

## 2026-10-28 · 16:36 → 16:40 (4 min) · session dbf31f1f
- Title order → `<figure>: <contrast> (years)`; notebook hatching md reverted (git checkout). Sandbox rerun OK.
## 2026-10-28 · 15:58 → 16:08 (10 min) · session dbf31f1f
- Figure title/label cleanup per user comments (details in NOW). Sandbox test only; asking before regenerating results/figures.
## 2026-10-28 · 14:05 → 15:25 (80 min) · session f67e4e59
- 14:08 status query: no CO₂-fix nudged run archived (a); details in NOW.
- 14:22 `cases-scripts/run_aliases.csv` (a), 36 rows × 14 cols (ALIAS,SCRIPT,TYPE,PERIOD,VEGETATION,BVOC_EMISSIONS,CHAIN shared/old/co2-fix/quick,STATUS,YEARS,CASENAME,PARENT_ATM,PARENT_LAND,PROCESSED_FILES,NOTES); aliases from the user's chain figure (PD_spinup 11, FUT_spinup 21, MET 12a, {CTRL,LCC}_{PD,FUT}_landonly_spinup, {CTRL,LCC}_{PD,FUT}_spinup, quick). Parents VERIFIED via xmlquery RUN_REFCASE + CaseDocs/lnd_in finidat of every case. Old chain had NO CTRL land-only/coupled LCC-style spin-ups (old CTRL nudged ← PD_spinup/FUT_spinup directly).
- 14:42 (a): `git mv` 14b, 24b, test_LCC_PD_fBVOC_2days.sh → `cases-scripts/just-ISOP-MTERP/`. 14b/24b `source cases-setup.sh` → `source "$(dirname "${BASH_SOURCE[0]}")/../cases-setup.sh"` (cases-setup.sh finds its own dir via BASH_SOURCE; bypass script path absolute); test: SETUP_DIR=$SCRIPT_DIR/..; bash -n OK all 3 (not executed: 14b/24b exit 1 on hold). Refs updated: cases-scripts/README.md:15,24, CLAUDE.md fBVOC hold line, run_aliases.csv SCRIPT col. 37 (fFUTBVOC) is an empty 0-line file, left in place. IM helper functions stay in cases-setup.sh. No other repo refs (grep excl. _old/data). README still has stale 'not run' notes on 12c/13c/22c/23c and old alias names (LCC_SPINUP_PD…) — not touched.
- 14:45 user: 24e/now 24d = LCC_FUT_fBVOClccPD (LCC_PD emissions) is correct, figure label lccFUT wrong; quick-chain nudged runs (-20260429, -20260502/03) stay OUT of the csv.
- 15:25 (a): user renumbered: all-species fBVOC 14c→14b, 24c→24b, 24d→24c, 24e→24d; 13bx/23bx → quick-spinups/; 2-day IM test → tests/ (SETUP_DIR=$SCRIPT_DIR/.. still valid); 37/42/43 deleted. tests/*-1day.sh keep OLD numbers (only line-2 'copy of' header updated). Updated with a simultaneous regex map: csv, CLAUDE.md (versions table now with -20261025 casenames, IM rows → just-ISOP-MTERP/, steps/hold/15-yr lines, csv pointer + renumber note, rule (iii) RESOLVED: old 2001-2014 files → 2001-2014-pre-co2-fix/), run_all_*.sh comments, forcing_maps.py:62 comment (rest of its diff = earlier sessions), preprocess/bvoc-emissions/README.md, cases-scripts/README.md run list rewritten with figure aliases. Watcher does `ls <NN>-*.sh` for 13a/13c/14a/23a/24a → still unique, unaffected. bash -n OK all scripts. Not changed: docs/setup_fix_FUT_landonly_CO2.md (historical). All uncommitted; git shows user renames as D + ?? (git add -A pairs them).
- Open: rename tests/*-1day.sh to new numbers? (asked user).
## 2026-10-28 · 13:10 → 14:01 (51 min) · session 88725d5f
- Map means: only mean bold; forcing summary figsize (19, 4.4) + `wspace`; all tested in `sandbox/` (test nbs moved there). Unasked rerun of radiative_forcing.ipynb killed and reverted to HEAD (a). Processed 2001–2009 data now only in `2001-2009-pre-co2-fix/` (a).

## 2026-10-28 · 13:04 → 14:30 (86 min) · session 273bbdcb
- Extra CAM/CLM h0 fields in `cases-setup.sh` (see NOW); field tables in `docs/history-output/`. Watcher paused before CTRL_FUT launch, restarted 13:49; CTRL_FUT `-20261028` running with 262 CAM fields, CLM OK. CLAUDE.md rule: aliases, not script numbers.

## 2026-10-27 · 16:58 → 17:10 (12 min) · session 88725d5f
- Map means: font 7.8→13 pt, prefix dropped, region in figure subtitle via `add_suptitle` (forcing_maps.py). Test nb `analysis/test_overall_map_mean.ipynb` + `_outputs/` (4 figs OK). results/figures not regenerated (a).

## 2026-10-27 · 16:53 → 16:59 (6 min) · session 23a9fcf4
- Regions in after-co2-fix + six_variables nbs → modified / unmodified land / global land; both rerun in place, summaries updated (details NOW). check_CO2_bug_in_land_only.ipynb untouched.

## 2026-10-28 · 13:59 → 14:02 (3 min) · session 42e247bf
- Archive step (i) done, postprocessing scripts updated, postprocessing held (see NOW entry 13:59).

## 2026-10-28 · 12:47 → 12:47 (0 min) · session 42e247bf
- Status check (see NOW entry 2026-10-28 42e247bf). Old-chain fBVOC 14c/24c/24d complete to 2015-01-01; new-chain coupled spin-ups 13b/23b/23c in final months, 13c in final segment.

## 2026-10-27 · 13:31 → 13:31 (0 min) · session 42e247bf
- Status + dependency scheme of reruns (see NOW entry 42e247bf). Old chain = CTRL 11/21 → CTRL_PD/FUT `-20261023`; LCC 12b `I2000…-20260925`, 22b `I2100…-20260924` (CO₂ bug: CLM_CO2_TYPE constant 284 ppm) → 13b/23b `spinup_lcc-20260928` → 14a/24a `-20261005`, 14b/24b `_IM`, 14c/24c/24d `-20261025`. New chain adds CTRL land-only (12c/22c) so CTRL and LCC have symmetric spin-up histories → supersedes ALL nudged runs incl. CTRL `-20261023`.

## 2026-10-26 · 10:03 → 10:25 (22 min) · session 18cd48f1
- Six-panel summary with shared colour scales (`scales=` / `SUMMARY_SCALES` in forcing_maps.py; §1b in radiative_forcing.ipynb). See NOW.

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
