#!/bin/bash
# CTRL_PD_fBVOCctrlPD_C0102 (user OK 2026-11-09): waits for the 2001-2002 BVOC climatology (sbatch job array),
# checks the 19 files, creates/builds/submits the case (14f), waits for the run (3 x 1-yr jobs), postprocesses it from
# the work archive and reruns diagnostics/fbvoc-prescription-artefact/fbvoc_artefact_causes.ipynb (section H6).
# Usage (login node, from cases-scripts/): nohup bash run_when_done/run_C0102_when_done.sh CLIM_JOBID > run_when_done/logs/run_C0102_when_done.log 2>&1 &
# Stop: kill the PID in run_when_done/pids/run_C0102_when_done.pid.
set -uo pipefail
CLIM_JOB="$1"
ALIAS=CTRL_PD_fBVOCctrlPD_C0102
RAW=/cluster/work/users/adelez/archive
REPO=/cluster/home/adelez/BOREAL-FOREST-EXPANSION
PY=/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python
RWD=$REPO/cases-scripts/run_when_done
NB=$REPO/diagnostics/fbvoc-prescription-artefact/fbvoc_artefact_causes.ipynb
PREFIX=/cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions/ems_NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20261023_2001-2002
CATEGORIES="BVOC SOA CHEM CLOUDPROP RADIATIVE"
mkdir -p "$RWD/logs" "$RWD/pids"; echo $$ > "$RWD/pids/run_C0102_when_done.pid"

# 1. Climatology: wait for the array to leave the queue, then 19 files + check
while squeue -h -j "$CLIM_JOB" 2>/dev/null | grep -q .; do sleep 300; done
n=$(ls ${PREFIX}_SF*.nc ${PREFIX}_MEG_*.nc 2>/dev/null | wc -l)
echo "$(date) climatology job $CLIM_JOB left the queue; files: $n"
(( n == 19 )) || { echo "expected 19 files, stop (see /cluster/work/users/adelez/bvoc-emissions/logs/bvoc-clim_${CLIM_JOB}_*.out)"; exit 1; }
(cd $REPO/preprocess/bvoc-emissions && $PY check_bvoc_climatology.py NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20261023 2001 2002) \
    > "$RWD/logs/check_clim_C0102.log" 2>&1 || { echo "$(date) climatology check FAILED, see logs/check_clim_C0102.log"; exit 1; }
echo "$(date) climatology check OK"

# 2. Create, build, submit (14f prints the case name)
cd $REPO/cases-scripts
bash 14f-NF2000norbc_tropstratchem_nudg_ctrl_fBVOCctrlPD_C0102_f19_f19.sh > "$RWD/logs/14f_setup.log" 2>&1 || { echo "$(date) 14f failed, see logs/14f_setup.log"; exit 1; }
CASE=$(grep -oE "Case NF2000norbc_tropstratchem_nudg_ctrl_fBVOCctrlPD_C0102_f19_f19-[0-9]{8}" "$RWD/logs/14f_setup.log" | head -1 | cut -c6-)
[[ -n $CASE ]] || { echo "case name not found in 14f_setup.log"; exit 1; }
CASEROOT=$HOME/cases/BRL_FRST_XPSN/$CASE
echo "$(date) submitted $CASE"

# 3. Wait for the last archive (restart 2003-01-01) and an empty queue for this case
while :; do
    if grep -qE "case.run error|st_archive error" "$CASEROOT/CaseStatus" 2>/dev/null; then
        echo "$(date) error in CaseStatus, stop"; tail -5 "$CASEROOT/CaseStatus"; exit 1
    fi
    if [[ -d $RAW/$CASE/rest/2003-01-01-00000 ]] && ! squeue -h -u "$USER" -o %Z | grep -q "/$CASE\$"; then break; fi
    sleep 600
done
n=$(ls "$RAW/$CASE/atm/hist/$CASE.cam.h0."200[0-2]-*.nc 2>/dev/null | wc -l)
echo "$(date) run archived, atm h0 files 2000-2002: $n"; (( n == 36 )) || { echo "archive incomplete, stop"; exit 1; }

# 4. Postprocess (first 12 months dropped -> 2001-2002) into the old-chain folder, next to the other test runs
OUT=data/processed-data/postprocessing/2001-2014-all-bvoc-pre-co2-fix
cd "$REPO"
for cat in $CATEGORIES; do
    $PY postprocess/run_postprocess.py $CASE $ALIAS atm --categories $cat --raw-path $RAW \
        --spinup-months 12 --out-path $OUT > "$RWD/logs/postprocess_C0102_$cat.log" 2>&1 &
done
wait
for cat in $CATEGORIES; do
    ls $OUT/${ALIAS}_atm_${cat}_2001-2002.nc || { echo "missing $cat, see logs/postprocess_C0102_$cat.log"; exit 1; }
done
echo "$(date) postprocessing done"

# 5. Notebook (H6 picks up the C0102 files)
$PY results/tables/logs/run_nb_inplace.py "$NB" > results/tables/logs/run_fbvoc_artefact_causes_C0102.log 2>&1
echo "$(date) notebook EXIT $?; finished"
