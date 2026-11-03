# Plotted variables: what each figure panel shows and how it is calculated

Code: `src/boreal_forest_expansion/plotting/forcing_maps.py`.
Input: the processed files `data/processed-data/postprocessing/<ALIAS>_<atm|lnd>_<CATEGORY>_2001-2014.nc` (see `postprocess/POSTPROCESSING.md`). They are monthly means; spin-up year 2000 is already dropped.

- **Category** = the processed-file category (`atm`/`lnd` + name) the variable is read from.
- **Long name** = the `long_name` attribute in the history file, verbatim (typos included). For secondary variables it is the long name set in `postprocess/derived.py`.

## 1. Common steps for every map panel

| Step | What | Code |
|---|---|---|
| 1. Yearly means | Each calendar year (2001–2014, n = 14) is averaged from its monthly means, **weighted by month length** in days. Seasonal panels (e.g. MAM) use only those months of each year. DJF = Jan + Feb + Dec of the **same** year. | `annual_mean` |
| 2. Paired differences | `case1 − case2` for each year, e.g. LCC_PD 2003 − CTRL_PD 2003. The two runs must have identical time axes. | `yearly_difference` |
| 3. Map | Mean of the 14 yearly differences. | `_plot_panel` |
| 4. Significance | Two-sided one-sample t-test of the 14 yearly differences in each cell, then Benjamini–Hochberg FDR at α = 0.10, applied over the cells ≥ 45°N. **Grey hatching = not significant.** | `analysis/stats.py` |
| 5. Number under the map | Area-weighted mean over 45–90°N of each yearly difference (cos-latitude weights), then the mean of the 14 values ± 95 % t-interval half-width (13 degrees of freedom). | `regional_mean_interval` |
| 6. Colour scale | Symmetric, ± the 98th percentile of \|map\| unless the panel fixes it. Five ticks: ±vmax floored to 2 significant digits, ±half of that, 0. | `symmetric_vmax`, `_five_ticks` |

**Note on the area mean (step 5):**
- Land-model (`lnd`) fields are NaN over ocean, so their mean is a **land** mean.
- Partly-land coastal cells count with their full cell area, not area × land fraction. The line charts (§7) do weight by land fraction.

**Contrasts (rows of the grids):**

| Grid | Rows (case1 − case2) |
|---|---|
| LCC-CTRL | LCC_PD − CTRL_PD; LCC_FUT − CTRL_FUT; LCC_FUT − CTRL_PD; CTRL_FUT − CTRL_PD |
| LCC-fBVOC | LCC_PD − LCC_PD_fBVOCctrlPD; LCC_FUT − LCC_FUT_fBVOCctrlPD; LCC_FUT − LCC_FUT_fBVOCctrlFUT; LCC_FUT_fBVOCctrlFUT − LCC_FUT_fBVOCctrlPD (emission source, = row 2 − row 3) |

Current set (2001–2014, all-BVOC, old spin-up chain): `LCC_PD_fBVOC` = `LCC_PD_fBVOCctrlPD`, `LCC_FUT_fBVOC` = `LCC_FUT_fBVOCctrlPD` (all 19 MEGAN species from CTRL_PD). The fBVOC − CTRL contrast is no longer computed; CTRL_FUT − CTRL_PD is row 4 of LCC-CTRL and an extra Ghan/budget contrast (FUT). `LCC_FUT_fBVOCctrlFUT` is compared in `fut-fbvoc-emission-source.ipynb`. The 2001–2009 `_IM` set: `*_2001_2009` figures.

## 2. Ghan decomposition terms (used in §3 and §4)

`{B}` = band NET, SW or LW. Sign: positive = downward (energy into the system).
`*_DRF` = an extra radiation call with aerosol optical depth set to 0 ("clean"); `*CDRF` = clean and clear-sky.

| Subtitle | Variable | Category | Long name | Calculation (one run; the maps show the difference between two runs) |
|---|---|---|---|---|
| F<sub>TOTAL</sub> | `{B}_toa` | atm RADIATIVE | Net flux at top of model (down positive) | NET `FSNT − FLNT`; SW `FSNT`; LW `−FLNT` |
| F<sub>AEROSOL-DIRECT</sub> | `{B}_dir` | atm RADIATIVE | Net aerosol direct radiative effect (all-sky) | all-sky flux − clean flux (AOD = 0): SW `FSNT − FSNT_DRF`; LW `−(FLNT − FLNT_DRF)` |
| F<sub>CLOUD</sub> | `{B}_cloud` | atm RADIATIVE | Net cloud radiative effect without aerosol (clean) | clean flux − clean clear-sky flux: SW `FSNT_DRF − FSNTCDRF`; LW `−(FLNT_DRF − FLNTCDRF)` |
| F<sub>REST</sub> | `{B}_rest` | atm RADIATIVE | Net flux, clear-sky and aerosol-free | clean clear-sky flux: SW `FSNTCDRF`; LW `−FLNTCDRF` |

F<sub>TOTAL</sub> = F<sub>AEROSOL-DIRECT</sub> + F<sub>CLOUD</sub> + F<sub>REST</sub>, exactly (checked in the notebook; closure ≤ 2e-5 W m⁻²).
Files made before 2026-10-28 call the last two terms `{B}_cre_clean` and `{B}_clearclean`. `open_class` renames them on loading.

**Model inputs:**

| Variable | Long name |
|---|---|
| `FSNT` | Net solar flux at top of model |
| `FLNT` | Net longwave flux at top of model |
| `FSNT_DRF` | Total column absorbed solar flux (DIRind) |
| `FLNT_DRF` | Total column longwave flux (DIRind) |
| `FSNTCDRF` | Clear sky total column absorbed solar flux (DIRind) |
| `FLNTCDRF` | Clear sky total column longwave flux (DIRind) |

## 3. Radiative forcing summary (`radiative_forcing.ipynb`, `make_forcing_summary_figure`)

Six panels per band. In the "Contrast" column, LCC − CTRL and LCC − fBVOC are both taken within the same period.

| Subtitle | Variable | Category | Long name | Contrast | Calculation |
|---|---|---|---|---|---|
| ALBEDO / SW CLEAR-SKY FORCING | `SFC_ALBEDO_FORCING_CLEAR` from `FSDSC`, `FSNSC` | atm RADIATIVE | FSDSC: Clearsky downwelling solar flux at surface; FSNSC: Clearsky net solar flux at surface | LCC − CTRL | Proxy, monthly: `−FSDSC₂ · (α₁ − α₂)`, with `α = (FSDSC − FSNSC)/FSDSC` (only where FSDSC > 1 W m⁻²; months without sunlight = 0). Then the yearly mean. Surface proxy, not a TOA term. |
| TOTAL RADIATIVE FORCING ({B}) | `{B}_toa` | atm RADIATIVE | see §2 | LCC − CTRL | F<sub>TOTAL</sub> |
| BVOC-RELATED FORCING ({B}) | `{B}_toa` | atm RADIATIVE | see §2 | LCC − fBVOC | F<sub>TOTAL</sub> |
| BVOC-SOA-CLOUD FORCING ({B}) | `{B}_cloud` | atm RADIATIVE | see §2 | LCC − fBVOC | F<sub>CLOUD</sub> |
| BVOC-DIRECT SOA FORCING ({B}) | `{B}_dir` | atm RADIATIVE | see §2 | LCC − fBVOC | F<sub>AEROSOL-DIRECT</sub> |
| BVOC CHEMISTRY / RESIDUAL FORCING ({B}) | `{B}_rest` | atm RADIATIVE | see §2 | LCC − fBVOC | F<sub>REST</sub> |

## 4. Ghan decomposition maps (`radiative_forcing.ipynb`, `make_ghan_figure`)

- Panels F<sub>TOTAL</sub>, F<sub>AEROSOL-DIRECT</sub>, F<sub>CLOUD</sub>, F<sub>REST</sub> (§2).
- One figure per contrast (LCC−CTRL, LCC−fBVOC, fBVOC−CTRL) × band × period.
- Each comes as an annual figure and a seasonal one (rows DJF/MAM/JJA/SON).

## 5. BVOC/SOA/cloud panels (`bvoc-soa-cloud-interactions.ipynb`)

Used by the context maps (`make_context_maps_figure`: LCC_X − LCC_X_fBVOC, 3 columns) and the context grids (`make_contrast_grid_figure(..., CONTEXT_PANELS, "context")`).

| Subtitle | Variable | Category | Long name | Calculation | Units |
|---|---|---|---|---|---|
| ISOPRENE EMISSIONS | `SFISOP` | atm BVOC | ISOP surface flux | yearly mean × 10⁶ × 86400 (kg m⁻² s⁻¹ → mg m⁻² d⁻¹). `SF*` = all emissions the atmosphere receives (MEGAN or prescribed). | mg m⁻² d⁻¹ |
| MONOTERPENE EMISSIONS | `SFMTERP` | atm BVOC | MTERP surface flux | as isoprene | mg m⁻² d⁻¹ |
| TOTAL SOA BURDEN | `SOA_cb` | atm SOA | SOA column burden (A1 + NA) | column of `SOA_A1` + `SOA_NA` (long names "SOA_A1 concentration", "SOA_NA concentration", kg kg⁻¹), computed in postprocessing, × 10⁶ (kg → mg). Interstitial only. | mg m⁻² |
| AEROSOL NUMBER CONCENTRATION | `N_AER` | atm SOA | Aerosol number concentration | lowest model level; unit label corrected in postprocessing (model writes "unitless") | cm⁻³ |
| LIQUID CLOUD FRACTION | `FCTL` | atm CLOUDPROP | Fractional occurrence of cloud top liquid | model output | fraction |
| CLOUD DROPLET EFFECTIVE RADIUS | `ACTREL` → `ACTREL_incld` | atm CLOUDPROP | Average Cloud Top droplet effective radius | in-cloud: `annual_mean(ACTREL) / annual_mean(FCTL)`, NaN where the mean FCTL < 0.01. CAM writes ACTREL = r_eff × FCTL at the cloud-top level. | µm |
| CLOUD DROPLET NUMBER CONCENTRATION | `ACTNL` → `ACTNL_incld` | atm CLOUDPROP | Average Cloud Top droplet number | `annual_mean(ACTNL) / annual_mean(FCTL)` × 10⁻⁶ (m⁻³ → cm⁻³), NaN where FCTL < 0.01. CAM writes ACTNL = in-cloud droplet number concentration × FCTL at cloud top. | cm⁻³ |
| LIQUID WATER PATH | `TGCLDLWP` | atm CLOUDPROP | Total grid-box cloud liquid water path | × 10³ (kg → g) | g m⁻² |
| EVAPOTRANSPIRATION | `QFLX_EVAP_TOT` | lnd ET | qflx_evap_soi + qflx_evap_can + qflx_tran_veg | × 86400 (mm s⁻¹ → mm d⁻¹), land only | mm d⁻¹ |

**Post-CO₂-fix runs:** these runs also write CAM's own SOA column burdens: `cb_SOA_A1`, `cb_SOA_NA` and the cloud-borne `cb_SOA_A1_OCW`, `cb_SOA_NA_OCW`. CAM computes them every timestep, so the within-month covariance is included. Ready in the code but not used yet:
- `cbSOA_mgm2` = `cb_SOA_A1 + cb_SOA_NA` (interstitial)
- `cbSOA_all_mgm2` = the same + cloud-borne

TOTAL SOA BURDEN switches to them once all runs of a contrast are on the new chain (`CLAUDE.md`, run-version step 7).

### Cloud types (§3 of the notebook; `CLOUD_TYPE_PANELS`, `make_monthly_chain_figure`, `make_cloud_profile_figure`)

Maps: `make_contrast_grid_figure(..., CLOUD_TYPE_PANELS, "cloud_types[_JJA]")`, annual and JJA. Seasonal lines: `MONTHLY_FIELDS` of the same names. Low + mid + high ≠ total (random overlap).

| Subtitle | Variable | Category | Long name | Calculation | Units |
|---|---|---|---|---|---|
| TOTAL CLOUD | `CLDTOT` | atm CLOUDPROP | Vertically-integrated total cloud | model output | fraction |
| LOW CLOUD | `CLDLOW` | atm CLOUDPROP | Vertically-integrated low cloud | model output, p > 700 hPa | fraction |
| MID-LEVEL CLOUD | `CLDMED` | atm CLOUDPROP | Vertically-integrated mid-level cloud | model output, 400–700 hPa | fraction |
| HIGH CLOUD | `CLDHGH` | atm CLOUDPROP | Vertically-integrated high cloud | model output, p < 400 hPa | fraction |
| LIQUID WATER PATH | `TGCLDLWP` → `TGCLDLWP_gm2` | atm CLOUDPROP | Total grid-box cloud liquid water path | × 10³ (kg → g) | g m⁻² |
| ICE WATER PATH | `TGCLDIWP` → `TGCLDIWP_gm2` | atm CLOUDPROP | Total grid-box cloud ice water path | × 10³ (kg → g) | g m⁻² |
| SW cloud term (lines only) | `SW_cloud` | atm RADIATIVE | Ghan SW cloud term (clean sky) | see §2 | W m⁻² |

Vertical structure (`make_cloud_profile_figure`, `PROFILE_FIELDS`): zonal mean over all longitudes, 45–90°N, 1000–150 hPa (`lev`, hybrid level midpoints in hPa), yearly (or JJA) means, case1 − case2 averaged over years; hatched = NOT significant, FDR (α = 0.10) on the paired yearly t-test within each panel (same `/////` look as the maps).

| Subtitle | Variable | Long name | Calculation | Units |
|---|---|---|---|---|
| CLOUD FRACTION | `CLOUD` | Cloud fraction | model output | fraction |
| CLOUD LIQUID (grid box) | `CLDLIQ` | Grid box averaged cloud liquid amount | × 10⁶ | mg kg⁻¹ |
| CLOUD ICE (grid box) | `CLDICE` | Grid box averaged cloud ice amount | × 10⁶ | mg kg⁻¹ |

## 6. Biogeophysical and hydrology grids (`biogeophysical-hydro.ipynb`, `make_contrast_grid_figure`)

### hydro (`HYDRO_PANELS`)
| Subtitle | Variable | Category | Long name | Calculation | Units |
|---|---|---|---|---|---|
| SURFACE SHORTWAVE DOWN | `FSDS` | atm RADIATIVE | Downwelling solar flux at surface | model output, all-sky | W m⁻² |
| PRECIPITATION | `PRECC + PRECL` | atm METEO | Convective precipitation rate (liq + ice); Large-scale (stable) precipitation rate (liq + ice) | sum × 10³ × 86400 (m s⁻¹ → mm d⁻¹) | mm d⁻¹ |
| EVAPOTRANSPIRATION | `QFLX_EVAP_TOT` | lnd ET | qflx_evap_soi + qflx_evap_can + qflx_tran_veg | × 86400 | mm d⁻¹ |
| TOTAL RUNOFF | `QRUNOFF` | lnd HYDRO | total liquid runoff not including correction for land use change | × 86400 | mm d⁻¹ |
| SNOWMELT | `QSNOMELT` | lnd HYDRO | snow melt rate | × 86400 | mm d⁻¹ |
| TOTAL WATER STORAGE | `TWS` | lnd HYDRO | total water storage | model output | mm |
| SOIL WATER 0–10 cm | `SOILWATER_10CM` | lnd LAND | soil liquid water + ice in top 10cm of soil (veg landunits only) | model output | kg m⁻² |
| LATENT HEAT FLUX | `LHFLX` | atm METEO | Surface latent heat flux | model output, up positive, grid box (land + ocean) | W m⁻² |
| SENSIBLE HEAT FLUX | `SHFLX` | atm METEO | Surface sensible heat flux | as LHFLX | W m⁻² |
| LOW CLOUD | `CLDLOW` | atm CLOUDPROP | Vertically-integrated low cloud | model output | fraction |

### snow_albedo (`SNOW_ALBEDO_PANELS`)
| Subtitle | Variable | Category | Long name | Calculation | Units |
|---|---|---|---|---|---|
| SNOW COVER | `FSNO` | lnd SNOW | fraction of ground covered by snow | model output | fraction |
| SNOW COVER (MAM) | `FSNO` | lnd SNOW | fraction of ground covered by snow | March–May mean only | fraction |
| SNOW WATER EQUIVALENT | `H2OSNO` | lnd SNOW | snow depth (liquid water) | model output | mm |
| SNOW PERSISTENCE | `SNOW_PERSISTENCE` | lnd SNOW | Length of time of continuous snow cover (nat. veg. landunits only) | yearly mean ÷ 86400 (s → days). **Suspect:** values of thousands of days seen on 2026-10-28; the yearly mean of a running length is probably the wrong aggregation. Not checked yet. | days |
| CANOPY SNOW | `SNOCAN` | lnd SNOW | intercepted snow | model output | mm |
| SURFACE ALBEDO (MAM) | `FSR / FSDS` (`ALBEDO`) | lnd ENERGY | FSR: reflected solar radiation; FSDS: atmospheric incident solar radiation | `annual_mean(FSR) / annual_mean(FSDS)` over March–May (a ratio of means, not a mean of monthly ratios), NaN where FSDS < 1 W m⁻² | – |
| LEAF AREA INDEX | `TLAI` | lnd LAND | total projected leaf area index | model output | m² m⁻² |

### surface_energy (`SURFACE_ENERGY_PANELS`)
| Subtitle | Variable | Category | Long name | Calculation | Units |
|---|---|---|---|---|---|
| NET SURFACE SHORTWAVE | `FSNS` | atm RADIATIVE | Net solar flux at surface | model output | W m⁻² |
| SURFACE LONGWAVE DOWN | `FLDS` | atm RADIATIVE | Downwelling longwave flux at surface | model output | W m⁻² |
| SURFACE TEMPERATURE | `TS` | atm METEO | Surface temperature (radiative) | model output | K |
| 2 m TEMPERATURE | `TREFHT` | atm METEO | Reference height temperature | model output | K |
| LATENT HEAT FLUX | `LHFLX` | atm METEO | Surface latent heat flux | model output, up positive | W m⁻² |
| SENSIBLE HEAT FLUX | `SHFLX` | atm METEO | Surface sensible heat flux | model output, up positive | W m⁻² |
| BOWEN RATIO | `SHFLX / LHFLX` (`BOWEN`) | atm METEO | (ratio of the two above) | `annual_mean(SHFLX) / annual_mean(LHFLX)`, NaN where \|LHFLX\| < 5 W m⁻² | – |

### fsds_split (`FSDS_SPLIT_PANELS`)
| Subtitle | Variable | Category | Long name | Calculation | Units |
|---|---|---|---|---|---|
| FSDS (ALL-SKY) | `FSDS` | atm RADIATIVE | Downwelling solar flux at surface | model output | W m⁻² |
| FSDS CLEAR-SKY | `FSDSC` | atm RADIATIVE | Clearsky downwelling solar flux at surface | model output (no clouds, with aerosol) | W m⁻² |
| FSDS CLOUD PART | `FSDS − FSDSC` (`FSDS_cloud`) | atm RADIATIVE | (difference of the two above) | difference of yearly means | W m⁻² |
| FSDS AEROSOL PART | `FSDS − FSDS_DRF` (`FSDS_aer`) | atm RADIATIVE | FSDS_DRF: SW downelling flux at surface (with AOD = 0) | difference of yearly means | W m⁻² |
| FSDS CLEAR-CLEAN | `FSDSCDRF` | atm RADIATIVE | SW downwelling clear sky flux at surface (with AOD = 0) | model output (no clouds, no aerosol) | W m⁻² |

The fsds_split panels are **not** an additive split: CLOUD PART + AEROSOL PART + CLEAR-CLEAN ≠ FSDS, because the cloud part uses `FSDSC`, which still contains aerosol.

## 7. Percent-change maps (`pd-fut-attribution.ipynb`, `make_percent_change_figure`)

These show `100 × (LCC − LCC_fBVOC) / mean(LCC_fBVOC)` for each year. Cells where the baseline is below a minimum are blank. Significance is tested on the yearly % values. Long names as in §5.

| Subtitle | Variable | Category | Minimum baseline |
|---|---|---|---|
| SOA BURDEN | `SOA_cb` (mg m⁻²) | atm SOA | 0.05 mg m⁻² |
| AEROSOL NUMBER | `N_AER` | atm SOA | 1 cm⁻³ |
| IN-CLOUD DROPLET NUMBER | `ACTNL_incld` | atm CLOUDPROP | 1 cm⁻³ |
| IN-CLOUD EFFECTIVE RADIUS | `ACTREL_incld` | atm CLOUDPROP | 1 µm |
| LIQUID WATER PATH | `TGCLDLWP` (g m⁻²) | atm CLOUDPROP | 5 g m⁻² |

## 8. Line and bar charts (`pd-fut-attribution.ipynb`, `biogeophysical-hydro.ipynb`)

**Regional means for these charts:**
- They use true cell area: CAM from `gw`, CLM from `area`.
- CLM fields are weighted by area × land fraction.
- Regions: `≥45°N`; `modified cells` (LCC-modified cells, `diagnostics/check-simulation-equilibrium/lcc-modified-cells/modified_cells.nc`); `unmodified land ≥45°N`; and four source boxes (Alaska/W Canada, E Canada, Europe, Siberia).

**Variables not listed in §2–§6:**

| Variable | Category | Long name |
|---|---|---|
| `cb_SOA_LV`, `cb_SOA_SV` | atm SOA | cb_SOA_LV in column; cb_SOA_SV in column (gas-phase low/semi-volatile SOA precursors) |
| `NUCLRATE` | atm SOA | Nucleation rate (lowest level) |
| `CCN3` | atm SOA | CCN concentration at S=0.1% |
| `SOLIN` | atm RADIATIVE | Solar insolation |
| `RAIN`, `SNOW` | lnd HYDRO | atmospheric rain / snow, after rain/snow repartitioning based on temperature |
| `QRUNOFF_TO_COUPLER` | lnd HYDRO | total liquid runoff sent to coupler (includes corrections for land use change) |
| `QRUNOFF_ICE_TO_COUPLER` | lnd HYDRO | total ice runoff sent to coupler (includes corrections for land use change) |
| `GAMMA_isoprene` | lnd BVOC | total VOC activity factor: isoprene |
| `GAMMAL` | lnd BVOC | LAI activity factor (all MEGAN compounds) |

| Figure | Variables | Calculation |
|---|---|---|
| `radiative_budget_3contrasts`, `paired_years_{NET,SW,LW}` | F<sub>TOTAL</sub>, F<sub>AEROSOL-DIRECT</sub>, F<sub>CLOUD</sub>, F<sub>REST</sub> (`{B}_toa/dir/cloud/rest`) + albedo proxy (atm RADIATIVE) | yearly regional means for LCC−CTRL, LCC_fBVOC−CTRL and LCC−LCC_fBVOC. Checked: the terms add up to the total, and LCC−CTRL = (fBVOC−CTRL) + (LCC−fBVOC). |
| `emission_origin_monthly` | `SFISOP_Tg`, `SFMTERP_Tg` (**regional totals** in Tg month⁻¹ = flux × cell area × days × 86400 × 10⁻⁹); `TLAI`; `GAMMA_isoprene`, `GAMMAL` (grid-cell area means) | monthly regional mean (or total) differences; early (2001–04) vs late (2006–09) years |
| `seasonal_chain_bvoc_soa_cloud_sw` | `SFISOP`, `SFMTERP` (mg m⁻² d⁻¹), `SOA_cb` (mg m⁻²), `N_AER`, `ACTNL_incld`, `ACTREL_incld`, `TGCLDLWP` (g m⁻²), `SW_cloud` (SW F<sub>CLOUD</sub>); context line `SOLIN` | monthly regional mean of LCC − LCC_fBVOC, mean ± 95 % CI over years. Here the in-cloud values are monthly ratios `ACTNL/FCTL` (FCTL ≥ 0.01), not ratios of yearly means. |
| `pd_mechanism_source_boxes` | `SFISOP`, `SFMTERP`, `cb_SOA_LV`, `cb_SOA_SV` (mg m⁻²), `SOA_cb`, `N_AER`, `NUCLRATE` (cm⁻³ s⁻¹) | as above, PD only, LCC−LCC_fBVOC and LCC−CTRL, in the four source boxes |
| `water_budget_*` | `RAIN + SNOW` (P), `QFLX_EVAP_TOT` (ET), `QRUNOFF_TO_COUPLER` (R_liq), `QRUNOFF_ICE_TO_COUPLER` (R_ice), `TWS` | yearly means × seconds per year → mm yr⁻¹. ΔTWS = TWS(Dec y) − TWS(Dec y−1), so 2001 is dropped. Residual = P − ET − R_liq − R_ice − ΔTWS. |
| `baseline_aerosol_cloud` (table) | `SOA_cb`, `N_AER`, `CCN3`, `ACTNL_incld`, `ACTREL_incld`, `TGCLDLWP`, `CLDLOW`, `FCTL` | CTRL and fBVOC regional means (annual, JJA); FUT − PD change; BVOC contrast as % of the fBVOC baseline |

## 9. MEGAN factor maps and attribution (`megan_factor_maps.ipynb`)

Code: `src/boreal_forest_expansion/plotting/megan_maps.py` (`make_factor_maps`, `make_attribution_maps`). Figures: `results/figures/megan_factors/`. It plots raw CLM `EPS_*` and `GAMMA*` for isoprene and 7 monoterpenes, as annual and JJA means per run. Grid-cell `GAMMA_*` is an area mean over vegetated patches, not emission-weighted.

Attribution figures (rows, residual, weighting vs co-variation, options to remove the residual): see `MEGAN_ATTRIBUTION.md`.
