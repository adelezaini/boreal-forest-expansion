#!/bin/bash
# Launcher of the MEGAN exact-split branch runs (analysis/MEGAN_ATTRIBUTION.md, option 1). See README.md here.
#
#   bash launch_megan_lmdi.sh test  PD                    production test: CTRL_PD + LCC_PD from 2005-01-01, 2 jobs x 30 days
#                                                           = 2 months + 1 day, restart on 31 Jan (user 2026-11-04; OK 3 Nov,
#                                                           date 2005 user 2026-11-04); raw files kept (delete dry run)
#   bash launch_megan_lmdi.sh batch PD|FUT YEAR [YEAR ...]  one batch of years, e.g. batch PD 2005 2006 2010
#   options (last): --plan-only  print what would be done, touch nothing
#                   --no-submit  build the new cases, don't submit, don't start the watcher
#                   --keep-raw   reduce but keep the raw tape-2 files (DELETE=no; user 2026-11-05: batch 1 keeps them
#                                until the driver swaps (option 1b) exist; work purges after 42 days). 2000 is still deleted.
#
# Years: the parents kept restarts only at 2005/2010/2015, so each run has two chains (one case each):
#   chain 2005: 2005, 2006, 2007, 2008 (2009 possible)   chain 2010: 2010, 2011, 2012 (2013, 2014 possible)
#   chain 2000: 2000 (identity check only, then deleted), 2001, 2002, 2003 (user 2026-11-04): hybrid from the spin-up
#   chain 2015: possible (2015–2019) but not planned; needs the extended met folder and the parents' 2015+ extension
# A batch must continue each chain where it stands (first batch: from the chain start). Per chain and batch:
# RESUBMIT = years − 1, one model year per job; CONTINUE_RUN=TRUE for an existing chain.
# Gate: a batch is refused while any earlier year of the same period is not reduced (.ok) or has failed,
# and before the production test has passed. Every launch needs the user's explicit OK (CLAUDE.md).
# State, plan and logs: /cluster/work/users/adelez/megan-lmdi/<PERIOD>/.

set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-}"; PERIOD="${2:-}"; shift 2 || true
PLAN_ONLY=0; NO_SUBMIT=0; KEEP_RAW=0; YEARS=(); PLAN_LINES=()
for x in "$@"; do
    case "$x" in
        --plan-only) PLAN_ONLY=1 ;;
        --no-submit) NO_SUBMIT=1 ;;
        --keep-raw)  KEEP_RAW=1 ;;
        [0-9][0-9][0-9][0-9]) YEARS+=("$x") ;;
        *) echo "unknown argument: $x" >&2; exit 1 ;;
    esac
done
[[ "$PERIOD" == PD || "$PERIOD" == FUT ]] || { echo "Usage: $0 test|batch PD|FUT [YEAR ...] [--plan-only|--no-submit]" >&2; exit 1; }
[[ "$MODE" == test && "$PERIOD" != PD ]] && { echo "the production test is PD only" >&2; exit 1; }
[[ "$MODE" == batch && ${#YEARS[@]} -eq 0 ]] && { echo "batch needs years" >&2; exit 1; }

ROOT="${MEGAN_LMDI_ROOT:-/cluster/work/users/$USER/megan-lmdi}"   # override only for tests
STATE="$ROOT/$PERIOD"
ARCHIVE="/cluster/work/users/$USER/archive"
CASES="$HOME/cases/BRL_FRST_XPSN"
# Same exclude as extend_nudg_runs_2015-2025.sh: all b5xxx compute nodes failed on 2026-11-03 ('Invalid argument')
BAD_NODES="b[5101,5103-5196,5203-5204,5207-5296]"
PLAN="$STATE/plan.txt"                    # LABEL YEAR CTRL_CASE CTRL_PARENT LCC_CASE LCC_PARENT NFILES DELETE TEST
CHAINS="$STATE/chains.txt"                # RUN CHAIN_START CASE
[[ $PLAN_ONLY -eq 1 ]] || mkdir -p "$STATE/logs"
touch_ok() { [[ $PLAN_ONLY -eq 1 ]] || "$@"; }

parent_of() {   # same table as branch_meganpatch.sh
    case "$1" in
        CTRL_PD)  echo NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20261029 ;;
        LCC_PD)   echo NF2000norbc_tropstratchem_nudg_lcc_f19_f19-20261028 ;;
        CTRL_FUT) echo NF2100ssp585norbc_tropstratchem_nudg_ctrl_f19_f19-20261028 ;;
        LCC_FUT)  echo NF2100ssp585norbc_tropstratchem_nudg_lcc_f19_f19-20261028 ;;
    esac
}
chain_of() {    # restarts of the parents: 2005, 2010, 2015 (2015 chain: extended met data, 2015-2019)
    if (( $1 >= 2000 && $1 <= 2004 )); then echo 2000      # hybrid from the spin-up, as the parent
    elif (( $1 >= 2005 && $1 <= 2009 )); then echo 2005
    elif (( $1 >= 2010 && $1 <= 2014 )); then echo 2010
    elif (( $1 >= 2015 && $1 <= 2019 )); then echo 2015
    else echo none; fi
}

build() {       # RUN START [--days N --resubmit K] -> echoes the case name
    local log="$STATE/logs/build_$1_$2$([[ -n "${3:-}" ]] && echo _test).log"
    bash "$HERE/branch_meganpatch.sh" "$@" > "$log" 2>&1 || { echo "ERROR: build failed, see $log" >&2; return 1; }
    tail -1 "$log" | sed -n 's/^CASE //p'
}

submit() {      # CASE -> echoes "run_id archive_id"
    local out
    out=$(env -i HOME="$HOME" USER="$USER" bash -l -c \
          "cd '$CASES/$1' && ./case.submit --batch-args='--exclude=$BAD_NODES'" 2>&1) || { echo "$out" >&2; return 1; }
    echo "$out" >> "$STATE/logs/submit_$1.log"
    grep -o 'case.submit success.*' "$CASES/$1/CaseStatus" | tail -1 | grep -o '[0-9]\{6,\}' | tr '\n' ' '
}

start_watcher() {
    [[ $PLAN_ONLY -eq 1 || $NO_SUBMIT -eq 1 ]] && return
    if [[ -f "$STATE/watcher.pid" ]] && kill -0 "$(cat "$STATE/watcher.pid")" 2>/dev/null; then
        echo "watcher already running (pid $(cat "$STATE/watcher.pid")); it reads the new plan lines"
    else
        nohup bash "$HERE/watch_megan_lmdi.sh" "$PERIOD" >> "$STATE/logs/watcher.log" 2>&1 &
        echo $! > "$STATE/watcher.pid"
        echo "watcher started (pid $!, $(hostname)), log $STATE/logs/watcher.log"
    fi
}

#–––––––––––– test –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
if [[ "$MODE" == test ]]; then
    grep -q '^PD_test60d ' "$PLAN" 2>/dev/null && { echo "test already in $PLAN" >&2; exit 1; }
    echo "production test: CTRL_PD + LCC_PD from 2005-01-01, 2 jobs x 30 days (to 2005-03-02), delete dry run"
    [[ $PLAN_ONLY -eq 1 ]] && exit 0
    C=$(build CTRL_PD 2005-01-01 --days 30 --resubmit 1); L=$(build LCC_PD 2005-01-01 --days 30 --resubmit 1)
    echo "built $C, $L"
    [[ $NO_SUBMIT -eq 1 ]] && exit 0
    echo "CTRL jobs $(submit "$C"); LCC jobs $(submit "$L")"
    echo "PD_test60d 2005 $C $(parent_of CTRL_PD) $L $(parent_of LCC_PD) 60 dry test" >> "$PLAN"
    start_watcher; exit 0
fi

#–––––––––––– batch: gate ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
PD_STATE="$ROOT/PD"
[[ -f "$PD_STATE/PD_test60d.ok" ]] || { echo "GATE: the production test has not passed ($PD_STATE/PD_test60d.ok)" >&2; exit 1; }
if [[ -f "$PLAN" ]]; then
    while read -r label _; do
        [[ "$label" == *test* ]] && continue
        [[ -f "$STATE/$label.failed" ]] && { echo "GATE: $label failed ($STATE/$label.failed)" >&2; exit 1; }
        [[ -f "$STATE/$label.ok" ]] || { echo "GATE: $label not reduced yet" >&2; exit 1; }
    done < "$PLAN"
fi

#–––––––––––– batch: years per chain –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
declare -A NY FIRST
for y in "${YEARS[@]}"; do
    c=$(chain_of "$y"); [[ $c == none ]] && { echo "$y: no restart chain (only 2000–2004, 2005–2009, 2010–2014, 2015–2019)" >&2; exit 1; }
    grep -q "^${PERIOD}_$y " "$PLAN" 2>/dev/null && { echo "$y already planned" >&2; exit 1; }
    NY[$c]=$(( ${NY[$c]:-0} + 1 )); FIRST[$c]=$(( ${FIRST[$c]:-9999} < y ? ${FIRST[$c]:-9999} : y ))
done
for c in "${!NY[@]}"; do      # contiguous within the chain
    for (( y = FIRST[$c]; y < FIRST[$c] + NY[$c]; y++ )); do
        [[ " ${YEARS[*]} " == *" $y "* ]] || { echo "chain $c: years must be contiguous (missing $y)" >&2; exit 1; }
    done
done

for c in $(echo "${!NY[@]}" | tr ' ' '\n' | sort); do
    n=${NY[$c]}; y0=${FIRST[$c]}
    declare -A CASE=()
    for veg in CTRL LCC; do
        run="${veg}_$PERIOD"
        existing=$(awk -v r="$run" -v s="$c" '$1 == r && $2 == s {print $3}' "$CHAINS" 2>/dev/null || true)
        if [[ -z "$existing" ]]; then
            [[ $y0 -eq $c ]] || { echo "$run chain $c does not exist yet: the first batch must start at $c" >&2; exit 1; }
            echo "$run: NEW chain case from $c-01-01, $n year(s) ($y0–$((y0 + n - 1))), RESUBMIT=$((n - 1))"
            [[ $PLAN_ONLY -eq 1 ]] && { CASE[$veg]="<new $run from$c>"; continue; }
            CASE[$veg]=$(build "$run" "$c-01-01")
            ( cd "$CASES/${CASE[$veg]}" && ./xmlchange RESUBMIT=$((n - 1)) )
            echo "$run $c ${CASE[$veg]}" >> "$CHAINS"
        else
            # the chain must stand at y0: its last archived restart is y0-01-01, and nothing of it is queued
            last=$(ls "$ARCHIVE/$existing/rest" 2>/dev/null | sort | tail -1)
            [[ "$last" == "$y0-01-01-00000" ]] || { echo "$existing stands at '${last:-nothing}', not $y0-01-01" >&2; exit 1; }
            squeue -u "$USER" -h -o '%Z' | grep -q "/$existing\$" && { echo "$existing has jobs queued" >&2; exit 1; }
            echo "$run: CONTINUE $existing from $y0-01-01, $n year(s), RESUBMIT=$((n - 1))"
            CASE[$veg]=$existing
            touch_ok bash -c "cd '$CASES/$existing' && ./xmlchange CONTINUE_RUN=TRUE,RESUBMIT=$((n - 1))"
        fi
    done
    for (( y = y0; y < y0 + n; y++ )); do
        # 2000 = spin-up year (dropped in all analyses): identity check, then raw files deleted, no split
        line="${PERIOD}_$y $y ${CASE[CTRL]} $(parent_of CTRL_$PERIOD) ${CASE[LCC]} $(parent_of LCC_$PERIOD) 365 $([[ $y -eq 2000 ]] && echo only || { [[ $KEEP_RAW -eq 1 ]] && echo no || echo yes; })"
        echo "plan: $line"
        [[ $PLAN_ONLY -eq 1 || $NO_SUBMIT -eq 1 ]] || PLAN_LINES+=("$line")
    done
    if [[ $PLAN_ONLY -eq 0 && $NO_SUBMIT -eq 0 ]]; then
        echo "${CASE[CTRL]}: jobs $(submit "${CASE[CTRL]}")"
        echo "${CASE[LCC]}: jobs $(submit "${CASE[LCC]}")"
    fi
    unset CASE
done
for l in "${PLAN_LINES[@]:-}"; do [[ -n "$l" ]] && echo "$l" >> "$PLAN"; done
start_watcher
