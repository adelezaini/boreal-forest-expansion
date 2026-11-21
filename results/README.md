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
| **artefacts** | art_LCC_PD | LCC_PD − LCC_PD_fBVOClccPD (own emissions, since 2026-11-16) | `art_LCC_PD` |
| | art_LCC_FUT | LCC_FUT − LCC_FUT_fBVOClccFUT (own emissions, since 2026-11-16) | `art_LCC_FUT` |
| | art_CTRL_PD | CTRL_PD − CTRL_PD_fBVOCctrlPD | `art_CTRL_PD` |
| | art_CTRL_FUT | CTRL_FUT − CTRL_FUT_fBVOCctrlFUT | `art_CTRL_FUT` |
| | δ_PD, δ_FUT | art_LCC_P − art_CTRL_P (VirtualRun `LCC_P_delta`) | `delta_PD`, `delta_FUT` |

**`LCC_FUT_fBVOClccFUT` is a design-B stand-in, to be replaced:** until the run (24g) is postprocessed it is LCC_FUT − art_CTRL_FUT = LCC_FUT − CTRL_FUT + CTRL_FUT_fBVOCctrlFUT (assumes art(LCC land) = art(CTRL land)). Rows/titles using it say "(design B)". To replace it: `forcing_maps.LCC_FUT_FBVOCLCCFUT_DESIGN_B = False`, then rerun `analysis/`.

## Layout (since 2026-11-16, user)

```
results/figures/<notebook stem>/            figures that mix categories (e.g. six-map decomposition, PD–FUT attribution)
results/figures/<notebook stem>/a_interactive/
results/figures/<notebook stem>/b_fBVOC/
results/figures/<notebook stem>/c_non-BVOC/
results/figures/artefacts/d_artefacts/      proper artefacts of every notebook: art_LCC_P, art_CTRL_P, δ_P
results/figures/artefacts/design-B/         design B (analysis/artefact-corrected-split.ipynb)
results/tables/…                            same structure; tables/logs/ = run scripts and logs
```

Code: `forcing_maps.set_output_notebook("<stem>")` in each notebook's setup cell sets `FIGURE_DIR`/`TABLE_DIR` (notebook folder) and `FIG_CATEGORY`/`TABLE_CATEGORY` (a_/b_/c_ subfolders, artefacts → `artefacts/d_artefacts/`). Notebooks: `radiative_forcing`, `radiative-forcing-decomposition` (six-map figures, design A, + design-A split budget), `bvoc-soa-cloud-interactions`, `biogeophysical-hydro`, `land-carbon-water`, `timeseries-responses`, `pd-fut-attribution`, `cumulative_radiative_decomposition`, `simulation-contrasts`, `megan-lmdi-attribution-maps`, `megan-lmdi-vs-approx`, `megan_factor_maps`. Not moved: `fut-fbvoc-emission-source-choice` (still writes to `analysis/fut-fbvoc-emission-source-choice_outputs/`).

**Artefacts (user 2026-11-16):** art_LCC_P = LCC_P − LCC_P_fBVOClccP (own emissions prescribed; before: LCC_P − LCC_P_fBVOCctrlP, which = BVOC_A + artefact), art_CTRL_P = CTRL_P − CTRL_P_fBVOCctrlP, δ_P = art_LCC_P − art_CTRL_P. Design A is the default: total [LCC − CTRL]_P = non-BVOC + BVOC_A + δ_P.

**Titles (user 2026-11-16, option 1):** no calendar years in figure titles (the years label the nudging winds of a free-running present-day run); map subtitles say "Maps: N-year mean". File names keep `_<y0>_<y1>`.

**Forcing decomposition files:** `<LCCP>_fBVOC<E>_forcing_decomposition_<band>_<y0>_<y1>[_<scale>]_<design>.png`, e.g. `LCCFUT_fBVOClccPD_forcing_decomposition_NET_2001_2025_split6-2_designA.png`; `LCCFUT-CTRLPD_fBVOCctrlPD_…` = LCC_FUT − CTRL_PD.

## Old sets (not regenerated)

| Folder | What |
|---|---|
| `figures-2001-2014/`, `tables-2001-2014/` | New chain, 2001–2014 period (`*_2001_2014`), same layout as `figures/` and `tables/`. Moved out 2026-11-09. |
| `figures-pre-reorg-20261108/`, `tables-pre-reorg-20261108/` | Layout 2026-11-04 → 2026-11-08: `LCC-CTRL/`, `CTRL_FUT-CTRL_PD/`, `fBVOC/{pre-artefact-correction, artefact-design-B}/`, `timeseries/`; tables `pre-artefact-correction/`, `artefact-design-B/`, flat `*_2001_2014.csv` and the older `*_2001_2009.csv`. New chain, but contrasts LCC − LCC_fBVOC* (uncorrected) etc. |
| `figures-2001-2014-all-bvoc-pre-co2-fix/`, `tables-2001-2014-all-bvoc-pre-co2-fix/` | Old spin-up chain (before the CO₂ fix). |
| `figures-pre-co2-fix/`, `figures-def-transparent/` | Older figure sets. |
