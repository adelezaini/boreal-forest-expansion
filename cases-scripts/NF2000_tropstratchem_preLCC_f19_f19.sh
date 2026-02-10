#!/bin/bash




######## OLD!
# CTRL case: 
# - no vegetation shift, 
# - AMIP simul (details in %NORPDDMSBC) with sectional scheme(%SEC) and nudging (%SDYN)
# - 7 years (starts in 2007, matching the nudging)

# OBS! This script copy the restart files from the work directory from the spin up run, 
# careful because the work directory is not backuped and can loose data

set -o errexit #like assert to check and quit program in case of error
set -o nounset

# Simulation specifics:
export CASENAME=CTRL_2000_f19_f19
export SPINUP_CASENAME=CTRL_2000_spinup_f19_f19
export RESTART_DATE=0036-01-01
#–––––––––––––––––––––––––––––––––––––––––

export NORESM_ACCOUNT=nn8057k #NN8057K
export PROJECT=nn8057k
export NORESM_ROOT=/cluster/home/$USER/NorESM-sec
export NORESM_DATA=/cluster/shared/noresm/inputdata
export COMPSET=2000_CAM60%NORESM%SEC%NORPDDMSBC%SDYN_CLM50%BGC-CROP_CICE%PRES_DOCN%DOM_MOSART_SGLC_SWAV
export RES=f19_f19
#–––––––––––For spin up
export RESTART_SPINUP_DIR=~/work/archive/$SPINUP_CASENAME/rest/${RESTART_DATE}-00000 #work -> /cluster/work/users/adelez
export RESTART_DIR=~/noresm-inputdata/restart-cases/$CASENAME/${RESTART_DATE}-00000 #/run #noresm-inputdata -> /cluster/projects/nn8057k/adelez/noresm-inputdata

cd $NORESM_ROOT

#TAG=$(git describe)
CASEROOT=~/cases/$CASENAME #-$RES #$COMPSET-$RES-$CASE_NAME

rm -rf $CASEROOT #remove previous cases

cd cime/scripts
./create_newcase --case $CASEROOT --compset $COMPSET --res $RES --machine betzy --run-unsupported --project $NORESM_ACCOUNT --handle-preexisting-dirs r

cd $CASEROOT

#–––––––––––––– Restart from spinup
# 1. move data from work/archive/spinup-casename/rest to noresm-inpudata and unzip it
mkdir -p $RESTART_DIR
rsync -avz $RESTART_SPINUP_DIR/* $RESTART_DIR/
gunzip -fv $RESTART_DIR/*.gz
# 2. Hybrid run: restart from spinned up climate, but with start date matching nudging
./xmlchange RUN_TYPE=hybrid
./xmlchange RUN_REFCASE=$SPINUP_CASENAME            # experiment name for restart files
./xmlchange RUN_REFDATE=${RESTART_DATE}                  # date of restart files
./xmlchange RUN_STARTDATE=2007-01-01                # date in simulation - matches with ERA-Interim nudging
# Alternatevely: I could directly copy to RUNDIR=/cluster/work/users/adelez/noresm/CASENAME/run and avoid the next commands
./xmlchange RUN_REFDIR=$RESTART_DIR                 # path to restarts 
./xmlchange GET_REFCASE=TRUE                        # get refcase from outside rundir 

#–––––––––––––––––
./xmlchange STOP_OPTION=nyears
./xmlchange STOP_N=6
# Restart default
./xmlchange REST_OPTION=nyears
./xmlchange REST_N=1 #Produce restart files every REST_N=1 years (or the REST_OPTION)
#./xmlchange CONTINUE_RUN=TRUE
./xmlchange JOB_WALLCLOCK_TIME=24:00:00
# Nudging
./xmlchange CALENDAR=GREGORIAN
#./xmlchange CAM_CONFIG_OPTS=-offline_dyn


#./case.build --clean
./case.setup

# Nudging ERA-Interrim
echo -e  "&metdata_nl\n met_nudge_only_uvps = .true.\n met_data_file= \"/cluster/shared/noresm/inputdata/noresm-only/inputForNudging/AZ/ERA_f19_tn14/2007-01-01.nc\"\n met_filenames_list = \"/cluster/shared/noresm/inputdata/noresm-only/inputForNudging/AZ/ERA_f19_tn14/fileList.txt\"\n met_rlx_time = 6\n&cam_initfiles_nl\n bnd_topo = \"/cluster/shared/noresm/inputdata/noresm-only/inputForNudging/ERA_f19_tn14/ERA_bnd_topo.nc\"\n" >> user_nl_cam
# Aerosol diagnostic and decomposition
echo -e  "&phys_ctl_nl\n history_aerosol = .true.\n" >> user_nl_cam
cp ~/noresm-inputdata/preprocessorDefinitions.h SourceMods/src.cam
# Output
echo -e "&cam_inparam\n mfilt = 1, 48\n nhtfrq = 0, 1\n avgflag_pertape='A','I'\n fincl1 = 'NNAT_0','FSNT','FLNT','FSNT_DRF','FLNT_DRF','FSNTCDRF','FLNTCDRF','FLNS','FSNS','FLNSC','FSNSC','FSDSCDRF','FSDS_DRF','FSUTADRF','FLUTC','FSUS_DRF','FLUS','CLOUD','FCTL','FCTI','NUCLRATE', 'FORMRATE','GRH2SO4', 'GRSOA', 'GR', 'COAGNUCL','H2SO4','SOA_LV','PS','LANDFRAC','COAGNUCL','FORMRATE','NUCLRATE','SOA_LV','H2SO4','SOA_NA','SO4_NA','NCONC01','NCONC02','NCONC03','NCONC04','NCONC05','NCONC06','NCONC07','NCONC08','NCONC09','NCONC10','NCONC11','NCONC12','NCONC13','NCONC14','SIGMA01','SIGMA02','SIGMA03','SIGMA04','SIGMA05','SIGMA06','SIGMA07','SIGMA08','SIGMA09','SIGMA10','SIGMA11','SIGMA12','SIGMA13','SIGMA14','NMR01','NMR02','NMR03','NMR04','NMR05','NMR06','NMR07','NMR08','NMR09','NMR10','NMR11','NMR12','NMR13','NMR14','FSNS','FSDS_DRF','GR','GRH2SO4','GRSOA','CCN1','CCN2','CCN3','CCN4','CCN5','CCN6','CCN7','CCN_B','TGCLDCWP','cb_H2SO4','cb_SOA_LV','cb_SOA_NA','cb_SO4_NA','CLDTOT','CDNUMC','SO2','isoprene','monoterp','SOA_SV','OH_vmr','AOD_VIS','CAODVIS','CLDFREE','CDOD550','CDOD440','CDOD870','AEROD_v','CABS550','CABS550A','SOA_SEC01','SOA_SEC02','SOA_SEC03','SOA_SEC04','SOA_SEC05','SO4_SEC01','SO4_SEC02','SO4_SEC03','SO4_SEC04','SO4_SEC05','nrSOA_SEC01','nrSOA_SEC02','nrSOA_SEC03','nrSOA_SEC04','nrSOA_SEC05','nrSO4_SEC01','nrSO4_SEC02','nrSO4_SEC03','nrSO4_SEC04','nrSO4_SEC05','SOA_SEC01','SOA_SEC02','SOA_SEC03','SOA_SEC04','SOA_SEC05','SO4_SEC01','SO4_SEC02','SO4_SEC03','SO4_SEC04','SO4_SEC05','nrSOA_SEC01','nrSOA_SEC02','nrSOA_SEC03','nrSOA_SEC04','nrSOA_SEC05','nrSO4_SEC01','nrSO4_SEC02','nrSO4_SEC03','nrSO4_SEC04','nrSO4_SEC05','cb_SOA_SEC01','cb_SOA_SEC02','cb_SOA_SEC03','cb_SOA_SEC04','cb_SOA_SEC05','cb_SO4_SEC01','cb_SO4_SEC02','cb_SO4_SEC03','cb_SO4_SEC04','cb_SO4_SEC05'\n fincl2='SFisoprene','SFmonoterp'" >> user_nl_cam

#./case.build
#./case.submit

