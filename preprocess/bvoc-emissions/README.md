# Prescribed BVOC emissions (fBVOC runs)

The fBVOC runs switch MEGAN off (`megan_specifier = ''`) and read biogenic emissions from files instead, all in `/cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions/`. This folder makes those files from a source run's CAM history output: a **climatology** of one emission field per file, in the format CAM's surface-emission reader expects.

| Folder | Species | Source run | Used by |
|---|---|---|---|
| this folder | all 19 MEGAN-fed CAM species | CTRL_PD / CTRL_FUT `-20261023`, 2001–2014 (later also LCC_PD) | 14c, 24c, 24d, 24e |
| `prescribe-just-ISOP-MTERP/` | ISOP, MTERP | CTRL_PD `-20260925`, 2001–2009 | 14b, 24b (`*_fBVOCctrlPD_IM`) |

`prescribe-just-ISOP-MTERP/` keeps the original scripts unchanged. Don't update it until the `_IM` runs are redone.

## Workflow (all species)

```
source run with cam_diagnostics HR_BVOC_ALL (13a, 23a; 14a for LCC_PD)
  │  h1: 30-min instantaneous SFISOP, SFMTERP, MEG_{BCARY,C3H6,BIGENE,CH3CHO,CH2O,C2H4}
  │  h0: monthly means of all 19 MEG_* (+ SFISOP, SFMTERP)
  ▼
1. run_bvoc_climatology_array.sh  (sbatch, one task per species)
     → create_bvoc_emissions_climatology_staged.py  --stage concat, then --stage climatology
     → work: /cluster/work/users/adelez/bvoc-emissions/ (staged_work; the final file is deleted here once copied)
     → final file moved (cp -n + cmp, then rm in work): /cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions/ems_<case>_<y0>-<y1>_<VAR>.nc   (19 files)
  ▼
2. check_bvoc_climatology.py      climatology vs h0 means of the source run (ratio ≈ 1), Tg/yr per species
  ▼
3. create_bvoc_emissions_for_year_2100.sh   (FUT targets only: copy with dates relabelled to 2100, made in the shared folder)
     → /cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions/ems_<case>_<y0>-<y1>_on_yr2100_<VAR>.nc
     (EMS_PREFIX in the fBVOC case scripts points to the shared folder)
  ▼
4. plot_bvoc_emissions.ipynb      maps, totals and seasonal cycles of the files (CTRL_PD vs CTRL_FUT)
  ▼
5. fBVOC case script: prescribed_bvoc_emissions_all <2000|2100> "$EMS_PREFIX"   (cases-scripts/cases-setup.sh)
```

### Commands (from this folder)
```bash
# 1. climatologies (one array per source run); work in /cluster/work/users/adelez/bvoc-emissions,
#    final files moved to the shared bvoc_emissions folder
sbatch run_bvoc_climatology_array.sh NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20261023 2001 2014
sbatch run_bvoc_climatology_array.sh NF2100ssp585norbc_tropstratchem_nudg_ctrl_f19_f19-20261023 2001 2014

# 2. check (login node: needs the conda env and the archive)
PY=/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python
$PY check_bvoc_climatology.py NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20261023 2001 2014

# 3. relabel to 2100 in the shared folder, for every source used by a FUT run (here both)
bash create_bvoc_emissions_for_year_2100.sh NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20261023_2001-2014
bash create_bvoc_emissions_for_year_2100.sh NF2100ssp585norbc_tropstratchem_nudg_ctrl_f19_f19-20261023_2001-2014
```

## Files
| File | What it does |
|---|---|
| `create_bvoc_emissions_climatology_staged.py` | One species per call. Concatenates each year (NCO), checks the time axis, aligns all years on reference year 2000, averages, converts kg/m²/s → molecules/cm²/s, and keeps one flux field. Checkpointed and restartable (`--stage concat` / `climatology`); never overwrites a final file. `--help` gives the details. |
| `run_bvoc_climatology_array.sh` | sbatch array on `preproc` (index = species, 0–18) that runs the `.py` in the work folder and moves the final file to the shared folder (`cp -n` + `cmp`, then the work copy is deleted; kept if `cmp` fails). Uses the module Python (`netcdf4-python/1.7.1.post2-foss-2024a`), because `/nird` is not mounted on compute nodes. |
| `create_bvoc_emissions_climatology.sh` | The same as the array, run serially on the login node. Slow; mainly for single species. |
| `check_bvoc_climatology.py` | Per species: number of records, units, annual mean vs h0 mean (should be 1 to ~1e-7), global total in Tg/yr. Exit 1 on any failure. |
| `create_bvoc_emissions_for_year_2100.sh` | Works in the shared folder (`EMS_DIR` overrides). Copies files with `date` + 1000000 and the time units moved to 2100 (values unchanged), for FUT runs (`srf_emis_cycle_yr = 2100`). Refuses to overwrite. |
| `plot_bvoc_emissions.ipynb` | Annual and seasonal maps, Tg/yr table (global, >45°N, modified cells) and seasonal cycles for the 19 species, CTRL_PD vs CTRL_FUT. |
| `prescribe-just-ISOP-MTERP/` | Original ISOP/MTERP-only scripts and notebook. |
| `to-clean/` | Old material. |

## Species and sampling
| Sampling (tape) | History field → CAM species |
|---|---|
| 30 min, instantaneous (h1) | `SFISOP`→ISOP, `SFMTERP`→MTERP, `MEG_BCARY`, `MEG_C3H6`, `MEG_BIGENE`, `MEG_CH3CHO`, `MEG_CH2O`, `MEG_C2H4` |
| monthly mean (h0) | `MEG_CH3OH`, `MEG_C2H5OH`, `MEG_CH3COOH`, `MEG_CH3COCH3`, `MEG_HCOOH`, `MEG_HCN`, `MEG_CO`, `MEG_C2H6`, `MEG_C3H8`, `MEG_BIGALK`, `MEG_TOLUENE` |

- The short-lived species (lifetime ≲ 1 day) are half-hourly because their diurnal cycle matters.
- Molar masses are CAM `adv_mass` (`pp_tropstrat_mam_oslo/mo_sim_dat.F90`), in `MOLAR_MASS` in the `.py`.

## Things to know
- **`SF*` vs `MEG_*`:** `SFISOP`/`SFMTERP` are the total flux (MEGAN + biomass burning), so the fBVOC namelist removes the biomass-burning ISOP/MTERP files. `MEG_*` is MEGAN only, so the anthropogenic and biomass-burning files of the other 17 species stay in `srf_emis_specifier`. `prescribed_bvoc_emissions_all` does both.
- **Isoprene diurnal cycle:** the half-hourly ISOP already contains it, so the fBVOC cases call `bypass_isoprene_diurnal_adjustment`.
- **Monthly files:** 12 records at mid-month. CAM (`srf_emis_type = 'CYCLICAL'`) interpolates linearly between them, so monthly means are reproduced only approximately, as for other monthly emission files.
- **Climatology limits:** no interannual or weather coupling. This is part of what an fBVOC contrast contains.
- **Source run versions:** every new CTRL_* (or LCC_PD) version requires redoing steps 1–3 and updating `EMS_PREFIX` in the fBVOC scripts. Follow the checklist in the repo `CLAUDE.md` § "When a run version changes". The defaults in `create_bvoc_emissions_climatology.sh` and `create_bvoc_emissions_for_year_2100.sh` must point to the latest CTRL_PD.
