#!/bin/bash
# Rerun the analysis notebooks that draw categorical colours, after the project palette was set (user 2026-11-03,
# palette Q1 in plotting/palette.py). In place (outputs saved), one at a time. Maps-only notebooks
# (radiative_forcing, megan_factor_maps) are not affected and not rerun.
# Log: results/tables/logs/rerun_palette_20261103.log (START / OK / FAIL per notebook).
# Usage: nohup setsid bash rerun_palette_20261103.sh > /dev/null 2>&1 &
REPO=/cluster/home/adelez/BOREAL-FOREST-EXPANSION
PY=/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python
LOG=$REPO/results/tables/logs/rerun_palette_20261103.log
cd "$REPO"
log() { echo "$(date '+%F %T') $*" >> "$LOG"; }
for nb in analysis/pd-fut-attribution.ipynb analysis/biogeophysical-hydro.ipynb analysis/bvoc-soa-cloud-interactions.ipynb \
          analysis/fut-fbvoc-emission-source.ipynb analysis/cumulative_radiative_decomposition.ipynb; do
    log "START $nb"
    if $PY results/tables/logs/run_nb_inplace.py "$nb" --timeout 7200 >> "$LOG.out" 2>&1; then log "OK    $nb"; else log "FAIL  $nb"; fi
done
log "DONE"
