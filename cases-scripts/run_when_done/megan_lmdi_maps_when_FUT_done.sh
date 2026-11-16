#!/bin/bash
# Rerun analysis/megan-lmdi-attribution-maps.ipynb once all 6 FUT LMDI years are reduced and copied
# (user OK 2026-11-16 13:06, session ae435137): adds the FUT exact attribution maps
# results/figures/megan_factors/FUT_<group>_attribution_LMDI_<season>_6yr.png (+ table megan_lmdi_attribution_FUT_45N.csv).
#
# Waits for FUT_<y>.copied (y = 2001 2002 2005 2006 2010 2011) in the FUT state folder of the MEGAN LMDI watcher
# and for the file megan_lmdi_FUT_<y>.nc; stops if any FUT_<y>.failed appears. Does not run while another run of
# the same notebook is going (e.g. the month-fix rerun of session 1b77ec0b).
# Start (login node):  setsid nohup bash megan_lmdi_maps_when_FUT_done.sh > $S/logs/maps_waiter.log 2>&1 < /dev/null &
# Stop: touch $S/STOP_MAPS_WAITER
set -u
REPO=/cluster/home/adelez/BOREAL-FOREST-EXPANSION
S=/cluster/work/users/adelez/megan-lmdi/FUT
PY=/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python
NB=analysis/megan-lmdi-attribution-maps.ipynb
YEARS="2001 2002 2005 2006 2010 2011"
STATUS=$REPO/results/tables/logs/run_megan_lmdi_maps_FUT.status
log() { echo "$(date '+%F %T') $*"; }
echo $$ > $S/maps_waiter.pid
log "start (pid $$, $(hostname))"

while true; do
    [[ -f $S/STOP_MAPS_WAITER ]] && { log "STOP file: exiting"; exit 0; }
    for y in $YEARS; do [[ -f $S/FUT_$y.failed ]] && { log "FUT_$y failed: not running the maps"; echo "FAILED FUT_$y" > $STATUS; exit 1; }; done
    missing=""
    for y in $YEARS; do
        [[ -f $S/FUT_$y.copied && -f $REPO/data/processed-data/megan-lmdi/megan_lmdi_FUT_$y.nc ]] || missing+=" $y"
    done
    if [[ -z $missing ]]; then
        if pgrep -f "run_nb_inplace.py.*megan-lmdi-attribution-maps" > /dev/null || pgrep -f after_finalize.sh > /dev/null; then
            log "all FUT years in, but another run of the notebook is going: waiting"
        else
            break
        fi
    fi
    sleep 900
done

log "all 6 FUT years reduced: running $NB"
cd /tmp
for attempt in 1 2 3; do
    echo "RUNNING attempt $attempt $(date '+%F %T')" > $STATUS
    if $PY $REPO/results/tables/logs/run_nb_inplace.py $REPO/$NB; then
        echo "OK $(date '+%F %T')" > $STATUS; log "notebook OK (attempt $attempt)"; exit 0
    fi
    log "notebook FAILED (attempt $attempt)"; sleep 600
done
echo "FAILED $(date '+%F %T')" > $STATUS
exit 1
