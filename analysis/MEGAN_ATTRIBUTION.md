# MEGAN attribution: what the residual is and how to remove it

Notebook: `megan_factor_maps.ipynb`. Code: `src/boreal_forest_expansion/plotting/megan_maps.py` (`make_factor_maps`, `make_attribution_maps`). Figures: `results/figures/megan_factors/`. It plots raw CLM `EPS_*` and `GAMMA*` for isoprene and 7 monoterpenes, as annual and JJA means per run. Grid-cell `GAMMA_*` is an area mean over vegetated patches, not emission-weighted.

## Attribution figure (`{PD,FUT}_{isoprene,MTERP}_attribution_{ANN,JJA}_2001_2014.png`)

All terms are 100·Δln(LCC/CTRL) (≈ % change for small changes), so they add up.

| Row | Panels | Exact? |
|---|---|---|
| 1 | Emission E = composition (ε) + γ_eff (effective activity, E/ε) | exact |
| 2 | Partial factors γL, γT, γP, γA (+ γC for isoprene), from the saved grid-cell maps | indicative only |
| 3 | Residual = γ_eff − (γL + γT + γP + γA) = **weighting** + **co-variation** | exact split |

Under the maps: mean north of 45°N weighted by CTRL emission × area, ± 95 % CI of the yearly means. With these weights the row sums hold for the means too.

Colour scale: fixed, ±60 for PD and ±100 for FUT (`ATTRIBUTION_VMAX` in `megan_maps.py`), the same for all panels of a figure so they can be added by eye.

## Where the residual comes from

**What CLM does.** In every patch (one plant type in a grid cell), every half hour, CLM computes

emission = ε × γL × γT × γP × γA

It multiplies first. It then writes monthly grid-cell averages to the history file: the emission E, and each γ separately, averaged over all patches and all half-hours of the month.

**What we do with the output.** To attribute, we take the saved averages of γL, γT, γP, γA and multiply them: we average first, then multiply. Average-then-multiply ≠ multiply-then-average. The residual is the change in that difference between LCC and CTRL.

**Toy cell:** two patches of equal size, same ε. Patch 1 = forest, with leaves (γL = 1). Patch 2 = sparse ground, no leaves (γL = 0), so it never emits, whatever its temperature.

CTRL:

| | γL | γT | γL × γT |
|---|---|---|---|
| Forest | 1 | 0.2 | 0.2 |
| Sparse | 0 | 0.2 | 0 |
| Average | 0.5 | 0.2 | 0.10 = true activity |

Average-then-multiply: 0.5 × 0.2 = 0.10. Same answer, no gap yet.

LCC: only the sparse patch gets warmer (γT 0.2 → 0.4); the forest is unchanged.

| | γL | γT | γL × γT |
|---|---|---|---|
| Forest | 1 | 0.2 | 0.2 |
| Sparse | 0 | 0.4 | 0 |
| Average | 0.5 | 0.3 | 0.10 = true activity |

| | Change, LCC vs CTRL |
|---|---|
| True activity (from the emission) | 0.10 → 0.10: 0 % |
| γL map | 0.5 → 0.5: 0 % |
| γT map | 0.2 → 0.3: +50 % |
| Product of the maps | 0.10 → 0.15: +50 % |
| **Residual** = true − maps | in 100·Δln: 0 − 41 = **−41** |

The γT map says "it got warmer, so emissions should rise". But the warming happened where there are no leaves, so emission did not change. The residual is the correction that says "that γT increase doesn't count". The same happens in time instead of space: γT rising at night, or in hours with little light, counts in the γT map but barely in the emission.

**A real cell behaves like the toy.** 50.2°N 110°E, PD monoterpenes, annual (old chain): the γT map is +20 %, but the true activity changed only +3 %, so the residual is −19. CLM's own multiply-first product (`GAMMA`) changed only +0.8 %, so γT rose where or when the other factors are small, like the sparse patch. Whether that means low-LAI patches or night-time cannot be told from monthly grid-cell output.

**A second source: patches weighted by area, not by emission.** In the toy both patches had the same ε. In reality trees can emit 10× more per unit γ than grass. The true activity weights each patch by how much it emits; the saved γ maps weight each patch by its area. So if the γ's change in the patches that emit a lot, the area-averaged maps under- or over-state it.

## The two residual panels

CLM also saves `GAMMA` = the γ's multiplied per patch and per half-hour, then averaged by area. This separates the two sources:

| Panel | Gap | Measures |
|---|---|---|
| **weighting** | Δln γ_eff − Δln GAMMA | emission-weighted vs area-weighted patches (second source) |
| **co-variation** | Δln GAMMA − (Δln γL + Δln γT + Δln γP + Δln γA) | multiply-then-average vs average-then-multiply (the toy), over patches and time |
| sum | | = residual |

PD, mean ≥45°N weighted by CTRL emission (old chain):

| | Weighting | Co-variation | Residual |
|---|---|---|---|
| Monoterpenes, annual | −0.7 | −1.1 | −1.8 |
| Isoprene, JJA | −7.8 | −1.6 | −9.4 |

The two panels show *why* the γ maps don't add up,## Options to reduce or remove the residual

The factor attribution (LAI vs temperature vs light vs leaf age) is a paper result, so the residual has to go: a reader cannot be told "temperature explains +1.5 %" when a term of −9 % is left unexplained.

### What any fix has to do

CLM computes, for every patch p and every 30-min time step t (`model/SourceMods/src.clm/VOCEmissionMod.F90`, `VOCEmission`):

E(p,t) = ε(p) · γL · γSM · γA · γP · γT · γC

- γSM (soil moisture) is fixed to 1 in this CLM version, so it never contributes.
- γC (CO₂ inhibition) exists only for isoprene.
- ε depends only on the plant type (PFT), so it is the same in CTRL and LCC for a given PFT.
- The γ's are written only when 0 ≤ γ < 100 (a safety check in the code).

At this level the logs add up exactly: ln E = ln ε + Σ ln γ_i. The residual appears only because the history file stores **monthly grid-cell averages** of each factor. So any exact fix has to do the split **before** averaging, at the patch × time-step level, or keep track online of what averaging destroys.

Two facts make this cheap in our setup:

1. All γ's, ε (`EPS_*`), CLM's product (`GAMMA_*`) and the emission (`MEG_*`) are already registered as **patch-level** history fields in our SourceMod. They become grid-cell averages only because the history tape is written with `hist_dov2xy = .true.` (`cases-scripts/cases-setup.sh`). Patch-level output needs **no code change**, only namelist settings.
2. CTRL and LCC are **nudged** to the same meteorology with the same time step, so every patch × time step of one run has a partner in the other. That is what an exact pairwise decomposition needs.

### Summary

| Option | Removes | Still left | Cost | Verdict |
|---|---|---|---|---|
| 1. Exact split from patch-level output (LMDI) | both parts | nothing | 7 one-year branch runs per run (2005–2008 + 2010–2012, user 2026-11-04; originally even years 2002–2014), in batches of 3 years; raw output reduced and deleted batch by batch | **recommended** |
| 1b. Offline MEGAN replay on the same output | both parts, and gives physical drivers, not just γ's | nothing (validated against CLM) | same runs, more fields, Python re-implementation | recommended extension |
| 2. SourceMod with online emission-weighted factors | most of both parts | one "dispersion" term, size unknown | same branch runs as 1 + a Fortran code change | worse than 1 |
| 3. Daily or hourly grid-cell γ output | part of the co-variation | weighting part + patch co-variation | same branch runs as 1 (the output does not exist yet), small files | insufficient |
| 4. Presentation only | nothing | everything | none | for drafts, not for the paper's factor claims |
| 5. Spread the residual over the factors | nothing (hides it) | an artefact disguised as physics | none | not defensible |

### Cost of each option

Numbers for **PD** (CTRL_PD + LCC_PD) and **all 14 years** (28 run-years), so that the options compare on the same basis; **FUT doubles** the compute and storage. **The plan for option 1 uses 7 alternate years, which halves its numbers** (≈ 95,600 core-hours, 3.0 TB raw for PD; see "How many years"). Basis (29 Oct): CTRL_PD `-20261023` costs **1,704 core-hours per simulated year** (7.2 simulated years per day on 512 cores, from its timing file); project `nn9188k` has **8.6 million core-hours** available this period (`cost -p nn9188k`). Every option that needs new output uses the same design: one-year branch runs from the yearly restarts, the years of a batch in parallel. For option 1 the years go in **batches of 3** (user decision 29 Oct, see the workflow), so its wall time is ≈ 5 batches × ≈ 1 day ≈ 5–6 days per experiment (queue permitting; each 1-year job ≈ 14 h at the measured speed).

| Option | New model runs | Core-hours, PD (+FUT) | Share of available | Storage kept (raw, transient) | Our work (estimate) |
|---|---|---|---|---|---|
| 1. Patch-level output + LMDI | 28 run-years | ≈ 191,000 (≈ 382,000), measured | ≈ 2.2 % (4.4 %) | a few GB kept; 6.0 TB raw written in total, deleted year by year (disk peak ≈ 1.3 TB per batch of 3 years) | reduction script + LMDI code: 2–3 days |
| 1b. Offline replay | none beyond 1 (driver fields are on the same tape) | + offline Python only | ≈ 0 | included in 1 | re-implement and validate the γ functions: 3–5 days |
| 2. SourceMod, online weighting | 28 run-years | ≈ 48,000 (≈ 96,000) | ≈ 0.6 % (1.1 %) | < 1 GB (monthly grid cells) | Fortran change + bit-for-bit tests: 3–5 days; analysis 1 day |
| 3. Daily / hourly grid-cell γ | 28 run-years | ≈ 48,000 (≈ 96,000) | ≈ 0.6 % (1.1 %) | daily ≈ 0.8 GB, hourly ≈ 20 GB per run-year | namelist only; analysis 1 day |
| 4. Presentation | none | 0 | 0 | 0 | done |
| 5. Spread the residual | none | 0 | 0 | 0 | < 1 day (not recommended) |
| 5-day test (before 1) | 5 days, CTRL_PD only | ≈ 230 (incl. 16 min start-up) | ≈ 0 | ≈ 5 GB | done, all checks passed |

Notes:
- **Option 1 is measured** (5-day test): writing 72 patch-level fields every time step makes the model **4× slower** (132 s per model day vs 33 s for the parent; almost all in CLM: 91 s, CAM 39 s), so a run-year costs ≈ 6,800 core-hours instead of 1,704. Options 2 and 3 write little, so they are assumed to run at the parent's speed (≈ 48,000 core-hours for PD): **4× cheaper in compute than option 1**. Option 1 is still recommended because it is the only exact one and its cost, ≈ 2 % of the available core-hours for PD, is affordable. Ways to make it cheaper, not yet tried: fewer fields on tape 2 (the 22 driver fields for 1b are ≈ 30 % of the writing), or faster parallel output settings for CLM (PIO).
- **Storage:** one patch-level field ≈ 4.6 GB per run-year at 30-min output (65,485 patches); one grid-cell field (96 × 144 grid) ≈ 0.48 GB per run-year hourly, ≈ 0.02 GB daily. Option 1 keeps the raw files only until the reduction script has processed each day.
- **Compute vs value.** Options 1, 2 and 3 all need new runs of all 14 years for both CTRL and LCC. Option 1 is ≈ 4× more expensive (heavy output), but only option 1 (with 1b) removes the residual exactly, and its cost is affordable (≈ 2 % for PD, ≈ 4 % with FUT).
- **Our work** is an estimate (b) of development time, not counting queue waits.

### Option 1: exact split from patch-level, every-time-step output (recommended)

**Idea.** Rerun the 2001–2014 period of the CTRL and LCC runs, writing the MEGAN factors for every patch at every time step. With that, the product is exact, and a standard index-decomposition method splits the change in emission into factor contributions with **no residual**.

**Why 14 years, not 15.** Every nudged run covers 15 years, 2000–2014, but the first 12 months (2000) are spin-up and are dropped in all analysis (`--spinup-months 12`). The attribution maps, and therefore the split, use **2001–2014 = 14 years**. No branch is needed for 2000.

**Words used below.** *Raw output* = the daily patch-level files the model writes (large). *Reduced output* = what the reduction script keeps after the LMDI and replay calculations (small). *Run-year* = one year of one run (CTRL or LCC).

**How the runs work.**
- **Branch runs in parallel.** The main nudged runs save a restart every 1 January (`rest/2001-01-01` … `rest/2015-01-01`). So each year can be its own **1-year branch run** (`RUN_TYPE=branch`), and all years of a run can go at the same time: e.g. 14 jobs for CTRL_PD and 14 for LCC_PD (and the same for CTRL_FUT, LCC_FUT once the new chain is archived). Because the runs are nudged, and a branch with only extra output should reproduce its parent, the pieces together equal the full run.
- **The only change is one extra CLM history tape** (tape 2), as in the 5-day test:
  ```
  hist_dov2xy          = .true., .false.   ! tape 2 per patch, not per grid cell
  hist_type1d_pertape  = ' ', 'PFTS'
  hist_nhtfrq          = 0, 1              ! tape 2 every time step (30 min)
  hist_avgflag_pertape = 'A', 'I'          ! instantaneous: no averaging at all
  hist_mfilt           = 1, 48             ! one file per day
  hist_fincl2          = MEG_*, EPS_*, GAMMA*_* of isoprene + 7 monoterpenes, GAMMAL, GAMMAC_isoprene, + driver fields for 1b
  ```
  Each file also contains the patch weights, PFT type and grid-cell index (`pfts1d_*` variables).
- **Only MEGAN-linked output (user decision, 29 Oct).** The production branches write only what the split and the checks need; all other history output of the parent is removed (it would duplicate the parent's, which is already archived and processed):

  | Tape | Content |
  |---|---|
  | CAM h0 (monthly) | `SFISOP`, `SFMTERP` |
  | CAM h1 (30 min, instantaneous) | `SFISOP`, `SFMTERP`: the bit-identity check against the parent |
  | CLM h0 (monthly) | `hist_empty_htapes = .true.`, then only the grid-cell MEGAN fields: `MEG_*`, `GAMMA*_*`, `GAMMAL`, `GAMMAC_isoprene` (8 compounds) |
  | CLM tape 2 (per patch, every step) | the 72 fields listed below |

  Physics and nudging settings stay exactly as in the parent. Removing output only stops the model from writing; it does not change the model state. The identity check of every year (workflow step 3) confirms this for the slim setup. The case script `cases-scripts/tests/13a-…-meganpatch-5day.sh` already builds this setup and is the template for the production scripts.

**Fields on CLM tape 2 (`hist_fincl2`, 72 fields).** Per patch, every time step, instantaneous. "×8" = one field per compound: isoprene, pinene_a, carene_3, pinene_b, myrcene, limonene, ocimene_t_b, sabinene.

*Emission and activity factors (50 fields), from our SourceMod `VOCEmissionMod.F90`:*

| Field | × | Long name (history file) | Units | Used for |
|---|---|---|---|---|
| `MEG_<compound>` | 8 | MEGAN flux | kg m⁻² s⁻¹ | E in the LMDI split |
| `EPS_<compound>` | 8 | baseline emission factor used | µg m⁻² h⁻¹ | ε; check E = ε · γ · unit factor |
| `GAMMA_<compound>` | 8 | total VOC activity factor | 1 | check that it equals the product of the factors |
| `GAMMAT_<compound>` | 8 | temperature activity factor | 1 | LMDI factor γT |
| `GAMMAP_<compound>` | 8 | light activity factor | 1 | LMDI factor γP |
| `GAMMAA_<compound>` | 8 | leaf-age activity factor | 1 | LMDI factor γA |
| `GAMMAL` | 1 | LAI activity factor (all MEGAN compounds) | 1 | LMDI factor γL |
| `GAMMAC_isoprene` | 1 | CO2 inhibition activity factor (isoprene only) | 1 | LMDI factor γC (isoprene) |

*Drivers for the replay (option 1b, 22 fields):*

| Field | Long name (history file) | Units | Enters |
|---|---|---|---|
| `TV`, `TV24`, `TV240` | vegetation temperature (now, last 24 h, last 240 h) | K | γT |
| `ELAI` | exposed one-sided leaf area index | m² m⁻² | γL, γA |
| `LAI240` | 240hr average of leaf area index | m² m⁻² | γA |
| `FSUN`, `FSUN24`, `FSUN240` | sunlit fraction of canopy (now, last 24 h, last 240 h) | fraction¹ | γP, γL |
| `FSD24`, `FSD240` | direct radiation (last 24 h, last 240 h) | W m⁻² ¹ | γP |
| `FSI24`, `FSI240` | indirect (diffuse) radiation (last 24 h, last 240 h) | W m⁻² ¹ | γP |
| `PAR_sun`, `PAR24_sun`, `PAR240_sun` | sunlit PAR (now, 24 h, 240 h) | µmol m⁻² s⁻¹ | γP |
| `PAR_shade`, `PAR24_shade`, `PAR240_shade` | shade PAR (now, 24 h, 240 h) | µmol m⁻² s⁻¹ | γP |
| `TOPT`, `EOPT` | topt / Eopt coefficient for VOC calc (intermediate values of γT) | — | check of γT |
| `ALPHA`, `currentPatch` | alpha / currentPatch coefficient for VOC calc (intermediate values of γP) | — | check of γP |

¹ CTSM labels `FSUN24`, `FSUN240`, `FSD*` and `FSI*` with units "K" in the history file; that metadata is wrong (they are a fraction and W m⁻²).

Not on the tape: leaf-internal CO₂ (needed to recompute γC; γC itself is saved) and `GAMMAS` (soil moisture, fixed to 1).

- **Bit-identity.** A branch with only extra history output should give **the same climate as its parent**, bit for bit. Checked by comparing the 30-min CAM `SFISOP`/`SFMTERP` (h1) with the parent's. If they match, the split is a split of the main runs themselves, not of a lookalike.

**How many years: uncertainty and cost.** PD numbers (CTRL_PD + LCC_PD); FUT doubles cost and storage. CI from the year-to-year spread of PD monoterpenes, annual (Δln E = +0.91 ± 0.21 over 14 years → spread ≈ 0.36). Core-hours **measured** in the 5-day test: 6,828 core-hours per simulated year (4× the parent's 1,704, because of writing every step); raw size measured: 0.59 GB per day = 216 GB per run-year. Project `nn9188k` had 8.6 million core-hours available on 29 Oct (`cost -p nn9188k`).

| Years | Jobs (CTRL + LCC) | 95 % CI of the ≥45°N mean | Per-cell hatching | Core-hours | Share of available | Raw output written (in total) | Reduced output kept |
|---|---|---|---|---|---|---|---|
| 2 | 4 | ± 3.2 | almost nothing passes | ≈ 27,300 | 0.32 % | 0.9 TB | < 1 GB |
| 3 | 6 | ± 0.89 | very little passes | ≈ 41,000 | 0.48 % | 1.3 TB | < 1 GB |
| 5 | 10 | ± 0.45 | partly | ≈ 68,300 | 0.79 % | 2.2 TB | < 1 GB |
| **7 (every 2nd year) — the plan** | **14** | **± 0.33** | **usable** | **≈ 95,600** | **1.1 %** | **3.0 TB** | **< 1 GB** |
| 14 | 28 | ± 0.21 | same as the current maps | ≈ 191,000 | 2.2 % | 6.0 TB | a few GB |

- *Raw output written* = 216 GB per run-year × years × 2 runs. It is **never all on disk at once**: each year's raw files are deleted as soon as that year is reduced (workflow below). The disk peak is ≈ 0.43 TB per year pair, ≈ 1.3 TB per batch of 3 years.
- With 3 years the CI is as large as the signal (+0.91), and the partial γ's are smaller still (γT +1.5, γL −0.6, γP −0.2). Only the 14-year split covers the same years as the 2001–2014 maps, so its pieces add up exactly to the emission change shown there.
- **Decision (user, 29 Oct): 7 alternate years, 2002, 2004, …, 2014.** *Superseded 2026-11-04: 2005–2008 + 2010–2012, see 'Years changed' below.*
  - *For:* half the cost, disk and time of 14 years; the years are spread over the whole period (early and late, the full range of weather), and alternate years are less correlated than consecutive ones; the CI (± 0.33) still separates the main factors (γT +1.5 and composition clearly; γL −0.6 and γP −0.2 closer to the noise).
  - *Against:* the exact terms add up to the emission change of these 7 years, not of 2001–2014, so the exact-split figure states its own years (or its shares are applied to the 14-year change, which assumes they are stable; checked from the year-to-year spread); per-cell significance with 6 degrees of freedom instead of 13; the early/late split of the analysis (2001–2007 vs 2008–2014) gets only 3–4 years each.
  - **Follow-up if the CI is too wide:** run the odd years (2001, 2003, …, 2013) with the same scripts; together they make the full 14 years, so nothing is wasted.
- Wall time depends on the number of **batches**: each 1-year job takes ≈ 14 h (at the measured 1.8 simulated years per day, plus start-up), so a batch takes ≈ 1 day with queue, archiving and reduction: 7 years = 3 batches ≈ **3 days** per experiment (14 years: 5 batches ≈ 5–6 days), queue permitting.

**Workflow, step by step.** For each year Y, the CTRL and LCC branch jobs are submitted together, and steps 1–6 run per year pair, independently of the other years.

| Step | What | Where | Disk for one year pair |
|---|---|---|---|
| 1. Run | Two branch jobs, CTRL_Y and LCC_Y (1 year each, ≈ 14 h). Each writes one raw patch-level file per day (≈ 0.6 GB), plus the small MEGAN-only monthly and 30-min files. | run dirs on `/cluster/work` | grows to 2 × 216 GB ≈ 0.43 TB |
| 2. Archive | CIME's `case.st_archive` job (automatic after each run) moves all output to `/cluster/work/users/adelez/archive/<case>/`. **Nothing is copied to NIRD**: raw files stay on `/cluster/work` (no user quota there; 3.1 PB free on 29 Oct; files purged after 42 days). | `/cluster/work` archive | 0.43 TB |
| 3. Identity check | Compare the branches' CAM h1 30-min `SFISOP`/`SFMTERP` with the parent's for year Y. If not identical: stop, report, keep the raw files. | — | 0.43 TB |
| 4. Reduce + LMDI + replay | One Python job per year pair (only when **both** runs of Y are archived): read the two runs' daily files day by day; keep vegetated patches ≥ 45°N (10,723 of 65,485 patches in CTRL_PD); pair CTRL and LCC patches by **grid cell + PFT type** (the patch lists differ: 65,485 patches in CTRL_PD, 64,751 in LCC_PD, because LCC changes which PFTs are present); compute the LMDI terms and the replay (1b) terms for each pair and time step; add them up into monthly grid-cell sums per factor. Output: one small file per year, `megan_lmdi_<PD|FUT>_<Y>.nc`. | Python, on Betzy | 0.43 TB + a few hundred MB |
| 5. Check + delete | Check that the factor terms add up to the emission change (to round-off) and that the replay's γ's reproduce CLM's `GAMMA_*`. Then **delete the raw daily files** of year Y (both runs) and the branch h0 files (identical to the parent's). | — | back to ≈ 0 |
| 6. Keep | Copy the per-year LMDI files and the logs to NIRD (`data/processed-data/megan-lmdi/`). | NIRD | a few hundred MB per year |
| 7. Analysis (once, after all years) | A notebook combines the yearly files: maps and ≥45°N means of each factor's exact contribution, ± 95 % CI over the years, in the style of the current attribution figure but without residual row. | `analysis/` | — |

- No standard postprocessing (`run_postprocess.py`) is needed for the branch runs: their h0 is identical to the parent's, which is already processed.
- **Batches of 3 years (user decision, 29 Oct; order changed 3 Nov).** The 7 years are run in batches of 3 year pairs: **batch 1 = 2002–2008–2014** (spread over the period, user 2026-11-03, so the first batch already spans early, middle and late years), then 2004–2006–2010, then 2012 (3 batches; the last has 1). If the odd years are added later: 2001–2003–2005, 2007–2009–2011, 2013. Within a batch the 6 jobs (3 CTRL + 3 LCC) run in parallel. The next batch is submitted only when the previous one has been reduced, checked and its raw files deleted (steps 4–5). So the disk peak is 3 × 0.43 ≈ **1.3 TB** on `/cluster/work` (instead of 3.0 TB with all 7 years at once), and a problem found in one batch stops the next before it starts. Cost: wall time ≈ 3 × ≈ 1 day ≈ 3 days per experiment instead of ≈ 1 day.
- **Years changed (user 2026-11-04): 2005–2008 + 2010–2012.** The new-chain parents kept restarts only at 2005, 2010 and 2015 (the other yearly `rest/` folders are empty, interim restarts not saved; checked on /cluster/work and NIRD for all four parents). Instead of regenerating restarts (≈ 19,000 core-hours per run), each run gets **two chains** (one case each): from 2005-01-01 (2005–2008) and from 2010-01-01 (2010–2012), one model year per job. Cost: consecutive years (more correlated, no years before 2005), so the CI of the 7 years is somewhat wider than for alternate years (b). Batches: 2005–2006–2010, then 2007–2008–2011, then 2012. **Plus 2000–2003 (user 2026-11-04, instead of a 2015–2017 chain):** a third chain starting exactly as the parents (hybrid from their coupled spin-up restart); 2000 = spin-up year, identity-checked then deleted without a split; 2001–2003 used. **Fewer years (user 2026-11-04 16:17): 2000–2002 (2000 discarded), 2005–2006, 2010–2011 = 6 years (2001, 2002, 2005, 2006, 2010, 2011)**; batches 2000-2001-2005-2010, then 2002-2006-2011. Cost PD ≈ 7 run-years × 2 runs × 6,828 ≈ 96,000 core-hours (b, from the 5-day measurement). With 6 years the CI of the ≥45°N mean is wider than with 7 alternate years (about ± 0.4 on 100·Δln for PD monoterpenes, from the year-to-year spread 0.36; b). Restarts: one per model year (end of every job), copied to the NIRD archive by the watcher. The alternate-year plan above (2002, 2004, …) and its batch order are superseded.
- **Status (2026-11-04):** scripts written (`cases-scripts/megan-lmdi/`: branch script, launcher, watcher; `postprocess/megan_lmdi/`: `check_identity.py`, `reduce_year_job.sh`, `reduce_megan_lmdi.py --year`). Still to do: the driver swaps (Shapley, option 1b) inside the reduction, before the production batches delete raw files. The 32-day test keeps its raw files, so the swaps can be developed on it. **Done 2026-11-06:** driver swaps in the reduction (`postprocess/megan_lmdi/megan_swaps.py`; user decisions 6 Nov 17:55: per matched patch pair, monthly, 8 compounds, batch 2 gated on the 60-day test); all checks pass on the 60-day test and on 1–3 July 2010 (replay = CLM to 10⁻¹⁵, flagged share 2.6 × 10⁻⁴ = first step only); details and output in `postprocess/megan_lmdi/README.md`.
- **The reduction script must be ready and tested before step 1**, because the replay (1b) needs the per-time-step drivers and they are deleted in step 5. It is written and tested on the 5-day test output (and, optionally, a 1-year old-chain pair).

**The method: LMDI (log-mean Divisia index).** For each pair of matched patches (same grid cell, same PFT) and each time step (CTRL value E⁰, LCC value E¹):

ΔE(p,t) = L(E¹, E⁰) · [Δln w + Δln γL + Δln γT + Δln γP + Δln γA (+ Δln γC)],  with L(a,b) = (a − b) / (ln a − ln b)

- This is an identity, not an approximation, because ln E is exactly a sum of the ln factors at this level. Summed over patches, time steps and cells, the factor terms add up to the total ΔE exactly.
- It does not depend on the order of the factors. A step-by-step "swap one factor, then the next" split does.
- To get the same 100·Δln units as the current figures, multiply each factor's total by Δln E_total / ΔE_total. The pieces still add up exactly.
- **Composition:** w is the patch's area share of the grid cell. ε cancels (same PFT, same ε), so composition = the change in patch weights. Patches that exist in only one run (a PFT introduced or removed by LCC) have E = 0 in the other run, and ln 0 is undefined. Their whole ΔE goes to composition, which is the standard zero-value rule for LMDI (Ang & Liu 2007).
- **Check on the toy cell** (section "Where the residual comes from"): the forest patch's emission does not change and the sparse patch emits nothing in either run. So LMDI gives γT a contribution of **exactly 0**, matching the true emission, where the area-mean maps gave +41. A scratchpad test with random data also confirmed that the terms add up to ΔE to round-off.

**Field count and file size.** One patch field ≈ 0.26 MB per time step (65,485 patches) → ≈ 4.6 GB per run-year at 30-min output. Each of the 7 monoterpenes is its own MEGAN class (APIN, 3CAR, BPIN, MYRC, LIMO, OCIM, SABI in `megan21_emis_factors_78pft_c20161108.nc`), so all their γT/γP/γA are needed: isoprene + 7 monoterpenes × (MEG, GAMMAT, GAMMAP, GAMMAA, GAMMA) + GAMMAL + GAMMAC = 42 fields, plus 22 driver fields for 1b = 72 fields → **216 GB per run-year, measured** (0.59 GB per daily file, 48 steps).

**Risks and limits.**
- Queue: the 6 jobs of a batch may not all start together. Each year pair is reduced only when both of its runs are done, so a delay only holds that year's raw files longer, and the next batch waits.
- Bit-identity with the parent is assumed until the 5-day test shows it. If it fails, the branch years are still a valid CTRL/LCC pair, but no longer the same runs as the 2001–2014 maps.
- LMDI attributes the change to the **γ functions**, not to physical drivers. LAI enters more than one γ (γL directly, γA through the LAI change, and γP through the sunlit fraction). That is what option 1b is for.
- FUT: only meaningful on the new chain. The old FUT γL and residual are dominated by the spin-up mismatch.

#### Option 1b: offline MEGAN replay (extension of option 1)

**Idea.** Re-implement CLM's MEGAN activity factors in Python and feed them the patch-level **drivers** from the same branch runs. Then build counterfactuals, e.g. CTRL with LCC's LAI, and average over all swap orders (Shapley values) so the split is again exact and order-free.

**Which code.** The functions are in our CLM SourceMod, `model/SourceMods/src.clm/VOCEmissionMod.F90` (the copy the runs are built with, identical to the parent case's):

| Function | Lines | Factor | Inputs |
|---|---|---|---|
| `get_gamma_P` | 743–812 | light | sunlit/shaded PAR now, 24-h and 240-h means; sunlit fraction; 240-h direct/diffuse solar |
| `get_gamma_L` | 815–840 | LAI | 240-h sunlit fraction, LAI |
| `get_gamma_T` | 916–974 | temperature | leaf temperature now, 24-h and 240-h means; class constants (ct1, ct2, βT, LDF, Ceo) |
| `get_gamma_A` | 977–1031 | leaf age | PFT, LAI now and 240-h mean |
| `get_gamma_C` | 1034–1125 | CO₂ (isoprene only) | sunlit/shaded leaf-internal CO₂, surface pressure, CO₂ |
| `get_gamma_SM` | 843–913 | soil moisture | not used (γSM fixed to 1) |

The class constants come from `megan21_emis_factors_78pft_c20161108.nc`. The main routine that calls them and multiplies the factors is `VOCEmission` in the same file (lines ≈ 396–700).

**Drivers on the tape.** `TV`, `TV24`, `TV240` (leaf temperature), `ELAI`, `LAI240`, `FSUN`, `FSUN24`, `FSUN240`, `FSD24`, `FSD240`, `FSI24`, `FSI240` (standard CLM fields), and `PAR_sun`, `PAR24_sun`, `PAR240_sun`, `PAR_shade`, `PAR24_shade`, `PAR240_shade`, `TOPT`, `EOPT`, `ALPHA`, `currentPatch` (our SourceMod). Leaf-internal CO₂ for γC is not on the tape yet; γC changes isoprene by only −0.03 % (PD JJA), so the replay can keep it as in CLM and treat it as its own small term.

**Why.** It answers the question reviewers will ask: "how much is LAI, how much is the warmer canopy, how much is the light environment", not "how much is γT".

**Driver groups for the swaps (user decision, 2 Nov).** Four groups, plus a three-group version computed from the same runs:

| Group | CLM inputs | Factors it changes |
|---|---|---|
| **Leaf area** | `ELAI` (now), `LAI240` (10-day mean) | γL, γA |
| **Leaf temperature** | `TV` (now), `TV24`, `TV240` | γT |
| **Incoming light** | direct and diffuse light reaching the canopy: now (grid-cell value, derived from `PAR_*` of any valid patch of the cell), `FSD24/240`, `FSI24/240` | γP |
| **Canopy light** | sunlit fraction of the leaves: `FSUN`, `FSUN24`, `FSUN240` | γP (and the branch switch in γL) |

The light on sunlit and shaded leaves is rebuilt from incoming light and sunlit fraction as in CLM, PAR_sun = (direct + FSUN · diffuse) · 4.6 and PAR_shade = (1 − FSUN) · diffuse · 4.6 (same for the 24- and 240-h means). This also repairs the steps where the tape's `PAR_*` fields are stale (`postprocess/megan_lmdi/README.md`). In CLM the sunlit fraction is `laisun / elai` (`SurfaceRadiationMod.F90:434`), from the two-stream canopy radiation: it depends on leaf + stem area, the PFT's leaf angle and the sun angle. Within a CTRL/LCC patch pair the PFT and the sun angle are the same, so the sunlit fraction differs only because the canopy differs. "Canopy light" is therefore the self-shading effect of the leaf-area change.

*Strengths.*
- The groups match the questions a reviewer will ask: more leaves, warmer canopy, more light, more self-shading.
- The split is exact, and order-free by construction.
- Canopy light makes a real effect visible: a denser canopy shades its own leaves. With three groups that effect would be hidden inside "leaf area".
- Incoming light is a useful check. The runs are nudged to the same weather, so differences in light reaching the canopy can only come from clouds or aerosols, including the BVOC → SOA → cloud feedback. It is expected to be small; if it is not, that is a finding in itself.

*Weaknesses (b: reasoning, not tested yet).*
- **Leaf area and canopy light are not independent.** CLM computes the sunlit fraction from the leaf area, so some swap combinations never occur in either run (e.g. LCC's leaf area with CTRL's sunlit fraction). The average still adds up exactly, but each of the two values alone describes a made-up canopy. **Their sum is robust; the split between them is a modelling convention.**
- **Leaf temperature is not "climate only".** The forest changes its own canopy temperature through albedo and evaporation. The swaps measure MEGAN's direct response to the temperature the leaves have, whatever its cause; the text must say so.
- **The CO₂ factor (γC, isoprene only) cannot be swapped.** It depends on leaf-internal CO₂, which comes from photosynthesis and is not on the tape. So it is not pure CO₂; it stays a separate term with CLM's own value. It is small: −0.7 % of the isoprene change in the 5-day test.
- **Plant cover has to be combined with the swaps.** Within a matched pair the patch's share of the grid cell (w) also changes. Each pair's change is split as Δ(w·E) = w̄ · ΔE + Ē · Δw (w̄, Ē = means of the two runs), which is exact; the swaps then split only ΔE. Patches present in one run only go entirely to plant cover, as in the LMDI script.

*Computation.* For each matched patch pair, step and compound, MEGAN is recomputed for all 2⁴ = 16 combinations of CTRL/LCC groups; the Shapley values of both splits come from these 16 values:
- **4 groups** (leaf area, canopy light, leaf temperature, incoming light): the detail, including self-shading;
- **3 groups** (leaf area + canopy light as one "canopy" group): the headline numbers.

The 3-group canopy value is not simply leaf area + canopy light from the 4-group split; each is computed on its own, at no extra cost. No choice between them is needed before the runs. Final terms, exact:

> plant cover + canopy (or leaf area + canopy light) + leaf temperature + incoming light + CO₂ factor + CLM safeguard = total change

**Validation.** The Python γ's must reproduce CLM's `GAMMA_*` to round-off before any result is used (tested on the 5-day output). **Done 2 Nov:** all γ's (L, A, T, P) of the 8 compounds reproduce CLM to ≤ 9 × 10⁻¹⁶ (both runs, all vegetated patches), using the previous step's ELAI, LAI240, TV24, TV240 (CLM updates them after MEGAN); `postprocess/megan_lmdi/megan_replay.py`.

**Cost.** No extra runs: the driver fields are on the same tape as option 1. The replay runs inside the reduction step (step 4), because the raw files are deleted afterwards. Plus 3–5 days of coding and validation.

**Implemented (2026-11-06, 21:15).** `postprocess/megan_lmdi/megan_swaps.py`, called by the live `reduce_megan_lmdi.py` (user decisions 6 Nov 17:55: inside the per-year reduction; output per matched patch pair, monthly sums of the per-step Shapley terms; all 8 compounds; batch 2 waits for validation on the 60-day test). **Validated** on the 60-day test pair (all 60 days) and on 1–3 July 2010: replayed γ product = CLM to 1.3 × 10⁻¹⁵, rebuilt PAR = CLM to 2.2 × 10⁻¹³, closure to round-off; flagged steps 2.6 × 10⁻⁴ of |ΔE|, all at the first step of the chain (no previous step on the tape). Output variables `swap4` (9 terms) and `swap3` (8 terms) per compound, month and patch pair; details in `postprocess/megan_lmdi/README.md`. First numbers (1–3 July 2010, ≥ 45°N, isoprene, 100 · Δln E): +2.68 = plant cover −0.84 + canopy +2.90 + leaf temperature +0.54 + incoming light +0.07 + CO₂ +0.01; canopy light (self-shading, 4-group split) −0.22. Status: 2010 re-reduced with the swaps (running 6 Nov night); 2001 and 2005 get them automatically; batch 2 needs the user's OK.

**Units for the headline numbers (open, b: not asked yet).** All terms are additive in kg, so any linear rescaling of the region total keeps them exact. Possibilities:

| Unit | Formula (region R, term C_f) | Adds up to | Good for | Problem |
|---|---|---|---|---|
| A. Absolute, Tg yr⁻¹ | Σ C_f | ΔE (Tg yr⁻¹) | the physical size; comparable to emission budgets | PD and FUT have different baselines; hard to compare between compounds |
| B. % of the CTRL emission | 100 · C_f / E_CTRL | 100 · ΔE / E_CTRL (= % change) | comparing PD vs FUT and isoprene vs monoterpenes | none serious; the base (CTRL) must be stated |
| C. Log-scaled, as the current attribution figures | 100 · Δln E · C_f / ΔE | 100 · Δln E (≈ %) | same scale as the LMDI split and the current figures | the scaling is per region: map cells cannot be summed to the region value |
| D. Share of the change, % | 100 · C_f / ΔE | 100 % | "how much of the change is leaf area" | blows up when ΔE ≈ 0 (monoterpenes ≥ 45°N ≈ 0 in PD), and signs flip |
| E. Flux for maps, mg m⁻² day⁻¹ | C_f per cell area and time | ΔE per m² | maps | not a headline number |

Claude's recommendation (b): A as the headline (Tg yr⁻¹, region ≥ 45°N), with B alongside in the text and tables; C only where the LMDI split is shown next to the swaps; D only for isoprene and only if ΔE is clearly non-zero. The plant-cover term already uses the midpoint split (w̄ · ΔE + Ē · Δw), which is the exact two-player Shapley split; the alternative (log-mean weights, as LMDI) only matters when shown next to the LMDI composition term, and differs by ≈ 0.1 % of E in the July test (−0.84 vs −0.73).

#### The 5-day test (before the production runs)

A **technical go/no-go check** before committing about 14 run-years of compute (28 for all 14 years). It gives no science result.

- **Run:** a 5-day branch of CTRL_PD (old chain, `-20261023`) at 2005-01-01. The parent's namelists are copied as they are, plus the patch-level tape (72 fields: emission, ε and γ's of the 8 compounds, and the driver fields for option 1b).
- **Script:** `cases-scripts/tests/13a-NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-meganpatch-5day.sh`. Before building, it compares the case's namelists with the parent's and stops if anything differs beyond start files, history output and run length.
- **Checks:** `diagnostics/megan-exact-split-test/megan_patch_branch_5day_test.ipynb` (all five questions, with tables and figure).

| # | Question | Why it matters | If it fails |
|---|---|---|---|
| 1 | Does a branch with extra output reproduce CTRL_PD exactly? (30-min CAM `SFISOP`/`SFMTERP`, bit for bit) | Only then are the 14 parallel one-year runs together the same run as the one behind the 2001–2014 maps | The split describes lookalike runs: still usable, but weaker and needing explanation |
| 2 | Is the output right? All 72 fields present, per patch (`PFTS`), every time step | A wrong setting found after 28 jobs means redoing them all | Fix the namelist and retest (minutes) |
| 3 | Is `GAMMA` exactly the product of the γ's per patch and step? | LMDI depends on it. CLM stores the γ's only when 0 ≤ γ < 100, so stale values may sit in some patches | Those patches need special handling before the method can be trusted |
| 4 | File size per day | Sizes the storage, and how fast the reduction script must keep up | Change the field list or the reduction plan |
| 5 | Slowdown from writing every step | Sets wall-clock limits and the real cost of the 28 jobs | Same as 4 |

**Result so far (29 Oct).** The test ran with the parent's full output plus tape 2 (job 1784026, 27 min wall time). **Check 1 passed:** `SFISOP` and `SFMTERP` are bit-identical to CTRL_PD at all 192 common 30-min steps of 1–4 January 2005 (`diagnostics/megan-exact-split-test/megan_patch_branch_5day_test.ipynb`). Checks 2–5 passed too; the land model is 4× slower (see the cost tables).

**32-day production test (approved by the user 2026-11-03; replaces the 29 Oct 'no separate slim test' decision).** Before batch 1: CTRL_PD + LCC_PD new-chain branches from 2002-01-01, 32 days (crosses January → February), run with the **production** branch script and the **batch launcher**, slim output. Checks: identity with the parents (30-min CAM h1 `SFISOP`/`SFMTERP`), monthly CLM and CAM h0 = the parents' January 2002 (monthly output never tested so far), reduction + replay on new-chain data across a month boundary, delete step as a dry run. Cost ≈ 600 core-hours per run, ≈ 1,200 for the pair (≈ 3 % of batch 1). **Start date moved to 2005-01-01** (user 2026-11-04: no 2002 restart exists). **Length changed to 2 jobs × 30 days = 2 months + 1 day** (user 2026-11-04): two complete months for the monthly identity check, two month boundaries, and one job restart (31 Jan) to test the continuation used by the production chains; ≈ 2,500–2,800 core-hours (b). Scripts written 2026-11-04: `bash cases-scripts/megan-lmdi/launch_megan_lmdi.sh test PD` (needs the user's OK to submit).

It also gives a real sample of output to write and test the reduction script and the LMDI code on. Cost: ≈ 230 core-hours (27 min on 512 cores, of which 16 min start-up), ≈ 5 GB.

**Why not a longer test (e.g. 3 years)?**

- No result: the exact split needs a **pair** (CTRL and LCC on the same days). A CTRL-only run, however long, answers nothing more than 5 days on the five questions.
- Wrong chain: it branches from the old CTRL_PD. The paper's split must come from the new chain.
- Storage: the model writes ≈ 216 GB of raw output per run-year (measured). In production the reduction script deletes it year by year (keeping < 1 GB), but that script does not exist yet, so a 3-year test would have to keep all of it: 3 × 216 GB ≈ 0.65 TB.
- Risk: if check 1 or 3 fails, 3 years are wasted instead of 5 days.

**Optional in-between step: a 1-year old-chain pair.** Once the reduction script works, CTRL_PD + LCC_PD (old chain) for one year (e.g. 2005) would give a real LMDI split for that year. Compared with the approximate split of the same year, it shows how wrong the area-mean maps are: a test of the method itself. The old chain's spin-up mismatch matters less for this comparison than for the final numbers. Worth doing only if that check is wanted before the new chain is archived.

### Option 2: SourceMod with online emission-weighted factors

**Idea.** Change the code so that CLM accumulates, per patch and time step, E and E·ln γ_i for each factor. The monthly grid-cell output is then the **emission-weighted** mean of ln γ_i, instead of the area-weighted mean of γ_i.

**What it removes.** With emission weights the weighting part disappears, and the logs of the factors are averaged directly, so most of the co-variation goes too. What is left is one term:

Δln Ē = Σ_i Δ⟨ln γ_i⟩_E + Δ⟨ln w ε⟩_E + ΔJ,  J = ln Ē − ⟨ln E⟩_E

J measures how unevenly emission is spread over patches and hours (it is 0 if E is the same everywhere and always). Emission has a strong daily cycle and varies a lot between PFTs, so J is large, and how much it **changes** between CTRL and LCC is unknown until computed.

**Why it cannot be exact.** An exact split needs both runs at once (the pair E⁰, E¹ for every patch and time step). A single running model only sees itself.

**Cost.** The same 28 one-year branch runs per pair as option 1, but without the heavy patch-level output, so at the parent's speed (≈ 48,000 core-hours for PD vs ≈ 191,000 for option 1; see "Cost of each option"), plus a Fortran change in `VOCEmissionMod.F90` that has to be tested for bit-identity. Code cannot be added to the runs already in progress, and the fBVOC runs have MEGAN switched off. Its advantages are small output files and ≈ 4× less compute than option 1.

**Verdict.** ≈ 4× cheaper in compute than option 1, but more code work and it still leaves a term of unknown size. Since option 1's compute (≈ 2 % of the available core-hours for PD) is affordable, the exact option is preferred.

### Option 3: daily or hourly grid-cell γ output

**Idea.** Keep grid-cell averages but write them more often, so less time co-variation is averaged away.

**What it removes.** Daily output removes only the co-variation between days (weather events). The **daily cycle** co-variation stays: γT and γP both peak at midday, which is the main time part. Hourly output removes the time co-variation almost entirely. Neither touches the patch co-variation or the **weighting part**, which is the largest part for isoprene in JJA (−7.8 of −9.4 in PD).

**Cost.** No code change and small files, but the output does not exist yet: it needs the same 28 one-year branch runs per pair as option 1, at the parent's speed (≈ 48,000 core-hours for PD).

**Verdict.** Insufficient on its own: cheaper than option 1, but it removes much less. It would at most show how much of the co-variation part is daily cycle.

### Option 4: presentation only

**Idea.** Report the exact terms (emission = composition + γ_eff) as the result, and show the single factors as indicative, with the residual and its two parts next to them. This is what the current figures do.

**Verdict.** Honest and good enough for drafts and group meetings. It does not support a quantitative claim like "temperature explains X %", which the paper needs.

### Option 5: spread the residual over the factors

**Idea.** Share the residual among γL, γT, γP, γA, in proportion to their size, or with a Shapley split of the product of the area means.

**Why not.** A Shapley split of the area means is exact for the *product of the means*, not for the true emission, so it still spreads an averaging artefact. Proportional sharing has no physical basis, and the residual can be larger than some factors (in the toy cell it is the whole γT signal). A reviewer would rightly reject either.

### Recommended path for the paper

1. **Now:** the current figures (option 4), with the weighting and co-variation panels. Done.
2. **Test (ran 29 Oct, identity passed; see "The 5-day test" above):** one 5-day branch of CTRL_PD (old chain, `-20261023`) at 2005-01-01 with the patch-level tape: file size per day, slowdown, bit-identity with the parent (30-min CAM h1), and per patch GAMMA = product of the γ's. Script `cases-scripts/tests/13a-…-meganpatch-5day.sh`, checks `diagnostics/megan-exact-split-test/megan_patch_branch_5day_test.ipynb`.
3. **Reduction script:** daily patch file → monthly LMDI sums + replay inputs ≥ 45°N, raw file deleted; tested on the 5-day output.
   *Optional:* 1-year old-chain CTRL_PD + LCC_PD pair (e.g. 2005), LMDI vs approximate split for that year, as a method check (see "The 5-day test").
4. **Before production (scripts written 4 Nov, `cases-scripts/megan-lmdi/README.md`; driver swaps done and validated 6 Nov, `postprocess/megan_lmdi/megan_swaps.py`, see option 1b):** write the production branch script (one 1-year branch per run and year, from the 5-day template), the driver swaps in `postprocess/megan_lmdi/reduce_megan_lmdi.py`, the per-year identity check and the batch launcher; then the **32-day production test** (approved 3 Nov, see "The 5-day test").
5. **PD (new-chain CTRL_PD and LCC_PD, archived):** 7 years per run, **2005–2008 + 2010–2012** in two chains (user 4 Nov; restarts exist only at 2005/2010), in 3 batches: 2005–2006–2010, then 2007–2008–2011, then 2012; patch-level tape; LMDI split and replay (1b) per year. If the CI is too wide: add the odd years (2001, 2003, …, 2013).
6. **To do after PD batch 1, before batches 2–3 (user 3 Nov):** compare the LMDI split with the approximate split (the current attribution maps) for the same 3 years (2005, 2006, 2010): how much of composition, activity and residual moves, and whether the year-to-year spread changes the plan for the remaining years.
7. **FUT:** the same (batch 1 = 2005–2006–2010, then the same comparison) with the new-chain CTRL_FUT and LCC_FUT.
8. Compare LMDI with the approximate split for all years, to say how much the residual mattered in the 2001–2014 maps.

Every model run needs the user's OK before it is submitted.
