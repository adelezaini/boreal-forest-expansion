#!/bin/bash

### EXTENSION OF THE NUDGED RUNS 2015-2025 (user 2026-11-04)
# Continue the new-chain nudged runs from their 2015-01-01 restart to 2026-01-01
# with the MET extension (folder ..._6h_2000-2025, built by
# preprocess/nudging/copy-nudging-data-to-inputForNudging-directory-2000-2025.sh).
# Same case, same namelists and output; only the met folder changes
# (switch_case_to_met_2000_2025: user_nl_cam + met file path stored in the run-dir restart).
#
# Two phases, because the MET data arrive in two segments:
#   phase1  2015-01-01 -> 2020-01-01 (5 yr)  needs the MET folder through 2020-01-01
#           (available after MET segment 1, 2015 -> 2021)
#   phase2  2020-01-01 -> 2026-01-01 (6 yr)  needs the MET folder through 2026-01-01 (MET done)
# ~7 simulated yr/day -> ~17 h / ~21 h per run; ~1720 pe-h/yr -> 10 runs x 11 yr ~ 190k core-h.
#
# Usage: bash extend_nudg_runs_2015-2025.sh phase1|phase2 [--check]
#   --check: all checks for every case, changes nothing, submits nothing.
# Without --check it SUBMITS: only with the user's OK.
# Stops at the first case that fails a check (earlier cases stay submitted).

set -euo pipefail
source cases-setup.sh

PHASE="${1:-}"
CHECK=0; [[ "${2:-}" == "--check" ]] && CHECK=1
case "$PHASE" in
    phase1) RESTDATE="2015-01-01-00000"; NYEARS=5; NEED_DAY="2020-01-01" ;;
    phase2) RESTDATE="2020-01-01-00000"; NYEARS=6; NEED_DAY="2026-01-01" ;;
    *) echo "Usage: $0 phase1|phase2 [--check]" >&2; exit 1 ;;
esac

export MET_END_YEAR=2026
# All b5xxx compute nodes failed on 2026-11-03 (python 'Invalid argument', launch failures).
# Kept in .submit_options, so it also applies to resubmits and st_archive.
export SUBMIT_BATCH_ARGS="--exclude=b[5101,5103-5196,5207-5296]"
[[ $CHECK -eq 1 ]] && export CHECK_ONLY=1

CASES=(
    "NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20261029"                # CTRL_PD
    "NF2000norbc_tropstratchem_nudg_lcc_f19_f19-20261028"                 # LCC_PD
    "NF2100ssp585norbc_tropstratchem_nudg_ctrl_f19_f19-20261028"          # CTRL_FUT
    "NF2100ssp585norbc_tropstratchem_nudg_lcc_f19_f19-20261028"           # LCC_FUT
    "NF2000norbc_tropstratchem_nudg_lcc_fBVOCctrlPD_f19_f19-20261031"     # LCC_PD_fBVOCctrlPD
    "NF2000norbc_tropstratchem_nudg_ctrl_fBVOCctrlPD_f19_f19-20261031"    # CTRL_PD_fBVOCctrlPD
    "NF2100ssp585norbc_tropstratchem_nudg_ctrl_fBVOCctrlFUT_f19_f19-20261031"  # CTRL_FUT_fBVOCctrlFUT
    "NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOCctrlFUT_f19_f19-20261031"   # LCC_FUT_fBVOCctrlFUT
    "NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOCctrlPD_f19_f19-20261031"    # LCC_FUT_fBVOCctrlPD
    "NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOClccPD_f19_f19-20261031"     # LCC_FUT_fBVOClccPD
#   "NF2000norbc_tropstratchem_nudg_lcc_fBVOClccPD_f19_f19-20261031"     # LCC_PD_fBVOClccPD: 3-yr test, now 2003-2007; not at 2015
)

for CASENAME in "${CASES[@]}"; do
    echo "=== $CASENAME"
    # Subshells: both functions cd into the case directory
    (
        cd "$HOME/cases/BRL_FRST_XPSN/$CASENAME"
        wall=$(./xmlquery --value JOB_WALLCLOCK_TIME --subgroup case.run)
        (( 10#${wall%%:*} >= 26 )) || { echo "ERROR: case.run wallclock $wall < 26 h" >&2; exit 1; }
    )
    # 1. checks only (queue empty, last st_archive success, rpointer at RESTDATE, end <= MET end)
    ( CHECK_ONLY=1 extend_case "$CASENAME" "$NYEARS" "$RESTDATE" )
    # 2. met folder: user_nl_cam + run-dir restart (checks only with --check)
    ( switch_case_to_met_2000_2025 "$CASENAME" "$RESTDATE" "$NEED_DAY" )
    # 3. continue run + submit (skipped with --check)
    [[ $CHECK -eq 1 ]] || ( extend_case "$CASENAME" "$NYEARS" "$RESTDATE" )
done
echo "${PHASE}: $([[ $CHECK -eq 1 ]] && echo checked || echo submitted) ${#CASES[@]} cases"
