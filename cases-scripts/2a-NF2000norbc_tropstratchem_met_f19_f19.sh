#!/bin/bash

# Meteorology for winds (u,v) for nudging
# Free run, no nudging
# Initial file: NF2000norbc_tropstratchem_spinup_f19_f19
# 20/30 years
# Output (u,v)

# Exit if error, undefined variable...
set -euo pipefail
# Load common functions for case setup
source cases-setup.sh

#––––––––––– SIMULATION SPECIFICS: –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
CASENAME="NF2000norbc_tropstratchem_spinup_f19_f19"
COMPSET=NF2000norbc_tropstratchem
set_project_noresm_res_vars

# Restart files specifics:
REFCASE="NHIST_tropstratchem_01_f19_tn14_r1990_s01_20241118"
REFDATE="2000-01-01"

REST_SRC="/nird/datalake/NS9560K/olivie/restart/${REFCASE}/${REFDATE}-00000"
REST_LOCAL="/cluster/home/$USER/restart/${REFCASE}_${REFDATE}-00000"

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
prepare_restart_files "$REST_SRC" "$REST_LOCAL"

CASEROOT=$HOME/cases/BRL_FRST_XPSN/$CASENAME
rm -rf "$CASEROOT" #remove previous case

cd $NORESM_ROOT/cime/scripts || exit 1

./create_newcase --case $CASEROOT --compset $COMPSET --res $RES --machine betzy --run-unsupported --project $PROJECT --handle-preexisting-dirs r

echo "Case $CASENAME created with compset $COMPSET and resolution $RES"

cd $CASEROOT
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

aerosol_cosp_diagnostics # In spinup no diagnostics necessary but I'm gonna run to chekc if it is everything that I need
forcings_2000


# Initial files from restart
./xmlchange RUN_TYPE=hybrid
./xmlchange RUN_REFCASE="$REFCASE"
./xmlchange RUN_REFDATE="$REFDATE"
./xmlchange RUN_REFDIR="$REST_LOCAL"
./xmlchange GET_REFCASE=TRUE

# Simulation length
./xmlchange STOP_OPTION=nyears,STOP_N=5
./xmlchange RESUBMIT=3 # 5 yrs + 3 x 5 yrs = 20 yrs
./xmlchange REST_OPTION=nyears,REST_N=1
./xmlchange DOUT_S_SAVE_INTERIM_RESTART_FILES=FALSE # To avoid saving restarts at the end of each run, which is not necessary for the spinup and takes a lot of space
./xmlchange RUN_STARTDATE=0001-01-01

./xmlchange JOB_WALLCLOCK_TIME=24:00:00 # ok with ~7 simulated years/day for STOP_N = 5 years

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
#./case.build --clean
./case.setup
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

# From error (why?)
echo -e " use_init_interp = .true.">> user_nl_clm

# Diagnostics
cosp_diagnostics
cam_diagnostics
clm_diagnostics

output_cplhist_auxiliary_files

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
./case.build
./case.submit
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––