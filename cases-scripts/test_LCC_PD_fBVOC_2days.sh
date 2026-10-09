#!/bin/bash
# LCC_PD_fBVOC: two-day July test of prescribed total ISOP/MTERP.
# January restart + July start tests the forcing, not July equilibrium.
# Keep this script beside case-setup.sh (or cases-setup.sh). Requires the existing fBVOC helpers.
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
SETUP_DIR="$SCRIPT_DIR"
if [[ -f "$SETUP_DIR/case-setup.sh" ]]; then
    source "$SETUP_DIR/case-setup.sh"
else
    source "$SETUP_DIR/cases-setup.sh"
fi

today=$(date +'%Y%m%d')
CASENAME="NF2000norbc_tropstratchem_nudg_lcc_fBVOC_f19_f19-test-2day-$today"
COMPSET="NF2000norbc_tropstratchem"
set_project_noresm_res_vars

REFCASE="NF2000norbc_tropstratchem_spinup_lcc_f19_f19-20260928"
REFDATE="0021-01-01"
REST_SRC="/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive/${REFCASE}/rest/${REFDATE}-00000"
REST_LOCAL="/cluster/home/$USER/restart/${REFCASE}/${REFDATE}-00000"
SURFDATA_FILE="/cluster/shared/noresm/inputdata/lnd/clm2/surfdata_map/surfdata_1.9x2.5_SSP5-8.5_2100_78pfts_LPJGUESS.nc"

# Original year-2000 files, NOT the on_yr2100 copies.
BVOC_DIR="/cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions"
CTRL="NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20260925"
ISOP_FILE="$BVOC_DIR/ems_${CTRL}_2001-2009_SFISOP.nc"
MTERP_FILE="$BVOC_DIR/ems_${CTRL}_2001-2009_SFMTERP.nc"
STARTDATE="2000-07-01"  # Requires nudging data covering July 1-3.

BASE_CASE_DIR="$HOME/cases/BRL_FRST_XPSN"
CASEROOT="$BASE_CASE_DIR/$CASENAME"
[[ ! -e "$CASEROOT" ]] || { echo "Case exists: $CASEROOT. Choose a new CASENAME." >&2; exit 1; }

for file in "$SURFDATA_FILE" "$ISOP_FILE" "$MTERP_FILE" "$SETUP_DIR/bypass_isoprene_diurnal_adjustment.py"; do
    [[ -f "$file" ]] || { echo "Missing input: $file" >&2; exit 1; }
done
prepare_restart_files "$REST_SRC" "$REST_LOCAL"
[[ -f "$REST_LOCAL/$REFCASE.clm2.r.$REFDATE-00000.nc" ]] || {
    echo 'Missing coupled LCC land restart' >&2; exit 1;
}

# 1. Create an independent test case; never remove a production case.
cd "$NORESM_ROOT/cime/scripts"
./create_newcase --case "$CASEROOT" --compset "$COMPSET" --res "$RES" \
    --machine betzy --run-unsupported --project "$PROJECT"
cd "$CASEROOT"

forcings_2000
setup_nudging_data

./xmlchange RUN_TYPE=hybrid
./xmlchange RUN_REFCASE="$REFCASE",RUN_REFDATE="$REFDATE"
./xmlchange RUN_REFDIR="$REST_LOCAL",GET_REFCASE=TRUE
./xmlchange RUN_STARTDATE="$STARTDATE",CONTINUE_RUN=FALSE
./xmlchange STOP_OPTION=ndays,STOP_N=2,RESUBMIT=0
./xmlchange REST_OPTION=ndays,REST_N=2
./xmlchange DOUT_S=FALSE  # Leave test histories/logs in RUNDIR.
./xmlchange --subgroup case.run JOB_QUEUE=normal
./xmlchange --subgroup case.run JOB_WALLCLOCK_TIME=02:00:00
# Two hours is a requested limit, not a measured runtime guarantee.
./case.setup

# 2. Land surface, diagnostics and case-local source modifications.
cat >> user_nl_clm <<EOF
fsurdat = '${SURFDATA_FILE}'
use_init_interp = .true.
EOF

cam_diagnostics HR_BVOC
install_clm_sourcemods
clm_diagnostics fBVOC

# Disable all interactive MEGAN and prescribe PD ISOP/MTERP.
prescribed_bvoc_emissions

# The prescribed ISOP already contains its diurnal cycle.
bypass_isoprene_diurnal_adjustment

./preview_namelists

grep -nE 'srf_emis_type|srf_emis_cycle_yr|ISOP[[:space:]]*->|MTERP[[:space:]]*->|nhtfrq|mfilt|avgflag_pertape|fincl2|dtime' \
    CaseDocs/atm_in

./case.build
./case.submit