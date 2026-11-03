# results/

| Folder | What |
|---|---|
| `figures/`, `tables/` (top level) | Current outputs of the `analysis/` notebooks, new chain, 2001–2014 (`*_2001_2014`). Since 2026-11-03 only the contrasts **without** an fBVOC run (LCC − CTRL, CTRL_FUT − CTRL_PD): no prescription artefact. |
| `figures/pre-artefact-correction/`, `tables/pre-artefact-correction/` | New chain, 2001–2014, outputs that contain an **uncorrected** fBVOC contrast (LCC − LCC_fBVOC, fBVOC − fBVOC, cumulative decomposition D2/D3), incl. mixed figures/tables that also show LCC − CTRL. Moved 2026-11-03, names unchanged. Superseded by the artefact-corrected outputs (design B, `analysis/FBVOC_ARTEFACT.md`). |
| `figures/<topic>/`, `tables/<topic>/` | Artefact-corrected analyses, one folder per notebook: `artefact-corrected-split`, `fut-emission-attribution`, `artefact-robustness`, `fut-emission-source`. |
| `figures/megan_factors/` | `analysis/megan_factor_maps.ipynb` (no fBVOC run involved). |
| `figures-2001-2014-all-bvoc-pre-co2-fix/`, `tables/2001-2014-all-bvoc-pre-co2-fix/` | Old spin-up chain (before the CO₂ fix). |
| `tables/*_2001_2009.csv`, `figures2-4`, `figures-*` | Older sets (ISOP/MTERP-only `_IM` runs, first rounds). |
| `tables/logs/` | Notebook run scripts (`run_nb_inplace.py`) and run logs. |
