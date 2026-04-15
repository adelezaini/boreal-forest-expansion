#!/bin/bash

# NF18500_tropstratchem test case to test and check output variables

# Exit if error, undefined variable...
set -euo pipefail
# Load common functions for case setup
source cases-setup.sh

# Simulation specifics:
#––––––––––– For tests - adding date to name to avoid overwriting previous tests: 
today=$(date +'%Y%m%d')
testname="test-$today"
export CASENAME="NF1850norbc_tropstratchem_f19_f19_$testname"
export COMPSET=1850_CAM60%NORESM%NORBC%TROPSTRATCHEM_CLM50%BGC_CICE%PRES_DOCN%DOM_MOSART_SGLC_SWAV
set_project_noresm_res_vars

# Restart files specifics:
# Use some Dirk's restart files
REFCASE="NHIST_tropstratchem_01_f19_tn14_r1990_s01_20241118"
REFDATE="2000-01-01"

REST_SRC="/nird/datalake/NS9560K/olivie/restart/${REFCASE}/${REFDATE}-00000"
REST_LOCAL="/cluster/home/$USER/restart/${REFCASE}_${REFDATE}-00000"

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
prepare_restart_files "$REST_SRC" "$REST_LOCAL"

CASEROOT=$HOME/cases/BRL_FRST_XPSN/$CASENAME
rm -rf "$CASEROOT" #remove previous case

cd $NORESM_ROOT/cime/scripts || exit 1

./create_newcase --case $CASEROOT --compset $COMPSET --res $RES --machine betzy --run-unsupported --project $PROJECT --handle-preexisting-dirs r

cd $CASEROOT

aerosol_cosp_diagnostics
forcings_2000

# Initial files from restart
./xmlchange RUN_TYPE=hybrid
./xmlchange RUN_REFCASE="$REFCASE"
./xmlchange RUN_REFDATE="$REFDATE"
./xmlchange RUN_REFDIR="$REST_LOCAL"
./xmlchange GET_REFCASE=TRUE

# Simulation length
./xmlchange STOP_OPTION=nyears
./xmlchange STOP_N=1
./xmlchange JOB_WALLCLOCK_TIME=24:00:00

#./case.build --clean
./case.setup

# From Error:
echo -e " use_init_interp = .true.">> user_nl_clm

# Diagnostics
cosp_diagnostics
cam_diagnostics

./case.build
./case.submit