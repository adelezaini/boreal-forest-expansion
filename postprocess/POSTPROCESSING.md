# Postprocessing: what is done to the raw model output

Raw NorESM monthly history files → one NetCDF file per **case × component × category**.
Code: `src/boreal_forest_expansion/postprocess/` (`pipeline.py`, `fileio.py`, `variables.py`, `derived.py`).
Entry points: `postprocess/run_postprocess.py` (one case) and `postprocess/run_all_parallel.sh` (all cases, in parallel).

## 1. Input and output

| | |
|---|---|
| **Input** | `<raw-path>/<case>/<atm\|lnd>/hist/<case>.<cam\|clm2>.h0.*.nc` (monthly means, tape `h0`) |
| **Output** | `data/processed-data/postprocessing/<ALIAS>_<atm\|lnd>_<CATEGORY>_<y0>-<y1>.nc` |
| **Example** | `CTRL_PD_atm_RADIATIVE_2001-2009.nc` |
| **Archive** | old 2001–2009 files (old chain): `data/processed-data/postprocessing/2001-2009-pre-co2-fix/` |

One output file holds the variables of one category (§3), the grid variables, and any secondary variables computed for that category (§4).

## 2. Operations, in order (`pipeline.run`)

| # | Step | What happens | Changes the numbers? |
|---|---|---|---|
| 1 | **Find files** | All `h0` files of the case, sorted by name. | no |
| 2 | **Check variables** | Reads the header of **every** file. A requested variable missing from **all** files is skipped and listed in the output attribute `missing_variables`. A variable missing from **only some** files stops the run, because xarray would otherwise fill those months with NaN without warning. | no |
| 3 | **Open** | Opens all files and keeps only the requested variables plus the time bounds. Time-invariant fields (`gw`, `hyai`, `area`, …) are taken from the first file. | no |
| 4 | **Validate the time axis** | Every record must: (i) span 28–31 days (1 h tolerance; CLM's first record starts one model timestep early); (ii) start where the previous record ended, so there are no gaps, duplicates or unsorted files; (iii) be a time mean, so no field may have `cell_methods = "time: point"`. Any failure stops the run. | no |
| 5 | **Fix the time stamp** | The model stamps each monthly mean at the **end** of the averaging interval (January is stamped 1 February). `time` is reset to the **midpoint** of the time bounds (January → 16 January 12:00). The `noleap` calendar is kept. | time coordinate only |
| 6 | **Drop spin-up** | The first **12 months** are removed (`--spinup-months 12`). For the nudged runs (start 2000-01) this means year 2000 is dropped and the files start in 2001. Recorded in the attribute `spinup_months_dropped`. | yes: removes year 1 |
| 7 | **Load into memory** | The data are read once, so each category does not re-read the files. | no |
| 8 | **Fix unit labels** | Corrects wrong `units` attributes without changing values. Only one case so far: `N_AER` is labelled `unitless` but is in **cm⁻³** (checked in the OsloAero source). | no (label only) |
| 9 | **Add secondary variables** | Computed only for the categories being processed (§4). Each gets `secondary = "yes"` and `derived_from = <formula>`. A missing input stops the run with an error naming that input. | adds variables |
| 10 | **Save** | Per category: `ALWAYS_INCLUDE` + the category's variables + its secondary variables + time bounds. Each file is written as `<file>.part` and renamed when complete, so a killed job leaves no valid-looking file. Global attributes: `casename`, `alias`, `component`, `tape`, `spinup_months_dropped`, `n_history_files`, `missing_variables`, `category`, `created`. | no |

**Not done in postprocessing:**
- **No unit conversion.** Values stay in model units (e.g. kg m⁻² s⁻¹, m⁻³, W m⁻²). Conversion happens at plot time (`postprocess/units.py`, `plotting/forcing_maps.py`).
- **No time or space averaging.** The files keep every month and every grid cell.
- **No regridding.**
- **3-D fields keep all levels.** The maps use the lowest model level.

## 3. Categories (`variables.py`)

Every file also contains the grid variables:
- **atm:** `gw`, `LANDFRAC`, `P0`, `PS`, `hyai`, `hybi`, `hyam`, `hybm`
- **lnd:** `area`, `landfrac`, `landmask`, `pftmask`, `PCT_LANDUNIT`

| Component | Category | Content (main variables) |
|---|---|---|
| atm | **BVOC** | `SFISOP`, `SFMTERP`, `SFBCARY` (all emissions the atmosphere receives); `MEG_*` (interactive MEGAN part only, absent in fBVOC runs); mixing ratios and column burdens `ISOP`, `MTERP`, `BCARY`, `cb_*`. `emis_ISOP`/`emis_MTERP` are left out because they are identical to `SF*`. |
| atm | **SOA** | `SOA_A1`, `SOA_NA`, `SOA_LV`, `SOA_SV`, `cb_SOA_LV/SV`; nucleation and growth (`NUCLRATE`, `FORMRATE`, `GR*`); budget terms (condensation, coagulation, deposition); `N_AER`; `CCN1–7`, `CCN_B` |
| atm | **SULFATE** | `H2SO4`, `SO4_A1`, `SO4_NA` and their budget terms |
| atm | **AEROPT** | `DOD440/550/870`, `AOD_VIS`, `ABS550`, `A550_*` by species |
| atm | **CLOUDPROP** | `AREL`, `AWNC`, `FREQL`, `ACTREL`, `ACTNL`, `FCTL`, ice analogues, `CDNUMC`, `CLDLIQ`, `CLDTOT/LOW/MED/HGH`, `TGCLDLWP/IWP/CWP` |
| atm | **RADIATIVE** | Ghan inputs `FSNT`, `FLNT`, `FSNT_DRF`, `FLNT_DRF`, `FSNTCDRF`, `FLNTCDRF`; `SWCF`, `LWCF`, `FSNTOA`, `FLUT`, `SOLIN`; surface `FSDS`, `FSDSC`, `FSNS`, `FSNSC`, `FLDS`, `FLNS`, `FSDS_DRF`, `FSDSCDRF`, … |
| atm | **CHEM** | `O3`, `OH`, `HO2`, `NO`, `NO2`, `CO`, `CH4`, tropopause `TROP_P/T/Z` |
| atm | **METEO** | `TS`, `TREFHT`, `QREFHT`, `U10`, `PSL`, `LHFLX`, `SHFLX`, `PRECC`, `PRECL`, `SNOWHLND`, `ICEFRAC`, 3-D `T`, `U`, `V`, `Q`, `OMEGA`, `Z3` |
| lnd | **LAND** | `TSA`, `TREFMNAV/MXAV`, `TG`, `TV`, `TSOI_10CM`, `SOILWATER_10CM`, `PCT_NAT_PFT`, `TLAI`, `ELAI`, `HTOP`, … |
| lnd | **ENERGY** | `FSDS`, `FSR`, `FSA`, `SABG`, `SABV`, `FLDS`, `FIRA`, `FSH(_V/_G)`, `EFLX_LH_TOT`, `FGR`, vis/NIR direct/diffuse `FSDS*`/`FSR*` |
| lnd | **SNOW** | `H2OSNO`, `FSNO`, `FSNO_EFF`, `SNOW_DEPTH`, `SNOWDP`, `SNOW_PERSISTENCE`, `SNOCAN`, `SNOFSR*` |
| lnd | **BIOGEOCHEM** | `GPP`, `NPP`, `AR`, `HR`, `NEE`, `NBP`, carbon and nitrogen pools |
| lnd | **BVOC** | all 46 `MEG_<compound>`; MEGAN factors `EPS_*`, `GAMMA*_*` (10 compounds), `GAMMAL`, `GAMMAS` |
| lnd | **ET** | `QFLX_EVAP_TOT`, `QSOIL`, `QVEGE`, `QVEGT`, `FCEV`, `FCTR`, `FGEV` |
| lnd | **QA** | conservation errors `ERRSEB`, `ERRSOL`, `ERRSOI`, `ERRH2O`, `ERRH2OSNO` |
| lnd | **HYDRO** | `QRUNOFF`, `QOVER`, `QDRAI`, `QSNOMELT`, `RAIN`, `SNOW`, `TWS`, soil water/ice, ice runoff `QSNWCPICE`, `QICE*`, `QRUNOFF(_ICE)_TO_COUPLER`, `QFLX_*_DYNBAL` |

The full lists are in `src/boreal_forest_expansion/postprocess/variables.py`.

## 4. Secondary variables computed in postprocessing (`derived.py`)

Computed per month and per grid cell from the monthly means.

| Variable | Category | Formula | Units |
|---|---|---|---|
| `SW_dir` | atm RADIATIVE | `FSNT − FSNT_DRF` | W m⁻² |
| `LW_dir` | atm RADIATIVE | `−(FLNT − FLNT_DRF)` | W m⁻² |
| `NET_dir` | atm RADIATIVE | `SW_dir + LW_dir` | W m⁻² |
| `SW_cloud` | atm RADIATIVE | `FSNT_DRF − FSNTCDRF` | W m⁻² |
| `LW_cloud` | atm RADIATIVE | `−(FLNT_DRF − FLNTCDRF)` | W m⁻² |
| `NET_cloud` | atm RADIATIVE | `SW_cloud + LW_cloud` | W m⁻² |
| `SW_rest` | atm RADIATIVE | `FSNTCDRF` | W m⁻² |
| `LW_rest` | atm RADIATIVE | `−FLNTCDRF` | W m⁻² |
| `NET_rest` | atm RADIATIVE | `SW_rest + LW_rest` | W m⁻² |
| `NET_toa` | atm RADIATIVE | `FSNT − FLNT` | W m⁻² |
| `SOA_A1_cb`, `SOA_NA_cb` | atm SOA | `Σ_k q_k · Δp_k / g`, with `Δp_k` from `hyai·P0 + hybi·PS` and g = 9.80616 m s⁻² | kg m⁻² |
| `SOA_cb` | atm SOA | `SOA_A1_cb + SOA_NA_cb` | kg m⁻² |
| `SOA_TOT` | atm SOA | `SOA_A1 + SOA_NA` | kg kg⁻¹ |
| `UV_meanvec` | atm METEO | `√(U² + V²)` of the monthly-mean components | m s⁻¹ |
| `ET_veg` | lnd ET | `QVEGE + QVEGT` | mm s⁻¹ |

**Ghan decomposition** (Ghan 2013, ACP 13, 9971):
- Applies to one run; sign convention is positive downward. `*_DRF` = the same radiation call with aerosol optical depth set to 0 ("clean"); `*CDRF` = clean and clear-sky.
- Closure: `NET_dir + NET_cloud + NET_rest = NET_toa` exactly.
- Names: `*_cloud` and `*_rest` since 2026-10-28; older files have `*_cre_clean` and `*_clearclean`, which `forcing_maps.open_class` renames on loading.
- In a difference between two runs:
  - Δdir = aerosol–radiation term (F_AEROSOL-DIRECT)
  - Δcloud = cloud term (F_CLOUD) (aerosol–cloud interactions + cloud adjustments)
  - Δrest = everything else (F_REST) in clear, clean sky (surface albedo, gases)

**SOA column limits:**
- Computed from monthly means of q and PS, so the within-month covariance of q and Δp is missed.
- Uses the moist Δp, as CAM's own `cb_*` fields do.
- Interstitial aerosol only: cloud-borne SOA is not in the output.
- Post-CO₂-fix runs also write CAM's own burdens `cb_SOA_A1`, `cb_SOA_NA`, `cb_SOA_A1_OCW`, `cb_SOA_NA_OCW` (category SOA). CAM computes them every timestep, and the `_OCW` fields include the cloud-borne SOA. Older runs lack them, and the pipeline skips them there.

**In-cloud values (`ACTREL`, `ACTNL`, `AREL`, `AWNC`) are not stored.** The model writes them multiplied by the cloud fraction. They are divided by `FCTL` (or `FREQL`) at analysis time, from means taken over the same months (see `analysis/PLOTTED_VARIABLES.md`).

## 5. Running

```bash
# one case
$PY postprocess/run_postprocess.py CASENAME ALIAS {atm,lnd} [--categories ...] [--spinup-months 12] [--skip-existing]
# all cases: one job per case × component × category, existing outputs skipped
[RAW_PATH=...] [CASES="ALIAS CASENAME ..."] bash postprocess/run_all_parallel.sh [NJOBS]
```

- Logs go to `<out>/logs/<alias>_<comp>_<cat>.log`, plus one OK/FAILED line per job in `logs_run_all.txt`.
- `--skip-existing` matches **any** year span. Move old files of an alias out of the folder before postprocessing a new version of that run (`CLAUDE.md`, "When a run version changes").
- `postprocess/prep/` (NCO selection, metadata CSVs) is an older pre-selection step and is not used by the current pipeline.
