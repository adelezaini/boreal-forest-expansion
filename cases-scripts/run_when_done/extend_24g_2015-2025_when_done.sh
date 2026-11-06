#!/bin/bash
# LCC_FUT_fBVOClccFUT (24g) extension 2015 -> 2026-01-01 (user OK 2026-11-05 18:34), same steps as
# extend_nudg_runs_2015-2025.sh (switch_case_to_met_2000_2025 + extend_case), after its 2000-2014 run:
#   wait: case known (/cluster/work/users/$USER/run-24g/case), rest 2015-01-01 archived, nothing queued,
#         MET folder built (BUILD_OK) -> phase1 (5 yr); then rest 2020-01-01 archived, nothing queued -> phase2 (6 yr).
# Failed st_archive jobs: archive_guard.sh. Detached:
#   setsid nohup bash extend_24g_2015-2025_when_done.sh > /cluster/work/users/$USER/run-24g/extend.log 2>&1 < /dev/null &
# State: /cluster/work/users/$USER/run-24g/ext_phase{1,2}.ok, ext.err   Stop: touch .../run-24g/STOP_EXT
set -uo pipefail
CS=/cluster/home/adelez/BOREAL-FOREST-EXPANSION/cases-scripts
ST=/cluster/work/users/$USER/run-24g
ARCHIVE=/cluster/work/users/$USER/archive
BUILD_LOG=/cluster/work/users/$USER/met-ext/build_final_manual_20261105.log
EXCL="--exclude=b[5101,5103-5196,5203-5204,5207-5296]"
log() { echo "$(date '+%F %T') $*"; }
fail() { log "ERROR: $*"; echo "$*" > "$ST/ext.err"; exit 1; }
last_line() { grep -n "$2" "$1/CaseStatus" | tail -1 | cut -d: -f1; }
ready() {   # ready RESTDATE: restart archived, archive after the last run, nothing queued
    [[ -d "$ARCHIVE/$CASE/rest/$1" ]] || return 1
    squeue -u "$USER" -h -o %Z | grep -qx -- "$WD" && return 1
    local lr la; lr=$(last_line "$WD" 'case.run success'); la=$(last_line "$WD" 'st_archive success')
    (( ${la:-0} > ${lr:-0} ))
}
phase() {   # phase N RESTDATE NYEARS NEED_DAY
    env -i HOME="$HOME" USER="$USER" bash -l -c "cd '$CS' && export MET_END_YEAR=2026 SUBMIT_BATCH_ARGS='$EXCL' && source cases-setup.sh \
        && ( CHECK_ONLY=1 extend_case '$CASE' $3 '$2' ) && ( switch_case_to_met_2000_2025 '$CASE' '$2' '$4' ) && ( extend_case '$CASE' $3 '$2' )" \
        > "$ST/ext_phase$1.log" 2>&1 || fail "phase$1 failed (see ext_phase$1.log)"
    date '+%F %T' > "$ST/ext_phase$1.ok"; log "phase$1 submitted ($2, $3 yr)"
}
log "start ($(hostname), pid $$)"
until [[ -s "$ST/case" ]]; do [[ -f "$ST/STOP_EXT" ]] && exit 0; [[ -f "$ST/watch.err" ]] && fail "run_24g watcher failed: $(cat "$ST/watch.err")"; sleep 900; done
CASE=$(cat "$ST/case"); WD=$(realpath "$HOME/cases/BRL_FRST_XPSN/$CASE"); log "case $CASE"
if [[ ! -f "$ST/ext_phase1.ok" ]]; then
    until ready 2015-01-01-00000 && grep -q BUILD_OK "$BUILD_LOG"; do [[ -f "$ST/STOP_EXT" ]] && exit 0; sleep 900; done
    phase 1 2015-01-01-00000 5 2020-01-01; sleep 300
fi
if [[ ! -f "$ST/ext_phase2.ok" ]]; then
    until ready 2020-01-01-00000; do [[ -f "$ST/STOP_EXT" ]] && exit 0; sleep 900; done
    phase 2 2020-01-01-00000 6 2026-01-01
fi
log "done"
