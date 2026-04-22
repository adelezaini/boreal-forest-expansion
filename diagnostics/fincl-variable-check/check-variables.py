#!/usr/bin/env python3
import os
import datetime

date = datetime.datetime.now().strftime("%Y-%m-%d")

# --- Define your fincl1 variables ---

comp = 'clm2' # [cam,clm2]
if comp == 'cam':
    fincl1 = [
    'NNAT_0','FSNT','FLNT','FSNT_DRF','FLNT_DRF','FSNTCDRF','FLNTCDRF','FLNS','FSNS','FLNSC','FSNSC',
    'FSDSCDRF','FSDS_DRF','FSUTADRF','FLUTC','FSUS_DRF','FLUS','CLOUD','FCTL','FCTI','NUCLRATE','FORMRATE',
    'GRH2SO4','GRSOA','GR','COAGNUCL','H2SO4','SOA_LV','PS','LANDFRAC','SOA_NA','SO4_NA',
    'NCONC01','NCONC02','NCONC03','NCONC04','NCONC05','NCONC06','NCONC07','NCONC08','NCONC09','NCONC10',
    'NCONC11','NCONC12','NCONC13','NCONC14','SIGMA01','SIGMA02','SIGMA03','SIGMA04','SIGMA05','SIGMA06',
    'SIGMA07','SIGMA08','SIGMA09','SIGMA10','SIGMA11','SIGMA12','SIGMA13','SIGMA14','NMR01','NMR02',
    'NMR03','NMR04','NMR05','NMR06','NMR07','NMR08','NMR09','NMR10','NMR11','NMR12','NMR13','NMR14',
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
    ]
    fincl2 = [
    'SFisoprene','SFmonoterp', 'TROP_O3', 'TROP_NO', 'TROP_NO2', 'TROP_H2O2', 'TROP_HNO3',
    'TROP_CO', 'TROP_SO2', 'TROP_NH3', 'TROP_HCHO', 'TROP_CH4', 'TROP_C2H6', 'TROP_C3H8',
    'TROP_C2H4', 'TROP_C3H6', 'TROP_C2H5OH', 'TROP_C10H16', 'TROP_ISOP', 'TROP_CH3OH',
    'TROP_isoprene', 'TROP_monoterp'
    ]      
elif comp == 'clm2':    
    fincl1 = ['LAISHA', 'LAISUN', 'TLAI', 'FSH', 'FLDS', 'FSDS', 'QSOIL', 'RAINRATE', 'SNOWRATE', 'TSA', 'TSOI', 'WIND', 'ZWT', 'MEG_acetaldehyde','MEG_acetic_acid','MEG_acetone','MEG_carene_3', 'MEG_ethanol','MEG_formaldehyde','MEG_isoprene','MEG_methanol', 'MEG_pinene_a','MEG_thujene_a']
    fincl2 =[]


# --- Function to check variables in a file ---
def check_variables(var_file, fincl, output_prefix):
    if not os.path.exists(var_file):
        print(f"No {var_file} has been generated. Skipping {output_prefix} check.\n")
        return
    with open(var_file) as f:
        vars_in_file = set(line.strip() for line in f)

    found = [v for v in fincl if v in vars_in_file]
    missing = [v for v in fincl if v not in vars_in_file]

    print(f"\n--- {output_prefix} ---")
    print(f"\nCorrected:", found)
    print()

    # Write results to a file
    out_file = f"{comp}_{output_prefix}_variable_check_{date}.txt"
    with open(out_file, "w") as f:
        f.write("Found variables:\n")
        for v in found:
            f.write(v + "\n")
        f.write("\nMissing variables:\n")
        for v in missing:
            f.write(v + "\n")

# --- Check H0 ---
check_variables(f"{comp}_h0_variables.txt", fincl1, "h0")

# --- Check H1 ---
check_variables(f"{comp}_h1_variables.txt", fincl2, "h1")