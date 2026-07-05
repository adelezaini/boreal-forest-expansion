#!/bin/bash

# Note: CASENAME="NF2100ssp585norbc_tropstratchem_spinup_f19_f19-3" with final -3

### 2100 Spinup for extra output cpl auxiliary files for land-only run
# Free run, no nudging
# Initial file: NSSP585frc2_f19_tn14_20191014 (2100-01-01)
# 20/30 years
# Clphist auxiliary files as extra output

# -2 I made the walltime longer:
#  ./xmlchange JOB_WALLCLOCK_TIME=48:00:00
# But then problem:
#   2026-04-18 17:18:26: case.submit error 
#   ERROR: Command: 'sbatch --time 48:00:00 --account nn9188k  --dependency=afterok:1490364 case.st_archive --resubmit' failed with error 'b'sbatch: error: Batch job submission failed: Requested time limit is invalid (missing or exceeds some limit)'' from dir '/cluster/projects/nn9188k/adelez/cases/BRL_FRST_XPSN/NF2100ssp585norbc_tropstratchem_spinup_f19_f19-2'
# -3 try fix:
#   ./xmlchange --subgroup case.st_archive JOB_WALLCLOCK_TIME=23:59:00
#   ./xmlchange --subgroup case.run        JOB_WALLCLOCK_TIME=48:59:00

# Exit if error, undefined variable...
set -euo pipefail
# Load common functions for case setup
source cases-setup.sh

#––––––––––– SIMULATION SPECIFICS: –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
CASENAME="NF2100ssp585norbc_tropstratchem_spinup_f19_f19-3"
COMPSET=NF2100ssp585norbc_tropstratchem
set_project_noresm_res_vars

# Restart files specifics:
REFCASE="NSSP585frc2_f19_tn14_20191014"
REFDATE="2100-01-01"

REST_SRC="/nird/datalake/NS9560K/olivie/restart/${REFCASE}/${REFDATE}-00000"
REST_LOCAL="/cluster/home/$USER/restart/${REFCASE}/${REFDATE}-00000"

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
prepare_restart_files "$REST_SRC" "$REST_LOCAL"

CASEROOT=$HOME/cases/BRL_FRST_XPSN/$CASENAME
rm -rf "$CASEROOT" #remove previous case

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
./xmlchange RESUBMIT=3 # 5 yrs + 3 x 5 yrs = 20 yrs
./xmlchange REST_OPTION=nyears,REST_N=1
./xmlchange DOUT_S_SAVE_INTERIM_RESTART_FILES=FALSE # To avoid saving restarts at the end of each run, which is not necessary for the spinup and takes a lot of space
./xmlchange RUN_STARTDATE=0001-01-01

#./xmlchange JOB_WALLCLOCK_TIME=48:00:00 # ok with ~7 simulated years/day for STOP_N = 5 years
./xmlchange --subgroup case.st_archive JOB_WALLCLOCK_TIME=23:59:00
./xmlchange --subgroup case.run        JOB_WALLCLOCK_TIME=48:59:00

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
#./case.build --clean
./case.setup

# From error (why?)
echo -e " use_init_interp = .true.">> user_nl_clm
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

cam_spinup_diagnostics
clm_spinup_diagnostics

output_cplhist_auxiliary_files

#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
./case.build
./case.submit
