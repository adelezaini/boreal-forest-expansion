#!/bin/bash

### Land-only spinup to equilibrate cells that can start from cold start after changing the land cover (even with initial_interp=.true. because the change is dramatic)
# Free run, no nudging
# Initial file:  NF2000norbc_tropstratchem_spinup_f19_f19 (0021-01-01)
# Input: cplhist auxiliary files from the previous spinup NF2000norbc_tropstratchem_spinup_f19_f19
# 100 years
# No output needed, just clm_diagnostics to check if equilibrated

# Exit if error, undefined variable...
set -euo pipefail
# Load common functions for case setup
source cases-setup.sh

#––––––––––– SIMULATION SPECIFICS: –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
today=$(date +'%Y%m%d')
CASENAME="I2000Clm50BgcCropCplHist_f19_f19_$today"
COMPSET=2000_DATM%CPLHIST_CLM50%BGC-CROP_SICE_SOCN_MOSART_SGLC_SWAV
set_project_noresm_res_vars

# Restart files specifics:
REFCASE="NF2000norbc_tropstratchem_spinup_f19_f19"
REFDATE="0021-01-01"

REST_SRC="/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive/${REFCASE}/rest/${REFDATE}-00000"
REST_LOCAL="/cluster/home/$USER/restart/${REFCASE}/${REFDATE}-00000"
# I transfer restart files because in original folder are zipped. The unzipped files are all in one place

# Surface data file with modified land cover for boreal forest expansion
SURFDATA_FILE="/cluster/shared/noresm/inputdata/lnd/clm2/surfdata_map/surfdata_1.9x2.5_78pfts_LPJGUESS_SSP585.nc"
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
prepare_restart_files "$REST_SRC" "$REST_LOCAL"

BASE_CASE_DIR="$HOME/cases/BRL_FRST_XPSN/"
CASEROOT="$BASE_CASE_DIR/$CASENAME"

remove_case_if_exists "$CASEROOT" "$BASE_CASE_DIR"

cd "$NORESM_ROOT/cime/scripts" || exit 1

./create_newcase --case "$CASEROOT" --compset "$COMPSET" --res "$RES" --machine betzy --run-unsupported --project "$PROJECT" --handle-preexisting-dirs r

echo "Case $CASENAME created with compset $COMPSET and resolution $RES"

cd "$CASEROOT"
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

datm_forcing_from_cplhist_files 2000

# Initial files from restart
./xmlchange RUN_TYPE=hybrid
./xmlchange RUN_REFCASE="$REFCASE"
./xmlchange RUN_REFDATE="$REFDATE"
./xmlchange RUN_REFDIR="$REST_LOCAL"
./xmlchange GET_REFCASE=TRUE

# Simulation length
./xmlchange STOP_OPTION=nyears,STOP_N=10
./xmlchange RESUBMIT=9 # 10 yrs + 9 x 10 yrs = 100 yrs
./xmlchange REST_OPTION=nyears,REST_N=10
./xmlchange DOUT_S_SAVE_INTERIM_RESTART_FILES=FALSE # To avoid saving restarts at the end of each run, which is not necessary for the spinup and takes a lot of space
./xmlchange RUN_STARTDATE=0001-01-01

#./xmlchange JOB_WALLCLOCK_TIME=24:00:00 # ok with ~7 simulated years/day for STOP_N = 5 years

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
clm_long_spinup_diagnostics

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
./case.build
./case.submit
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––