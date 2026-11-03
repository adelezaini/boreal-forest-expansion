#!/bin/bash
# Waits for the 5-yr extension of LCC_PD_fBVOClccPD (2003-2007; user OK 2026-11-03; case.run 1787416 ->
# case.st_archive 1787417), then:
#   1. copies the run to NIRD (same rsync as the auto-launcher),
#   2. moves the old 2001-2002 processed files of the alias aside (new-chain files, so NOT into the
#      pre-co2-fix folders) to data/processed-data/postprocessing/superseded/LCC_PD_fBVOClccPD_2001-2002/,
#   3. postprocesses the whole run (2000-2007, first 12 months dropped -> 2001-2007; all categories, 19 files),
#   4. reruns how_big_artefact_is_PD.ipynb in place (its comparison years follow the processed span),
#   5. updates the LCC_PD_fBVOClccPD (14e) row in CLAUDE.md and cases-scripts/run_aliases.csv (3 yr -> 8 yr).
# Result: run_when_done/pids/run_14e_extension.{ok,err}; log run_when_done/logs/run_14e_extension_when_done.log.
# Usage (login node): nohup bash run_when_done/run_14e_extension_when_done.sh RUN_JOBID ARCHIVE_JOBID >> run_when_done/logs/run_14e_extension_when_done.log 2>&1 &
# (job ids from the last 'case.submit success case.run:<id>, case.st_archive:<id>' line of the case's CaseStatus)
# 2026-11-03: first submission 1787416 failed at start ('/usr/bin/env: python: Invalid argument', submitted from the
# Claude/VS Code shell); resubmitted from a clean login environment: env -i HOME=$HOME USER=$USER bash -l -c './case.submit'.
# Stop: kill the PID in run_when_done/pids/run_14e_extension_when_done.pid.
set -uo pipefail

CASE=NF2000norbc_tropstratchem_nudg_lcc_fBVOClccPD_f19_f19-20261031
ALIAS=LCC_PD_fBVOClccPD
RUN_JOB=$1
ARCHIVE_JOB=$2
LAST_REST=2008-01-01-00000
RAW=/cluster/work/users/adelez/archive
NIRD=/cluster/home/adelez/nird/BRL-FRST-XPSN_archive
REPO=/cluster/home/adelez/BOREAL-FOREST-EXPANSION
PY=/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python
PP=$REPO/data/processed-data/postprocessing
OLD=$PP/superseded/${ALIAS}_2001-2002
HERE=$REPO/diagnostics/fbvoc-prescription-artefact
RWD=$HERE/run_when_done
LOCK=/cluster/work/users/adelez/auto-launch/postprocess.lock   # shared with the auto-launcher's postprocessing
mkdir -p "$RWD/logs" "$RWD/pids"
echo $$ > "$RWD/pids/run_14e_extension_when_done.pid"
rm -f "$RWD/pids/run_14e_extension".{ok,err}
fail() { echo "$(date '+%F %T') ERROR: $*"; touch "$RWD/pids/run_14e_extension.err"; exit 1; }
log() { echo "$(date '+%F %T') $*"; }

# 1. Wait for the archive job; it never starts if the model run fails (afterok dependency)
log "waiting for $CASE (run $RUN_JOB, archive $ARCHIVE_JOB)"
while :; do
    reason=$(squeue -h -j $ARCHIVE_JOB -o %r 2>/dev/null)
    [[ -z $reason ]] && break
    [[ $reason == *DependencyNeverSatisfied* ]] && fail "model run failed (archive dependency never satisfied)"
    sleep 600
done
state=$(sacct -n -X -j $ARCHIVE_JOB -o State | head -1 | tr -d ' ')
n=$(ls "$RAW/$CASE/atm/hist/$CASE.cam.h0."200[0-7]-*.nc 2>/dev/null | wc -l)
log "archive job: $state, atm h0 files 2000-2007: $n"
[[ $state == COMPLETED ]] || fail "archive job state $state"
[[ -d $RAW/$CASE/rest/$LAST_REST ]] || fail "restart $LAST_REST missing"
(( n == 96 )) || fail "expected 96 atm h0 files, found $n"

# 2. NIRD copy
rsync -ah --exclude='*_tmp.pid*.ncks.tmp' "$RAW/$CASE/" "$NIRD/$CASE/" || fail "rsync to NIRD"
log "copied to NIRD"

exec 9> "$LOCK"; log "waiting for postprocessing lock"; flock 9

# 3. Move the old 2001-2002 files (+ logs) aside, never overwriting
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
log "old 2001-2002 files moved to $OLD"

# 4. Postprocess the whole run (all categories), check 19 files spanning 2001-2007
cd "$REPO"
out=$(CASES="$ALIAS $CASE" bash postprocess/run_all_parallel.sh 10)
echo "$out"
grep -q '^FAILED' <<< "$out" && fail "some categories failed"
n=$(ls "$PP/${ALIAS}"_{atm,lnd}_*_2001-2007.nc 2>/dev/null | wc -l)
(( n == 19 )) || fail "expected 19 files *_2001-2007.nc, found $n"
flock -u 9
log "postprocessing done, $n files"

# 5. Notebook
$PY results/tables/logs/run_nb_inplace.py "$HERE/how_big_artefact_is_PD.ipynb" || fail "notebook failed (error saved in the notebook)"
log "notebook rerun"

# 6. CLAUDE.md and run_aliases.csv: 14e = 8 yr (2000-2007)
$PY - "$REPO" <<'EOF' || fail "CLAUDE.md / run_aliases.csv update"
import sys, pathlib
repo = pathlib.Path(sys.argv[1])
edits = [(repo / 'CLAUDE.md',
          'its own LCC_PD emissions prescribed; **3 yr (2000–2002)**, exception to the 15-yr rule;',
          'its own LCC_PD emissions prescribed; **8 yr (2000–2007)**: 3 yr, extended by 5 (2003–2007; user OK 2026-11-03, '
          'automatic postprocessing + notebook rerun by `diagnostics/fbvoc-prescription-artefact/run_when_done/run_14e_extension_when_done.sh`), '
          'exception to the 15-yr rule;'),
         (repo / 'CLAUDE.md',
          'the 3-yr tests CTRL_PD_fBVOCctrlPD old chain, CTRL_PD_fBVOCctrlPD_HR (14d), LCC_PD_fBVOClccPD (14e).',
          'the 3-yr tests CTRL_PD_fBVOCctrlPD old chain, CTRL_PD_fBVOCctrlPD_HR (14d), and LCC_PD_fBVOClccPD (14e; 8 yr since the 2026-11-03 extension).'),
         (repo / 'cases-scripts/run_aliases.csv',
          ',2000-2002,-,LCC_PD_spinup -20261025,LCC_PD_spinup -20261025,-,3-yr test (user 2026-10-30)',
          ',2000-2007,-,LCC_PD_spinup -20261025,LCC_PD_spinup -20261025,-,3-yr test (user 2026-10-30) extended to 8 yr 2003-2007 (user 2026-11-03)')]
for path, old, new in edits:
    s = path.read_text()
    if new in s:
        print(f'{path.name}: already updated'); continue
    if s.count(old) != 1:
        print(f'{path.name}: text not found once, NOT edited: {old[:60]}...'); continue
    path.write_text(s.replace(old, new)); print(f'{path.name}: updated')
EOF
log "finished"
touch "$RWD/pids/run_14e_extension.ok"
