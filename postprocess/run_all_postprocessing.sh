#!/usr/bin/env bash
# Run from the folder containing run_postprocess.py, with your Python environment active.
set -e

RAW_PATH="${RAW_PATH:-/cluster/work/users/adelez/archive}"   # work archive: postprocess as soon as a run is done (user 2026-10-28); NIRD copy = ~/BRL-FRST-XPSN_archive
OUT_PATH="/cluster/home/adelez/BOREAL-FOREST-EXPANSION/data/processed-data/postprocessing"
SPINUP_MONTHS=12

# Aliases: <VEG>_<PERIOD>[_fBVOC<source run>[_IM]], e.g. LCC_FUT_fBVOCctrlPD = emissions from CTRL_PD;
# All fBVOC runs prescribe all 19 MEGAN species (the ISOP+MTERP-only _IM runs are dropped, 2026-10-28).
# Current set (2026-10-28): 2000-2014 runs of the all-species fBVOC setup, before the CO2 fix (CTRL -20261023, LCC -20261005, fBVOC -20261025).
# Raw files are read from the work archive by default (purged after 42 days); RAW_PATH=~/BRL-FRST-XPSN_archive reads the NIRD copy.
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
CTRL_FUT NF2100ssp585norbc_tropstratchem_nudg_ctrl_f19_f19-20261023
LCC_FUT NF2100ssp585norbc_tropstratchem_nudg_lcc_f19_f19-20261005
LCC_PD_fBVOCctrlPD NF2000norbc_tropstratchem_nudg_lcc_fBVOCctrlPD_f19_f19-20261025
LCC_FUT_fBVOCctrlPD NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOCctrlPD_f19_f19-20261025
LCC_FUT_fBVOCctrlFUT NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOCctrlFUT_f19_f19-20261025
CASES
