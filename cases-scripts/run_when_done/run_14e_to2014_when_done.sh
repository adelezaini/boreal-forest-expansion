#!/bin/bash
# Extends LCC_PD_fBVOClccPD (14e) from 2008-01-01 to 2015-01-01 (7 yr; user OK 2026-11-04) once the
# 2003-2007 extension is processed, then processes the full run. Steps:
#   0. needs the 2003-2007 segment archived (CaseStatus 'st_archive success'; checked by extend_case),
#   1. submits the 7-yr extension from a clean login shell (extend_case, bad nodes excluded; CHECK_ONLY first),
#   2. waits for its archive job; checks 180 atm h0 files 2000-2014 and the 2015-01-01 restart,
#   3. copies the run to NIRD,
#   4. moves the 2001-2007 processed files aside to superseded/LCC_PD_fBVOClccPD_2001-2007/ (never overwriting),
#   5. postprocesses the whole run (2001-2014, all categories, 19 files),
#   6. reruns how_big_artefact_is_PD.ipynb in place,
#   7. updates the 14e row in CLAUDE.md and cases-scripts/run_aliases.csv (8 yr -> 15 yr).
# Result: run_when_done/pids/run_14e_to2014.{ok,err}; log run_when_done/logs/run_14e_to2014_when_done.log.
# Usage (login node, from cases-scripts/): nohup setsid bash run_when_done/run_14e_to2014_when_done.sh >> run_when_done/logs/run_14e_to2014_when_done.log 2>&1 &
# Skip step 0-1 (already submitted): bash ... RUN_JOBID ARCHIVE_JOBID
# Stop: kill the PID in run_when_done/pids/run_14e_to2014_when_done.pid.
set -uo pipefail

CASE=NF2000norbc_tropstratchem_nudg_lcc_fBVOClccPD_f19_f19-20261031
ALIAS=LCC_PD_fBVOClccPD
RESTDATE=2008-01-01
NYEARS=7
LAST_REST=2015-01-01-00000
EXCLUDE=--exclude=b5165,b5175,b5179,b5180   # nodes where python fails at job start (2026-11-03)
RAW=/cluster/work/users/adelez/archive
NIRD=/cluster/home/adelez/nird/BRL-FRST-XPSN_archive
REPO=/cluster/home/adelez/BOREAL-FOREST-EXPANSION
PY=/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python
PP=$REPO/data/processed-data/postprocessing
OLD=$PP/superseded/${ALIAS}_2001-2007
HERE=$REPO/diagnostics/fbvoc-prescription-artefact
RWD=$REPO/cases-scripts/run_when_done   # moved from diagnostics/fbvoc-prescription-artefact/ 2026-11-04
LOCK=/cluster/work/users/adelez/auto-launch/postprocess.lock   # shared with the auto-launcher's postprocessing
mkdir -p "$RWD/logs" "$RWD/pids"
echo $$ > "$RWD/pids/run_14e_to2014_when_done.pid"
rm -f "$RWD/pids/run_14e_to2014".{ok,err}
fail() { echo "$(date '+%F %T') ERROR: $*"; touch "$RWD/pids/run_14e_to2014.err"; exit 1; }
log() { echo "$(date '+%F %T') $*"; }

if [[ $# -eq 2 ]]; then
    RUN_JOB=$1; ARCHIVE_JOB=$2
else
    # 0. (no wait: the 2003-2007 segment is archived; its postprocessing reads only the archive, which the new
    #    run changes only at its own st_archive ~27 h later, and both postprocessings share the flock)

    # 1. Submit from a clean login shell (python fails at job start when submitted from the VS Code shell)
    CASEROOT=$(readlink -f "$HOME/cases/BRL_FRST_XPSN/$CASE")
    sub=$(env -i HOME="$HOME" USER="$USER" bash -l -c "
        cd '$REPO/cases-scripts' && source cases-setup.sh >/dev/null &&
        CHECK_ONLY=1 extend_case '$CASE' $NYEARS $RESTDATE &&
        SUBMIT_BATCH_ARGS='$EXCLUDE' extend_case '$CASE' $NYEARS $RESTDATE" 2>&1)
    echo "$sub"
    grep -q 'CHECK OK' <<< "$sub" || fail "extend_case check failed"
    line=$(grep 'case.submit success' "$CASEROOT/CaseStatus" | tail -1)
    RUN_JOB=$(sed -n 's/.*case.run:\([0-9]*\).*/\1/p' <<< "$line")
    ARCHIVE_JOB=$(sed -n 's/.*case.st_archive:\([0-9]*\).*/\1/p' <<< "$line")
    [[ -n $RUN_JOB && -n $ARCHIVE_JOB ]] || fail "no job ids in CaseStatus: $line"
    squeue -h -j "$RUN_JOB" >/dev/null 2>&1 || fail "run job $RUN_JOB not in queue"
    log "submitted: run $RUN_JOB, archive $ARCHIVE_JOB ($RESTDATE + $NYEARS yr)"
fi

# 2. Wait for the archive job; it never starts if the model run fails (afterok dependency)
log "waiting for $CASE (run $RUN_JOB, archive $ARCHIVE_JOB)"
while :; do
    reason=$(squeue -h -j $ARCHIVE_JOB -o %r 2>/dev/null)
    [[ -z $reason ]] && break
    [[ $reason == *DependencyNeverSatisfied* ]] && fail "model run failed (archive dependency never satisfied)"
    sleep 600
done
state=$(sacct -n -X -j $ARCHIVE_JOB -o State | head -1 | tr -d ' ')
n=$(ls "$RAW/$CASE/atm/hist/$CASE.cam.h0."20{0[0-9],1[0-4]}-*.nc 2>/dev/null | wc -l)
log "archive job: $state, atm h0 files 2000-2014: $n"
[[ $state == COMPLETED ]] || fail "archive job state $state"
[[ -d $RAW/$CASE/rest/$LAST_REST ]] || fail "restart $LAST_REST missing"
(( n == 180 )) || fail "expected 180 atm h0 files, found $n"

# 3. NIRD copy
rsync -ah --exclude='*_tmp.pid*.ncks.tmp' "$RAW/$CASE/" "$NIRD/$CASE/" || fail "rsync to NIRD"
log "copied to NIRD"

exec 9> "$LOCK"; log "waiting for postprocessing lock"; flock 9

# 4. Move the 2001-2007 files (+ logs) aside, never overwriting
shopt -s nullglob
mkdir -p "$OLD/logs"
for f in "$PP/${ALIAS}"_{atm,lnd}_*.nc; do
    [[ -e "$OLD/$(basename "$f")" ]] && fail "$OLD/$(basename "$f") exists, not overwritten"
    mv -n "$f" "$OLD/" || fail "mv $f"
    l="$PP/logs/$(basename "${f%_*.nc}").log"
    [[ -e $l ]] && { mv -n "$l" "$OLD/logs/" || fail "mv $l"; }
done
left=("$PP/${ALIAS}"_{atm,lnd}_*.nc)
(( ${#left[@]} == 0 )) || fail "old files left: ${left[*]}"
log "2001-2007 files moved to $OLD"

# 5. Postprocess the whole run (all categories), check 19 files spanning 2001-2014
cd "$REPO"
out=$(CASES="$ALIAS $CASE" bash postprocess/run_all_parallel.sh 10)
echo "$out"
grep -q '^FAILED' <<< "$out" && fail "some categories failed"
n=$(ls "$PP/${ALIAS}"_{atm,lnd}_*_2001-2014.nc 2>/dev/null | wc -l)
(( n == 19 )) || fail "expected 19 files *_2001-2014.nc, found $n"
flock -u 9
log "postprocessing done, $n files"

# 6. Notebook
$PY results/tables/logs/run_nb_inplace.py "$HERE/how_big_artefact_is_PD.ipynb" || fail "notebook failed (error saved in the notebook)"
log "notebook rerun"

# 7. CLAUDE.md and run_aliases.csv: 14e = 15 yr (2000-2014)
$PY - "$REPO" <<'EOF' || fail "CLAUDE.md / run_aliases.csv update"
import sys, pathlib, re
repo = pathlib.Path(sys.argv[1])
for path, pat, new in [
        (repo / 'CLAUDE.md', r'\*\*(?:3|8) yr \((?:2000–2002|2000–2007)\)\*\*',
         '**15 yr (2000–2014)** since the 2026-11-04 extension (user OK; '
         '`cases-scripts/run_when_done/run_14e_to2014_when_done.sh`); before that'),
        (repo / 'CLAUDE.md', r'and LCC_PD_fBVOClccPD \(14e; 8 yr since the 2026-11-03 extension\)\.|LCC_PD_fBVOClccPD \(14e\)\.',
         'LCC_PD_fBVOClccPD (14e) was one until its extension to 15 yr (2026-11-04).'),
        (repo / 'cases-scripts/run_aliases.csv', r',2000-200[27],-,LCC_PD_spinup -20261025,',
         ',2000-2014,-,LCC_PD_spinup -20261025,')]:
    s = path.read_text()
    s2, k = re.subn(pat, new, s, count=1)
    print(f'{path.name}: ' + ('updated' if k else f'pattern not found, NOT edited: {pat}'))
    if k: path.write_text(s2)
EOF
log "finished"
touch "$RWD/pids/run_14e_to2014.ok"
