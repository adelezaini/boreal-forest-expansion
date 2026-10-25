#!/bin/bash
# 1-day test: copy of 14c-NF2000norbc_tropstratchem_nudg_lcc_fBVOCctrlPD_f19_f19.sh with test casename, xmlchange_test_1day and daily h0.
# Run from cases-scripts/. Check with tests/check_fbvoc_all_1day.py

### LCC_PD_fBVOCctrlPD RUN
# Nudging, 15 years (2000-2014). MEGAN off; all 19 MEGAN-fed species prescribed from CTRL_PD:
#   ISOP/MTERP from SF* (half-hourly), BCARY C3H6 BIGENE CH3CHO CH2O C2H4 from MEG_* (half-hourly),
#   the other 11 from MEG_* (monthly); 2001-2014 climatology (preprocess/bvoc-emissions, run_bvoc_climatology_array.sh).
# Initial state: LCC coupled spin-up restart (REFCASE below), as for the LCC run.
# Keep REFCASE and EMS_PREFIX up to date (CLAUDE.md "When a run version changes").

# Exit if error, undefined variable...
set -euo pipefail
# Load common functions for case setup
source cases-setup.sh
#––––––––––– SIMULATION SPECIFICS: –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
today=$(date +'%Y%m%d')
CASENAME="NF2000norbc_tropstratchem_nudg_lcc_fBVOCctrlPD_f19_f19-test-1day-$today"
COMPSET=NF2000norbc_tropstratchem
set_project_noresm_res_vars

# Restart files specifics:
REFCASE="NF2000norbc_tropstratchem_spinup_lcc_f19_f19-20260928"
REFDATE="0021-01-01"
REST_SRC="/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive/$REFCASE/rest/$REFDATE-00000"
REST_LOCAL="/cluster/home/$USER/restart/${REFCASE}/${REFDATE}-00000"

# Surface data file with modified land cover for boreal forest expansion
SURFDATA_FILE="/cluster/shared/noresm/inputdata/lnd/clm2/surfdata_map/surfdata_1.9x2.5_SSP5-8.5_2100_78pfts_LPJGUESS.nc"

# Prescribed BVOC files: <EMS_PREFIX>_SFISOP.nc, <EMS_PREFIX>_MEG_<species>.nc (19 files)
EMS_PREFIX="/cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions/ems_NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20261023_2001-2014"

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
prepare_restart_files "$REST_SRC" "$REST_LOCAL"

[[ -f "$REST_LOCAL/$REFCASE.clm2.r.$REFDATE-00000.nc" ]] || { echo 'Missing coupled LCC land restart' >&2; exit 1; }
[[ -f "$SURFDATA_FILE" ]] || { echo "Missing surfdata: $SURFDATA_FILE" >&2; exit 1; }
n_ems=$(ls "$EMS_PREFIX"_SF*.nc "$EMS_PREFIX"_MEG_*.nc 2>/dev/null | wc -l)
(( n_ems == 19 )) || { echo "Expected 19 prescribed BVOC files ${EMS_PREFIX}_*.nc, found $n_ems" >&2; exit 1; }

BASE_CASE_DIR="$HOME/cases/BRL_FRST_XPSN/"
CASEROOT="$BASE_CASE_DIR/$CASENAME"

remove_case_if_exists "$CASEROOT" "$BASE_CASE_DIR"

cd $NORESM_ROOT/cime/scripts

./create_newcase --case $CASEROOT --compset $COMPSET --res $RES --machine betzy --run-unsupported --project $PROJECT --handle-preexisting-dirs r

echo "Case $CASENAME created with compset $COMPSET and resolution $RES"

cd $CASEROOT
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

forcings_2000
setup_nudging_data

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

./xmlchange --subgroup case.run JOB_QUEUE=normal
./xmlchange --subgroup case.run        JOB_WALLCLOCK_TIME=30:00:00
./xmlchange --subgroup case.st_archive JOB_QUEUE=preproc
./xmlchange --subgroup case.st_archive JOB_WALLCLOCK_TIME=03:00:00
xmlchange_test_1day   # TEST: 1 model day

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
#./case.build --clean
./case.setup
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

cat << EOF >> user_nl_clm
fsurdat = '${SURFDATA_FILE}'
use_init_interp = .true.
EOF

cam_diagnostics
sed -i -E "s/^nhtfrq( *)= *0$/nhtfrq\1= -24/" user_nl_cam; grep -Eq "^nhtfrq *= -24$" user_nl_cam  # TEST: daily h0
install_clm_sourcemods
clm_diagnostics fBVOC

# Disable all interactive MEGAN and prescribe all 19 MEGAN-fed species from CTRL_PD.
prescribed_bvoc_emissions_all 2000 "$EMS_PREFIX"

# The prescribed ISOP already contains its diurnal cycle.
bypass_isoprene_diurnal_adjustment

./case.build
./case.submit
