#!/bin/bash

### LC_FUT_fBVOC RUN
# Nudging
# Initial file: NF2000norbc_tropstratchem_spinup_lcc_f19_f19 (XXXX-XX-XX)
# 15 years to start

# Exit if error, undefined variable...
set -euo pipefail
# Load common functions for case setup
source cases-setup.sh
#––––––––––– SIMULATION SPECIFICS: –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
today=$(date +'%Y%m%d')
CASENAME="NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOC_f19_f19-$today"
COMPSET=NF2100ssp585norbc_tropstratchem
set_project_noresm_res_vars

# Restart files specifics:
REFCASE="NF2100ssp585norbc_tropstratchem_quick_spinup_lcc_f19_f19"
REFDATE="XXXX-01-01"

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
./xmlchange STOP_OPTION=nyears,STOP_N=5
./xmlchange RESUBMIT=1 # 5 yrs + 1 x 5 yrs = 10 yrs
./xmlchange REST_OPTION=nyears,REST_N=1
#./xmlchange DOUT_S_SAVE_INTERIM_RESTART_FILES=FALSE # To avoid saving restarts at the end of each run, which is not necessary for the spinup and takes a lot of space
./xmlchange RUN_STARTDATE=2000-01-01

./xmlchange --subgroup case.st_archive JOB_WALLCLOCK_TIME=23:59:00
./xmlchange --subgroup case.run        JOB_WALLCLOCK_TIME=47:59:00

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
#./case.build --clean
./case.setup
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

setup_nudging_data 

# Land cover change - boreal forest expansion
# Modified idealized surfdata file
cat << EOF >> user_nl_clm
fsurdat = '${SURFDATA_FILE}'
use_init_interp = .true.
EOF

cosp_diagnostics
cam_diagnostics #HR_BVOC
clm_diagnostics

prescribed_bvoc_emissions

echo "CHECK IN CaseDocs/atm_in IF srf_emis_specifierS REPLACED IT OR MERGED IT"

#./case.build
#./case.submit

