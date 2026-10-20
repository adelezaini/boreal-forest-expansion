#!/usr/bin/env bash
# Run from the folder containing run_postprocess.py, with your Python environment active.
set -e

RAW_PATH="/cluster/home/adelez/BRL-FRST-XPSN_archive"
OUT_PATH="/cluster/home/adelez/BOREAL-FOREST-EXPANSION/data/processed-data/postprocessing"
SPINUP_MONTHS=12


while read -r alias casename; do
    for component in atm lnd; do
        echo "Processing $alias: $component"
        python run_postprocess.py "$casename" "$alias" "$component" \
            --raw-path "$RAW_PATH" --out-path "$OUT_PATH" \
            --spinup-months "$SPINUP_MONTHS"
    done
done <<'CASES'
CTRL_PD NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20260925
LCC_PD NF2000norbc_tropstratchem_nudg_lcc_f19_f19-20261005
LCC_PD_fBVOC NF2000norbc_tropstratchem_nudg_lcc_fBVOC_f19_f19-20261008
CTRL_FUT NF2100ssp585norbc_tropstratchem_nudg_ctrl_f19_f19-20260925
LCC_FUT NF2100ssp585norbc_tropstratchem_nudg_lcc_f19_f19-20261005
LCC_FUT_fBVOC NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOC_f19_f19-20261009
CASES
