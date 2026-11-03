# analysis/

Paper notebooks. Plotting code: `src/boreal_forest_expansion/plotting/forcing_maps.py`. Figures go to `results/figures/`, tables to `results/tables/`.
Run with `$PY results/tables/logs/run_nb_inplace.py analysis/<nb>.ipynb` (outputs saved in the notebook).
Variables in each figure (subtitle, variable, category, calculation): `PLOTTED_VARIABLES.md`.

| Notebook | Content |
|---|---|
| `radiative_forcing.ipynb` | 6-panel forcing summary; Ghan decomposition (total + ARI + cloud + clear-clean) per contrast (LCC−CTRL, LCC−fBVOC; FUT also CTRL_FUT−CTRL_PD), annual and seasonal |
| `bvoc-soa-cloud-interactions.ipynb` | BVOC → SOA → aerosol → cloud context maps; contrast grids (rows = contrasts, columns = variables); §3 cloud types: low/mid/high/total cloud + LWP/IWP grids (`contrast_grid_cloud_types[_JJA]_*`), seasonal lines (`seasonal_cloud_types_{fbvoc,ctrl}_*`), zonal-mean profiles (`cloud_profile_{ANN,JJA}_*`) |
| `biogeophysical-hydro.ipynb` | Hydrology, snow/albedo, surface energy, FSDS split contrast grids; land water budget P − ET − R − ΔTWS |
| `pd-fut-attribution.ipynb` | Why the response reverses PD → FUT: radiative budget of LCC−CTRL / LCC−fBVOC (+ CTRL_FUT−CTRL_PD for FUT), emission & LAI origin (modified vs unmodified, early vs late), seasonal BVOC→SOA→cloud→SW chain, baselines and % changes, paired years, PD source boxes |
| `megan_factor_maps.ipynb` | MEGAN emission/activity factor maps; attribution residual explained in `MEGAN_ATTRIBUTION.md` |
| `FBVOC_ARTEFACT.md` | fBVOC prescription artefact: evidence, cause, designs A/B (formulas), decision (matched baseline) and first new-chain numbers |
| `fut-fbvoc-emission-source.ipynb` | FUT fBVOC with CTRL_PD vs CTRL_FUT emissions: LCC_FUT − fBVOCctrlPD, LCC_FUT − fBVOCctrlFUT, fBVOCctrlFUT − fBVOCctrlPD (emissions, radiative budget, context maps, Ghan, seasonal chain); figures in `results/figures/` |
| `timeseries-responses.ipynb` | Yearly time series 2001–2014 (2000 = spin-up, dropped) of the 9 context-map variables + NET Ghan terms, per contrast (Total PD/FUT, CTRL_FUT − CTRL_PD, artefact-corrected BVOC PD / FUT ctrlPD / FUT ctrlFUT); two lines: global and modified cells (ISOP, MTERP) / ≥45°N (others); §3 absolute yearly values of every nudged run (PD/FUT × global/regional, one line per run); new chain; figures `results/figures/timeseries/`, tables `results/tables/timeseries_{regional_means,absolute}_2001_2014.csv` |
| `cumulative_radiative_decomposition.ipynb` | Cumulative net TOA response (P1 → P4 of the supervisor's overview): D1 CTRL_FUT − CTRL_PD, D2 LCC_FUT_fBVOCctrlFUT − CTRL_FUT (BGP), D3 LCC_FUT − LCC_FUT_fBVOCctrlFUT (BVOC); ≥45°N and modified cells, mean ± 95 % CI over years; figures in `results/figures/cumulative-radiative-decomposition/`, table `results/tables/cumulative_radiative_decomposition_2001_2014.csv` |

**Current set (2026-10-28):** 2001–2014, all-species fBVOC (`LCC_*_fBVOCctrlPD`), CTRL `-20261023`, LCC `-20261005`, old spin-up chain; outputs named `*_2001_2014`; figures that involve an fBVOC run name it (`PD_fBVOCctrlPD_…`, `FUT_fBVOCctrlPD_…`, `FUT_fBVOCctrlFUT_…`, Ghan `LCC-fBVOCctrlPD`). The 2001–2009 `_IM` outputs (`*_2001_2009`) are kept. The fBVOC − CTRL contrast was dropped (user 2026-10-28).

**Artefact correction (2026-11-03):** outputs with an uncorrected fBVOC contrast (69 figures, the cumulative-decomposition folder, all 8 `*_2001_2014` tables) moved to `results/{figures,tables}/pre-artefact-correction/`; pure LCC − CTRL / CTRL_FUT − CTRL_PD outputs stay. Corrected contrasts: `forcing_maps.VirtualRun`, `corrected_fbvoc`, `CORRECTED_PAIRS` (see `results/README.md`). The notebooks above still show the uncorrected figures in their saved outputs.

`forcing_maps.ipynb` was split into the first two notebooks (2026-10-25). Its first-round figures are in `results/figures/first-round/`.
