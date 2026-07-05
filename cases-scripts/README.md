## Cases technical names:
The numbering refers to the order of simulations.
  - first digit: `1` PD, `2` is FUT
  - second digit: step of running (`1` is required for `2`)
  - letter: parallel runs (`a` and `b` can run simultaneously)
----
- SPINUP_PD: `11-NF2000norbc_tropstratchem_spinup_f19_f19.sh`
- MET: `12a-NF2000norbc_tropstratchem_met_f19_f19.sh`
- LANDONLY_SPINUP_PD: `12b-NF2000norbc_tropstratchem_landonly_spinup_lcc_f19_f19.sh`
- CTRL_PD: `13a-NF2000norbc_tropstratchem_nudg_ctrl_f19_f19.sh`
- LCC_SPINUP_PD: `13b-NF2000norbc_tropstratchem_spinup_lcc_f19_f19.sh`
- LCC_PD: `14a-NF2000norbc_tropstratchem_nudg_lcc_f19_f19.sh`
- LCC_fBVOC_PD: `14b-NF2000norbc_tropstratchem_nudg_lcc_fBVOC_f19_f19.sh`

- SPINUP_FUT: `21-NF2100ssp585norbc_tropstratchem_spinup_f19_f19.sh`
- LANDONLY_SPINUP_FUT: `22b-NF2100ssp585norbc_tropstratchem_landonly_spinup_lcc_f19_f19.sh`
- CTRL_FUT: `23a-NF2100ssp585norbc_tropstratchem_nudg_ctrl_f19_f19.sh`
- LCC_SPINUP_FUT: `23b-NF2100ssp585norbc_tropstratchem_spinup_lcc_f19_f19.sh`
- LCC_FUT: `24a-NF2100ssp585norbc_tropstratchem_nudg_lcc_f19_f19.sh`
- LCC_FUT_fBVOC: `24b-NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOC_f19_f19.sh`

### Quick lcc spinups to avoid land-only+coupled spinup, used preliminary:
- `13bx-NF2000norbc_tropstratchem_quick_spinup_lcc_f19_f19.sh`
- `23bx-NF2100ssp585norbc_tropstratchem_quick_spinup_lcc_f19_f19.sh`

```
37-NF2100ssp585norbc_tropstratchem_nudg_lcc_fFUTBVOC_f19_f19.sh
42-NF2100ssp585norbc_tropstratchem_met_f19_f19.sh
43-NF2100ssp585norbc_tropstratchem_fut_nudg_ctrl_f19_f19.sh
```
