#!/bin/bash

# Copy of 2000 spin up, but without initial files
# 
# -2: change the ozone to O3 (this is the letter O not the numbero zero)
# -3: change the O3 to 03
# -4: I add restart files
# there were tests because NorESM was not cloned well with the new edits, and dms files missed 2000 year

# Exit if error, undefined variable...
set -euo pipefail
# Load common functions for case setup
source cases-setup.sh

#––––––––––– For tests - adding date to name to avoid overwriting previous tests:
today=$(date +'%Y%m%d')
testname="test-$today"
CASENAME="NF2000norbc_tropstratchem_${testname}-timing_C"

#––––––––––– SIMULATION SPECIFICS: –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
COMPSET=NF2000norbc_tropstratchem
set_project_noresm_res_vars

# Restart files specifics:
REFCASE="NHIST_tropstratchem_01_f19_tn14_r1990_s01_20241118"
REFDATE="2000-01-01"

REST_SRC="/nird/datalake/NS9560K/olivie/restart/${REFCASE}/${REFDATE}-00000"
REST_LOCAL="/cluster/home/$USER/restart/${REFCASE}_${REFDATE}-00000"

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
prepare_restart_files "$REST_SRC" "$REST_LOCAL"

CASEROOT=$HOME/cases/BRL_FRST_XPSN/$CASENAME
rm -rf "$CASEROOT" #remove previous case

cd $NORESM_ROOT/cime/scripts || exit 1

./create_newcase --case $CASEROOT --compset $COMPSET --res $RES --machine betzy --run-unsupported --project $PROJECT --handle-preexisting-dirs r

echo "Case $CASENAME created with compset $COMPSET and resolution $RES"

cd $CASEROOT 

# chek permance with layout change:
# improve_performance -v C

aerosol_cosp_diagnostics
forcings_2000

#Troubleshooting:
#./xmlchange CAM_CONFIG_OPTS="-phys cam6 -chem tropstrat_mam_oslo -camnor -cosp"

# Initial files from restart
./xmlchange RUN_TYPE=hybrid
./xmlchange RUN_REFCASE="$REFCASE"
./xmlchange RUN_REFDATE="$REFDATE"
./xmlchange RUN_REFDIR="$REST_LOCAL"
./xmlchange GET_REFCASE=TRUE

# Simulation length
./xmlchange STOP_OPTION=nyears
./xmlchange STOP_N=1
./xmlchange JOB_WALLCLOCK_TIME=24:00:00

#./case.build --clean
./case.setup

# From error (why?)
echo -e " use_init_interp = .true.">> user_nl_clm

# Diagnostics
cosp_diagnostics
cam_diagnostics

#cat << EOF >> user_nl_clm 
# hist_fincl1 = 'LAISHA', 'LAISUN', 'TLAI', 'FSH', 'FLDS', 'FSDS', 'QSOIL', 'RAINRATE', 'SNOWRATE', 'TSA', 'TSOI', 'WIND', 'ZWT', 'MEG_acetaldehyde','MEG_acetic_acid','MEG_acetone','MEG_carene_3', 'MEG_ethanol','MEG_formaldehyde','MEG_isoprene','MEG_methanol', 'MEG_pinene_a','MEG_thujene_a'
#EOF

./case.build
./case.submit
