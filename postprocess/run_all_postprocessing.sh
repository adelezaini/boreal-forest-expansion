#!/usr/bin/env bash
# Run from the folder containing run_postprocess.py, with your Python environment active.
set -e

RAW_PATH="/cluster/home/adelez/BRL-FRST-XPSN_archive"
OUT_PATH="/cluster/home/adelez/BOREAL-FOREST-EXPANSION/data/processed-data/postprocessing"
SPINUP_MONTHS=12

# Aliases: <VEG>_<PERIOD>[_fBVOC<source run>[_IM]], e.g. LCC_FUT_fBVOCctrlPD = emissions from CTRL_PD;
# _IM = only ISOP and MTERP prescribed (original fBVOC runs). Add when they exist (all 19 MEGAN species):
#   LCC_PD_fBVOCctrlPD, LCC_FUT_fBVOCctrlPD, LCC_FUT_fBVOCctrlFUT; later LCC_FUT_fBVOClccPD
# Case names: keep up to date (CLAUDE.md "When a run version changes"; move old processed files first).
while read -r alias casename; do
    for component in atm lnd; do
        echo "Processing $alias: $component"
        python run_postprocess.py "$casename" "$alias" "$component" \
            --raw-path "$RAW_PATH" --out-path "$OUT_PATH" \
            --spinup-months "$SPINUP_MONTHS"
    done
done <<'CASES'
CTRL_PD NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20261023
LCC_PD NF2000norbc_tropstratchem_nudg_lcc_f19_f19-20261005
LCC_PD_fBVOCctrlPD_IM NF2000norbc_tropstratchem_nudg_lcc_fBVOC_f19_f19-20261008
CTRL_FUT NF2100ssp585norbc_tropstratchem_nudg_ctrl_f19_f19-20261023
LCC_FUT NF2100ssp585norbc_tropstratchem_nudg_lcc_f19_f19-20261005
LCC_FUT_fBVOCctrlPD_IM NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOC_f19_f19-20261009
CASES
