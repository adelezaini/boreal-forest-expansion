#!/bin/bash

# 2000 Coupled spinup for 
# Initial file: NF2000norbc_tropstratchem_spinup_f19_f19 (0021-01-01)
# 20/30 years
# No nudging

# Exit if error, undefined variable...
set -euo pipefail
# Load common functions for case setup
source cases-setup.sh

#––––––––––– SIMULATION SPECIFICS: –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
today=$(date +'%Y%m%d')
CASENAME="NF2000norbc_tropstratchem_quick_spinup_lcc_f19_f19-test_$today"
COMPSET=NF2000norbc_tropstratchem
set_project_noresm_res_vars

# Restart files specifics:
REFCASE="NF2000norbc_tropstratchem_spinup_f19_f19"
REFDATE="0021-01-01"

REST_SRC="/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive/${REFCASE}/rest/${REFDATE}-00000"
REST_LOCAL="/cluster/home/$USER/restart/${REFCASE}/${REFDATE}-00000"

# Surface data file with modified land cover for boreal forest expansion
SURFDATA_FILE="/cluster/shared/noresm/inputdata/lnd/clm2/surfdata_map/surfdata_1.9x2.5_78pfts_LPJGUESS_SSP585.nc"
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
prepare_restart_files "$REST_SRC" "$REST_LOCAL"

BASE_CASE_DIR="$HOME/cases/BRL_FRST_XPSN/"
CASEROOT="$BASE_CASE_DIR/$CASENAME"

remove_case_if_exists "$CASEROOT" "$BASE_CASE_DIR"

cd $NORESM_ROOT/cime/scripts || exit 1

./create_newcase --case $CASEROOT --compset $COMPSET --res $RES --machine betzy --run-unsupported --project $PROJECT --handle-preexisting-dirs r

echo "Case $CASENAME created with compset $COMPSET and resolution $RES"

cd $CASEROOT
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

forcings_2000


# Initial files from restart
./xmlchange RUN_TYPE=hybrid
./xmlchange RUN_REFCASE="$REFCASE"
./xmlchange RUN_REFDATE="$REFDATE"
./xmlchange RUN_REFDIR="$REST_LOCAL"
./xmlchange GET_REFCASE=TRUE

# Simulation length
./xmlchange STOP_OPTION=ndays,STOP_N=1
# ./xmlchange STOP_OPTION=nyears,STOP_N=5
#./xmlchange RESUBMIT=3 # 5 yrs + 3 x 5 yrs = 20 yrs
#./xmlchange REST_OPTION=nyears,REST_N=1
#./xmlchange DOUT_S_SAVE_INTERIM_RESTART_FILES=FALSE # To avoid saving restarts at the end of each run, which is not necessary for the spinup and takes a lot of space
./xmlchange RUN_STARTDATE=0001-01-01 # I should have set 0000-01-01

./xmlchange --subgroup case.st_archive JOB_WALLCLOCK_TIME=23:59:00
./xmlchange --subgroup case.run        JOB_WALLCLOCK_TIME=47:59:00

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
#./case.build --clean
./case.setup
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

# Land cover change - boreal forest expansion
# Modified idealized surfdata file
cat << EOF >> user_nl_clm
fsurdat = '${SURFDATA_FILE}'
use_init_interp = .true.
EOF

# Diagnostics
cam_spinup_diagnostics
clm_spinup_diagnostics

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
./case.build
./case.submit
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––