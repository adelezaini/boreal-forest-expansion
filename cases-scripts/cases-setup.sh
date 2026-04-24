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

dms_forcing_2100_to_2000(){
# DMS forcing to 2000 (for 2100 simulation)
cat << EOF >> user_nl_cam
&oslo_ctl_nl
ocean_filename = 'dms-hamocc-dow-taylor_chlor_a-lanaclim_NHIST_f19_tn14_20190710_1995-2005_cycle_version20260209.nc'
ocean_filepath = '/cluster/shared/noresm/inputdata/noresm-only/atm/cam/camoslo'
/
EOF
}

##----------------- general utility functions -----------------##
set_project_noresm_res_vars() {
    PROJECT="nn9188k"
    NORESM_ROOT="/cluster/home/$USER/NorESM2.3_beta01"
    RES="f19_f19"
}

##----------------- restart file handling -----------------##
prepare_restart_files() {
    # Synchronizes restart files from a source directory to a local directory.
    # Usage: prepare_restart_files <source_directory> <local_directory>
    #
    # Example:
    # REST_SRC="/nird/datalake/NS9560K/olivie/restart/${REFCASE}/${REFDATE}-00000"
    # REST_LOCAL="/cluster/home/$USER/restart/${REFCASE}_${REFDATE}-00000"
    # prepare_restart_files "$REST_SRC" "$REST_LOCAL"

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

##----------------- coupler history auxiliary files -----------------##
output_cplhist_auxiliary_files(){
    # Output auxiliary files for coupler history (cplhist) to be able to run an offline CLM simulation with my climate data and not the default ones in NorESM2.3
    # To add to the coupled/AMIP run, prior to the land-only run 
    # Source: https://noresm-docs.readthedocs.io/en/noresm2/configurations/clm.html#spin-up-of-clm5
cat << EOF >> user_nl_cpl
&seq_infodata_inparm
  histaux_a2x      = .true.
  histaux_a2x1hr   = .true.
  histaux_a2x1hri  = .true.
  histaux_a2x3hr   = .true.
  histaux_a2x3hrp  = .false.
  histaux_a2x24hr  = .true.
  histaux_l2x      = .true.
  histaux_l2x1yrg  = .false.
  histaux_r2x      = .true.
/
EOF
}

datm_forcing_from_cplhist_files() {
    # xmlchange to use the cplhist auxiliary files as forcing for the datm component in a land-only simulation (after a coupled/AMIP run)
    # To add to the land-only run, after the coupled/AMIP run
    # Source: https://noresm-docs.readthedocs.io/en/noresm2/configurations/clm.html#spin-up-of-clm5
    # Source: https://docs.cesm.ucar.edu/models/cesm2/settings/2.1.1/datm_input.html
    local year="${1:?Usage: datm_forcing_from_cplhist_files <2000|2100>}"

    local cplhist_dir
    local cplhist_case

    case "$year" in
        2000)
            cplhist_case="NF2000norbc_tropstratchem_spinup_f19_f19"
            cplhist_dir="/cluster/shared/noresm/inputdata/cplhist/NF2000norbc_tropstratchem_spinup_f19_f19_20260421_01-20"
            ;;
        2100)
            cplhist_case="NF2100ssp585norbc_tropstratchem_spinup_f19_f19-3"
            cplhist_dir="/cluster/shared/noresm/inputdata/cplhist/NF2100ssp585norbc_tropstratchem_spinup_f19_f19_20260422_01-20"
            ;;
        *)
            echo "ERROR: unsupported CPLHIST forcing year"
            echo "Usage: datm_forcing_from_cplhist_files <2000|2100>"
            return 1
            ;;
    esac

    ./xmlchange DATM_MODE=CPLHIST,DATM_PRESAERO=cplhist,DATM_TOPO=cplhist
    ./xmlchange DATM_CPLHIST_DIR="$cplhist_dir"
    ./xmlchange DATM_CPLHIST_CASE="$cplhist_case"

    # Forcing year = model_year - ALIGN + START
    ./xmlchange DATM_CPLHIST_YR_ALIGN=1
    ./xmlchange DATM_CPLHIST_YR_START=11
    ./xmlchange DATM_CPLHIST_YR_END=20
    # With RUN_STARTDATE=0001-01-01, model year 1 uses CPLHIST year 11.
    # Avoid using the first 10 years of the cplhist data, which are the spinup years, and loop over the last 10 years of the cplhist data (years 11-20).
    # Example: if a simulation is 100 years long, it will loop 10 x over 11-20 of the cplhist data (1 -> 11, 2 -> 12, ..., 10 -> 20, 11 -> 11, ...,  100 -> 20).
}


##----------------- nudging ------------------##
cam_generate_nudging_data(){
# Generate meteorological fields for nudging (NorESM2 / CAM)
cat << EOF >> user_nl_cam
&camexp
  mfilt = 1, 4
  nhtfrq = 0, -6
  avgflag_pertape = 'A','I'

  fincl2 = 'PS','U','V','T','Q'
EOF

}

##----------------- extra diagnostics -----------------##
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

clm_diagnostics(){
cat << EOF >> user_nl_clm 
hist_fincl1 = 'TSA','TLAI','LAISHA','LAISUN','FSH','EFLX_LH_TOT','FSA','FIRA','FSDS','FLDS',
'RAIN','SNOW','RAINRATE','SNOWRATE',
'QSOIL','QVEGE','QVEGT','QOVER','QRUNOFF','H2OSOI','SOILLIQ','SOILICE','TSOI',
'GPP','NPP','AR','HR','NEE','WIND', 'ZWT', 
'MEG_acetaldehyde','MEG_acetic_acid','MEG_acetone','MEG_carene_3', 'MEG_ethanol',
'MEG_formaldehyde','MEG_isoprene','MEG_methanol', 'MEG_pinene_a','MEG_thujene_a'
EOF
}


cam_spinup_diagnostics(){
# To check if reached equilibrium in the spinup
cat << EOF >> user_nl_cam
mfilt = 365
nhtfrq = -24
avgflag_pertape = 'A'

fincl1 = 'TREFHT','PSL','PRECT','PS','U10','V10','FSNT','FLNT','FSNS','FLNS','FSNSC','FLNSC','FLUTC','FSNT_DRF','FLNT_DRF','FSNTCDRF','FLNTCDRF','CLOUD','CLDTOT','LANDFRAC'
EOF
}

clm_spinup_diagnostics(){
# To check if reached equilibrium in the spinup
cat << EOF >> user_nl_clm
hist_mfilt = 365
hist_nhtfrq = -24

hist_fincl1 = 'TSA','TLAI','LAISHA','LAISUN',
'TOTVEGC','TOTSOMC','TOTECOSYSC',
'GPP','NPP','AR','HR','NEE',
'FSH','EFLX_LH_TOT','FSA','FIRA','FSDS','FLDS',
'RAIN','SNOW',
'QSOIL','QVEGE','QVEGT','QOVER','QRUNOFF',
'H2OSOI','SOILLIQ','SOILICE','TSOI','ZWT'

EOF
}

clm_long_spinup_diagnostics(){
# To check if reached equilibrium in the spinup
cat << EOF >> user_nl_clm
hist_mfilt  = 10
hist_nhtfrq = -8760

hist_fincl1 = 'TSA','TLAI','TOTVEGC','TOTSOMC','TOTECOSYSC',
'GPP','NPP','AR','HR','NEE',
'FSH','EFLX_LH_TOT','FSA','FIRA','FSDS','FLDS',
'RAIN','SNOW',
'QSOIL','QVEGE','QVEGT','QOVER','QRUNOFF',
'H2OSOI','SOILLIQ','SOILICE','TSOI','ZWT'

EOF
}

# Safely remove a case directory.
# Asks for confirmation (y/[n], default = no)
# Usage: remove_case_if_exists "$CASEROOT" "$BASE_CASE_DIR"
# Example: 
#   BASE_CASE_DIR="$HOME/cases/BRL_FRST_XPSN"
#   CASEROOT="$BASE_CASE_DIR/$CASENAME"

remove_case_if_exists() {
    local caseroot="$1"   # full path to the case directory to delete
    local base_dir="$2"   # only allow deletion inside this directory

    # Resolve absolute paths (important for safety):
    # removes "..", symbolic links, etc., so checks are reliable
    local caseroot_abs
    local base_dir_abs
    caseroot_abs=$(realpath -m "$caseroot")
    base_dir_abs=$(realpath "$base_dir")

    # Fail if path resolution failed (unexpected → safer to stop)
    if [[ -z "$caseroot_abs" || -z "$base_dir_abs" ]]; then
        echo "ERROR: could not resolve paths. Only absolute paths are allowed."
        exit 1
    fi

    # Only allow deletion if caseroot is INSIDE base_dir
    if [[ "$caseroot_abs" == "$base_dir_abs" || "$caseroot_abs" != "$base_dir_abs/"* ]]; then
        echo "ERROR: refusing to delete case directory, because it is outside base directory."
        echo "       attempted – absolute path: $caseroot_abs"
        exit 1
    fi

    # If directory does not exist, nothing to remove → exit function, continue script
    [ -d "$caseroot_abs" ] || return 0

    # Ask user confirmation (default = NO to avoid accidental Enter)
    read -rp "Remove $caseroot_abs? y/[n]: " confirm
    confirm=${confirm:-n}

    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        rm -rf -- "$caseroot_abs"   # -- protects against weird path names
        echo "Removed existing $caseroot_abs
        "
    else
        echo "Aborted. Try again!"
        exit 1
    fi
}




##----------------- -------------------------------------------------------- -----------------##
##----------------- performance testing function (layout of the simulations) -----------------##
improve_performance() {
    # Usage: improve_performance [-v|--verbose] A|B|C|Z
    # Z (original) > C > A > B 
    # -> this function is good to test but it is not used in the final simulations (we use Z/original for all simulations)

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