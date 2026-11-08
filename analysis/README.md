# analysis/

Paper notebooks. **Contrasts (user 2026-11-08): only the 19 contrasts of 4 categories, interactive / fBVOC / non-BVOC / artefacts**, defined once in `src/boreal_forest_expansion/plotting/forcing_maps.py` (`CONTRASTS`; list and file keys in `results/README.md`). `LCC_FUT_fBVOClccFUT` is a design-B stand-in (LCC_FUT − CTRL_FUT + CTRL_FUT_fBVOCctrlFUT) until the run is processed: **to be replaced** via `forcing_maps.LCC_FUT_FBVOCLCCFUT_DESIGN_B = False` + rerun.
Figures go to `results/figures/<category>/`, tables to `results/tables/` (cross-category) or `results/tables/<category>/`; the pre-2026-11-08 outputs are in `results/{figures,tables}-pre-reorg-20261108/`.
Run with `$PY results/tables/logs/run_nb_inplace.py analysis/<nb>.ipynb` (outputs saved in the notebook).
Variables in each figure (subtitle, variable, category, calculation): `PLOTTED_VARIABLES.md`.

| Notebook | Content |
|---|---|
| `radiative_forcing.ipynb` | Per category: radiative budget bars (Ghan terms + albedo proxy, ≥45°N and modified cells) and paired years; Ghan maps (total + ARI + cloud + clear-clean) per contrast, annual and seasonal, NET/SW/LW. Six-panel summaries dropped 2026-11-08 |
| `bvoc-soa-cloud-interactions.ipynb` | Per category: BVOC → SOA → aerosol → cloud context grids (rows = contrasts), cloud-type grids (annual, JJA), seasonal cloud-type lines, zonal-mean cloud profiles. Per-period context maps dropped 2026-11-08 |
| `biogeophysical-hydro.ipynb` | Per category: hydrology, snow/albedo, surface energy, FSDS split grids; land water budget P − ET − R − ΔTWS (table + bars) |
| `pd-fut-attribution.ipynb` | Why the response differs PD → FUT, with the category contrasts grouped by period ([LCC − CTRL]_P, LCC_P_fBVOC [lccP − ctrlP], non-BVOC, art_LCC_P, art_CTRL_P; FUT also CTRL_[FUT − PD]): radiative budget, emission/LAI origin, seasonal chain of the fBVOC contrasts, baselines and % changes, paired years, PD source boxes. Text/findings still describe the old contrasts; figures `results/figures/pd-fut-attribution/` |
| `megan_factor_maps.ipynb` | MEGAN emission/activity factor maps; attribution residual explained in `MEGAN_ATTRIBUTION.md` |
| `FBVOC_ARTEFACT.md` | fBVOC prescription artefact: evidence, cause, designs A/B (formulas), decision (matched baseline) and first new-chain numbers |
| `fut-fbvoc-emission-source-choice.ipynb` | Which prescribed emissions for the FUT fBVOC reference, now with the FUT fBVOC-category contrasts LCC_FUT_fBVOC [lccFUT − ctrlPD / ctrlFUT / lccPD] (design B stand-in = the former corrected rows, same numbers) and [ctrlFUT − ctrlPD], plus art_CTRL_FUT; outputs in `fut-fbvoc-emission-source-choice_outputs/` (old ones in its `pre-reorg-20261108/`) |
| `timeseries-responses.ipynb` | Yearly time series 2001–2014 of the 9 context-map variables + NET Ghan terms for each of the 19 contrasts (global and modified cells / ≥45°N), figures in the category folders; §3 absolute yearly values of every nudged run (`results/figures/timeseries/`); tables `results/tables/timeseries_{regional_means,absolute}_2001_2014.csv` |
| `cumulative_radiative_decomposition.ipynb` | Cumulative net TOA response (P1 → P4): D1 = CTRL_[FUT − PD], D2 = [LCC_FUT − CTRL_FUT]_fBVOCctrlFUT (non-BVOC), D3 = art_LCC_FUT − art_CTRL_FUT (BVOC, corrected), T = LCC_FUT − CTRL_PD = D1 + D2 + D3 (switched 2026-11-08); ≥45°N and modified cells; figures `results/figures/interactive/`, table `results/tables/cumulative_radiative_decomposition_2001_2014.csv` |
| `simulation-contrasts.ipynb` | The same contrasts, one contrast-grid figure per question (user 2026-11-07/08): 1a–1c interactive, 2/2b fBVOC, 3a/3b non-BVOC, 4a/4b artefacts; third rows = row 2 − row 1 in 1b, 1c, 3a, 3b, 4b; short row names; outputs in `simulation-contrasts_outputs/figures/` |
| `artefact-corrected-split.ipynb` | Closed split per period with listed contrasts: [LCC − CTRL]_P = [LCC_P − CTRL_P]_fBVOCctrlP + (art_LCC_P − art_CTRL_P); radiative budget, chain table, Ghan and context maps; outputs `results/{figures,tables}/artefacts/` |

**Before 2026-11-08** the notebooks used `BVOC_PAIRS` (LCC − CTRL, LCC − LCC_fBVOC*, CTRL_FUT − CTRL_PD; folders `LCC-CTRL/`, `CTRL_FUT-CTRL_PD/`, `fBVOC/…`); those functions stay in `forcing_maps` for `diagnostics/` and `analysis-2001-2019/`, and those outputs are in `results/*-pre-reorg-20261108/`.
