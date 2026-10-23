#!/bin/bash
# 1-day test of cam_diagnostics HR_BVOC_ALL: copy of 13a-NF2000norbc_tropstratchem_nudg_ctrl_f19_f19.sh with test casename,
# xmlchange_test_1day and daily h0. Run from cases-scripts/. Check with tests/check_hr_bvoc_all_1day.py

### CTRL RUN
# Nudging
# Initial file: NF2000norbc_tropstratchem_spinup_f19_f19 (0021-01-01)
# 15 years (2000-2014), matching the extended LCC runs

# Exit if error, undefined variable...
set -euo pipefail
# Load common functions for case setup
source cases-setup.sh
#––––––––––– SIMULATION SPECIFICS: –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
today=$(date +'%Y%m%d')

CASENAME="NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-test-hrbvocall-$today"
COMPSET=NF2000norbc_tropstratchem
set_project_noresm_res_vars

# Restart files specifics:
REFCASE="NF2000norbc_tropstratchem_spinup_f19_f19"
REFDATE="0021-01-01"

REST_SRC="/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive/${REFCASE}/rest/${REFDATE}-00000"
REST_LOCAL="/cluster/home/$USER/restart/${REFCASE}/${REFDATE}-00000"
# I transfer restart files because in original folder are zipped. The unzipped files are all in one place

SURFDATA_FILE='/cluster/shared/noresm/inputdata/lnd/clm2/surfdata_map/release-clm5.0.18/surfdata_1.9x2.5_hist_78pfts_CMIP6_simyr2000_c190304.nc'
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
./xmlchange STOP_OPTION=nyears,STOP_N=5
./xmlchange RESUBMIT=2 # 5 yrs + 2 x 5 yrs = 15 yrs (2000-2014; nudging data end 2015-01-01)
./xmlchange REST_OPTION=nyears,REST_N=1
#./xmlchange DOUT_S_SAVE_INTERIM_RESTART_FILES=FALSE # To avoid saving restarts at the end of each run, which is not necessary for the spinup and takes a lot of space
./xmlchange RUN_STARTDATE=2000-01-01

./xmlchange --subgroup case.st_archive JOB_WALLCLOCK_TIME=23:59:00
./xmlchange --subgroup case.run        JOB_WALLCLOCK_TIME=47:59:00
xmlchange_test_1day   # TEST: 1 model day

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
#./case.build --clean
./case.setup
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

setup_nudging_data 

# Be sure it's the same PD land cover
cat << EOF >> user_nl_clm
fsurdat = '${SURFDATA_FILE}'
use_init_interp = .true.
EOF
cam_diagnostics HR_BVOC_ALL
sed -i -E "s/^nhtfrq( *)= *0, *1$/nhtfrq\1= -24, 1/" user_nl_cam; grep -Eq "^nhtfrq *= -24, 1" user_nl_cam  # TEST: daily h0

install_clm_sourcemods
clm_diagnostics

./case.build
./case.submit