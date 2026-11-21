#!/bin/bash

### EXTENSION OF THE 12 NUDGED RUNS 2026-2040 (user 2026-11-11, plan approved 2026-11-15)
# Continue the 12 new-chain nudged runs from their 2026-01-01 restart to 2041-01-01, nudged by the MET
# continuation (12e-NF2000norbc_tropstratchem_met_ext_2026-2040_f19_f19.sh). Same cases, namelists and output; only the met file list
# changes, once, in phase A: switch_case_to_met_list -> ..._6h_2000-2040/<MET>.cam.h1_filelist_2000-2040.txt
# (user_nl_cam + met path stored in the run-dir restart: _6h_2000-2025 -> _6h_2000-2040).
# Record: docs/met-nudg-2026-2040.md.
#
# Three phases of 5 yr, each needs the MET days through its end (MET jobs: 2026->32->38->41-01-02):
#   phaseA  2026-01-01 -> 2031-01-01  needs the list through 2031-01-01 (after MET job 1)
#   phaseB  2031-01-01 -> 2036-01-01  needs 2036-01-01 (after MET job 2)
#   phaseC  2036-01-01 -> 2041-01-01  needs 2041-01-01 (after MET job 3)
# ~7 simulated yr/day -> ~17 h per phase; ~1720 pe-h/yr -> 12 runs x 15 yr ~ 310k core-h.
#
# Usage: bash extend_nudg_runs_2026-2040.sh phaseA|phaseB|phaseC [--check] [--case CASENAME]
#   --check: all checks, changes nothing, submits nothing.
#   --case:  only that case (the watcher run_when_done/met_nudg_2026-2040_when_done.sh calls it per run).
# Without --check it SUBMITS. Stops at the first case that fails a check (earlier cases stay submitted).

set -euo pipefail
source cases-setup.sh

PHASE="${1:-}"
CHECK=0; ONLY=""
shift || true
while [[ $# -gt 0 ]]; do
    case "$1" in
        --check) CHECK=1 ;;
        --case) ONLY="${2:?--case needs a case name}"; shift ;;
        *) echo "unknown argument $1" >&2; exit 1 ;;
    esac
    shift
done
case "$PHASE" in
    phaseA) RESTDATE="2026-01-01-00000"; NEED_DAY="2031-01-01" ;;
    phaseB) RESTDATE="2031-01-01-00000"; NEED_DAY="2036-01-01" ;;
    phaseC) RESTDATE="2036-01-01-00000"; NEED_DAY="2041-01-01" ;;
    *) echo "Usage: $0 phaseA|phaseB|phaseC [--check] [--case C]" >&2; exit 1 ;;
esac
NYEARS=5
MET=NF2000norbc_tropstratchem_met_f19_f19_20260422
MET_LIST=/cluster/shared/noresm/inputdata/noresm-only/inputForNudging/AZ/${MET}_6h_2000-2040/${MET}.cam.h1_filelist_2000-2040.txt
NEED_DAY="${NEED_DAY_OVERRIDE:-$NEED_DAY}"   # tests only (dry check before the MET days exist)

export MET_END_YEAR=2041
export SUBMIT_BATCH_ARGS="--exclude=b[5101,5103-5196,5203-5204,5207-5296]"
[[ $CHECK -eq 1 ]] && export CHECK_ONLY=1

CASES=(
    "NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20261029"                     # CTRL_PD
    "NF2000norbc_tropstratchem_nudg_lcc_f19_f19-20261028"                      # LCC_PD
    "NF2100ssp585norbc_tropstratchem_nudg_ctrl_f19_f19-20261028"               # CTRL_FUT
    "NF2100ssp585norbc_tropstratchem_nudg_lcc_f19_f19-20261028"                # LCC_FUT
    "NF2000norbc_tropstratchem_nudg_lcc_fBVOCctrlPD_f19_f19-20261031"          # LCC_PD_fBVOCctrlPD
    "NF2000norbc_tropstratchem_nudg_ctrl_fBVOCctrlPD_f19_f19-20261031"         # CTRL_PD_fBVOCctrlPD
    "NF2100ssp585norbc_tropstratchem_nudg_ctrl_fBVOCctrlFUT_f19_f19-20261031"  # CTRL_FUT_fBVOCctrlFUT
    "NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOCctrlFUT_f19_f19-20261031"   # LCC_FUT_fBVOCctrlFUT
    "NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOCctrlPD_f19_f19-20261031"    # LCC_FUT_fBVOCctrlPD
    "NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOClccPD_f19_f19-20261031"     # LCC_FUT_fBVOClccPD
    "NF2000norbc_tropstratchem_nudg_lcc_fBVOClccPD_f19_f19-20261031"           # LCC_PD_fBVOClccPD
    "NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOClccFUT_f19_f19-20261106"    # LCC_FUT_fBVOClccFUT
)

if [[ -n "$ONLY" ]]; then
    printf '%s\n' "${CASES[@]}" | grep -qx -- "$ONLY" || { echo "ERROR: $ONLY is not in the case list" >&2; exit 1; }
    CASES=("$ONLY")
fi
for CASENAME in "${CASES[@]}"; do
    echo "=== $CASENAME ($PHASE)"
    (
        cd "$HOME/cases/BRL_FRST_XPSN/$CASENAME"
        wall=$(./xmlquery --value JOB_WALLCLOCK_TIME --subgroup case.run)
        (( 10#${wall%%:*} >= 26 )) || { echo "ERROR: case.run wallclock $wall < 26 h" >&2; exit 1; }
    )
    # 1. checks only (queue empty, last st_archive success, rpointer at RESTDATE, end <= MET end)
    ( CHECK_ONLY=1 extend_case "$CASENAME" "$NYEARS" "$RESTDATE" )
    # 2. met list: phase A switches (user_nl_cam + run-dir restart); B and C: the list must reach NEED_DAY
    #    and the case must already read it
    if [[ "$PHASE" == phaseA ]]; then
        ( switch_case_to_met_list "$CASENAME" "$RESTDATE" "$NEED_DAY" "$MET_LIST" )
    else
        grep -q "met_filenames_list[[:space:]]*=[[:space:]]*'$MET_LIST'" "$HOME/cases/BRL_FRST_XPSN/$CASENAME/CaseDocs/atm_in" \
            || { echo "ERROR: $CASENAME does not read $MET_LIST (phase A switch missing)" >&2; exit 1; }
        last=$(tail -n 1 "$MET_LIST" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}-00000\.nc$' | cut -c1-10)
        [[ ! "$last" < "$NEED_DAY" ]] || { echo "ERROR: $MET_LIST ends at $last, $PHASE needs $NEED_DAY" >&2; exit 1; }
        echo "CHECK OK: list ends $last"
    fi
    # 3. continue run + submit (skipped with --check)
    [[ $CHECK -eq 1 ]] || ( extend_case "$CASENAME" "$NYEARS" "$RESTDATE" )
done
echo "${PHASE}: $([[ $CHECK -eq 1 ]] && echo checked || echo submitted) ${#CASES[@]} cases"
