#!/bin/bash
# Rerun the analysis + diagnostics notebooks on the new (CO2-fix) chain (user 2026-11-02), in place (outputs saved).
# Stage 1 now (runs already processed); stage 2 after pp14b.ok (LCC_PD_fBVOCctrlPD); stage 3 after pp14c.ok
# (CTRL_PD_fBVOCctrlPD). A pp<n>.err stops the waiting stage. One notebook at a time.
# Log: results/tables/logs/rerun_new_chain_20261102.log (START / OK / FAIL per notebook).
# Usage: nohup setsid bash rerun_new_chain_20261102.sh > /dev/null 2>&1 &
REPO=/cluster/home/adelez/BOREAL-FOREST-EXPANSION
PY=/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python
STATE=/cluster/work/users/adelez/auto-launch
LOG=$REPO/results/tables/logs/rerun_new_chain_20261102.log
cd "$REPO"
log() { echo "$(date '+%F %T') $*" >> "$LOG"; }

run() {
    log "START $1"
    if $PY results/tables/logs/run_nb_inplace.py "$1" --timeout 7200 >> "$LOG.out" 2>&1; then log "OK    $1"
    else log "FAIL  $1"; fi
}

wait_pp() {  # wait for $STATE/pp$1.ok (and the postprocessing lock to be free); 0 = ok, 1 = pp failed
    while [[ ! -e $STATE/pp$1.ok ]]; do
        [[ -e $STATE/pp$1.err ]] && { log "pp$1 FAILED -> stage skipped"; return 1; }
        sleep 300
    done
    log "pp$1 ok"
}

log "stage 1"
for nb in analysis/fut-fbvoc-emission-source.ipynb analysis/cumulative_radiative_decomposition.ipynb \
          analysis/megan_factor_maps.ipynb diagnostics/other-BVOC-emission-magnitude/D2_megan_budget.ipynb \
          diagnostics/how-warmer-future-climate-is/how_warmer_future_climate_is.ipynb; do run $nb; done

log "stage 2: waiting for pp14b"
if wait_pp 14b; then
    for nb in analysis/radiative_forcing.ipynb analysis/bvoc-soa-cloud-interactions.ipynb \
              analysis/biogeophysical-hydro.ipynb analysis/pd-fut-attribution.ipynb \
              diagnostics/other-BVOC-emission-magnitude/D1_farfield_check.ipynb; do run $nb; done
fi

log "stage 3: waiting for pp14c"
if wait_pp 14c; then
    for nb in diagnostics/fbvoc-prescription-artefact/how_big_artefact_is_PD.ipynb \
              diagnostics/fbvoc-prescription-artefact/fbvoc_prescription_artefact.ipynb; do run $nb; done
fi
log "all done"
