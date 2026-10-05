#!/bin/bash

### LCC_SPINUP_PD
# Free run, no nudging
# Set LCC
# Linking
# Initial state: I2000Clm50BgcCropCplHist_f19_f19 (0101-01-01)
# 20 year spinup

# Exit if error, undefined variable...
set -euo pipefail
# Load common functions for case setup
source cases-setup.sh
#––––––––––– SIMULATION SPECIFICS: –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
today=$(date +'%Y%m%d')
CASENAME="NF2000norbc_tropstratchem_spinup_lcc_f19_f19-$today"
COMPSET=NF2000norbc_tropstratchem
set_project_noresm_res_vars

# Restart files specifics:
REFCASE="NF2000norbc_tropstratchem_spinup_f19_f19"
REFDATE="0021-01-01"
REST_SRC="/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive/$REFCASE/rest/$REFDATE-00000"
REST_LOCAL="/cluster/home/$USER/restart/$REFCASE/$REFDATE-00000"

# Surface data file with modified land cover for boreal forest expansion
SURFDATA_FILE="/cluster/shared/noresm/inputdata/lnd/clm2/surfdata_map/surfdata_1.9x2.5_SSP5-8.5_2100_78pfts_LPJGUESS.nc"

# CLM finitdat = 100 year spinup
LAND_CASE="I2000Clm50BgcCropCplHist_f19_f19-20260925"
LAND_REFDATE="0101-01-01"
LAND_SRC="/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive/$LAND_CASE/rest/$LAND_REFDATE-00000"
LAND_LOCAL="/cluster/home/$USER/restart/$LAND_CASE/$LAND_REFDATE-00000"
LAND_RESTART="$LAND_LOCAL/$LAND_CASE.clm2.r.$LAND_REFDATE-00000.nc"

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
prepare_restart_files "$REST_SRC" "$REST_LOCAL"
prepare_restart_files "$LAND_SRC" "$LAND_LOCAL"
[[ -f "$LAND_RESTART" ]] || { echo "Missing land restart: $LAND_RESTART" >&2; exit 1; }
[[ -f "$SURFDATA_FILE" ]] || { echo "Missing surfdata: $SURFDATA_FILE" >&2; exit 1; }

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
./xmlchange STOP_OPTION=nyears,STOP_N=5
./xmlchange RESUBMIT=3 # 5 yrs + 3 x 5 yrs = 20 yrs
./xmlchange REST_OPTION=nyears,REST_N=5
./xmlchange DOUT_S_SAVE_INTERIM_RESTART_FILES=FALSE # To avoid saving restarts at the end of each run, which is not necessary for the spinup and takes a lot of space
./xmlchange RUN_STARTDATE=0001-01-01
#./xmlchange RUN_REFCASE_LAND="$LAND_CASE"
#./xmlchange RUN_REFDATE_LAND="$LAND_REFDATE"
#./xmlchange RUN_REFDIR_LAND="$LAND_LOCAL"

# Simulated years ~ 5
./xmlchange --subgroup case.st_archive JOB_WALLCLOCK_TIME=03:00:00
./xmlchange --subgroup case.run JOB_WALLCLOCK_TIME=35:00:00

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
#./case.build --clean
./case.setup
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

cat >> user_nl_clm <<EOF
fsurdat = '$SURFDATA_FILE'
finidat = '$LAND_RESTART'
use_init_interp = .true.
EOF

cam_spinup_diagnostics
clm_spinup_diagnostics

./case.build
./case.submit
