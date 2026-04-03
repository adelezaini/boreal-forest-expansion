#!/bin/bash

##----------------- 2000 specific functions -----------------##
forcings_2000(){
# NORBC - fSST
./xmlchange SSTICE_DATA_FILENAME=/cluster/shared/noresm/inputdata/noresm-only/atm/cam/sst/fice-micom-divocn_sst-micom-dow_NHIST_f19_tn14_20190710_1995-2005_series_version20260209_clim.nc
./xmlchange OCN_FLUX_SCHEME=1
}

##----------------- 2100 specific functions -----------------##
forcings_2100(){
# NORBC - fSST
./xmlchange SSTICE_DATA_FILENAME=/cluster/shared/noresm/inputdata/noresm-only/atm/cam/sst/fice-micom-divocn_sst-micom-dow_NSSP585frc2_f19_tn14_20191014_2090-2100_series_version20260209_clim.nc
./xmlchange OCN_FLUX_SCHEME=1
}

dms_forcing(){
# DMS forcing to 2000
cat << EOF >> user_nl_cam
&oslo_ctl_nl
ocean_filename = 'dms-hamocc-dow-taylor_chlor_a-lanaclim_NHIST_f19_tn14_20190710_1995-2005_cycle_version20260209.nc'
ocean_filepath = '/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo'
/
EOF
}

##-------------------- common functions --------------------##
base_case_vars() {
    PROJECT="nn9188k"
    NORESM_ROOT="/cluster/home/$USER/NorESM2.3_beta01"
    RES="f19_f19"
}

improve_performance(){
# Improve performance by using more nodes and less threads per node (if needed)
#./xmlchange NTASKS=144
#./xmlchange NTHRDS=1
#./xmlchange ROOTPE_NODE=0
#./xmlchange NTASKS_PER_NODE=36
./xmlchange NTASKS=496
./xmlchange NTASKS_ATM=16
./xmlchange ROOTPE_ATM=496
}

aerosol_cosp_diagnostics(){
# Aerosol diagnostics
./xmlchange CAM_AEROCOM=TRUE

# COSP diagnostics
./xmlchange --append CAM_CONFIG_OPTS='-cosp'
}

cosp_diagnostics(){
# COSP diagnostics
cat << EOF >> user_nl_cam
&cospsimulator_nl
docosp    = .true.
cosp_amwg = .true.
/
EOF
}

cam_diagnostics(){
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

'SOA_SEC01','SOA_SEC02','SOA_SEC03','SOA_SEC04','SOA_SEC05',
'SO4_SEC01','SO4_SEC02','SO4_SEC03','SO4_SEC04','SO4_SEC05',
'nrSOA_SEC01','nrSOA_SEC02','nrSOA_SEC03','nrSOA_SEC04','nrSOA_SEC05',
'nrSO4_SEC01','nrSO4_SEC02','nrSO4_SEC03','nrSO4_SEC04','nrSO4_SEC05',
'cb_SOA_SEC01','cb_SOA_SEC02','cb_SOA_SEC03','cb_SOA_SEC04','cb_SOA_SEC05',
'cb_SO4_SEC01','cb_SO4_SEC02','cb_SO4_SEC03','cb_SO4_SEC04','cb_SO4_SEC05',

'SST','PRECC','PRECL','PRECT','ozone','O3','TROP_P','TROP_T','TROP_Z','VT100',
'MEG_CH3COCH3','MEG_CH3CHO','MEG_CH2O','MEG_CO','MEG_C2H6','MEG_C3H8','MEG_C2H4','MEG_C3H6',
'MEG_C2H5OH','MEG_C10H16','MEG_ISOP','MEG_CH3OH','MEG_isoprene','MEG_monoterp',
'SFisoprene','SFmonoterp','cb_isoprene','cb_monoterp'

fincl2 = 'SFisoprene','SFmonoterp', 
'TROP_O3', 'TROP_NO', 'TROP_NO2', 'TROP_H2O2', 'TROP_HNO3', 'TROP_CO', 
'TROP_SO2', 'TROP_NH3', 'TROP_HCHO', 'TROP_CH4', 'TROP_C2H6', 'TROP_C3H8', 
'TROP_C2H4', 'TROP_C3H6', 'TROP_C2H5OH', 'TROP_C10H16', 'TROP_ISOP', 
'TROP_CH3OH', 'TROP_isoprene', 'TROP_monoterp'
/
EOF
}