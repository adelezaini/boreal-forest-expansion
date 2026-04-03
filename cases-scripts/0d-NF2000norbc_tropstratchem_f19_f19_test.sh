#!/bin/bash

# Copy of 2000 spin up, but without initial files

# Exit if error, undefined variable...
set -euo pipefail
# Load common functions for case setup
source cases-setup.sh

#For test:
today=$(date +'%Y%m%d')
testname="test-$today"
CASENAME="NF2000norbc_tropstratchem_$testname-3"

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Simulation specifics:
COMPSET=NF2000norbc_tropstratchem
base_case_vars


CASEROOT=$HOME/cases/BRL_FRST_XPSN/$CASENAME
#rm -rf "$CASEROOT" #remove previous case

cd $NORESM_ROOT/cime/scripts || exit 1

./create_newcase --case $CASEROOT --compset $COMPSET --res $RES --machine betzy --run-unsupported --project $PROJECT --handle-preexisting-dirs r

cd $CASEROOT

aerosol_cosp_diagnostics
forcings_2000

#Troubleshooting:
./xmlchange CAM_CONFIG_OPTS="-phys cam6 -chem tropstrat_mam_oslo -camnor -cosp"

./xmlchange STOP_OPTION=nyears
./xmlchange STOP_N=1
./xmlchange JOB_WALLCLOCK_TIME=24:00:00

#./case.build --clean
./case.setup

# Diagnostics
cosp_diagnostics
cam_diagnostics

#cat << EOF >> user_nl_clm 
# hist_fincl1 = 'LAISHA', 'LAISUN', 'TLAI', 'FSH', 'FLDS', 'FSDS', 'QSOIL', 'RAINRATE', 'SNOWRATE', 'TSA', 'TSOI', 'WIND', 'ZWT', 'MEG_acetaldehyde','MEG_acetic_acid','MEG_acetone','MEG_carene_3', 'MEG_ethanol','MEG_formaldehyde','MEG_isoprene','MEG_methanol', 'MEG_pinene_a','MEG_thujene_a'
#EOF

./case.build
./case.submit
