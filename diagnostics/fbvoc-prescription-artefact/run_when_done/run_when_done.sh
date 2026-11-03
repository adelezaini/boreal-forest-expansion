#!/bin/bash
# Waits for CTRL_PD_fBVOCctrlPD (case.run 1783539 -> case.st_archive 1783540), postprocesses it from the
# work archive and reruns fbvoc_prescription_artefact.ipynb (outputs saved in the notebook).
# Usage (login node): nohup bash run_when_done/run_when_done.sh > run_when_done/logs/run_when_done.log 2>&1 &
# Stop: kill the PID in run_when_done/pids/run_when_done.pid.
set -uo pipefail

CASE=NF2000norbc_tropstratchem_nudg_ctrl_fBVOCctrlPD_f19_f19-20261028
ALIAS=CTRL_PD_fBVOCctrlPD
ARCHIVE_JOB=1783540
RAW=/cluster/work/users/adelez/archive
REPO=/cluster/home/adelez/BOREAL-FOREST-EXPANSION
PY=/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python
HERE=$REPO/diagnostics/fbvoc-prescription-artefact
RWD=$HERE/run_when_done
CATEGORIES="BVOC SOA CHEM CLOUDPROP RADIATIVE"
mkdir -p "$RWD/logs" "$RWD/pids"
echo $$ > "$RWD/pids/run_when_done.pid"

# 1. Wait for the archive job; it never starts if the model run fails (afterok dependency)
while :; do
    reason=$(squeue -h -j $ARCHIVE_JOB -o %r 2>/dev/null)
    [[ -z $reason ]] && break
    [[ $reason == *DependencyNeverSatisfied* ]] && { echo "$(date) model run failed, stop"; exit 1; }
    sleep 300
done
state=$(sacct -n -X -j $ARCHIVE_JOB -o State | head -1 | tr -d ' ')
n=$(ls "$RAW/$CASE/atm/hist/$CASE.cam.h0."200[0-2]-*.nc 2>/dev/null | wc -l)
echo "$(date) archive job: $state, atm h0 files 2000-2002: $n"
[[ $state == COMPLETED && $n -eq 36 ]] || { echo "archive incomplete, stop"; exit 1; }

# 2. Postprocess (one process per category), first 12 months dropped -> 2001-2002
cd "$REPO"
for cat in $CATEGORIES; do
    $PY postprocess/run_postprocess.py $CASE $ALIAS atm --categories $cat --raw-path $RAW \
        --spinup-months 12 --out-path data/processed-data/postprocessing > "$RWD/logs/postprocess_$cat.log" 2>&1 &
done
wait
for cat in $CATEGORIES; do
    ls data/processed-data/postprocessing/${ALIAS}_atm_${cat}_2001-2002.nc || { echo "missing $cat, see run_when_done/logs/postprocess_$cat.log"; exit 1; }
done
echo "$(date) postprocessing done"

# 3. Notebook
$PY results/tables/logs/run_nb_inplace.py "$HERE/fbvoc_prescription_artefact.ipynb" && cat "$HERE/fbvoc_prescription_artefact_outputs/tables/verdict.txt"
echo "$(date) finished"
