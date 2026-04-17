#!/bin/bash

# Test of 2100 spin up

# Exit if error, undefined variable...
set -euo pipefail
# Load common functions for case setup
source cases-setup.sh

#––––––––––– For tests - adding date to name to avoid overwriting previous tests:
today=$(date +'%Y%m%d')
testname="test-$today"
CASENAME="NF2100ssp585norbc_tropstratchem_$testname"

#––––––––––– SIMULATION SPECIFICS: –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
COMPSET=NF2100ssp585norbc_tropstratchem
set_project_noresm_res_vars

###TO EDIT
# Restart files specifics:
REFCASE="NSSP585frc2_f19_tn14_20191014"
REFDATE="2100-01-01"

REST_SRC="/nird/datalake/NS9560K/olivie/restart/${REFCASE}/${REFDATE}-00000"
REST_LOCAL="/cluster/home/$USER/restart/${REFCASE}/${REFDATE}-00000"

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
prepare_restart_files "$REST_SRC" "$REST_LOCAL"

CASEROOT=$HOME/cases/BRL_FRST_XPSN/$CASENAME
rm -rf "$CASEROOT" #remove previous case

cd $NORESM_ROOT/cime/scripts || exit 1

./create_newcase --case $CASEROOT --compset $COMPSET --res $RES --machine betzy --run-unsupported --project $PROJECT --handle-preexisting-dirs r

echo "Case $CASENAME created with compset $COMPSET and resolution $RES"

cd $CASEROOT 
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

aerosol_cosp_diagnostics
forcings_2100
dms_forcing_2100_to_2000

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

# From error (why?)
echo -e " use_init_interp = .true.">> user_nl_clm

cam_spinup_diagnostics
clm_spinup_diagnostics

output_cplhist_auxiliary_files

./case.build
./case.submit
