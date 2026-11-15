#!/bin/bash
# Session d23b46ef 2026-11-11: after the design-A reruns (designA_24g_when_done.sh -> DONE), build the land
# carbon/water deck from the rerun land-carbon-water.ipynb figures. Gives up if that waiter FAILED.
ST=/cluster/work/users/adelez/designA-24g
until [[ -f $ST/DONE || -f $ST/FAILED ]]; do sleep 600; done
[[ -f $ST/FAILED ]] && { echo "$(date '+%F %T') designA FAILED, deck not built" >> $ST/pptx.log; exit 1; }
cd /cluster/home/adelez/BOREAL-FOREST-EXPANSION/results/pptx
/cluster/work/users/adelez/pptx-venv/bin/python build_land_carbon_water_pptx.py BOREAL_land_carbon_water_2001-2025_CICERO.pptx >> $ST/pptx.log 2>&1 \
  && echo "$(date '+%F %T') deck OK" >> $ST/pptx.log || echo "$(date '+%F %T') deck FAILED" >> $ST/pptx.log
