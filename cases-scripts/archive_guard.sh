#!/bin/bash
# Archive guard (user 2026-11-05: "if archiving fails, correct it automatically").
# Every 10 min: every case.st_archive job of $USER that ended FAILED / NODE_FAIL / TIMEOUT /
# BOOT_FAIL / OUT_OF_MEMORY (since 2026-11-03 the b52xx preproc nodes die at start, exit 126)
# is rerun ON THIS LOGIN NODE, one at a time, exactly as CIME would have run it:
#     ./case.st_archive [--resubmit if RESUBMIT > 0]
# --resubmit continues the chain; CIME reads the node exclude from <case>/.submit_options.
# It acts only when ALL of these hold (otherwise it leaves the job alone):
#   - the case.run job the archive depended on (afterok:N) COMPLETED;
#   - no job of that case is queued or running;
#   - CaseStatus: the last 'case.run success' is after the last 'st_archive success'
#     (something is unarchived; if another watcher already fixed it, the job is marked done).
# One try per failed job: success -> <jobid>.ok, failure -> <jobid>.err (no retry, see log).
# Cancelled jobs (by hand, or dependency never satisfied) are ignored on purpose.
# Detached: setsid nohup bash archive_guard.sh > $STATE/guard.log 2>&1 < /dev/null &
# State/logs: /cluster/work/users/$USER/archive-guard/  Stop: touch .../archive-guard/STOP
# Status:     bash archive_guard.sh --check
set -uo pipefail
STATE=/cluster/work/users/$USER/archive-guard
SINCE="${ARCHIVE_GUARD_SINCE:-2026-11-04T12:00}"
mkdir -p "$STATE"
log() { echo "$(date '+%F %T') $*"; }

failed_archives() {   # JOBID|STATE|NODE|WORKDIR|SUBMITLINE for failed st_archive jobs
    sacct -u "$USER" -S "$SINCE" -X -n -P -o JobID,State,NodeList,WorkDir,SubmitLine 2>/dev/null \
        | awk -F'|' '$5 ~ /case\.st_archive/ && $2 ~ /^(FAILED|NODE_FAIL|TIMEOUT|BOOT_FAIL|OUT_OF_MEMORY)/'
}
last_line() { grep -n "$2" "$1/CaseStatus" | tail -1 | cut -d: -f1; }

if [[ "${1:-}" == --check ]]; then
    failed_archives | while IFS='|' read -r id st node wd _; do
        s=todo; [[ -f "$STATE/$id.ok" ]] && s=ok; [[ -f "$STATE/$id.err" ]] && s=ERR
        echo "$id $st $node $(basename "$wd"): $s"
    done
    exit 0
fi

exec 9> "$STATE/guard.lock"
flock -n 9 || { log "another guard holds $STATE/guard.lock"; exit 1; }
echo $$ > "$STATE/guard.pid"
log "archive guard start ($(hostname), pid $$, failed archives since $SINCE)"
while true; do
    [[ -f "$STATE/STOP" ]] && { log "STOP file found, exiting"; exit 0; }
    while IFS='|' read -r id st node wd sub; do
        [[ -f "$STATE/$id.ok" || -f "$STATE/$id.err" ]] && continue
        name=$(basename "$wd")
        [[ -f "$wd/CaseStatus" ]] || { log "$id $name: no CaseStatus in $wd, skipped"; echo "no CaseStatus" > "$STATE/$id.err"; continue; }
        squeue -u "$USER" -h -o %Z | grep -qx -- "$wd" && continue          # case busy: next round
        run=$(grep -o 'afterok:[0-9]*' <<< "$sub" | cut -d: -f2)
        if [[ -n "$run" ]]; then
            rs=$(sacct -n -X -j "$run" -o State 2>/dev/null | head -1 | tr -d ' ')
            [[ "$rs" == COMPLETED ]] || { log "$id $name: run $run is $rs, not archiving"; echo "run $run $rs" > "$STATE/$id.err"; continue; }
        fi
        lr=$(last_line "$wd" 'case.run success'); la=$(last_line "$wd" 'st_archive success')
        if [[ -z "$lr" ]] || (( ${la:-0} > lr )); then
            echo "already archived (CaseStatus)" > "$STATE/$id.ok"; log "$id $name: already archived, nothing to do"; continue
        fi
        resub=$(cd "$wd" && ./xmlquery --value RESUBMIT 2>/dev/null)
        args=""; [[ "${resub:-0}" -gt 0 ]] && args="--resubmit"
        log "$id $name: archive $st on $node -> ./case.st_archive $args on $(hostname) (RESUBMIT=$resub)"
        echo "$node" >> "$STATE/bad_nodes.txt"
        n_ok=$(grep -c 'st_archive success' "$wd/CaseStatus")
        env -i HOME="$HOME" USER="$USER" bash -l -c "cd '$wd' && ./case.st_archive $args" > "$STATE/$id.log" 2>&1
        rc=$?
        if [[ $rc -eq 0 ]] && (( $(grep -c 'st_archive success' "$wd/CaseStatus") > n_ok )); then
            log "$id $name: archived OK$([[ -n "$args" ]] && echo ', next segment submitted: '"$(grep -o 'Submitted job [a-z._]* with id [0-9]*' "$STATE/$id.log" | tr '\n' ' ')")"
            echo "ok $(date '+%F %T')" > "$STATE/$id.ok"
        else
            log "$id $name: ERROR, st_archive rc=$rc (see $STATE/$id.log)"; echo "rc=$rc" > "$STATE/$id.err"
        fi
    done < <(failed_archives)
    sleep "${ARCHIVE_GUARD_SLEEP:-600}"
done
