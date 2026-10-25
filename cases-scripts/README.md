## Cases technical names:
The numbering refers to the order of simulations.
  - first digit: `1` PD, `2` is FUT
  - second digit: step of running (`1` is required for `2`)
  - letter: parallel runs (`a` and `b` can run simultaneously)
----
- SPINUP_PD: `11-NF2000norbc_tropstratchem_spinup_f19_f19.sh`
- MET: `12a-NF2000norbc_tropstratchem_met_f19_f19.sh`
- LANDONLY_SPINUP_PD: `12b-NF2000norbc_tropstratchem_landonly_spinup_lcc_f19_f19.sh`
- CTRL_LANDONLY_SPINUP_PD: `12c-NF2000norbc_tropstratchem_landonly_spinup_ctrl_f19_f19.sh` (CTRL twin of 12b; not run, run decision pending)
- CTRL_PD: `13a-NF2000norbc_tropstratchem_nudg_ctrl_f19_f19.sh`
- LCC_SPINUP_PD: `13b-NF2000norbc_tropstratchem_spinup_lcc_f19_f19.sh`
- CTRL_SPINUP_PD: `13c-NF2000norbc_tropstratchem_spinup_ctrl_f19_f19.sh` (CTRL twin of 13b, finidat from 12c; not run. If run, repoint 13a to it)
- LCC_PD: `14a-NF2000norbc_tropstratchem_nudg_lcc_f19_f19.sh`
- LCC_PD_fBVOCctrlPD_IM: `14b-NF2000norbc_tropstratchem_nudg_lcc_fBVOC_f19_f19.sh`

- SPINUP_FUT: `21-NF2100ssp585norbc_tropstratchem_spinup_f19_f19.sh`
- LANDONLY_SPINUP_FUT: `22b-NF2100ssp585norbc_tropstratchem_landonly_spinup_lcc_f19_f19.sh`
- CTRL_LANDONLY_SPINUP_FUT: `22c-NF2100ssp585norbc_tropstratchem_landonly_spinup_ctrl_f19_f19.sh` (CTRL twin of 22b; not run)
- CTRL_FUT: `23a-NF2100ssp585norbc_tropstratchem_nudg_ctrl_f19_f19.sh`
- LCC_SPINUP_FUT: `23b-NF2100ssp585norbc_tropstratchem_spinup_lcc_f19_f19.sh`
- CTRL_SPINUP_FUT: `23c-NF2100ssp585norbc_tropstratchem_spinup_ctrl_f19_f19.sh` (CTRL twin of 23b, finidat from 22c; not run. Then repoint 23a to it)
- LCC_FUT: `24a-NF2100ssp585norbc_tropstratchem_nudg_lcc_f19_f19.sh`
- LCC_FUT_fBVOCctrlPD_IM: `24b-NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOC_f19_f19.sh`

- LCC_PD_fBVOCctrlPD: `14c-NF2000norbc_tropstratchem_nudg_lcc_fBVOCctrlPD_f19_f19.sh` (all 19 MEGAN species from CTRL_PD)
- LCC_FUT_fBVOCctrlPD: `24c-NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOCctrlPD_f19_f19.sh` (all 19 species from CTRL_PD, relabelled to 2100)
- LCC_FUT_fBVOCctrlFUT: `24d-NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOCctrlFUT_f19_f19.sh` (all 19 species from CTRL_FUT, relabelled to 2100)
- LCC_FUT_fBVOClccPD: `24e-NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOClccPD_f19_f19.sh` (all 19 species from LCC_PD, relabelled to 2100; needs an LCC_PD run with HR_BVOC_ALL, new spin-up chain; set LCC_PD_CASE)

### Analysis aliases

| Alias | Environment and vegetation | Prescribed BVOC emissions |
|---|---|---|
| `CTRL_PD` | Present-day, control vegetation | Interactive |
| `LCC_PD` | Present-day, expanded vegetation | Interactive |
| `LCC_PD_fBVOCctrlPD_IM` | Present-day, expanded vegetation | ISOP, MTERP from `CTRL_PD` (existing run) |
| `LCC_PD_fBVOCctrlPD` | Present-day, expanded vegetation | All 19 MEGAN species from `CTRL_PD` |
| `CTRL_FUT` | Future, control vegetation | Interactive |
| `LCC_FUT` | Future, expanded vegetation | Interactive |
| `LCC_FUT_fBVOCctrlPD_IM` | Future, expanded vegetation | ISOP, MTERP from `CTRL_PD` (existing run; sensitivity) |
| `LCC_FUT_fBVOCctrlPD` | Future, expanded vegetation | All 19 MEGAN species from `CTRL_PD` |
| `LCC_FUT_fBVOCctrlFUT` | Future, expanded vegetation | All 19 MEGAN species from `CTRL_FUT` |
| `LCC_FUT_fBVOClccPD` | Future, expanded vegetation | All 19 MEGAN species from `LCC_PD` (planned) |

Suffix `_fBVOC<source run>` = run the prescribed emissions come from; `_IM` = ISOP and MTERP only.

### Extensions (2010-2014, continue runs within nudging data 2000-2015):
- `extend_nudg_runs_2010-2014.sh` (comment in/out the cases to extend)

### Quick lcc spinups to avoid land-only+coupled spinup, used preliminary:
- `13bx-NF2000norbc_tropstratchem_quick_spinup_lcc_f19_f19.sh`
- `23bx-NF2100ssp585norbc_tropstratchem_quick_spinup_lcc_f19_f19.sh`

```
37-NF2100ssp585norbc_tropstratchem_nudg_lcc_fFUTBVOC_f19_f19.sh
42-NF2100ssp585norbc_tropstratchem_met_f19_f19.sh
43-NF2100ssp585norbc_tropstratchem_fut_nudg_ctrl_f19_f19.sh
```
