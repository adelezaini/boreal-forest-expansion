#!/bin/bash
# MET + 12 nudged runs 2026-2040, fully automatic (user 2026-11-11; plan approved 2026-11-15).
# Record of the whole workflow: docs/met-nudg-2026-2040.md (this script appends job ids to its "Job log").
#
# Every 10 min:
#   1. MET job k archived (k = 1, 2, 3: last h1 file of the job in the work archive and a 'st_archive
#      success' after the last 'case.run success'; archive_guard.sh fixes failed archive jobs):
#        k = 1: GATE first (12e-NF2000norbc_tropstratchem_met_ext_2026-2040_f19_f19.sh --gate: new h1 2026-01-01-21600 = original);
#               a mismatch halts everything (GATE.failed, exit) before any nudged run is submitted;
#        sbatch preprocess/nudging/build_met_2000-2040_job.sh (--final for k = 3) -> BUILD_OK in its log.
#   2. per run, next phase (A 2026->31, B 31->36, C 36->41) via extend_nudg_runs_2026-2040.sh <phase> --case,
#      --check first, when: the 2000-2040 list reaches the phase end, the previous phase is archived
#      (rpointer at the phase start + st_archive success after the last case.run success), nothing queued.
#      A run that stops with no job queued and its restart not advanced -> <phase>_<case>.failed; the others go on.
#   3. run at 2041-01-01 and archived: NIRD rsync, then postprocessing 2001-2040 in the background, in 2 queues
#      (flock pp.lock.0 / pp.lock.1, runs alternate by list position; the 12 runs end within hours of each other,
#      so one queue would take ~30 h): run_all_parallel.sh 6 jobs, one retry of failed jobs,
#      OUT_PATH = postprocessing-2001-2040-staging, 19 files per run.
#   4. MET done (build 3 OK): NIRD rsync of MET.
#   5. all 12 runs postprocessed: start run_when_done/analysis_2001-2040_when_done.sh (detached) and exit.
# Detached: setsid nohup bash met_nudg_2026-2040_when_done.sh > $STATE/watch.log 2>&1 < /dev/null &
# Dry run (prints what it would do, changes nothing, one pass): bash met_nudg_2026-2040_when_done.sh --once --dry
# State: /cluster/work/users/adelez/met-nudg-2040/   Stop: touch .../STOP   Status: ls ...; tail watch.log
set -uo pipefail
ONCE=0; DRY=0
for a in "$@"; do case "$a" in --once) ONCE=1 ;; --dry) DRY=1 ;; *) echo "unknown argument $a" >&2; exit 1 ;; esac; done

REPO=/cluster/home/adelez/BOREAL-FOREST-EXPANSION
CS=$REPO/cases-scripts
SCRIPT=$CS/extend_nudg_runs_2026-2040.sh
STATE=/cluster/work/users/$USER/met-nudg-2040
CASEDIR=/cluster/home/adelez/cases/BRL_FRST_XPSN
ARCHIVE=/cluster/work/users/$USER/archive
NIRD=/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive
MET=NF2000norbc_tropstratchem_met_f19_f19_20260422
METLIST=/cluster/shared/noresm/inputdata/noresm-only/inputForNudging/AZ/${MET}_6h_2000-2040/${MET}.cam.h1_filelist_2000-2040.txt
STG=/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN/data/processed-data/postprocessing-2001-2040-staging
RECORD=$REPO/docs/met-nudg-2026-2040.md
BADNODES="b[5101,5103-5196,5203-5204,5207-5296]"   # same exclude list as the model jobs (preproc b5203/b5204 failed 4-5 Nov)
PP_NJOBS=6                                         # per postprocessing queue; 2 queues -> 12 at a time on the login node
mkdir -p "$STATE"

log() { echo "$(date '+%F %T') $*"; }
fail() { log "ERROR: $*"; echo "$(date '+%F %T') $*" > "$STATE/watch.err"; exit 1; }
record() { (( DRY )) || echo "- $(date '+%F %T') $*" >> "$RECORD"; }
ext() { env -i HOME="$HOME" USER="$USER" bash -l -c "cd '$CS' && bash '$SCRIPT' $*"; }
last_line() { grep -n "$2" "$1/CaseStatus" | tail -1 | cut -d: -f1; }
archived() { local lr la; lr=$(last_line "$1" 'case.run success'); la=$(last_line "$1" 'st_archive success'); (( ${la:-0} > ${lr:-0} )); }
queued() { squeue -u "$USER" -h -o %Z | grep -qx -- "$(realpath "$1")"; }
list_last() { [[ -f "$METLIST" ]] && tail -n 1 "$METLIST" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}-00000\.nc$' | cut -c1-10; }
alias_of() { grep -F " $1" "$STATE/aliases.txt" | cut -d' ' -f1; }

exec 9> "$STATE/watch.lock"; flock -n 9 || fail "another watcher holds the lock"
log "start ($(hostname), pid $$, once=$ONCE dry=$DRY)"

mapfile -t CASES < <(sed -n '/^CASES=(/,/^)/p' "$SCRIPT" | grep -o '^ *"NF[^"]*"' | tr -d ' "')
(( ${#CASES[@]} == 12 )) || fail "expected 12 cases in $SCRIPT, found ${#CASES[@]}"
# alias + case (same list as the 2001-2025 staging, + 24g)
cat > "$STATE/aliases.txt" <<'EOF'
CTRL_PD NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20261029
LCC_PD NF2000norbc_tropstratchem_nudg_lcc_f19_f19-20261028
CTRL_FUT NF2100ssp585norbc_tropstratchem_nudg_ctrl_f19_f19-20261028
LCC_FUT NF2100ssp585norbc_tropstratchem_nudg_lcc_f19_f19-20261028
LCC_PD_fBVOCctrlPD NF2000norbc_tropstratchem_nudg_lcc_fBVOCctrlPD_f19_f19-20261031
CTRL_PD_fBVOCctrlPD NF2000norbc_tropstratchem_nudg_ctrl_fBVOCctrlPD_f19_f19-20261031
LCC_PD_fBVOClccPD NF2000norbc_tropstratchem_nudg_lcc_fBVOClccPD_f19_f19-20261031
CTRL_FUT_fBVOCctrlFUT NF2100ssp585norbc_tropstratchem_nudg_ctrl_fBVOCctrlFUT_f19_f19-20261031
LCC_FUT_fBVOCctrlFUT NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOCctrlFUT_f19_f19-20261031
LCC_FUT_fBVOCctrlPD NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOCctrlPD_f19_f19-20261031
LCC_FUT_fBVOClccPD NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOClccPD_f19_f19-20261031
LCC_FUT_fBVOClccFUT NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOClccFUT_f19_f19-20261106
EOF
for c in "${CASES[@]}"; do [[ -n "$(alias_of "$c")" ]] || fail "no alias for $c"; done

# MET job k: last h1 file it archives; restart date the nudged phase starts from; phase end day
JOB_END_H1=( "" 2031-12-31-21600 2037-12-31-21600 2041-01-01-21600 )
declare -A PH_START=( [A]=2026-01-01-00000 [B]=2031-01-01-00000 [C]=2036-01-01-00000 )
declare -A PH_END=( [A]=2031-01-01 [B]=2036-01-01 [C]=2041-01-01 )
declare -A PH_PREV=( [B]=A [C]=B )

met_step() {
    local wd="$CASEDIR/$MET" k
    [[ -f "$STATE/met.submitted" ]] || { log "MET: not submitted yet (12e-NF2000norbc_tropstratchem_met_ext_2026-2040_f19_f19.sh)"; return; }
    for k in 1 2 3; do
        [[ -f "$STATE/build$k.ok" ]] && continue
        [[ -f "$STATE/build$k.failed" ]] && return
        if [[ -f "$STATE/build$k.jobid" ]]; then           # build submitted: done?
            local jid; jid=$(cat "$STATE/build$k.jobid")
            if grep -q BUILD_OK "$STATE/build_met_2000-2040_$jid.log" 2>/dev/null; then
                touch "$STATE/build$k.ok"; log "MET build $k OK: $(grep BUILD_OK "$STATE/build_met_2000-2040_$jid.log")"
                record "nudging build $k (job $jid) BUILD_OK, list ends $(list_last)"
                if (( k == 3 )) && (( ! DRY )); then
                    rsync -ah --exclude='*_tmp.pid*.ncks.tmp' "$ARCHIVE/$MET/" "$NIRD/$MET/" > "$STATE/rsync_MET.log" 2>&1 \
                        && { log "MET: NIRD rsync OK"; record "MET archive copied to NIRD"; } || log "MET: NIRD rsync FAILED (see rsync_MET.log)"
                fi
                continue
            fi
            squeue -h -j "$jid" 2>/dev/null | grep -q . && return   # still queued/running
            echo "build job $jid ended without BUILD_OK" > "$STATE/build$k.failed"; log "MET build $k FAILED (job $jid)"; return
        fi
        # MET job k archived?
        [[ -f "$ARCHIVE/$MET/atm/hist/$MET.cam.h1.${JOB_END_H1[$k]}.nc" ]] || return
        archived "$wd" || return
        if (( k == 1 )) && [[ ! -f "$STATE/gate.ok" ]]; then
            if (( DRY )); then log "DRY: would run the gate"; return; fi
            if bash "$CS/12e-NF2000norbc_tropstratchem_met_ext_2026-2040_f19_f19.sh" --gate > "$STATE/gate.log" 2>&1; then
                touch "$STATE/gate.ok"; log "GATE OK: $(tail -1 "$STATE/gate.log")"; record "gate OK: $(tail -1 "$STATE/gate.log")"
            else
                cp "$STATE/gate.log" "$STATE/GATE.failed"; record "GATE FAILED: $(tail -1 "$STATE/gate.log") - watcher stopped"
                fail "GATE FAILED: the continuation does not reproduce MET (see gate.log); nothing nudged submitted"
            fi
        fi
        local fin=(); (( k == 3 )) && fin=(--final)
        if (( DRY )); then log "DRY: would sbatch build $k ${fin[*]}"; return; fi
        local jid; jid=$(sbatch --parsable --exclude="$BADNODES" "$REPO/preprocess/nudging/build_met_2000-2040_job.sh" "${fin[@]}") || { log "sbatch build $k failed"; return; }
        echo "$jid" > "$STATE/build$k.jobid"; log "MET job $k archived -> build $k submitted (job $jid)"
        record "MET job $k archived; nudging build $k submitted (job $jid)"
        return
    done
}

run_step() {   # one nudged run
    local c=$1 wd="$CASEDIR/$1" p rundir
    [[ -f "$STATE/done_$c" ]] && return
    queued "$wd" && return
    rundir=$(cd "$wd" && ./xmlquery --value RUNDIR)
    for p in A B C; do
        [[ -f "$STATE/phase${p}_$c.failed" ]] && return
        [[ -f "$STATE/phase${p}_$c.submitted" ]] && continue
        # previous phase finished and archived?
        if [[ -n "${PH_PREV[$p]:-}" ]]; then
            if ! grep -q "${PH_START[$p]}" "$rundir/rpointer.atm"; then
                echo "phase ${PH_PREV[$p]} stopped, rpointer: $(head -1 "$rundir/rpointer.atm")" > "$STATE/phase${PH_PREV[$p]}_$c.failed"
                log "$c: phase ${PH_PREV[$p]} FAILED (no job queued, restart not advanced)"; record "$(alias_of "$c"): phase ${PH_PREV[$p]} FAILED"; return
            fi
            archived "$wd" || return
        fi
        local last; last=$(list_last)
        [[ -n "$last" && ! "$last" < "${PH_END[$p]}" ]] || return     # MET days not there yet
        if (( DRY )); then log "DRY: $c would get phase $p (list ends $last)"; return; fi
        if ext "phase$p" --check --case "$c" > "$STATE/phase${p}_$c.log" 2>&1 && ext "phase$p" --case "$c" >> "$STATE/phase${p}_$c.log" 2>&1; then
            date '+%F %T' > "$STATE/phase${p}_$c.submitted"
            local ids; ids=$(grep -oE 'Submitted job [^ ]+ with id [0-9]+' "$STATE/phase${p}_$c.log" | awk '{print $3"="$6}' | tr '\n' ' ')
            log "$c: phase $p submitted ($ids)"; record "$(alias_of "$c"): phase $p submitted ($ids)"
        else
            echo "see phase${p}_$c.log" > "$STATE/phase${p}_$c.failed"
            log "$c: phase $p check/submit FAILED (see phase${p}_$c.log)"; record "$(alias_of "$c"): phase $p check/submit FAILED"
        fi
        return
    done
    # all three phases submitted: done?
    if ! grep -q 2041-01-01-00000 "$rundir/rpointer.atm"; then
        echo "phase C stopped, rpointer: $(head -1 "$rundir/rpointer.atm")" > "$STATE/phaseC_$c.failed"
        log "$c: phase C FAILED"; record "$(alias_of "$c"): phase C FAILED"; return
    fi
    archived "$wd" || return
    if (( DRY )); then log "DRY: $c done -> would rsync + postprocess"; return; fi
    touch "$STATE/done_$c"; log "$c: at 2041-01-01, archived"; record "$(alias_of "$c"): reached 2041-01-01, archived"
    local a q i; a=$(alias_of "$c")
    for i in "${!CASES[@]}"; do [[ "${CASES[$i]}" == "$c" ]] && q=$(( i % 2 )); done
    # NIRD copy, then postprocessing; background, one run at a time
    setsid bash -c "
        flock 8
        rsync -ah --exclude='*_tmp.pid*.ncks.tmp' '$ARCHIVE/$c/' '$NIRD/$c/' > '$STATE/rsync_$a.log' 2>&1 || { echo rsync > '$STATE/pp_$a.err'; exit 1; }
        mkdir -p '$STG'
        cd '$REPO/postprocess' && OUT_PATH='$STG' CASES='$a $c' bash run_all_parallel.sh $PP_NJOBS > '$STATE/pp_$a.log' 2>&1
        grep -q '^FAILED' '$STATE/pp_$a.log' && OUT_PATH='$STG' CASES='$a $c' bash run_all_parallel.sh 4 > '$STATE/pp_${a}_retry.log' 2>&1
        n=\$(ls '$STG'/${a}_{atm,lnd}_*_2001-2040.nc 2>/dev/null | wc -l)
        if (( n == 19 )); then touch '$STATE/pp_$a.ok'; else echo \"\$n files\" > '$STATE/pp_$a.err'; fi
    " 8> "$STATE/pp.lock.$q" < /dev/null > /dev/null 2>&1 &
    log "$c: NIRD rsync + postprocessing started in the background, queue $q (pp_$a.{ok,err})"
}

while true; do
    [[ -f "$STATE/STOP" ]] && { log "STOP file, exiting"; exit 0; }
    met_step
    if [[ -f "$STATE/gate.ok" ]] || (( DRY )); then
        for c in "${CASES[@]}"; do run_step "$c"; done
    fi
    nok=0; nend=0
    while read -r a c; do
        [[ -f "$STATE/pp_$a.ok" ]] && nok=$((nok+1))
        [[ -f "$STATE/pp_$a.ok" || -f "$STATE/pp_$a.err" || -n "$(ls "$STATE"/phase?_"$c".failed 2>/dev/null)" ]] && nend=$((nend+1))
    done < "$STATE/aliases.txt"
    if (( nend == 12 )); then
        if (( nok == 12 )) && [[ -f "$STATE/build3.ok" ]]; then
            log "all 12 runs postprocessed -> starting the 2001-2040 analysis"; record "all 12 runs postprocessed (228 files); analysis_2001-2040_when_done.sh started"
            (( DRY )) || setsid nohup bash "$CS/run_when_done/analysis_2001-2040_when_done.sh" > /dev/null 2>&1 < /dev/null &
            exit 0
        fi
        (( nok < 12 )) && fail "all runs ended but only $nok/12 postprocessed: see *.failed / pp_*.err in $STATE"
    fi
    (( ONCE )) && { log "--once: one pass done"; exit 0; }
    sleep 600
done
