#!/bin/bash

# NF2000_tropstratchem test case to see if tropstratchem works - it doesn't:
#case.build error 
# ERROR: Command /cluster/home/adelez/NorESM2.3_beta01/components/cam/bld/build-namelist -ntasks 512 -csmdata /cluster/shared/noresm/inputdata -infile /cluster/home/adelez/cases/BRL_FRST_XPSN/NF2000norbc_tropstratchem_f19_f19_test/Buildconf/camconf/namelist -ignore_ic_year -use_case 2000_cam6_noresm -inputdata /cluster/home/adelez/cases/BRL_FRST_XPSN/NF2000norbc_tropstratchem_f19_f19_test/Buildconf/cam.input_data_list -namelist " &atmexp  aerocomk0_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/aerocomk0.out'   aerocomk1_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/aerocomk1.out'   aerocomk2_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/aerocomk2.out'   aerocomk3_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/aerocomk3.out'   aerocomk4_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/aerocomk4.out'   aerocomk5_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/aerocomk5.out'   aerocomk6_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/aerocomk6.out'   aerocomk7_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/aerocomk7.out'   aerocomk8_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/aerocomk8.out'   aerocomk9_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/aerocomk9.out'   aerocomk10_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/aerocomk10.out'   aerodryk0_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/aerodryk0.out'   aerodryk1_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/aerodryk1.out'   aerodryk2_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/aerodryk2.out'   aerodryk3_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/aerodryk3.out'   aerodryk4_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/aerodryk4.out'   aerodryk5_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/aerodryk5.out'   aerodryk6_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/aerodryk6.out'   aerodryk7_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/aerodryk7.out'   aerodryk8_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/aerodryk8.out'   aerodryk9_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/aerodryk9.out'   aerodryk10_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/aerodryk10.out'   kcomp0_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/kcomp0.out'   kcomp1_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/kcomp1.out'   kcomp2_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/kcomp2.out'   kcomp3_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/kcomp3.out'   kcomp4_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/kcomp4.out'   kcomp5_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/kcomp5.out'   kcomp6_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/kcomp6.out'   kcomp7_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/kcomp7.out'   kcomp8_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/kcomp8.out'   kcomp9_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/kcomp9.out'   kcomp10_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/kcomp10.out'   logntilp1_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/logntilp1.out'   logntilp2_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/logntilp2.out'   logntilp3_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/logntilp3.out'   logntilp4_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/logntilp4.out'   logntilp5_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/logntilp5.out'   logntilp6_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/logntilp6.out'   logntilp7_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/logntilp7.out'   logntilp8_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/logntilp8.out'   logntilp9_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/logntilp9.out'   logntilp10_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/logntilp10.out'   lwkcomp0_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/lwkcomp0.out'   lwkcomp1_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/lwkcomp1.out'   lwkcomp2_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/lwkcomp2.out'   lwkcomp3_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/lwkcomp3.out'   lwkcomp4_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/lwkcomp4.out'   lwkcomp5_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/lwkcomp5.out'   lwkcomp6_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/lwkcomp6.out'   lwkcomp7_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/lwkcomp7.out'   lwkcomp8_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/lwkcomp8.out'   lwkcomp9_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/lwkcomp9.out'   lwkcomp10_file='/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo/AeroTab_8jun17/lwkcomp10.out' /"  failed rc=255
# out===> Using Oslo aerosols: PRESCRIBED AERO = FALSE (not yet implemented)
# err=Cannot set both prescribed_volcaero_file and prescribed_strataero_file

# this is the same error as + %NORBC: NF2000norbc_tropstratchem_f19_f19_test

# so I try NF1850norbc_tropstratchem, which has been already tested. To check tropstratchem variables

# Simulation specifics:
export CASENAME=NF2000_tropstratchem_f19_f19_test
export PROJECT=nn9188k
export NORESM_ROOT=/cluster/home/$USER/NorESM2.3_beta01
export COMPSET=2000_CAM60%NORESM%TROPSTRATCHEM_CLM50%BGC_CICE%PRES_DOCN%DOM_MOSART_SGLC_SWAV
export RES=f19_f19

CASEROOT=$HOME/cases/BRL_FRST_XPSN/$CASENAME
rm -rf $CASEROOT #remove previous cases

cd $NORESM_ROOT/cime/scripts || exit 1

./create_newcase --case $CASEROOT --compset $COMPSET --res $RES --machine betzy --run-unsupported --project $PROJECT --handle-preexisting-dirs r

cd $CASEROOT

./xmlchange CAM_AEROCOM=TRUE #aerosol diagnostics

./xmlchange RUN_TYPE=hybrid
./xmlchange RUN_REFCASE=/nird/datalake/NS9560K/noresm2.3/cases/NF1850norbc_f19_f19_20241127_test01
./xmlchange RUN_REFDATE=1751-01-01
./xmlchange STOP_OPTION=nyears,STOP_N=1

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
