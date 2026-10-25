#!/bin/bash

### EXTENSION OF NUDGED RUNS
# Nudging
# Continue existing cases from 2010-01-01 for 5 more years (2010-2014),
# within nudging data 2000-2015 (last met file 2015-01-01-00000).
# Comment in/out the cases to extend in CASES below.
# Stops at the first case that fails a check (earlier cases stay submitted).

# Exit if error, undefined variable...
set -euo pipefail
# Load common functions for case setup
source cases-setup.sh
#––––––––––– SIMULATION SPECIFICS: –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
RESTDATE="2010-01-01-00000"
NYEARS=5

CASES=(
#    "NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20260925"              # CTRL_PD
    "NF2000norbc_tropstratchem_nudg_lcc_f19_f19-20261005"               # LCC_PD
#    "NF2100ssp585norbc_tropstratchem_nudg_ctrl_f19_f19-20260925"        # CTRL_FUT
    "NF2100ssp585norbc_tropstratchem_nudg_lcc_f19_f19-20261005"         # LCC_FUT
#   "NF2000norbc_tropstratchem_nudg_lcc_fBVOC_f19_f19-20261008"         # LCC_PD_fBVOCctrlPD_IM
#   "NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOC_f19_f19-20261009"   # LCC_FUT_fBVOCctrlPD_IM
)
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

for CASENAME in "${CASES[@]}"; do
    # Subshell: extend_case cd's into the case directory
    ( extend_case "$CASENAME" "$NYEARS" "$RESTDATE" )
done

echo "Submitted extensions for: ${CASES[*]}"
