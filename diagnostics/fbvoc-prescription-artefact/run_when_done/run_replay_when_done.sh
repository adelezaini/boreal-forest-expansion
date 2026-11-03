#!/bin/bash
# Waits for CTRL_PD_fBVOCctrlPD_HR (replay of CTRL_PD's actual 2000-2002 emissions; three 1-year jobs, auto resubmit),
# postprocesses it from the work archive and reruns fbvoc_artefact_causes.ipynb (section H5; outputs saved in the notebook).
# Usage (login node): nohup bash run_when_done/run_replay_when_done.sh CASENAME > run_when_done/logs/run_replay_when_done.log 2>&1 &
# Stop: kill the PID in run_when_done/pids/run_replay_when_done.pid.
set -uo pipefail

CASE="$1"
ALIAS=CTRL_PD_fBVOCctrlPD_HR
RAW=/cluster/work/users/adelez/archive
REPO=/cluster/home/adelez/BOREAL-FOREST-EXPANSION
PY=/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python
HERE=$REPO/diagnostics/fbvoc-prescription-artefact
RWD=$HERE/run_when_done
CASEROOT=$HOME/cases/BRL_FRST_XPSN/$CASE
CATEGORIES="BVOC SOA CHEM CLOUDPROP RADIATIVE"
mkdir -p "$RWD/logs" "$RWD/pids"
echo $$ > "$RWD/pids/run_replay_when_done.pid"

# 1. Wait for the last archive (restart 2003-01-01) and for no job of this case left in the queue
while :; do
    if grep -qE "case.run error|st_archive error" "$CASEROOT/CaseStatus" 2>/dev/null; then
        echo "$(date) error in CaseStatus, stop"; tail -5 "$CASEROOT/CaseStatus"; exit 1
    fi
    if [[ -d $RAW/$CASE/rest/2003-01-01-00000 ]] && ! squeue -h -u "$USER" -o %Z | grep -q "/$CASE\$"; then
        break
    fi
    sleep 600
done
n=$(ls "$RAW/$CASE/atm/hist/$CASE.cam.h0."200[0-2]-*.nc 2>/dev/null | wc -l)
echo "$(date) run archived, atm h0 files 2000-2002: $n"
(( n == 36 )) || { echo "archive incomplete, stop"; exit 1; }

# 2. Postprocess (one process per category), first 12 months dropped -> 2001-2002
cd "$REPO"
for cat in $CATEGORIES; do
    $PY postprocess/run_postprocess.py $CASE $ALIAS atm --categories $cat --raw-path $RAW \
        --spinup-months 12 --out-path data/processed-data/postprocessing > "$RWD/logs/postprocess_HR_$cat.log" 2>&1 &
done
wait
for cat in $CATEGORIES; do
    ls data/processed-data/postprocessing/${ALIAS}_atm_${cat}_2001-2002.nc || { echo "missing $cat, see run_when_done/logs/postprocess_HR_$cat.log"; exit 1; }
done
echo "$(date) postprocessing done"

# 3. Notebook (H5 picks up the replay files and the h1 output)
$PY results/tables/logs/run_nb_inplace.py "$HERE/fbvoc_artefact_causes.ipynb"
echo "$(date) finished"
