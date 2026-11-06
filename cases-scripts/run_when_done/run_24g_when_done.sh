#!/bin/bash
# LCC_FUT_fBVOClccFUT (24g, design A; user OK 2026-11-05 18:12), automatic:
#   1. wait for the LCC_FUT emission climatology array CLIM_JOB (19 tasks, input = LCC_FUT_HRBVOC merged by
#      preprocess/bvoc-emissions/merge_lcc_fut_hrbvoc.sh); every task must be COMPLETED;
#   2. check_bvoc_climatology.py LCC_FUT 2001 2014 (vs LCC_FUT's own h0) -> create_bvoc_emissions_for_year_2100.sh;
#   3. run the 24g script (create, build, submit; 15 yr 2000-2014, 3 x 5 yr);
#   4. when the run is done (rest 2015-01-01 archived, nothing queued): NIRD copy, then
#      postprocess/postprocess_new_chain_run.sh LCC_FUT_fBVOClccFUT <case>.
#   Failed st_archive jobs on the way are fixed by cases-scripts/archive_guard.sh.
# Detached: setsid nohup bash run_24g_when_done.sh CLIM_JOB > $STATE/run_24g.log 2>&1 < /dev/null &
# State: /cluster/work/users/$USER/run-24g/ (<step>.ok, watch.err)  Stop: touch .../run-24g/STOP
set -uo pipefail
CLIM_JOB="${1:?CLIM_JOB}"
REPO=/cluster/home/adelez/BOREAL-FOREST-EXPANSION
BV=$REPO/preprocess/bvoc-emissions
LCC_FUT=NF2100ssp585norbc_tropstratchem_nudg_lcc_f19_f19-20261028
ARCHIVE=/cluster/work/users/$USER/archive
NIRD=/cluster/home/adelez/nird/BRL-FRST-XPSN_archive
EMS_DIR=/cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions
PY=/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python
STATE=/cluster/work/users/$USER/run-24g
mkdir -p "$STATE"
log() { echo "$(date '+%F %T') $*"; }
fail() { log "ERROR: $*"; echo "$*" > "$STATE/watch.err"; exit 1; }
stop() { [[ -f "$STATE/STOP" ]] && { log "STOP file, exiting"; exit 0; }; }
exec 9> "$STATE/watch.lock"; flock -n 9 || fail "another watcher holds the lock"
log "start ($(hostname), pid $$), climatology job $CLIM_JOB"

if [[ ! -f "$STATE/ems.ok" ]]; then
    while squeue -h -j "$CLIM_JOB" 2>/dev/null | grep -q .; do stop; sleep 300; done
    sleep 60
    bad=$(sacct -n -P -j "$CLIM_JOB" -o JobID,State | grep -E '^[0-9]+_[0-9]+\|' | grep -v '|COMPLETED' || true)
    [[ -z "$bad" ]] || fail "climatology tasks not COMPLETED: $(echo $bad)"
    n=$(ls "$EMS_DIR"/ems_${LCC_FUT}_2001-2014_{SF,MEG_}*.nc 2>/dev/null | grep -v on_yr2100 | wc -l)
    (( n == 19 )) || fail "expected 19 ems_${LCC_FUT}_2001-2014_* files, found $n"
    (cd "$BV" && $PY check_bvoc_climatology.py "$LCC_FUT" 2001 2014) > "$STATE/check_climatology.log" 2>&1 \
        || fail "check_bvoc_climatology failed (see check_climatology.log)"
    (cd "$BV" && bash create_bvoc_emissions_for_year_2100.sh "${LCC_FUT}_2001-2014") > "$STATE/relabel_2100.log" 2>&1 \
        || fail "relabel to 2100 failed (see relabel_2100.log)"
    n=$(ls "$EMS_DIR"/ems_${LCC_FUT}_2001-2014_on_yr2100_*.nc 2>/dev/null | wc -l)
    (( n == 19 )) || fail "expected 19 _on_yr2100 files, found $n"
    touch "$STATE/ems.ok"; log "emissions OK (19 files, checked, relabelled to 2100)"
fi

if [[ ! -f "$STATE/launch.ok" ]]; then
    (cd "$REPO/cases-scripts" && echo n | env -i HOME="$HOME" USER="$USER" bash -l -c \
        "cd '$REPO/cases-scripts' && bash 24g-NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOClccFUT_f19_f19.sh") \
        > "$STATE/launch_24g.log" 2>&1 || fail "24g script failed (see launch_24g.log)"
    ls -td "$HOME"/cases/BRL_FRST_XPSN/NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOClccFUT_f19_f19-2026* | head -1 | xargs basename > "$STATE/case"
    touch "$STATE/launch.ok"; log "24g launched: $(cat "$STATE/case")"
fi
CASE=$(cat "$STATE/case"); WD=$(realpath "$HOME/cases/BRL_FRST_XPSN/$CASE")

until [[ -d "$ARCHIVE/$CASE/rest/2015-01-01-00000" ]] && ! squeue -u "$USER" -h -o %Z | grep -qx -- "$WD"; do stop; sleep 900; done
log "run done (rest 2015-01-01 archived)"
if [[ ! -f "$STATE/nird.ok" ]]; then
    rsync -ah --exclude='*_tmp.pid*.ncks.tmp' "$ARCHIVE/$CASE/" "$NIRD/$CASE/" > "$STATE/rsync.log" 2>&1 || fail "NIRD rsync failed"
    touch "$STATE/nird.ok"; log "copied to NIRD"
fi
bash "$REPO/postprocess/postprocess_new_chain_run.sh" LCC_FUT_fBVOClccFUT "$CASE" "$STATE/pp24g" \
    && log "postprocessing OK" || fail "postprocessing failed (see $STATE/pp24g.log)"
log "done"
