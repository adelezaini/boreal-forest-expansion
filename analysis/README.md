# analysis/

Paper notebooks. Plotting code: `src/boreal_forest_expansion/plotting/forcing_maps.py`. Figures go to `results/figures/`, tables to `results/tables/`.
Run with `$PY results/tables/logs/run_nb_inplace.py analysis/<nb>.ipynb` (outputs saved in the notebook).

| Notebook | Content |
|---|---|
| `radiative_forcing.ipynb` | 6-panel forcing summary; Ghan decomposition (total + ARI + cloud + clear-clean) per contrast (LCC−CTRL, LCC−fBVOC, fBVOC−CTRL), annual and seasonal |
| `bvoc-soa-cloud-interactions.ipynb` | BVOC → SOA → aerosol → cloud context maps; contrast grids (rows = contrasts, columns = variables) |
| `biogeophysical-hydro.ipynb` | Hydrology, snow/albedo, surface energy, FSDS split contrast grids; land water budget P − ET − R − ΔTWS |
| `pd-fut-attribution.ipynb` | Why the response reverses PD → FUT: radiative budget of LCC−CTRL / fBVOC−CTRL / LCC−fBVOC, emission & LAI origin (modified vs unmodified, early vs late), seasonal BVOC→SOA→cloud→SW chain, baselines and % changes, paired years, PD source boxes |
| `megan_factor_maps.ipynb` | MEGAN emission/activity factor maps |
| `test_significance_marking.ipynb` | Choice of the significance marking style |

`forcing_maps.ipynb` was split into the first two notebooks (2026-10-25). Its first-round figures are in `results/figures/first-round/`.
