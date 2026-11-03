#!/bin/bash

### LCC_PD_fBVOClccPD RUN (short test: does the fBVOC prescription artefact depend on the land cover?)
# Nudging, 3 years (2000-2002; 2000 = spin-up), exception to the 15-yr rule (user 2026-10-30).
# LCC land; MEGAN off; all 19 MEGAN-fed species prescribed from LCC_PD (its OWN emissions):
#   ISOP/MTERP from SF* (half-hourly), BCARY C3H6 BIGENE CH3CHO CH2O C2H4 from MEG_* (half-hourly),
#   the other 11 from MEG_* (monthly); 2001-2014 climatology of LCC_PD (14a, HR_BVOC_ALL).
# delta_PD = (LCC_PD_fBVOClccPD - LCC_PD) - (CTRL_PD_fBVOCctrlPD - CTRL_PD) = artefact(LCC land) - artefact(CTRL land):
#   diagnostics/fbvoc-prescription-artefact/how_big_artefact_is_PD.ipynb.
# Initial state: LCC coupled spin-up restart, as for LCC_PD and LCC_PD_fBVOCctrlPD.
# New chain: auto_launch_new_chain.sh sets REFCASE and EMS_PREFIX and launches it once the LCC_PD climatology is checked.

# Exit if error, undefined variable...
set -euo pipefail
# Load common functions for case setup
source cases-setup.sh
#––––––––––– SIMULATION SPECIFICS: –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
today=$(date +'%Y%m%d')
CASENAME="NF2000norbc_tropstratchem_nudg_lcc_fBVOClccPD_f19_f19-$today"
COMPSET=NF2000norbc_tropstratchem
set_project_noresm_res_vars

# Restart files specifics:
REFCASE="NF2000norbc_tropstratchem_spinup_lcc_f19_f19-20261025"
REFDATE="0021-01-01"
REST_SRC="/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive/$REFCASE/rest/$REFDATE-00000"
REST_LOCAL="/cluster/home/$USER/restart/${REFCASE}/${REFDATE}-00000"

# Surface data file with modified land cover for boreal forest expansion
SURFDATA_FILE="/cluster/shared/noresm/inputdata/lnd/clm2/surfdata_map/surfdata_1.9x2.5_SSP5-8.5_2100_78pfts_LPJGUESS.nc"

# Prescribed BVOC files: <EMS_PREFIX>_SFISOP.nc, <EMS_PREFIX>_MEG_<species>.nc (19 files)
EMS_PREFIX="/cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions/ems_NF2000norbc_tropstratchem_nudg_lcc_f19_f19-20261028_2001-2014"

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
./xmlchange STOP_OPTION=nyears,STOP_N=3
./xmlchange RESUBMIT=0 # 3 yrs (2000-2002), short test (user 2026-10-30)
./xmlchange REST_OPTION=nyears,REST_N=1
#./xmlchange DOUT_S_SAVE_INTERIM_RESTART_FILES=FALSE # To avoid saving restarts at the end of each run, which is not necessary for the spinup and takes a lot of space
./xmlchange RUN_STARTDATE=2000-01-01

./xmlchange --subgroup case.run JOB_QUEUE=normal
./xmlchange --subgroup case.run        JOB_WALLCLOCK_TIME=30:00:00
./xmlchange --subgroup case.st_archive JOB_QUEUE=preproc
./xmlchange --subgroup case.st_archive JOB_WALLCLOCK_TIME=03:00:00

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
#./case.build --clean
./case.setup
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

cat << EOF >> user_nl_clm
fsurdat = '${SURFDATA_FILE}'
use_init_interp = .true.
EOF

cam_diagnostics
install_clm_sourcemods
clm_diagnostics fBVOC

# Disable all interactive MEGAN and prescribe all 19 MEGAN-fed species from LCC_PD (its own emissions).
prescribed_bvoc_emissions_all 2000 "$EMS_PREFIX"

# The prescribed ISOP already contains its diurnal cycle.
bypass_isoprene_diurnal_adjustment

./case.build
./case.submit
