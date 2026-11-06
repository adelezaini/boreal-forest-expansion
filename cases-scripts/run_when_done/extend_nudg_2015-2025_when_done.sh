#!/bin/bash
# Extension of the 11 nudged runs (10 + LCC_PD_fBVOClccPD, user 2026-11-05 18:12) to 2026-01-01, automatic (user OK 2026-11-05 17:25).
#   1. wait for the final build of the 2000-2025 MET folder: BUILD_OK in BUILD_LOG (BUILD_PID is only checked
#      when it runs on this node; '-' = log only), error after 24 h without BUILD_OK;
#   2. phase1 (2015 -> 2020) for all runs: extend_nudg_runs_2015-2025.sh phase1 --check, then submit;
#   3. per run, as soon as its phase1 is archived (rpointer 2020-01-01 + a 'st_archive success' after the
#      last 'case.run success', nothing queued): phase2 (2020 -> 2026) for that run only (--case).
#      A failed phase1 archive is fixed by cases-scripts/archive_guard.sh; this script just waits.
#      A run that stops with no job queued and no 2020 restart -> phase2_<case>.failed, the others go on.
# Detached: setsid nohup bash extend_nudg_2015-2025_when_done.sh BUILD_PID BUILD_LOG > $STATE/watch.log 2>&1 < /dev/null &
# State: /cluster/work/users/$USER/nudg-ext/   Stop: touch .../nudg-ext/STOP   Status: ls .../nudg-ext; tail watch.log
set -uo pipefail
BUILD_PID="${1:?BUILD_PID}"; BUILD_LOG="${2:?BUILD_LOG}"
CS=/cluster/home/adelez/BOREAL-FOREST-EXPANSION/cases-scripts
SCRIPT="$CS/extend_nudg_runs_2015-2025.sh"
STATE=/cluster/work/users/$USER/nudg-ext
CASEDIR=/cluster/home/adelez/cases/BRL_FRST_XPSN
mkdir -p "$STATE"
log() { echo "$(date '+%F %T') $*"; }
fail() { log "ERROR: $*"; echo "$*" > "$STATE/watch.err"; exit 1; }
ext() { env -i HOME="$HOME" USER="$USER" bash -l -c "cd '$CS' && bash '$SCRIPT' $*"; }
last_line() { grep -n "$2" "$1/CaseStatus" | tail -1 | cut -d: -f1; }

exec 9> "$STATE/watch.lock"; flock -n 9 || fail "another watcher holds the lock"
log "start ($(hostname), pid $$); waiting for MET folder build pid $BUILD_PID"
t0=$(date +%s)
until grep -q BUILD_OK "$BUILD_LOG" 2>/dev/null; do
    [[ -f "$STATE/STOP" ]] && { log "STOP file, exiting"; exit 0; }
    [[ "$BUILD_PID" != - ]] && ! kill -0 "$BUILD_PID" 2>/dev/null && { sleep 30; grep -q BUILD_OK "$BUILD_LOG" || fail "MET folder build ended without BUILD_OK (see $BUILD_LOG)"; }
    (( $(date +%s) - t0 > 86400 )) && fail "no BUILD_OK after 24 h (see $BUILD_LOG)"
    sleep 300
done
log "MET folder build OK: $(grep BUILD_OK "$BUILD_LOG" | tail -1)"

mapfile -t CASES < <(sed -n '/^CASES=(/,/^)/p' "$SCRIPT" | grep -o '^ *"NF[^"]*"' | tr -d ' "')
(( ${#CASES[@]} == 11 )) || fail "expected 11 cases in $SCRIPT, found ${#CASES[@]}"

if [[ ! -f "$STATE/phase1.submitted" ]]; then
    ext phase1 --check > "$STATE/phase1_check.log" 2>&1 || fail "phase1 --check failed (see phase1_check.log)"
    log "phase1 checks OK"
    ext phase1 > "$STATE/phase1_submit.log" 2>&1 || fail "phase1 submission failed (see phase1_submit.log; earlier cases may be submitted)"
    date '+%F %T' > "$STATE/phase1.submitted"; log "phase1 submitted for ${#CASES[@]} runs"
    sleep 120
fi

while true; do
    [[ -f "$STATE/STOP" ]] && { log "STOP file, exiting"; exit 0; }
    left=0
    for c in "${CASES[@]}"; do
        [[ -f "$STATE/phase2_$c.submitted" || -f "$STATE/phase2_$c.failed" ]] && continue
        left=1
        wd=$(realpath "$CASEDIR/$c")
        squeue -u "$USER" -h -o %Z | grep -qx -- "$wd" && continue
        rundir=$(cd "$wd" && ./xmlquery --value RUNDIR)
        if ! grep -q 2020-01-01-00000 "$rundir/rpointer.atm"; then
            echo "phase1 stopped, rpointer: $(head -1 "$rundir/rpointer.atm")" > "$STATE/phase2_$c.failed"
            log "$c: FAILED, no job queued and no 2020 restart (see CaseStatus)"; continue
        fi
        lr=$(last_line "$wd" 'case.run success'); la=$(last_line "$wd" 'st_archive success')
        (( ${la:-0} > ${lr:-0} )) || continue                              # archive not done yet (guard fixes failures)
        if ext phase2 --check --case "$c" > "$STATE/phase2_$c.log" 2>&1 && ext phase2 --case "$c" >> "$STATE/phase2_$c.log" 2>&1; then
            date '+%F %T' > "$STATE/phase2_$c.submitted"; log "$c: phase2 submitted (2020 -> 2026)"
        else
            echo "see phase2_$c.log" > "$STATE/phase2_$c.failed"; log "$c: phase2 check/submit FAILED (see phase2_$c.log)"
        fi
    done
    (( left == 0 )) && { log "phase2 handled for all runs, exiting"; exit 0; }
    sleep 900
done
