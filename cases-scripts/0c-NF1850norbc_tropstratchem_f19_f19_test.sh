#!/bin/bash

# NF18500_tropstratchem test case to check output variables

# Simulation specifics:
export CASENAME=NF1850norbc_tropstratchem_f19_f19_test
export PROJECT=nn9188k
export NORESM_ROOT=/cluster/home/$USER/NorESM2.3_beta01
export COMPSET=1850_CAM60%NORESM%NORBC%TROPSTRATCHEM_CLM50%BGC_CICE%PRES_DOCN%DOM_MOSART_SGLC_SWAV
export RES=f19_f19

# Initial files:
export REFCASE=NF1850norbc_f19_f19_20241127_test01
export REFDATE=0031-01-01
export REFDIR=run
#–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

CASEROOT=$HOME/cases/BRL_FRST_XPSN/$CASENAME
rm -rf $CASEROOT #remove previous cases

cd $NORESM_ROOT/cime/scripts || exit 1

./create_newcase --case $CASEROOT --compset $COMPSET --res $RES --machine betzy --run-unsupported --project $PROJECT --handle-preexisting-dirs r

cd $CASEROOT

./xmlchange CAM_AEROCOM=TRUE #aerosol diagnostics

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
mkdir -p $CASEROOT/run
cp /nird/datalake/NS9560K/noresm2.3/cases/$REFCASE/rest/${REFDATE}-00000/* $CASEROOT/run/
gunzip $CASEROOT/run/*.gz 
echo "Copied restarts from $REFCASE at $REFDATE to $CASEROOT/run/ and unzipped them"

./xmlchange RUN_TYPE=hybrid
./xmlchange RUN_REFCASE=$REFCASE
./xmlchange RUN_REFDATE=$REFDATE
#./xmlchange STOP_OPTION=nyears,STOP_N=1
# Alternatevely: I could directly copy to RUNDIR=/cluster/projects/nn9188k/adelez/cases/$CASENAME/run and avoid the next commands
./xmlchange RUN_REFDIR=$REFDIR                     # path to restarts 
./xmlchange GET_REFCASE=TRUE                       # get refcase from outside rundir
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

#./xmlchange --subgroup case.st_archive JOB_WALLCLOCK_TIME=23:59:00
#./xmlchange --subgroup case.run        JOB_WALLCLOCK_TIME=48:59:00

#./case.build --clean
./case.setup

# Diagnostics
cat << EOF >> user_nl_cam
 mfilt = 1, 48
 nhtfrq = 0, 1
 avgflag_pertape='A','I' 
 history_aerosol=.true.
 fincl1 = 'NNAT_0','FSNT','FLNT','FSNT_DRF','FLNT_DRF','FSNTCDRF','FLNTCDRF','FLNS','FSNS','FLNSC','FSNSC',
'FSDSCDRF','FSDS_DRF','FSUTADRF','FLUTC','FSUS_DRF','FLUS','CLOUD','FCTL','FCTI','NUCLRATE','FORMRATE',
'GRH2SO4','GRSOA','GR','COAGNUCL','H2SO4','SOA_LV','PS','LANDFRAC','SOA_NA','SO4_NA',

'NCONC01','NCONC02','NCONC03','NCONC04','NCONC05','NCONC06','NCONC07','NCONC08','NCONC09','NCONC10','NCONC11','NCONC12','NCONC13','NCONC14',
'SIGMA01','SIGMA02','SIGMA03','SIGMA04','SIGMA05','SIGMA06','SIGMA07','SIGMA08','SIGMA09','SIGMA10','SIGMA11','SIGMA12','SIGMA13','SIGMA14',
'NMR01','NMR02','NMR03','NMR04','NMR05','NMR06','NMR07','NMR08','NMR09','NMR10','NMR11','NMR12','NMR13','NMR14',


'CCN1','CCN2','CCN3','CCN4','CCN5','CCN6','CCN7','CCN_B','TGCLDCWP','cb_H2SO4','cb_SOA_LV','cb_SOA_NA','cb_SO4_NA',
'CLDTOT','CDNUMC','SO2','isoprene','monoterp','SOA_SV','OH_vmr','AOD_VIS','CAODVIS','CLDFREE',
'CDOD550','CDOD440','CDOD870','AEROD_v','CABS550','CABS550A',

'SST','PRECC','PRECL','PRECT','ozone','O3','TROP_P','TROP_T','TROP_Z','VT100',
'MEG_isoprene','MEG_monoterp', 'SFisoprene','SFmonoterp','cb_isoprene','cb_monoterp',
'MEG_CH3COCH3','MEG_CH3CHO','MEG_CH2O','MEG_CO','MEG_C2H6','MEG_C3H8','MEG_C2H4','MEG_C3H6', 'MEG_C2H5OH','MEG_C10H16','MEG_ISOP','MEG_CH3OH'
 fincl2 = 'SFisoprene','SFmonoterp',
'TROP_O3', 'TROP_NO', 'TROP_NO2', 'TROP_H2O2', 'TROP_HNO3', 'TROP_CO', 'TROP_SO2', 'TROP_NH3', 'TROP_HCHO', 'TROP_CH4', 'TROP_C2H6', 'TROP_C3H8', 'TROP_C2H4', 'TROP_C3H6', 'TROP_C2H5OH', 'TROP_C10H16', 'TROP_ISOP', 'TROP_CH3OH', 'TROP_isoprene', 'TROP_monoterp'
EOF

# Look when full atmospheric chemistry:
# fincl1 = 'MEG_CH3COCH3','MEG_CH3CHO','MEG_CH2O','MEG_CO','MEG_C2H6','MEG_C3H8','MEG_C2H4','MEG_C3H6', 'MEG_C2H5OH','MEG_C10H16','MEG_ISOP','MEG_CH3OH'
# fincl2 = 'TROP_O3', 'TROP_NO', 'TROP_NO2', 'TROP_H2O2', 'TROP_HNO3', 'TROP_CO', 'TROP_SO2', 'TROP_NH3', 'TROP_HCHO', 'TROP_CH4', 'TROP_C2H6', 'TROP_C3H8', 'TROP_C2H4', 'TROP_C3H6', 'TROP_C2H5OH', 'TROP_C10H16', 'TROP_ISOP', 'TROP_CH3OH', 'TROP_isoprene', 'TROP_monoterp'

#cat << EOF >> user_nl_clm 
# doesn't work
# hist_fincl1 = 'LAISHA', 'LAISUN', 'TLAI', 'FSH', 'FLDS', 'FSDS', 'QSOIL', 'RAINRATE', 'SNOWRATE', 'TSA', 'TSOI', 'WIND', 'ZWT', 'MEG_acetaldehyde','MEG_acetic_acid','MEG_acetone','MEG_carene_3', 'MEG_ethanol','MEG_formaldehyde','MEG_isoprene','MEG_methanol', 'MEG_pinene_a','MEG_thujene_a'
#EOF

./xmlchange STOP_OPTION=nyears
./xmlchange STOP_N=1
./xmlchange JOB_WALLCLOCK_TIME=24:00:00

#./case.build
#./case.submit


#Sara's sectional scheme:

#fincl1 = 'SOA_SEC01','SOA_SEC02','SOA_SEC03','SOA_SEC04','SOA_SEC05',
#'SO4_SEC01','SO4_SEC02','SO4_SEC03','SO4_SEC04','SO4_SEC05',
#'nrSOA_SEC01','nrSOA_SEC02','nrSOA_SEC03','nrSOA_SEC04','nrSOA_SEC05',
#'nrSO4_SEC01','nrSO4_SEC02','nrSO4_SEC03','nrSO4_SEC04','nrSO4_SEC05',
#'cb_SOA_SEC01','cb_SOA_SEC02','cb_SOA_SEC03','cb_SOA_SEC04','cb_SOA_SEC05',
#'cb_SO4_SEC01','cb_SO4_SEC02','cb_SO4_SEC03','cb_SO4_SEC04','cb_SO4_SEC05',
