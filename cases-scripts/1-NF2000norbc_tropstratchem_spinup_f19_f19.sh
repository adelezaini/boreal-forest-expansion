#!/bin/bash

# Spinup for MET and CTRL_PD, extra output: cpl auxiliary files for land-only run
# Free run, no nudging
# Initial file: NHIST_f19_tn14_20190710 (2000-01-01)
# 20/30 years

# Exit if error, undefined variable...
set -euo pipefail
# Load common functions for case setup
source cases-setup.sh

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Simulation specifics:
CASENAME=NF2000norbc_tropstratchem_spinup_f19_f19
COMPSET=NF2000norbc_tropstratchem
base_case_vars

# Initial files:
REFCASE=NHIST_f19_tn14_20190710
REFDATE=0031-01-01-00000
RUNDIR=/cluster/projects/$PROJECT/$USER/cases/$CASENAME/run/
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

CASEROOT=$HOME/cases/BRL_FRST_XPSN/$CASENAME
rm -rf "$CASEROOT" #remove previous case

cd $NORESM_ROOT/cime/scripts || exit 1

./create_newcase --case $CASEROOT --compset $COMPSET --res $RES --machine betzy --run-unsupported --project $PROJECT --handle-preexisting-dirs r

cd $CASEROOT

aerosol_cosp_diagnostics
forcings_2000

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
mkdir -p "$RUNDIR"
cp /nird/datalake/NS9560K/noresm2.3/cases/"$REFCASE"/rest/"$REFDATE"/* "$RUNDIR"

shopt -s nullglob
gz_files=("$RUNDIR"/*.gz)
if ((${#gz_files[@]})); then
    gunzip "${gz_files[@]}"
fi
shopt -u nullglob

./xmlchange RUN_TYPE=hybrid
./xmlchange RUN_REFCASE="$REFCASE"
./xmlchange RUN_REFDATE="$REFDATE"
#./xmlchange STOP_OPTION=nyears,STOP_N=1
# Alternatevely: I could directly copy to RUNDIR=/cluster/projects/nn9188k/adelez/cases/$CASENAME/run and avoid the next commands
#./xmlchange RUN_REFDIR=$REFDIR                     # path to restarts 
#./xmlchange GET_REFCASE=TRUE                       # get refcase from outside rundir
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

#./xmlchange --subgroup case.st_archive JOB_WALLCLOCK_TIME=23:59:00
#./xmlchange --subgroup case.run        JOB_WALLCLOCK_TIME=48:59:00

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

#./case.build
#./case.submit
