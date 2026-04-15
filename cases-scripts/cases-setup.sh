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
# DMS forcing to 2000 (for 2100 simulation)
cat << EOF >> user_nl_cam
&oslo_ctl_nl
ocean_filename = 'dms-hamocc-dow-taylor_chlor_a-lanaclim_NHIST_f19_tn14_20190710_1995-2005_cycle_version20260209.nc'
ocean_filepath = '/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo'
/
EOF
}

##--------------------coupler history
output_cplhist_auxiliary_files(){
    cat << EOF >> user_nl_cpl
        &seq_infodata_inparm
          histaux_a2x      = .true.
          histaux_a2x1hr   = .true.
          histaux_a2x1hri  = .true.
          histaux_a2x3hr   = .true.
          histaux_a2x3hrp = .false.
          histaux_a2x24hr = .true.
          histaux_l2x     = .true.
          histaux_l2x1yrg = .true.
          histaux_r2x     = .true.
        /
    EOF
}

##-------------------- common functions --------------------##
set_project_noresm_res_vars() {
    PROJECT="nn9188k"
    NORESM_ROOT="/cluster/home/$USER/NorESM2.3_beta01"
    RES="f19_f19"
}

prepare_restart_files() {
    local REST_SRC="$1"
    local REST_LOCAL="$2"

    echo "Preparing restart files..."

    # Check source exists
    if [ ! -d "$REST_SRC" ]; then
        echo "ERROR: source directory does not exist: $REST_SRC"
        return 1
    fi

    # Ensure local directory exists
    mkdir -p "$REST_LOCAL" || return 1

    # Local variables for list of filenames
    local src_list dst_list
    src_list=$(mktemp)
    dst_list=$(mktemp)

    # Remove local temp files to save space when exit
    trap 'rm -f "$src_list" "$dst_list"' RETURN

    # Expected file list from source (strip .gz)
    find "$REST_SRC" -maxdepth 1 -type f -printf '%f\n' \
        | sed 's/\.gz$//' \
        | sort -u > "$src_list"

    # Actual file list from local (exclude .gz)
    find "$REST_LOCAL" -maxdepth 1 -type f ! -name '*.gz' -printf '%f\n' \
        | sort -u > "$dst_list"

    # If list differs, copy files; otherwise skip
    if diff -q "$src_list" "$dst_list" >/dev/null; then
        echo "Restart files already in $REST_LOCAL"
    else
        rsync -havP "$REST_SRC"/ "$REST_LOCAL"/ || return 1
    fi

    # Unzip .gz files
    if find "$REST_LOCAL" -maxdepth 1 -type f -name '*.gz' -print -quit | grep -q .; then
        gunzip -fv "$REST_LOCAL"/*.gz || return 1
        echo "Restart files in $REST_LOCAL"
    fi
}

improve_performance() {
    # Usage: improve_performance [-v|--verbose] A|B|C|Z
    # in 1 day simulation Z (original) > C > A > B 

    if [ ! -x ./xmlchange ] || [ ! -x ./pelayout ]; then
        echo "Error: run this from your case directory."
        return 1
    fi

    TPN=128
    VERBOSE=0

    if [ "$1" = "-v" ] || [ "$1" = "--verbose" ]; then
        VERBOSE=1
        shift
    fi

    case "$1" in
        A|a)
            CASE_NAME="A"
            NTASKS_OTHER=128
            NTASKS_ATM=384
            ROOT_OTHER=384
            ROOT_ATM=0
            STRATEGY="Atmosphere-heavy (~75/25)"
            ;;
        B|b)
            CASE_NAME="B"
            NTASKS_OTHER=256
            NTASKS_ATM=256
            ROOT_OTHER=256
            ROOT_ATM=0
            STRATEGY="Balanced (50/50)"
            ;;
        C|c)
            CASE_NAME="C"
            NTASKS_OTHER=64
            NTASKS_ATM=448
            ROOT_OTHER=448
            ROOT_ATM=0
            STRATEGY="Extreme ATM-heavy (~90/10)"
            ;;
        Z|z)
            CASE_NAME="Z"
            NTASKS_OTHER=512
            NTASKS_ATM=512
            ROOT_OTHER=0
            ROOT_ATM=0
            STRATEGY="Original fully shared layout"
            ;;
        *)
            echo "Usage: improve_performance [-v|--verbose] A|B|C|D|Z"
            return 1
            ;;
    esac

    # Build SETTINGS string (special case for Z)
    if [ "$CASE_NAME" = "Z" ]; then
        SETTINGS="NTASKS=512,NTASKS_ATM=512,ROOTPE_ATM=0,ROOTPE_CPL=0,ROOTPE_LND=0,ROOTPE_ICE=0,ROOTPE_OCN=0,ROOTPE_ROF=0,ROOTPE_GLC=0,ROOTPE_WAV=0"
        TOTAL_TASKS=512
    else
        SETTINGS="NTASKS=$NTASKS_OTHER,NTASKS_ATM=$NTASKS_ATM,ROOTPE_ATM=$ROOT_ATM,ROOTPE_CPL=$ROOT_OTHER,ROOTPE_LND=$ROOT_OTHER,ROOTPE_ICE=$ROOT_OTHER,ROOTPE_OCN=$ROOT_OTHER,ROOTPE_ROF=$ROOT_OTHER,ROOTPE_GLC=$ROOT_OTHER,ROOTPE_WAV=$ROOT_OTHER"
        TOTAL_TASKS=$((ROOT_OTHER + NTASKS_OTHER))
    fi

    ./xmlchange "$SETTINGS" || {
        echo "Error: xmlchange failed."
        return 1
    }

    NODES_USED=$(( (TOTAL_TASKS + TPN - 1) / TPN ))

    if [ "$VERBOSE" -eq 1 ]; then
        echo
        echo "Setting PE layout:"
        echo "  Case                        : $CASE_NAME"
        echo "  Strategy                    : $STRATEGY"
        echo "  ATM tasks                   : $NTASKS_ATM"
        echo "  Shared non-ATM task block   : $NTASKS_OTHER"
        echo "  ATM ROOTPE                  : $ROOT_ATM"
        echo "  Non-ATM ROOTPE              : $ROOT_OTHER"
        echo "  Total tasks                 : $TOTAL_TASKS"
        echo "  Tasks per node              : $TPN"
        echo "  Nodes used                  : $NODES_USED"
        echo
        echo "Resulting pelayout:"
        ./pelayout
    else
        echo "PE layout updated (case=$CASE_NAME)"
    fi
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