#!/bin/bash

# Watcher for the MET extension (12d production, user 2026-11-04):
# after each segment, make sure it is archived (and segment 2 submitted), then fill the
# 2000-2025 nudging folder with every archived day.
#
#   1. wait until the case.run job RUN_JOBID has ended; stop if it did not COMPLETE;
#   2. wait until its st_archive job ARCH_JOBID has ended. If it did not COMPLETE (the b52xx
#      preproc nodes fail at random since 2026-11-03: 'Invalid argument' in shell/python
#      start-up), rerun st_archive ON THE LOGIN NODE: with --resubmit only if no MET case.run
#      job is queued and RESUBMIT > 0 (never a double segment);
#   3. build the folder (copy-nudging-data-to-inputForNudging-directory-2000-2025.sh --run,
#      --final after the last segment);
#   4. if a new MET case.run job is queued (segment 2), re-exec itself on it with --final.
# Detached:  nohup setsid bash met_ext_watch_and_build.sh RUN_JOBID ARCH_JOBID [--final] \
#                > /cluster/work/users/adelez/met-ext/watch_<RUN_JOBID>.log 2>&1 < /dev/null &
# State: /cluster/work/users/adelez/met-ext/watch_<RUN_JOBID>.{ok,err}; stop: touch .../met-ext/STOP

set -uo pipefail
RUN_JOBID="$1"; ARCH_JOBID="$2"; FINAL="${3:-}"
CASEROOT=/cluster/home/adelez/cases/BRL_FRST_XPSN/NF2000norbc_tropstratchem_met_f19_f19_20260422
STATE=/cluster/work/users/adelez/met-ext
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
TAG="$STATE/watch_$RUN_JOBID"
log() { echo "$(date '+%F %T') $*"; }
fail() { log "ERROR: $*"; echo "$*" > "$TAG.err"; exit 1; }
state() { sacct -X -n -P -j "$1" -o State 2>/dev/null | tail -1 | awk '{print $1}'; }
in_queue() { squeue -h -j "$1" 2>/dev/null | grep -q .; }
met_run_jobs() {   # queued case.run jobs of the MET case
    squeue -h -u "$USER" -o "%i|%Z|%o" | awk -F'|' -v c="/${CASEROOT##*/}" 'substr($2, length($2)-length(c)+1)==c && $3 ~ /\.case\.run/ {print $1}'
}
met_arch_jobs() {
    squeue -h -u "$USER" -o "%i|%Z|%o" | awk -F'|' -v c="/${CASEROOT##*/}" 'substr($2, length($2)-length(c)+1)==c && $3 ~ /case\.st_archive/ {print $1}'
}
wait_end() {   # wait until job $1 is out of the queue
    while in_queue "$1"; do
        [[ -e "$STATE/STOP" ]] && fail "STOP file"
        # an archive job whose dependency can never be met stays queued: treat as ended
        squeue -h -j "$1" -o "%r" | grep -q DependencyNeverSatisfied && { scancel "$1"; break; }
        sleep 300
    done
}

log "watching run $RUN_JOBID, archive $ARCH_JOBID ${FINAL}"
wait_end "$RUN_JOBID"
rs=$(state "$RUN_JOBID"); log "run $RUN_JOBID: $rs"
[[ "$rs" == COMPLETED ]] || fail "run $RUN_JOBID ended $rs: not archiving, not building"

wait_end "$ARCH_JOBID"
as=$(state "$ARCH_JOBID"); log "archive $ARCH_JOBID: $as"
if [[ "$as" != COMPLETED ]]; then
    cd "$CASEROOT" || fail "no caseroot"
    resub=$(./xmlquery --value RESUBMIT)
    queued=$(met_run_jobs)
    args=()
    if [[ -z "$queued" && "$resub" -gt 0 ]]; then args=(--resubmit); fi
    log "rerunning st_archive on the login node (RESUBMIT=$resub, queued MET runs: '${queued}', args: ${args[*]:-none})"
    n_ok=$(grep -c 'st_archive success' CaseStatus)
    env -i HOME="$HOME" USER="$USER" bash -l -c "cd '$CASEROOT' && ./case.st_archive ${args[*]:-}" \
        > "$STATE/st_archive_login_$RUN_JOBID.log" 2>&1 || fail "st_archive on login failed (see st_archive_login_$RUN_JOBID.log)"
    # count, not tail: with --resubmit the last CaseStatus lines are the resubmission (bug 2026-11-04)
    (( $(grep -c 'st_archive success' CaseStatus) > n_ok )) || fail "CaseStatus has no new st_archive success"
    log "st_archive on login OK"
fi

log "building the 2000-2025 folder ${FINAL}"
nice -n 10 bash "$HERE/copy-nudging-data-to-inputForNudging-directory-2000-2025.sh" --run $FINAL \
    > "$STATE/build_$RUN_JOBID.log" 2>&1 || fail "build failed (see build_$RUN_JOBID.log)"
grep 'BUILD_OK' "$STATE/build_$RUN_JOBID.log" | tee "$TAG.ok"

if [[ -z "$FINAL" ]]; then
    sleep 60
    nr=$(met_run_jobs | head -1); na=$(met_arch_jobs | head -1)
    [[ -n "$nr" && -n "$na" ]] || fail "segment 2 not found in the queue (run '$nr', archive '$na')"
    log "segment 2: run $nr, archive $na -> watching it (final build)"
    exec bash "$0" "$nr" "$na" --final > "$STATE/watch_$nr.log" 2>&1 < /dev/null
fi
log "done"
