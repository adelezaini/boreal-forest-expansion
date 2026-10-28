# h0 history fields of the nudged runs

Tables of the fields that the CAM and CLM monthly history files (h0) contain, with metadata. The source is the first month (2000-01) of **CTRL_FUT** `NF2100ssp585norbc_tropstratchem_nudg_ctrl_f19_f19-20261028`, the first run of the new chain (tables regenerated 2026-10-28 20:58 from the relaunched run, which also writes `cb_SOA_A1`, `cb_SOA_NA_OCW`, `cb_SOA_A1_OCW`).

| File | Content |
|---|---|
| `cam_h0_fields.csv` | all 295 variables in the CAM h0: 265 requested (`fincl1`) + 30 grid/coordinate variables |
| `clm_h0_fields.csv` | all 599 variables in the CLM h0: 158 requested (`hist_fincl1`), 414 active by default, 27 grid/coordinate variables |
| `added_fields_20261028.csv` | the 117 fields added on 2026-10-28 (82 CAM, 35 CLM) |

## Columns
| Column | Meaning |
|---|---|
| `kind` | `whitelist` = requested in `cases-scripts/cases-setup.sh`; `default` = CLM default field (CAM uses `empty_htapes`, so it has none); `grid/coord` = no time × space dims |
| `added` | in the whitelist now, not in git `HEAD` (before 2026-10-28) |
| `group` | purpose of an added field |
| `absent_in_fBVOC` | not written in fBVOC runs. **CAM:** `MEG_*` (MEGAN off). **CLM:** `MEG_*`, `EPS_*`, `GAMMA*` (`clm_diagnostics std` only). |
| `postprocess_category` | category in `src/boreal_forest_expansion/postprocess/variables.py`; empty = **not picked up by the postprocessing yet** |
| `est_MB_per_month` | uncompressed size, 4 bytes × non-time dims. Rough: the archived files are netCDF-4 compressed. |

## Notes
- The tables hold the CTRL setup: `cam_diagnostics HR_BVOC_ALL`, `clm_diagnostics std`. LCC runs have the same h0 lists; fBVOC runs lack the `absent_in_fBVOC` fields.
- Size: the added CAM fields are 44% of the uncompressed CAM h0 (82 of 184 MB per month). The added CLM fields are 3%.
- 7 suggested CLM fields **do not exist in this build** and were left out. CLM aborts on an unknown name. The fields are `Z0M_TO_COUPLER`, `RAH1`, `RAW1`, `RB`, `VPD_CAN`, `ALBDSF`, `ALBISF`.
- `SOA_*DDF` already = GVF + TBF, so do not add them.
- `SOA_LV`/`SOA_SV` are in mol/mol, while `SOA_NA`/`SOA_A1` are in kg/kg.

## Regenerate
```
PY=/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python
$PY diagnostics/fincl-variable-check/make_history_field_tables.py CAM_H0.nc CLM_H0.nc [--base <git rev>] [--tag YYYYMMDD]
```
