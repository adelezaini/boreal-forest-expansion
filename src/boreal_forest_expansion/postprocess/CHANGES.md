# Postprocessing refactor — what changed and why

Old code: `postprocess/postprocess.py` (script), `dataset_manipulation/postprocess.py`,
`functions.py`. New code: this package plus `postprocess/run_postprocess.py`.
Each module's docstring repeats the changes that concern it.

Evidence tags: **(a)** verified in NorESM2.3 source (CAM `cam_noresm2_3_v1.0.0j`,
OsloAero `oslo_aero_2_3a5`, CLM `release-clm5.0.14-Nor_v1.0.7`) or on a real/synthetic
file · **(b)** inference · **(c)** not verified.

## 1. Where the old code went

| Old function | New location |
|---|---|
| `create_dataset` | `fileio.find_history_files` + `fileio.open_history` |
| `fix_cam_time` | `fileio.fix_time` |
| spin-up slicing in `create_dataset` | `fileio.drop_spinup` |
| `variables_by_component`, `*_always_include` | `variables.CATEGORIES`, `variables.ALWAYS_INCLUDE` |
| `fix_units` | removed; `units.convert` at plot time |
| `fix_ds` (in-cloud) | `derived.incloud` (analysis time, weighted) |
| `fix_ds` (`cb_SOA_dry`) | `derived.soa_columns` → `SOA_cb` |
| `fix_ds` (`T_C`, `WIND_SPEED`) | `units.convert(ds.T, "degC")`; `derived.wind_meanvec` → `UV_meanvec` |
| `aerosol_cloud_forcing_scomposition_Ghan` | `derived.ghan_decomposition` |
| `save_postprocessed` | `fileio.save_category` (called by `pipeline.run`) |
| `functions.load_dataset_dict` | `fileio.load_processed` |
| `functions.add_SOA_TOT`, `fix_et` | `derived.soa_total` → `SOA_TOT`, `derived.et_veg` → `ET_veg` |
| `functions.fix_soa`, `fix_cloud`, `fix_names_soa`, `fix_radiative_names` | deleted |

## 2. Bugs fixed

| # | Old behaviour | Effect | New |
|---|---|---|---|
| 1 | `CLDHGH/LOW/MED` × 1e3, labelled g/kg | cloud fractions became meaningless | kept as fractions (a) |
| 2 | `ACTNL` converted to cm⁻³ in `fix_units`, then × 1e-6 again in `ACTNL_incld` | `ACTNL_incld` 10⁶ too small | single conversion, at plot time (a) |
| 3 | `functions.fix_cloud`: `ACTNL` × 1e-12 | stacked conversions | deleted (a) |
| 4 | `return` inside the loop in `fix_soa`, `fix_cloud` | returned after first match, or `None` | deleted (a) |
| 5 | `WIND_SPEED` units written on the dataset | global attrs overwritten | removed; use `U10` (a) |
| 6 | Ghan code overwrote model `SWCF`, `LWCF` | same name, two meanings | new names, model fields untouched (a) |
| 7 | undefined `casename` in `save_postprocessed` | `NameError` for lnd | fixed (a) |
| 8 | saving looped over all categories | `KeyError` when one category was loaded | saves only processed categories (a) |
| 9 | `fix_ds` required many fields unconditionally | `KeyError` with any subset | computed only if inputs exist (a) |
| 10 | `GRIDAREA` in always-include | not in NorESM2.3 output → every atm run failed | use `gw` (a) |
| 11 | `fix_cam_time` assigned time to the unrenamed `ds` | CLM renames lost | fixed (a) |
| 12 | `'datetime64'` time option | `UFuncTypeError` on noleap/cftime times | midpoint of bounds (a, tested) |
| 13 | `'OFF'` in case name ⇒ no BVOC | never matches current case names | presence-based selection (a) |
| 14 | `ds[var].values = ...` | loads arrays into memory | lazy arithmetic (b) |
| 15 | old names `SFisoprene`, `SFmonoterp`, `cb_SOA_*`, `CLOUDCOVER_CLUBB` | not in NorESM2.3 output | renamed / computed / removed (a) |

## 3. Behaviour that changed on purpose

- **Units**: processed files keep model units. Only correction: `N_AER` label
  "unitless" → `cm-3`; OsloAero converts mode concentrations × 1e-6 before summing (a).
- **Time**: midpoint of `time_bnds`/`time_bounds`. Verified on a CAM h0 file:
  `time = 3316`, bounds `[3285, 3316]` days since 2000-01-01 → January 2009 mean (a).
- **Secondary variables** carry `secondary = "yes"` and `derived_from`.
  - Ghan: `SW/LW/NET_dir`, `SW/LW/NET_cre_clean`, `SW/LW/NET_clearclean`, `NET_toa`;
    `NET_dir + NET_cre_clean + NET_clearclean == NET_toa` exactly. `_DRF` and
    `FSNT/FLNT` are written on the same radiation steps (a).
  - SOA columns: `SOA_A1_cb`, `SOA_NA_cb`, `SOA_cb` = Σ q·Δp/g from monthly means (b: small
    covariance error vs. a model `cb_` field, not quantified).
- **In-cloud values** at analysis time: `incloud(ds, "AREL", dim="time", min_frac=0.01)`
  = weighted mean(AREL) / weighted mean(FREQL), masked where mean FREQL < 0.01. The model
  writes `AREL = r_eff × f_liq` (`micro_mg_cam.F90`) (a). Weights: see section 6.
- **Output file name**: `<alias>_<component>_<category>_<y0>-<y1>.nc` + provenance attributes.

## 4. Variable selection

- **CAM**: all 163 fields of the curated `fincl` list kept except `emis_ISOP`, `emis_MTERP`,
  which OsloAero `chemistry.F90` writes from the same array as `SFISOP`, `SFMTERP` (a).
  New categories: `SULFATE`, `AEROPT`, `CHEM`, `METEO`.
- **CLM**: ~180 of ~560 default fields: `LAND`, `ENERGY`, `SNOW`, `BIOGEOCHEM`, `BVOC`, `ET`, `QA`.
  - `BVOC` has all 46 MEGAN fluxes in the file, matching the tropstratchem
    `megan_specifier` default in CAM `build-namelist` (a): 27 lumped into
    `ISOP`/`MTERP`/`BCARY` (the old list had 7 of the 21 MTERP compounds) and 19
    non-terpene compounds (methanol, acetone, CO, formaldehyde, …) that feed CAM
    gas-phase chemistry, hence the ozone and OH/methane channels (b). Plus MEGAN
    emission/activity factors for 10 compounds.
  - `SNOW` includes canopy snow (`SNOCAN`) and solar reflected by snow (`SNOFSR*`):
    the canopy-masking albedo effect.
  - `ENERGY` splits sensible heat into vegetation/ground (`FSH_V`, `FSH_G`); `LAND` has
    daily min/max 2 m temperature (`TREFMNAV`, `TREFMXAV`).
  - `QA`: conservation errors (`ERRSEB`, `ERRSOL`, `ERRSOI`, `ERRH2O`, `ERRH2OSNO`), for a
    one-off check of the modified surface data; all should be ~0.
  - Left out on purpose: N cycle, detailed C pools, land-use conversion (`DWT_*`,
    expected zero with a fixed modified surfdata (b)), vertically resolved soil, hydrology
    detail, atmospheric forcing duplicated in CAM, CH₄, crop/urban/lake/glacier, fire,
    heat-stress indices, photosynthesis/stomata, rural/local-noon duplicates.

## 5. Review round 2 (external review, all five points adopted)

| # | Review point | Change | Where | Test |
|---|---|---|---|---|
| 1 | Records dropped as "months" without checking they are months | `validate_monthly_means()` runs before the time fix and spin-up removal: records 28–31 days, contiguous (no gaps, duplicates, unsorted files), no `cell_methods: time: point` (instantaneous tapes such as the 30-min BVOC tape; CAM writes `time_bnds` for those too (a)) | `fileio.py`, `pipeline.py` | gap, duplicate, out-of-order, instantaneous, 1-day record |
| 2 | Availability read from the first file only | `scan_files()` reads every file header. A variable in only some files is an **error**; xarray would otherwise fill the gaps with NaN silently (a, tested). Missing inputs of a requested category's secondary variables are now an **error**, not a skipped warning | `fileio.py`, `derived.py` | variable dropped from 6 of 24 files; Ghan input missing |
| 3 | SOA column: NaN handling and unchecked assumptions | `sum(..., skipna=False)`: an all-NaN profile gives NaN, not 0 (a, tested). Checks: `P0`, `PS` in Pa, `SOA_*` in kg/kg, `len(ilev) = len(lev)+1`, Δp > 0 in every layer (checked at min and max `PS`; exact since Δp is linear in `PS`). Documented, not changed: moist Δp as in CAM's own `cb_` fields (a), while CAM registers tracers as dry (a), difference ≲ 1–2 % (b); cloud-borne SOA (`cb_SOA_*_OCW`) not in output, not replaceable | `derived.py` | NaN profile, hPa units, reversed `hybi` |
| 4 | `incloud()` averaged with equal weights; "never" too categorical | New `averaging.py`: `record_days()` from the time bounds, `area_weights()` (`gw` or `area·landfrac`), `weighted_mean()` choosing weights from the averaged dims. `incloud()` uses it. Docstring now explains when the mean of monthly ratios is the right choice | `averaging.py`, `derived.py` | 31/28-day weighted mean; weighted in-cloud ratio |
| 5 | Restore small diagnostics | `SOA_TOT` (→ SOA), `ET_veg = QVEGE + QVEGT` (→ ET), `UV_meanvec = √(U²+V²)` of monthly means (→ METEO), documented as the magnitude of the mean wind vector, not mean wind speed, not `U10` | `derived.py` | values and `secondary` attribute |

Input units of all new checks match your pasted metadata: `P0`, `PS` Pa; `SOA_A1/NA`
kg/kg; `U`, `V` m/s; `QVEGE`, `QVEGT` mm/s (a).

## 6. Averaging rule for analysis

Use `averaging.weighted_mean(da, dims, ds)` instead of `.mean()`: over `time` it weights
by record length (days), over `lat`/`lon` by cell area. Example: an annual mean of a
31-day and a 28-day record with values 1 and 0 is 31/59 = 0.525, not 0.5.

## 7. Still open

- Confirm `megan_specifier` in your `CaseDocs/drv_flds_in` matches `variables.MEGAN_LUMPING`.
- Confirm no diagnostic radiation calls (`rad_diag_*` absent in `CaseDocs/atm_in`); otherwise
  the `_DRF` fields average over several calls (a, source).
- CLM CH₄ fields left out on the assumption that CH₄ is prescribed at the lower boundary (c).
- `min_frac=0.01` for in-cloud ratios is a starting value to test.
