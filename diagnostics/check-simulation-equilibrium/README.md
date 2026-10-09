# CAM and CLM equilibrium diagnostics

Put `equilibrium.py`, `build_modified_cells.py`, and `check_case_equilibrium.ipynb` in the same directory on Betzy. Open the notebook in that directory. Dependencies: Python 3.10+, numpy, pandas, xarray, netCDF4, cftime, matplotlib, Jupyter. No dask or cartopy required.

## Workflow

1. Set the case/archive path, component switches, year range and regional selections in the notebook.
2. Run the one-time mask-builder cell (or CLI below) with the original and modified surfdata. It writes `modified_cells.nc` plus `modified_cells.csv` containing zero-based indices, latitude, longitude and maximum PFT change in percentage points. Later runs load the NetCDF directly; they do not reopen the surface files. Use a different cache for a different modification. Rebuild deliberately if surface files change; the cache stores source paths and tolerance, not automatic source-content checksums.
3. Inspect one history header via the inventory cell. Verify soil depths, gas definitions, pressure auxiliaries and monthly averaging.
4. Run CLM time series, CAM time series, gas profiles and burden cells. Tables, figures and audit are saved under `outputs/<case>/`.

The supplied surface paths are copied from the attached notebook; confirm they are the intended pair. The real model history and surfdata are not attached, so this package contains no actual modified-cell list or equilibrium conclusion. The CSV and NetCDF will be generated on Betzy.

CLI alternative:

```bash
python build_modified_cells.py --baseline /path/original_surfdata.nc --modified /path/lcc_surfdata.nc --output modified_cells.nc
```

## Interpretation

- **CLM:** use land-area-weighted modified-cell means. H2OSOI and TSOI are the nearest saved physical level to 1 m (not a 0–1 m average); the selected depth is printed. Unknown/index-only depth coordinates raise an error. Supply verified model layer depths in `DEPTH_OVERRIDES`, never guessed values. GPP stays a mean rate in native units, not an annual accumulated flux.
- **CAM:** retain global profiles and global burdens as primary diagnostics. Add north of 45°N to detect regional drift, and columns above modified cells for local responses. CAM weights use full atmospheric cell area, not land fraction. A modified-cell mask is not the footprint of a transported chemical perturbation. Different grids cause an error rather than implicit nearest-neighbour remapping; remap a fractional mask conservatively as a separate, reviewed step if grids differ.
- **Radiation:** RESTOM is read if present, otherwise derived as FSNT − FLNT (positive downward). CAM labels FSNT/FLNT as top-of-model fluxes, distinct from FSNTOA at true TOA. For prescribed SST/SIC, inspect drift and stability rather than requiring zero radiative imbalance. Prescribed oceans and meteorological nudging constrain the evolution; nudged-run variability is not purely spinup adjustment.
- **Gases:** a stable prescribed scalar is not evidence of equilibrated chemistry. Verify whether each field is prognostic, boundary-constrained or prescribed throughout the atmosphere. Fixed surface mixing ratios still permit evolving profiles aloft. Continuously emitted long-lived tracers without balancing losses need not approach a stationary burden. Interpret SF6 and CFC115 against their actual forcing and tracer configuration.
- **Burden:** column = sum(q_mass × layer_air_mass), kg m−2; domain total = sum(column × cell_area)/1e9, Tg. Hybrid pressures use A×P0 + B×PS; dry-air mass uses (1−Q)Δp/g. Set each tracer's `GAS_BASIS` to `dry` or `moist` after verification. Unspecified basis leaves profiles available and explicitly skips burdens. No unit-based guess can determine dry versus moist air. Molar conversions use species molecular weight and the appropriate air molecular mass. Q is required for dry-air mass and moist molar conversion. Burdens cover the saved model column, not the atmosphere above the model top.
- Products of monthly mean mixing ratio and monthly layer mass omit their submonthly covariance. Pressure interpolation of monthly fields is also approximate. For exact burdens, prefer a model-produced mass-burden diagnostic or calculate at native temporal resolution before averaging.

## Time handling and limits

Monthly bounds must span complete calendar months; annual, daily or partial intervals are rejected. Without bounds, set `TIMESTAMP` explicitly to `start`, `end` (next-month timestamp) or `mid` after inspection. The code supports CF calendars and year 0001, does not force dates into pandas timestamps, rejects duplicate months, and makes incomplete annual means NaN. Missing years break rolling windows.

Annual means are weighted by interval duration. The trailing 20-year mean weights complete annual means equally. Its one-year difference is `(X[y] − X[y−20])/20`: 21 consecutive annual values are needed for the first derivative. A 2000–2009 control can show monthly/annual evolution, a 10-year descriptive slope and two 5-year blocks, but cannot supply this 20-year diagnostic. Do not shorten the window silently to imply the same test.

The final summary includes the last 10-year OLS slope (descriptive; no significance claim), difference between the last two 5-year blocks, and derivative at the final year. No universal pass/fail threshold is imposed. Compare drift with variability and the scientific perturbation of interest; a small derivative alone does not establish equilibrium. Opposing cell trends can cancel in regional means; this package's regional time series do not establish cell-by-cell equilibrium. Check spatial drift before claiming all modified cells have equilibrated.

Surface means require ≥99% finite weighted coverage; coverage columns remain in the CSV. Profiles are interpolated in log pressure before spatial averaging, with no below-ground or above-model extrapolation. Their plots require ≥95% monthly area coverage; coverage is saved. Integrated totals become NaN if selected columns are incomplete. Native unknown tracer units are still usable for relative profile drift but cannot produce mass burdens.

## References and validation

- [CAM history field definitions](https://www2.cesm.ucar.edu/models/cesm1.2/cam/docs/ug5_3/hist_flds_fv_cam5.html): flux terminology; check your NorESM field metadata too.
- [NCAR hybrid pressure convention](https://www.ncl.ucar.edu/Document/Functions/Built-in/pres_hybrid_ccm.shtml).
- [CAM5 technical description](https://www2.cesm.ucar.edu/models/cesm2/atmosphere/docs/description/cam5_desc.pdf): dry/moist constituent representations; verify your specific NorESM implementation.

Validation here uses synthetic fixtures for calendar, weighting, missing-year, depth, mask and burden calculations, plus ordered execution of every notebook code cell with temporary fixture paths in plain Python. A Jupyter kernel could not launch in this environment, so kernel-based execution remains to be checked on Betzy. It does not validate your actual simulations. Run the notebook top-to-bottom on Betzy after setting paths and inspect `audit.csv`, depths, coverage and figures before interpreting results.
