#!/bin/bash

### LCC_SPINUP_FUT
# Free run, no nudging
# Set LCC
# Initial state: I2100ssp585Clm50BgcCropCplHist_f19_f19 (0101-01-01)
# 20 year spinup

# Exit if error, undefined variable...
set -euo pipefail
# Load common functions for case setup
source cases-setup.sh
#––––––––––– SIMULATION SPECIFICS: –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
today=$(date +%Y%m%d)
CASENAME="NF2100ssp585norbc_tropstratchem_spinup_lcc_f19_f19-$today"
COMPSET=NF2100ssp585norbc_tropstratchem
set_project_noresm_res_vars

REFCASE=NF2100ssp585norbc_tropstratchem_spinup_f19_f19-3
REFDATE=0021-01-01
REST_SRC="/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive/$REFCASE/rest/$REFDATE-00000"
REST_LOCAL="/cluster/home/$USER/restart/$REFCASE/$REFDATE-00000"

# CLM finitdat = 100 year spinup
LAND_CASE="I2100ssp585Clm50BgcCropCplHist_f19_f19-20260924"
LAND_REFDATE="0101-01-01"
LAND_SRC="/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive/$LAND_CASE/rest/$LAND_REFDATE-00000"
LAND_LOCAL="/cluster/home/$USER/restart/$LAND_CASE/$LAND_REFDATE-00000"
LAND_RESTART="$LAND_LOCAL/$LAND_CASE.clm2.r.$LAND_REFDATE-00000.nc"

SURFDATA_FILE=/cluster/shared/noresm/inputdata/lnd/clm2/surfdata_map/surfdata_1.9x2.5_SSP5-8.5_2100_78pfts_LPJGUESS.nc

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
prepare_restart_files "$REST_SRC" "$REST_LOCAL"
prepare_restart_files "$LAND_SRC" "$LAND_LOCAL"
[[ -f "$LAND_RESTART" ]] || { echo "Missing land restart: $LAND_RESTART" >&2; exit 1; }
[[ -f "$SURFDATA_FILE" ]] || { echo "Missing surfdata: $SURFDATA_FILE" >&2; exit 1; }

BASE_CASE_DIR="$HOME/cases/BRL_FRST_XPSN"
CASEROOT="$BASE_CASE_DIR/$CASENAME"
remove_case_if_exists "$CASEROOT" "$BASE_CASE_DIR"
cd "$NORESM_ROOT/cime/scripts"
./create_newcase --case "$CASEROOT" --compset "$COMPSET" --res "$RES" --machine betzy --run-unsupported --project "$PROJECT" --handle-preexisting-dirs r
cd "$CASEROOT"
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

forcings_2100
dms_forcing_2100_to_2000

# Change CAM_NAMELIST_OPTS, which overrides ocean_filename in user_nl_cam.
#cam_opts=$(./xmlquery CAM_NAMELIST_OPTS --value)
#future_dms=dms-hamocc-dow-taylor_chlor_a-lanaclim_NSSP585frc2_f19_tn14_20191014_2090-2100_cycle_version20260209.nc
#pd_dms=dms-hamocc-dow-taylor_chlor_a-lanaclim_NHIST_f19_tn14_20190710_1995-2005_cycle_version20260209.nc
#[[ "$cam_opts" == *"$future_dms"* && "$cam_opts" == *dms_cycle_year=2100* ]] || { echo 'Unexpected CAM_NAMELIST_OPTS DMS settings' >&2; exit 1; }
#cam_opts="${cam_opts//$future_dms/$pd_dms}"
#cam_opts="${cam_opts//dms_cycle_year=2100/dms_cycle_year=2000}"
#./xmlchange "CAM_NAMELIST_OPTS=$cam_opts"

./xmlchange RUN_TYPE=hybrid,RUN_REFCASE="$REFCASE",RUN_REFDATE="$REFDATE",RUN_REFDIR="$REST_LOCAL",GET_REFCASE=TRUE
./xmlchange RUN_STARTDATE=0001-01-01,STOP_OPTION=nyears,STOP_N=5,RESUBMIT=3
./xmlchange REST_OPTION=nyears,REST_N=5,DOUT_S_SAVE_INTERIM_RESTART_FILES=FALSE

# Simulated years ~ 4.5
./xmlchange --subgroup case.st_archive JOB_WALLCLOCK_TIME=03:00:00
./xmlchange --subgroup case.run JOB_WALLCLOCK_TIME=35:00:00

./case.setup

cat >> user_nl_clm <<EOF
fsurdat = '$SURFDATA_FILE'
finidat = '$LAND_RESTART'
use_init_interp = .true.
EOF
cam_spinup_diagnostics
clm_spinup_diagnostics

#grep -Fq "$pd_dms" CaseDocs/atm_in
#grep -Eq 'dms_cycle_year[[:space:]]*=[[:space:]]*2000' CaseDocs/atm_in
./case.build
./case.submit
