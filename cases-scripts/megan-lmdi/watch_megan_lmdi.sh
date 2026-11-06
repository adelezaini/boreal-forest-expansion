#!/bin/bash
# Watcher of the MEGAN exact-split runs (started by launch_megan_lmdi.sh with nohup on a login node).
# Every 10 min, for each line of /cluster/work/users/adelez/megan-lmdi/<PERIOD>/plan.txt
#   (LABEL YEAR CTRL_CASE CTRL_PARENT LCC_CASE LCC_PARENT NFILES DELETE [test]):
#   1. both runs have NFILES tape-2 files of YEAR in the work archive (= the year is archived)
#        -> postprocess/megan_lmdi/reduce_year_job.sh (identity, reduction, delete)          [LABEL.submitted]
#           on this login node (default, one at a time) or as sbatch job (MEGAN_LMDI_RUN=sbatch)
#   2. the job wrote LABEL.ok -> copy megan_lmdi_LABEL.nc + its log to NIRD
#        (data/processed-data/megan-lmdi/, cp -n + cmp), and the restarts of both cases
#        (archive rest/, no history copies) to BRL-FRST-XPSN_archive/<case>/rest/              [LABEL.copied]
#   A year waits until both parents have their own monthly output of it (2015+: parents' extension).
#   LABEL.failed (written by the job, or here if the job died) -> that year stops, raw files are kept.
# Exits when every plan line is copied or failed. Stop: touch <state>/STOP. Status: bash watch_megan_lmdi.sh PERIOD --check
set -uo pipefail
PERIOD="${1:?PD|FUT}"
ROOT="${MEGAN_LMDI_ROOT:-/cluster/work/users/$USER/megan-lmdi}"   # override only for tests
STATE="$ROOT/$PERIOD"
PLAN="$STATE/plan.txt"; OUT="$STATE/out"; LOGS="$STATE/logs"
ARCHIVE="/cluster/work/users/$USER/archive"
REPO=/cluster/home/adelez/BOREAL-FOREST-EXPANSION
NIRD_OUT="${MEGAN_LMDI_NIRD_OUT:-$REPO/data/processed-data/megan-lmdi}"   # override only for tests
JOB="$REPO/postprocess/megan_lmdi/reduce_year_job.sh"
BAD_NODES="b5165,b5175,b5179,b5180,b5203,b5204"   # jobs died at start there ("Invalid argument", 2026-11-03/04; b5204 st_archive exit 126, 2026-11-04/05)
# login (default): the reduction runs on this login node, one year at a time (single-core, ≈ 26 s per model day
# → ≈ 3 h per year). sbatch: preproc job; on 2026-11-04 even a trivial module-load job hung on preproc.
RUN_MODE="${MEGAN_LMDI_RUN:-login}"
mkdir -p "$OUT" "$LOGS"
log() { echo "$(date '+%F %T') $*"; }

nfiles() { ls "$ARCHIVE/$1/lnd/hist/$1.clm2.h1.$2-"*.nc 2>/dev/null | wc -l; }
# the parent must have its own output of that period, or the identity check has nothing to compare
# (2015+: only after the parents' 2015-2025 extension)
parent_has() { [[ -f "$ARCHIVE/$1/atm/hist/$1.cam.h0.$2.nc" ]]; }
NIRD_ARCHIVE="${MEGAN_LMDI_NIRD_REST:-/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive}"   # override only for tests
# restarts of the branch cases (one per model year = end of each job and batch) -> NIRD, without history copies
copy_rest() {
    mkdir -p "$NIRD_ARCHIVE/$1/rest" && rsync -a --exclude='*.h0.*' --exclude='*.h1.*' --exclude='*.h0[a-z]*' \
        "$ARCHIVE/$1/rest/" "$NIRD_ARCHIVE/$1/rest/"
}

status() {
    while read -r label year ctrl _ lcc _ n _; do
        s=planned
        for f in submitted ok copied failed; do [[ -f "$STATE/$label.$f" ]] && s=$f; done
        echo "$label: $s (archived tape-2 files: CTRL $(nfiles "$ctrl" "$year")/$n, LCC $(nfiles "$lcc" "$year")/$n)"
    done < "$PLAN"
}
if [[ "${2:-}" == --check ]]; then status; exit 0; fi

exec 9> "$STATE/watcher.lock"
flock -n 9 || { log "another watcher holds $STATE/watcher.lock"; exit 1; }
log "watcher start ($PERIOD, $(hostname), pid $$)"
while true; do
    [[ -f "$STATE/STOP" ]] && { log "STOP file found, exiting"; exit 0; }
    pending=0
    while read -r label year ctrl cparent lcc lparent n del test; do
        [[ -f "$STATE/$label.copied" || -f "$STATE/$label.failed" ]] && continue
        pending=1
        if [[ ! -f "$STATE/$label.submitted" ]]; then
            lastmonth=$([[ -n "${test:-}" ]] && echo "$year-01" || echo "$year-12")
            if [[ $(nfiles "$ctrl" "$year") -ge $n && $(nfiles "$lcc" "$year") -ge $n ]] \
               && parent_has "$cparent" "$lastmonth" && parent_has "$lparent" "$lastmonth"; then
                args=("$label" "$year" "$ctrl" "$cparent" "$lcc" "$lparent" "$del" "$OUT" "$STATE" ${test:-})
                if [[ "$RUN_MODE" == login ]]; then
                    # one reduction at a time on this login node, clean login environment (module Python)
                    busy=0
                    for f in "$STATE"/*.submitted; do
                        [[ -f "$f" ]] || continue; l=$(basename "$f" .submitted); p=$(sed -n 's/^pid://p' "$f")
                        [[ -n "$p" && ! -f "$STATE/$l.ok" && ! -f "$STATE/$l.failed" ]] && kill -0 "$p" 2>/dev/null && busy=1
                    done
                    if [[ $busy -eq 0 ]]; then
                        env -i HOME="$HOME" USER="$USER" bash -l "$JOB" "${args[@]}" > "$LOGS/$label.login.log" 2>&1 &
                        echo "pid:$!" > "$STATE/$label.submitted"; log "$label: reduction started on $(hostname), pid $!"
                    fi
                else
                    id=$(sbatch --parsable --exclude="$BAD_NODES" -o "$LOGS/$label.%j.log" "$JOB" "${args[@]}") \
                        && { echo "$id" > "$STATE/$label.submitted"; log "$label: reduction job $id submitted"; } \
                        || log "$label: sbatch failed, retry next round"
                fi
            fi
        elif [[ -f "$STATE/$label.ok" && "$del" == only ]]; then      # 2000: no split, restarts only
            copy_rest "$ctrl" && copy_rest "$lcc" && { touch "$STATE/$label.copied"; log "$label: identity OK, raw deleted, restarts copied"; }
        elif [[ -f "$STATE/$label.ok" ]]; then
            mkdir -p "$NIRD_OUT/logs"
            f="$OUT/megan_lmdi_$label.nc"
            if cp -n "$f" "$NIRD_OUT/" && cmp -s "$f" "$NIRD_OUT/$(basename "$f")" && copy_rest "$ctrl" && copy_rest "$lcc"; then
                cp -n "$LOGS/$label".*log "$NIRD_OUT/logs/" 2>/dev/null
                touch "$STATE/$label.copied"; log "$label: done, copied to $NIRD_OUT; restarts of both cases to $NIRD_ARCHIVE"
            else
                log "$label: copy to NIRD failed (or a different file exists there), retry next round"
            fi
        else
            id=$(cat "$STATE/$label.submitted")
            if [[ "$id" == pid:* ]]; then          # login-node run
                kill -0 "${id#pid:}" 2>/dev/null || { sleep 5; [[ -f "$STATE/$label.ok" ]] || {
                    echo "process ${id#pid:} ended without .ok" > "$STATE/$label.failed"; log "$label: FAILED (see log)"; }; }
                continue
            fi
            st=$(sacct -n -X -j "$id" -o State 2>/dev/null | head -1 | tr -d ' ')
            case "$st" in
                PENDING|RUNNING|REQUEUED|"") ;;
                *) [[ -f "$STATE/$label.ok" ]] || { echo "job $id ended $st without .ok" > "$STATE/$label.failed";
                                                     log "$label: job $id $st, no .ok -> FAILED"; } ;;
            esac
        fi
    done < "$PLAN"
    [[ $pending -eq 0 ]] && { log "all plan lines done or failed, exiting"; status; exit 0; }
    sleep "${MEGAN_LMDI_SLEEP:-600}"
done
