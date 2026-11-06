#!/bin/bash
# MEGAN exact split, PD batch 1 (2000 2001 2005 2010), launched as soon as the production test passed
# (user OK 2026-11-05 18:12: "launch batch 1 as soon as the test passes, keep its raw files until the swaps exist").
# Waits for /cluster/work/users/$USER/megan-lmdi/PD/PD_test60d.ok; stops (no launch) on PD_test60d.failed.
# Detached: setsid nohup bash megan_batch1_when_test_ok.sh > /cluster/work/users/$USER/megan-lmdi/PD/logs/batch1_when_test_ok.log 2>&1 < /dev/null &
set -uo pipefail
ST=/cluster/work/users/$USER/megan-lmdi/PD
ML=/cluster/home/adelez/BOREAL-FOREST-EXPANSION/cases-scripts/megan-lmdi
log() { echo "$(date '+%F %T') $*"; }
log "waiting for $ST/PD_test60d.ok ($(hostname), pid $$)"
while [[ ! -f "$ST/PD_test60d.ok" ]]; do
    [[ -f "$ST/PD_test60d.failed" ]] && { log "test FAILED ($(cat "$ST/PD_test60d.failed")): batch 1 NOT launched"; exit 1; }
    [[ -f "$ST/STOP_BATCH1" ]] && { log "STOP_BATCH1 found, exiting"; exit 0; }
    sleep 600
done
log "test passed -> launching batch PD 2000 2001 2005 2010 --keep-raw"
env -i HOME="$HOME" USER="$USER" bash -l -c "cd '$ML' && bash launch_megan_lmdi.sh batch PD 2000 2001 2005 2010 --keep-raw" \
    > "$ST/logs/launch_batch1_$(date +%Y%m%d-%H%M).log" 2>&1 && log "batch 1 launched" || log "ERROR: launcher failed (see $ST/logs/launch_batch1_*.log)"
