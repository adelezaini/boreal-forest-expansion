#!/bin/bash

# not tested

CASENAME=NF2000norbc_tropstratchem_met_f19_f19_20260422
TIME_RANGE=2000-2010
FREQUENCY=6h

#save-archived-case-to-boreal NF2000norbc_tropstratchem_met_f19_f19_20260422 "$CASENAME"

NUDGDIR=/cluster/shared/noresm/inputdata/noresm-only/inputForNudging/AZ/${CASENAME}_${FREQUENCY}_${TIME_RANGE}
mkdir -p /cluster/shared/noresm/inputdata/noresm-only/inputForNudging/AZ/NF2000norbc_tropstratchem_met_f19_f19_20260422_6h_2000-2010
mkdir -p "$NUDGDIR"
#rsync -avP /cluster/home/adelez/BRL-FRST-XPSN_archive/$CASENAME/atm/hist/$CASENAME.cam.h1.*.nc "$NUDGDIR"/
#ls -1v "$NUDGDIR"/*.h1.*.nc > "$NUDGDIR"/fileList.txt