# results/

Layout since 2026-11-04 (user). New chain, 2001–2014 (`*_2001_2014`) unless stated.

## figures/ (one folder per contrast)

| Folder | What |
|---|---|
| `figures/LCC-CTRL/` | LCC − CTRL (total effect of the forest expansion), incl. the CTRL baseline `seasonal_cloud_types_ctrl`. No fBVOC run, no artefact. |
| `figures/CTRL_FUT-CTRL_PD/` | CTRL_FUT − CTRL_PD (future background). |
| `figures/fBVOC/` | Fixed-BVOC contrasts with the **design-A** artefact correction (planned; empty until then). |
| `figures/fBVOC/pre-artefact-correction/` | **Uncorrected** fBVOC contrasts (LCC − LCC_fBVOC*, fBVOC − fBVOC, cumulative decomposition D2/D3), incl. mixed figures that also show LCC − CTRL. |
| `figures/fBVOC/artefact-design-B/` | Design-B artefact-corrected split (`analysis/artefact-corrected-split.ipynb`; was `figures/artefact-corrected-split/`). |
| `figures/megan_factors/` | `analysis/megan_factor_maps.ipynb`, `diagnostics/3_megan-exact-split-test/lake_fix_effect.ipynb`. |
| `figures/timeseries/` | `analysis/timeseries-responses.ipynb`. |

Code: `forcing_maps.figure_path(figdir, name)`. With `figdir=None` (the default of every `make_*` function) a figure goes by the contrast tag in its name: `CTRLFUT-CTRLPD` → `CTRL_FUT-CTRL_PD/`, `LCC-CTRL` (or `seasonal_cloud_types_ctrl`) → `LCC-CTRL/`, everything else → `fBVOC/pre-artefact-correction/`. Folder constants: `FIG_LCC_CTRL`, `FIG_BACKGROUND`, `FIG_FBVOC`, `FIG_FBVOC_PRE`, `FIG_FBVOC_B`.

## tables/ (flat)

| Folder | What |
|---|---|
| `tables/` | Design-A tables (planned) and everything without an fBVOC contrast (e.g. `timeseries_*`). |
| `tables/pre-artefact-correction/` | Tables with an uncorrected fBVOC contrast (`TABLE_FBVOC_PRE`). |
| `tables/artefact-design-B/` | `analysis/artefact-corrected-split.ipynb` (`TABLE_FBVOC_B`; was `tables/artefact-corrected-split/`). |
| `tables/logs/` | Notebook run scripts (`run_nb_inplace.py`) and run logs. |
| `tables/*_2001_2009.csv` | Older sets (ISOP/MTERP-only `_IM` runs, first rounds). |

## Old sets

| Folder | What |
|---|---|
| `figures-2001-2014-all-bvoc-pre-co2-fix/`, `tables-2001-2014-all-bvoc-pre-co2-fix/` | Old spin-up chain (before the CO₂ fix). The tables folder was `tables/2001-2014-all-bvoc-pre-co2-fix/` until 2026-11-04. |
| `figures-pre-co2-fix/`, `figures-def-transparent/` | Older figure sets. |
