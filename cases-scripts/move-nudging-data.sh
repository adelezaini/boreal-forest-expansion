#!/bin/bash

# not tested

CASENAME=NF2000norbc_tropstratchem_met_f19_f19_20260422
TIME_RANGE=2000-2010
FREQUENCY=6h
save-archived-case-to-boreal "$CASENAME"

NUDGDIR=/cluster/shared/noresm/inputdata/noresm-only/inputForNudging/AZ/${CASENAME}_${FREQUENCY}_${TIME_RANGE}
mkdir -p "$NUDGDIR"
cd /cluster/work/users/adelez/archive/$CASENAME/atm/hist
mv *.h1.*.nc "$NUDGDIR"/
ls -1v "$NUDGDIR"/*.h1.*.nc > "$NUDGDIR"/fileList.txt