#!/bin/bash
### CTRL_PD_fBVOCctrlPD_C0102 RUN (diagnostic: 2001-2002 climatology of CTRL_PD's emissions)
# Same as CTRL_PD_fBVOCctrlPD (14c, old-chain 3-yr test) and CTRL_PD_fBVOCctrlPD_HR (14d), but the 19 prescribed species are a
# climatology of CTRL_PD's emissions of the SAME years that are compared (2001-2002) instead of 2001-2014.
# Question (user OK 2026-11-09): the old-chain artefact A = CTRL_PD - CTRL_PD_fBVOCctrlPD = -3.03 % SOA_cb mixes
#   (i) the lost link between emissions and each day's weather and (ii) the 2001-2014 mean differing from 2001-2002.
#   This run has (i) but not (ii): CTRL_PD - C0102 = (i) + prescription path; C0102 - CTRL_PD_fBVOCctrlPD = (ii).
#   Files: <EMS_PREFIX>_{SFISOP,SFMTERP,MEG_*}.nc from preprocess/bvoc-emissions/run_bvoc_climatology_array.sh <CTRL_PD case> 2001 2002.
#   h1: 30-min SFISOP, SFMTERP (HR_BVOC), as in 14d.
# 3 yr (2000-2002, 2000 dropped as spin-up): exception to the 15-yr rule, like 14c-old/14d.
# Old chain on purpose: REFCASE and EMS_PREFIX pinned (not set by auto_launch).
# Exit if error, undefined variable...
set -euo pipefail
# Load common functions for case setup
source cases-setup.sh
#––––––––––– SIMULATION SPECIFICS: –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
today=$(date +'%Y%m%d')
CASENAME="NF2000norbc_tropstratchem_nudg_ctrl_fBVOCctrlPD_C0102_f19_f19-$today"
COMPSET=NF2000norbc_tropstratchem
set_project_noresm_res_vars

# Restart files specifics (as 14c and CTRL_PD -20261023):
REFCASE="NF2000norbc_tropstratchem_spinup_f19_f19"
REFDATE="0021-01-01"
REST_SRC="/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive/$REFCASE/rest/$REFDATE-00000"
REST_LOCAL="/cluster/home/$USER/restart/${REFCASE}/${REFDATE}-00000"

# PD surface data (CTRL land cover), as in 13a
SURFDATA_FILE="/cluster/shared/noresm/inputdata/lnd/clm2/surfdata_map/release-clm5.0.18/surfdata_1.9x2.5_hist_78pfts_CMIP6_simyr2000_c190304.nc"

# Prescribed BVOC files: 2001-2002 climatology of CTRL_PD -20261023 (19 species)
EMS_PREFIX="/cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions/ems_NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20261023_2001-2002"
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
prepare_restart_files "$REST_SRC" "$REST_LOCAL"

[[ -f "$REST_LOCAL/$REFCASE.clm2.r.$REFDATE-00000.nc" ]] || { echo 'Missing coupled CTRL land restart' >&2; exit 1; }
[[ -f "$SURFDATA_FILE" ]] || { echo "Missing surfdata: $SURFDATA_FILE" >&2; exit 1; }
n_ems=$(ls "${EMS_PREFIX}"_SF*.nc "${EMS_PREFIX}"_MEG_*.nc 2>/dev/null | wc -l)
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

# Simulation length: three 1-year jobs (2000-2002), as 14d; 2000 dropped as spin-up -> compare 2001-2002 with CTRL_PD
./xmlchange STOP_OPTION=nyears,STOP_N=1
./xmlchange RESUBMIT=2
./xmlchange REST_OPTION=nyears,REST_N=1
./xmlchange RUN_STARTDATE=2000-01-01

./xmlchange --subgroup case.run JOB_QUEUE=normal
./xmlchange --subgroup case.run        JOB_WALLCLOCK_TIME=08:00:00
./xmlchange --subgroup case.st_archive JOB_QUEUE=preproc
./xmlchange --subgroup case.st_archive JOB_WALLCLOCK_TIME=03:00:00

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
./case.setup
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

cat << EOF >> user_nl_clm
fsurdat = '${SURFDATA_FILE}'
use_init_interp = .true.
EOF

cam_diagnostics HR_BVOC
install_clm_sourcemods
clm_diagnostics fBVOC

# Disable all interactive MEGAN and prescribe all 19 MEGAN-fed species (2001-2002 climatology of CTRL_PD).
prescribed_bvoc_emissions_all 2000 "$EMS_PREFIX"
# The prescribed ISOP already contains its diurnal cycle.
bypass_isoprene_diurnal_adjustment
./case.build
./case.submit
