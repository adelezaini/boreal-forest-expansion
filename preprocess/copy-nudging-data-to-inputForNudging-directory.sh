#!/bin/bash

# not tested

CASENAME=NF2000norbc_tropstratchem_met_f19_f19_20260422
TIME_RANGE=2000-2015
FREQUENCY=6h

#save-archived-case-to-boreal "$CASENAME"

NUDGDIR=/cluster/shared/noresm/inputdata/noresm-only/inputForNudging/AZ/${CASENAME}_${FREQUENCY}_${TIME_RANGE}

mkdir -p "$NUDGDIR"
#rsync -avP /cluster/home/adelez/BRL-FRST-XPSN_archive/$CASENAME/atm/hist/$CASENAME.cam.h1.*.nc "$NUDGDIR"/
rsync -avP ~/work/archive/$CASENAME/atm/hist/$CASENAME.cam.h1.*.nc "$NUDGDIR"/
ls -1v "$NUDGDIR"/*.h1.*.nc > "$NUDGDIR"/${CASENAME}.cam.h1_filelist.txt

#ls -1v /cluster/shared/noresm/inputdata/cplhist/NF2000norbc_tropstratchem_spinup_f19_f19_20260421_01-20_hist/* > /cluster/shared/noresm/inputdata/cplhist/NF2000norbc_tropstratchem_spinup_f19_f19_20260421_01-20_hist/z_fileList.txt
