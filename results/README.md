# results/

Layout since **2026-11-08** (user): one folder per **contrast category**. New chain. Since **2026-11-09** `figures/` and `tables/` hold only the 2001–2025 period (`*_2001_2025`); the 2001–2014 outputs are in `figures-2001-2014/` and `tables-2001-2014/` (same subfolder layout).

## The contrasts (the only ones used in `analysis/`)

Defined once in `src/boreal_forest_expansion/plotting/forcing_maps.py` (`CONTRASTS`, `Contrast.key` = file-name tag).

| Category | Contrast (short name) | case1 − case2 | Key |
|---|---|---|---|
| **interactive** | LCC_FUT − CTRL_PD | LCC_FUT − CTRL_PD | `LCC_FUT-CTRL_PD` |
| | [LCC − CTRL]_PD | LCC_PD − CTRL_PD | `LCC-CTRL_PD` |
| | [LCC − CTRL]_FUT | LCC_FUT − CTRL_FUT | `LCC-CTRL_FUT` |
| | CTRL_[FUT − PD] | CTRL_FUT − CTRL_PD | `CTRL_FUT-PD` |
| | LCC_[FUT − PD] | LCC_FUT − LCC_PD | `LCC_FUT-PD` |
| **fBVOC** | LCC_PD_fBVOC [lccPD − ctrlPD] | LCC_PD_fBVOClccPD − LCC_PD_fBVOCctrlPD | `fBVOC_PD_lccPD-ctrlPD` |
| | LCC_FUT_fBVOC [lccFUT − ctrlFUT] | LCC_FUT_fBVOClccFUT − LCC_FUT_fBVOCctrlFUT | `fBVOC_FUT_lccFUT-ctrlFUT` |
| | LCC_FUT_fBVOC [lccFUT − lccPD] | LCC_FUT_fBVOClccFUT − LCC_FUT_fBVOClccPD | `fBVOC_FUT_lccFUT-lccPD` |
| | LCC_FUT_fBVOC [lccFUT − ctrlPD] | LCC_FUT_fBVOClccFUT − LCC_FUT_fBVOCctrlPD | `fBVOC_FUT_lccFUT-ctrlPD` |
| | LCC_FUT_fBVOC [ctrlFUT − ctrlPD] | LCC_FUT_fBVOCctrlFUT − LCC_FUT_fBVOCctrlPD | `fBVOC_FUT_ctrlFUT-ctrlPD` |
| | LCC_FUT_fBVOC [lccPD − ctrlPD] (not really physical) | LCC_FUT_fBVOClccPD − LCC_FUT_fBVOCctrlPD | `fBVOC_FUT_lccPD-ctrlPD` |
| **non-BVOC** | [LCC_PD − CTRL_PD]_fBVOCctrlPD | LCC_PD_fBVOCctrlPD − CTRL_PD_fBVOCctrlPD | `nonBVOC_LCC-CTRL_PD` |
| | [LCC_FUT − CTRL_FUT]_fBVOCctrlFUT | LCC_FUT_fBVOCctrlFUT − CTRL_FUT_fBVOCctrlFUT | `nonBVOC_LCC-CTRL_FUT` |
| | [LCC_FUT − LCC_PD]_fBVOCctrlPD | LCC_FUT_fBVOCctrlPD − LCC_PD_fBVOCctrlPD | `nonBVOC_LCC_FUT-PD` |
| | [LCC_FUT − CTRL_PD]_fBVOCctrlPD | LCC_FUT_fBVOCctrlPD − CTRL_PD_fBVOCctrlPD | `nonBVOC_LCC_FUT-CTRL_PD` |
| **artefacts** | art_LCC_PD | LCC_PD − LCC_PD_fBVOCctrlPD | `art_LCC_PD` |
| | art_LCC_FUT | LCC_FUT − LCC_FUT_fBVOCctrlFUT | `art_LCC_FUT` |
| | art_CTRL_PD | CTRL_PD − CTRL_PD_fBVOCctrlPD | `art_CTRL_PD` |
| | art_CTRL_FUT | CTRL_FUT − CTRL_FUT_fBVOCctrlFUT | `art_CTRL_FUT` |

**`LCC_FUT_fBVOClccFUT` is a design-B stand-in, to be replaced:** until the run (24g) is postprocessed it is LCC_FUT − art_CTRL_FUT = LCC_FUT − CTRL_FUT + CTRL_FUT_fBVOCctrlFUT (assumes art(LCC land) = art(CTRL land)). Rows/titles using it say "(design B)". To replace it: `forcing_maps.LCC_FUT_FBVOCLCCFUT_DESIGN_B = False`, then rerun `analysis/`.

## figures/

| Folder | What |
|---|---|
| `figures/interactive/`, `figures/fBVOC/`, `figures/non-BVOC/`, `figures/artefacts/` | Everything about the contrasts of that category: contrast grids (`contrast_grid_<panels>_<category>_*`), Ghan maps per contrast (`ghan[_seasonal]_<key>_<band>_*`), radiative budget bars and paired years per category, seasonal cloud types, cloud profiles, water budget, land carbon and ET-split grids (`contrast_grid_{carbon,et_split}_*`, `analysis/land-carbon-water.ipynb`; `interactive/` also its seasonal cycle), yearly time series per contrast (`timeseries_<key>_*`). `interactive/` also holds the cumulative decomposition (T = LCC_FUT − CTRL_PD; `analysis/cumulative_radiative_decomposition.ipynb`); `artefacts/design-B-split/` the closed split [LCC − CTRL]_P = non-BVOC + (art_LCC_P − art_CTRL_P) (`analysis/artefact-corrected-split.ipynb`); its six-panel forcing summaries (`<P>_fBVOC<E>corr_forcing_decomposition_<band>[_split6-2]_*`; FUT also E = ctrlPD, lccPD, made 2026-11-09 by a separate script) are in `design-B-split/individual-scale/` (per-panel scales) and `design-B-split/split6-2/` (albedo + total ±6, BVOC terms ±2), same in `figures-2001-2014/`. |
| `figures/pd-fut-attribution/` | `analysis/pd-fut-attribution.ipynb`: PD vs FUT comparisons that mix categories. |
| `figures/timeseries/` | Absolute yearly values of every run (no differences), `analysis/timeseries-responses.ipynb` §3. |
| `figures/megan_factors/` | `analysis/megan_factor_maps.ipynb` (LCC vs CTRL, same period), `diagnostics/3_megan-exact-split-test/lake_fix_effect.ipynb`. |

Code: `forcing_maps.FIG_CATEGORY[<category>]`; grids and Ghan maps of a category go there by default (`make_contrast_grid_figure(<category>, …)`, `make_ghan_contrast_figure(contrast)`).

## tables/

| Path | What |
|---|---|
| `tables/*_2001_2025.csv` | Tables that span categories: `radiative_budget_categories[_yearly]`, `water_budget_categories`, `timeseries_regional_means` (column `category`), `timeseries_absolute`, `cumulative_radiative_decomposition`, `pd_fut_*`, `baseline_aerosol_cloud`, `emission_origin_annual`, `land_carbon_water_regional`, `seasonal_cycle_lcc_minus_ctrl_modified`. |
| `tables/<category>/` | Tables of one category (`TABLE_CATEGORY`), e.g. `artefacts/` = design-B split. |
| `tables/logs/` | Notebook run scripts (`run_nb_inplace.py`) and run logs. |

## Old sets (not regenerated)

| Folder | What |
|---|---|
| `figures-2001-2014/`, `tables-2001-2014/` | New chain, 2001–2014 period (`*_2001_2014`), same layout as `figures/` and `tables/`. Moved out 2026-11-09. |
| `figures-pre-reorg-20261108/`, `tables-pre-reorg-20261108/` | Layout 2026-11-04 → 2026-11-08: `LCC-CTRL/`, `CTRL_FUT-CTRL_PD/`, `fBVOC/{pre-artefact-correction, artefact-design-B}/`, `timeseries/`; tables `pre-artefact-correction/`, `artefact-design-B/`, flat `*_2001_2014.csv` and the older `*_2001_2009.csv`. New chain, but contrasts LCC − LCC_fBVOC* (uncorrected) etc. |
| `figures-2001-2014-all-bvoc-pre-co2-fix/`, `tables-2001-2014-all-bvoc-pre-co2-fix/` | Old spin-up chain (before the CO₂ fix). |
| `figures-pre-co2-fix/`, `figures-def-transparent/` | Older figure sets. |
