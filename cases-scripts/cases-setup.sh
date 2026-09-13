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

    # Set other important paths
    SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)" 
    REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
}

##------ safely remove a case directory
# Asks for confirmation (y/[n], default = no)
# Usage: remove_case_if_exists "$CASEROOT" "$BASE_CASE_DIR"

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

setup_nudging_data () {
    local CASENAME=NF2000norbc_tropstratchem_met_f19_f19_20260422

    local NUDGDIR="/cluster/shared/noresm/inputdata/noresm-only/inputForNudging/AZ/${CASENAME}_6h_2000-2015"
    local FILELIST="${NUDGDIR}/${CASENAME}.cam.h1_filelist.txt"
    local METFILE="${NUDGDIR}/${CASENAME}.cam.h1.2000-01-01-00000.nc"

    ./xmlchange --append CAM_CONFIG_OPTS='-offline_dyn'

    [[ -d "$NUDGDIR" ]] || { echo "ERROR: missing NUDGDIR: $NUDGDIR"; return 1; }
    [[ -f "$FILELIST" ]] || { echo "ERROR: missing file list: $FILELIST"; return 1; }
    [[ -f "$METFILE" ]] || { echo "ERROR: missing met_data_file: $METFILE"; return 1; }

    cat >> user_nl_cam <<EOF

&metdata_nl
  met_nudge_only_uvps = .true.
  met_data_file       = '${METFILE}'
  met_filenames_list  = '${FILELIST}'
  met_rlx_time        = 6
/

EOF
}

##----------------- BVOC emissions -----------------##
prescribed_bvoc_emissions(){
cat << EOF >> user_nl_cam
&megan_emis_nl
 megan_specifier = ''
/

&chem_inparm
 srf_emis_specifier		= 'BC_AX  ->  /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_BC_AX_anthrosurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'BC_N   ->  /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_BC_N_anthrosurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'OM_NI  ->  /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_OM_NI_anthrosurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'SO2    ->  /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_SO2_anthrosurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'SO4_PR ->  /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_SO4_PR_anthrosurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'BENZENE -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_BENZENE_anthrosurfgasALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'BENZENE -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_BENZENE_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'BIGALK -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_BIGALK_anthrosurfgasALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'BIGALK -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_BIGALK_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'BIGENE -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_BIGENE_anthrosurfgasALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'BIGENE -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_BIGENE_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'C2H2 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_C2H2_anthrosurfgasALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'C2H2 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_C2H2_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'C2H4 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_C2H4_anthrosurfgasALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'C2H4 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_C2H4_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'C2H5OH -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_C2H5OH_anthrosurfgasALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'C2H5OH -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_C2H5OH_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'C2H6 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_C2H6_anthrosurfgasALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'C2H6 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_C2H6_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'C3H6 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_C3H6_anthrosurfgasALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'C3H6 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_C3H6_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'C3H8 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_C3H8_anthrosurfgasALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'C3H8 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_C3H8_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'CH2O -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_CH2O_anthrosurfgasALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'CH2O -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_CH2O_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'CH3CHO -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_CH3CHO_anthrosurfgasALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'CH3CHO -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_CH3CHO_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'CH3CN -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_CH3CN_anthrosurfgasALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'CH3CN -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_CH3CN_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'CH3COCH3 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_CH3COCH3_anthrosurfgasALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'CH3COCH3 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_CH3COCH3_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'CH3COCHO -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_CH3COCHO_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'CH3COOH -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_CH3COOH_anthrosurfgasALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'CH3COOH -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_CH3COOH_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'CH3OH -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_CH3OH_anthrosurfgasALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'CH3OH -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_CH3OH_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'CO -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_CO_anthrosurfgasALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'CO -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_CO_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'DMS -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_DMS_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'GLYALD -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_GLYALD_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'HCN -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_HCN_anthrosurfgasALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'HCN -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_HCN_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'HCOOH -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_HCOOH_anthrosurfgasALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'HCOOH -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_HCOOH_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'ISOP -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_ISOP_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'MEK -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_MEK_anthrosurfgasALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'MEK -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_MEK_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'MTERP -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_MTERP_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'NH3 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_NH3_anthrosurfgasALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'NH3 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_NH3_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'NO -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_NO_anthrosurfgasALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'NO -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_NO_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'TOLUENE -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_TOLUENE_anthrosurfgasALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'TOLUENE -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_TOLUENE_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'XYLENES -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_XYLENES_anthrosurfgasALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'XYLENES -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_XYLENES_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'E90 ->  /cluster/shared/noresm/inputdata/atm/cam/chem/emis/CMIP6_emissions_1750_2015/emissions_E90global_surface_1750-2100_0.9x1.25_c20170322.nc',
         'C2H4 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/CMIP6_emissions_1750_2015_2deg/emissions-cmip6_C2H4_other_surface_1750-2015_1.9x2.5_c20170322.nc',
         'C2H6 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/CMIP6_emissions_1750_2015_2deg/emissions-cmip6_C2H6_other_surface_1750-2015_1.9x2.5_c20170322.nc',
         'C3H6 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/CMIP6_emissions_1750_2015_2deg/emissions-cmip6_C3H6_other_surface_1750-2015_1.9x2.5_c20170322.nc',
         'C3H8 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/CMIP6_emissions_1750_2015_2deg/emissions-cmip6_C3H8_other_surface_1750-2015_1.9x2.5_c20170322.nc',
         'CO -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/CMIP6_emissions_1750_2015_2deg/emissions-cmip6_CO_other_surface_1750-2015_1.9x2.5_c20170322.nc',
         'NH3 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/CMIP6_emissions_1750_2015_2deg/emissions-cmip6_NH3_other_surface_1750-2015_1.9x2.5_c20170322.nc',
         'NO -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/CMIP6_emissions_1750_2015_2deg/emissions-cmip6_NO_other_surface_1750-2015_1.9x2.5_c20170322.nc',
         'ISOP  -> /cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions/ems_NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20260429_2002-2011_SFISOP.nc',
         'MTERP -> /cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions/ems_NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20260429_2002-2011_SFMTERP.nc'
/
EOF
}

prescribed_bvoc_emissions_2100(){
cat << EOF >> user_nl_cam
&megan_emis_nl
 megan_specifier = ''
/

&chem_inparm
 srf_emis_specifier		= 'BC_AX  ->  /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_BC_AX_anthrosurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'BC_N   ->  /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_BC_N_anthrosurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'OM_NI  ->  /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_OM_NI_anthrosurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'SO2    ->  /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_SO2_anthrosurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'SO4_PR ->  /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_SO4_PR_anthrosurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'BENZENE -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_BENZENE_anthrosurfgasALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'BENZENE -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_BENZENE_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'BIGALK -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_BIGALK_anthrosurfgasALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'BIGALK -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_BIGALK_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'BIGENE -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_BIGENE_anthrosurfgasALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'BIGENE -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_BIGENE_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'C2H2 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_C2H2_anthrosurfgasALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'C2H2 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_C2H2_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'C2H4 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_C2H4_anthrosurfgasALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'C2H4 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_C2H4_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'C2H5OH -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_C2H5OH_anthrosurfgasALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'C2H5OH -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_C2H5OH_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'C2H6 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_C2H6_anthrosurfgasALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'C2H6 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_C2H6_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'C3H6 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_C3H6_anthrosurfgasALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'C3H6 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_C3H6_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'C3H8 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_C3H8_anthrosurfgasALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'C3H8 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_C3H8_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'CH2O -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_CH2O_anthrosurfgasALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'CH2O -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_CH2O_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'CH3CHO -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_CH3CHO_anthrosurfgasALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'CH3CHO -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_CH3CHO_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'CH3CN -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_CH3CN_anthrosurfgasALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'CH3CN -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_CH3CN_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'CH3COCH3 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_CH3COCH3_anthrosurfgasALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'CH3COCH3 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_CH3COCH3_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'CH3COCHO -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_CH3COCHO_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'CH3COOH -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_CH3COOH_anthrosurfgasALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'CH3COOH -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_CH3COOH_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'CH3OH -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_CH3OH_anthrosurfgasALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'CH3OH -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_CH3OH_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'CO -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_CO_anthrosurfgasALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'CO -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_CO_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'DMS -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_DMS_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'GLYALD -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_GLYALD_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'HCN -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_HCN_anthrosurfgasALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'HCN -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_HCN_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'HCOOH -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_HCOOH_anthrosurfgasALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'HCOOH -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_HCOOH_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'ISOP -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_ISOP_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'MEK -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_MEK_anthrosurfgasALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'MEK -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_MEK_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'MTERP -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_MTERP_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'NH3 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_NH3_anthrosurfgasALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'NH3 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_NH3_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'NO -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_NO_anthrosurfgasALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'NO -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_NO_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'TOLUENE -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_TOLUENE_anthrosurfgasALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'TOLUENE -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_TOLUENE_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'XYLENES -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_XYLENES_anthrosurfgasALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'XYLENES -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_XYLENES_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'E90 ->  /cluster/shared/noresm/inputdata/atm/cam/chem/emis/CMIP6_emissions_1750_2015/emissions_E90global_surface_175001-210101_0.9x1.25_c20190224.nc',
         'C2H4 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/emissions_ssp585_2deg/emissions-cmip6_C2H4_other_surface_1750-2015-2101_1.9x2.5_c20170322.nc',
         'C2H6 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/emissions_ssp585_2deg/emissions-cmip6_C2H6_other_surface_1750-2015-2101_1.9x2.5_c20170322.nc',
         'C3H6 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/emissions_ssp585_2deg/emissions-cmip6_C3H6_other_surface_1750-2015-2101_1.9x2.5_c20170322.nc',
         'C3H8 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/emissions_ssp585_2deg/emissions-cmip6_C3H8_other_surface_1750-2015-2101_1.9x2.5_c20170322.nc',
         'CO -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/emissions_ssp585_2deg/emissions-cmip6_CO_other_surface_1750-2015-2101_1.9x2.5_c20170322.nc',
         'NH3 -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/emissions_ssp585_2deg/emissions-cmip6_NH3_other_surface_1750-2015-2101_1.9x2.5_c20170322.nc',
         'NO -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/emissions_ssp585_2deg/emissions-cmip6_NO_other_surface_1750-2015-2101_1.9x2.5_c20170322.nc'
         'ISOP  -> /cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions/ems_NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20260429_2002-2011_on_yr2100_SFISOP.nc',
         'MTERP -> /cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions/ems_NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20260429_2002-2011_on_yr2100_SFMTERP.nc'
/
EOF
}

xmlchange_test_1day() {
# Run for one model day.
# Remember to change the casename
    ./xmlchange STOP_OPTION=ndays,STOP_N=1
    ./xmlchange RESUBMIT=0
    ./xmlchange REST_OPTION=ndays,REST_N=1
    ./xmlchange DOUT_S_SAVE_INTERIM_RESTART_FILES=FALSE

    ./xmlchange --subgroup case.run        JOB_WALLCLOCK_TIME=01:00:00
    ./xmlchange --subgroup case.st_archive JOB_WALLCLOCK_TIME=00:30:00
}

##----------------- diagnostics -----------------##
aerosol_diagnostics(){
./xmlchange CAM_AEROCOM=TRUE
}

cosp_diagnostics_presetup(){
./xmlchange --append CAM_CONFIG_OPTS='-cosp'
}

cosp_diagnostics_postsetup(){
# COSP diagnostics
cat << EOF >> user_nl_cam
&cospsimulator_nl
docosp    = .true.
cosp_amwg = .true.
/
EOF
}

cam_diagnostics(){
    # optional arg "HR_BVOC" -> add an h1 tape of 30-min BVOC surface fluxes (CTRL only),
    # for tests: set nhtfrq = -24
    ./xmlchange CAM_AEROCOM=TRUE

    if [[ "${1:-}" == "HR_BVOC" ]]; then
        cat << 'EOF' >> user_nl_cam
empty_htapes    = .true.
history_aerosol = .true.
docosp          = .false.
mfilt           = 1, 48
nhtfrq          = 0, 1
avgflag_pertape = 'A', 'I'
EOF
    else
        cat << 'EOF' >> user_nl_cam
empty_htapes    = .true.
history_aerosol = .true.
docosp          = .false.
mfilt           = 1
nhtfrq          = 0
avgflag_pertape = 'A'
EOF
    fi

    # --- h0 whitelist (fincl1): identical for every member ---
    cat << 'EOF' >> user_nl_cam
fincl1 = 'FSNT','FSNTC','FLNT','FLNTC','FLUT','FLUTC',
       'FSNTOA','FSNTOAC','SOLIN','FSNS','FSNSC','FLNS',
       'FLNSC','FSDS','FSDSC','FLDS','SWCF','LWCF',
       'FSNT_DRF','FLNT_DRF','FSNTCDRF','FLNTCDRF','FSDS_DRF','FSDSCDRF',
       'FSUTADRF','FSUS_DRF','FLUS',
       'SFISOP','SFMTERP','SFBCARY','cb_ISOP','cb_MTERP','cb_BCARY',
       'MEG_ISOP','MEG_MTERP','MEG_BCARY','emis_ISOP','emis_MTERP','ISOP',
       'MTERP','BCARY',
       'SOA_LV','SOA_SV','H2SO4','SOA_NA','SOA_A1','SO4_NA',
       'SO4_A1','N_AER','cb_SOA_LV','cb_SOA_SV','cb_H2SO4',
       'NUCLRATE','FORMRATE','COAGNUCL','GR','GRH2SO4','GRSOA',
       'ORGNUCL','NUCLSOA',
       'SOA_NAcondTend','SOA_A1condTend','SOA_NAcoagTend','SOA_A1coagTend','SOA_NA_mixnuc1','SOA_A1_mixnuc1',
       'SO4_NAcondTend','SO4_A1condTend','SO4_NAcoagTend','SO4_A1coagTend','SO4_NA_mixnuc1','SO4_A1_mixnuc1',
       'SOA_NADDF','SOA_A1DDF','SO4_NADDF','SO4_A1DDF','DF_H2SO4','SOA_NASFWET',
       'SOA_A1SFWET','SO4_NASFWET','SO4_A1SFWET','WD_A_H2SO4','WD_H2SO4',
       'CCN1','CCN2','CCN3','CCN4','CCN5','CCN6',
       'CCN7','CCN_B',
       'AOD_VIS','AEROD_v','DOD550','DOD440','DOD870','ABS550',
       'ABS550_A','OD550DRY','AB550DRY','CABS550','A550_BC','A550_POM',
       'A550_SO4','A550_SS','A550_DU',
       'CDNUMC','TGCLDLWP','TGCLDIWP','TGCLDCWP','CLDTOT','CLDLOW',
       'CLDMED','CLDHGH','ACTREL','ACTREI','ACTNL','FCTL',
       'FCTI',
       'CLOUD','CLDLIQ','CLDICE','AREL','AREI','AWNC',
       'FREQL','FREQI','NUMLIQ','NUMICE',
       'TS','TREFHT','SHFLX','LHFLX','PRECC','PRECL',
       'PRECSC','PRECSL','TAUX','TAUY','PSL','U10',
       'QREFHT','LANDFRAC','OCNFRAC','ICEFRAC','SNOWHLND',
       'O3','OH','CH4','NO','NO2','CO',
       'HO2','TROP_P','TROP_T','TROP_Z',
       'T','Q','U','V','OMEGA','Z3',
       'PS'
EOF

    # --- h1 hourly-BVOC tape (CTRL only), feeds the emission-climatology script ---
    if [[ "${1:-}" == "HR_BVOC" ]]; then
        cat << 'EOF' >> user_nl_cam
fincl2 = 'SFISOP','SFMTERP'
EOF
    fi

    cat << 'EOF' >> user_nl_cam
/
EOF
}

#-------------------------------------------------------------------------------
# Install CLM SourceMods
#
# Copies the repository version of VOCEmissionMod.F90 into the current CIME
# case. This modified module adds compound-specific MEGAN diagnostics:
# EPS_<compound>,GAMMA_<compound>,GAMMAP_<compound>,GAMMAT_<compound>,GAMMAA_<compound>
# It also provides GAMMAL, GAMMAS, and GAMMAC_isoprene.
#
# Call this function after create_newcase and before case.build. It can be
# called either before or after case.setup.
#-------------------------------------------------------------------------------
install_clm_sourcemods() {

    local source_file="$REPO_ROOT/model/SourceMods/src.clm/VOCEmissionMod.F90"
    local destination_dir="$CASEROOT/SourceMods/src.clm"

    if [[ ! -f "$source_file" ]]; then
        echo "ERROR: SourceMod not found: $source_file" >&2
        return 1
    fi

    mkdir -p "$destination_dir"

    cp "$source_file" \
       "$destination_dir/VOCEmissionMod.F90"

    echo "Installed CLM SourceMod:"
    echo "  $destination_dir/VOCEmissionMod.F90"
}

#-------------------------------------------------------------------------------
# Configure CLM history diagnostics
#
# Installs the modified VOCEmissionMod.F90 required for the compound-specific
# EPS_* and GAMMA_* history fields, then configures the CLM h0 history stream.
#
# With hist_dov2xy(1)=.true., diagnostics registered at patch level are
# aggregated by the CLM history system and written on the model grid. These
# GAMMA_* fields should be interpreted as area-weighted diagnostics over the
# contributing patches, not necessarily as emission-weighted effective gamma.

# Require: install_clm_sourcemods should be called before
#-------------------------------------------------------------------------------
_clm_diagnostics_base() {
# if test: hist_nhtfrq = -24   # daily instead of 0 (monthly)

    cat << 'EOF' >> user_nl_clm
hist_mfilt        = 1
hist_nhtfrq       = 0
hist_avgflag_pertape = 'A'
hist_dov2xy            = .true.
hist_fincl1 = 'FSA','FSR','FIRA','FIRE','FSH','EFLX_LH_TOT',
       'FGR','FSDS','FLDS','FSDSVD','FSDSVI','FSDSND',
       'FSDSNI','FSRVD','FSRND','H2OSNO','SNOWDP','FSNO',
       'SNOWLIQ','SNOWICE','TSA','TV','TG','TSKIN',
       'TSOI','TLAI','ELAI','LAISUN','LAISHA','TSAI',
       'HTOP','PARVEGLN','BTRANMN','QFLX_EVAP_TOT','QSOIL','QVEGE',
       'QVEGT','QINTR','QOVER','QRUNOFF','RAIN','SNOW',
       'H2OSOI','SOILLIQ','SOILICE','ZWT','GPP','NPP',
       'AR','HR','NEE','WIND','PCT_NAT_PFT',

EOF
}

#-------------------------------------------------------------------------------
# Configure CLM history diagnostics
#
# Usage:
#   clm_diagnostics         Std run with extended MEGAN diagnostics
#   clm_diagnostics fBVOC   Fixed-BVOC run with base CLM diagnostics only
#
# Both configurations install the same CLM SourceMod so that paired experiments
# are compiled from identical CLM source, even if the fixed-BVOC configuration does not
# request EPS_*, GAMMA_*, or MEG_* history fields.
#-------------------------------------------------------------------------------
clm_diagnostics() {
    local configuration="${1:-std}"

    case "$configuration" in
        std|fBVOC)
            ;;
        *)
            echo "ERROR: unknown CLM diagnostics configuration: $configuration" >&2
            echo "Expected: std or fBVOC" >&2
            return 1
            ;;
    esac

    # Add the common surface, hydrology and carbon-cycle fields.
    _clm_diagnostics_base

    # Fixed-BVOC runs do not need the extended MEGAN history fields.
    if [[ "$configuration" == "fBVOC" ]]; then
        return 0
    fi

    cat <<'EOF' >> user_nl_clm

hist_fincl1 += 'MEG_isoprene','MEG_carene_3','MEG_limonene','MEG_myrcene',
    'MEG_pinene_a','MEG_pinene_b',     
    'MEG_acetaldehyde','MEG_acetic_acid','MEG_acetone', 'MEG_ethanol',
    'MEG_formaldehyde','MEG_methanol',
    'GAMMAL','GAMMAS','GAMMAC_isoprene',
    'EPS_isoprene','GAMMA_isoprene','GAMMAP_isoprene','GAMMAT_isoprene','GAMMAA_isoprene',
    'EPS_pinene_a','GAMMA_pinene_a','GAMMAP_pinene_a','GAMMAT_pinene_a','GAMMAA_pinene_a',
    'EPS_carene_3','GAMMA_carene_3','GAMMAP_carene_3','GAMMAT_carene_3','GAMMAA_carene_3',
    'EPS_pinene_b','GAMMA_pinene_b','GAMMAP_pinene_b','GAMMAT_pinene_b','GAMMAA_pinene_b',
    'EPS_myrcene','GAMMA_myrcene','GAMMAP_myrcene','GAMMAT_myrcene','GAMMAA_myrcene',
    'EPS_limonene','GAMMA_limonene','GAMMAP_limonene','GAMMAT_limonene','GAMMAA_limonene'

EOF
}

cam_spinup_diagnostics(){
# To check if reached equilibrium in the spinup
cat << EOF >> user_nl_cam
mfilt = 1
nhtfrq = 0
avgflag_pertape = 'A'

fincl1 = 'TREFHT','PSL','PRECT','PS','U10','V10','FSNT','FLNT','FSNS','FLNS','FSNSC','FLNSC','FLUTC','FSNT_DRF','FLNT_DRF','FSNTCDRF','FLNTCDRF','CLOUD','CLDTOT','LANDFRAC'
/
EOF
}

clm_spinup_diagnostics(){
# To check if reached equilibrium in the spinup
# Monthly average output, each file has 1 month
cat << EOF >> user_nl_clm
hist_mfilt = 1
hist_nhtfrq = 0

hist_fincl1 = 'TSA','TLAI','LAISHA','LAISUN',
'TOTVEGC','TOTSOMC','TOTECOSYSC',
'GPP','NPP','AR','HR','NEE',
'FSH','EFLX_LH_TOT','FSA','FIRA','FSDS','FLDS',
'RAIN','SNOW',
'QSOIL','QVEGE','QVEGT','QOVER','QRUNOFF',
'H2OSOI','SOILLIQ','SOILICE','TSOI','ZWT'
/
EOF
}

clm_long_spinup_diagnostics(){
# Yearly average output, everyfile have 10 years

# For an equilibrium check, I care about long-term drift in slow pools 
#like TOTSOMC (soil carbon can take decades to centuries to equilibrate) and TOTECOSYSC, 
# plus whether flux balance (NEE → 0, GPP ≈ AR+HR) stabilizes over time. 
# Seasonal/monthly detail is irrelevant noise for that question
# I'm looking at trend, not seasonality.

cat << EOF >> user_nl_clm
hist_mfilt  = 10
hist_nhtfrq = -8760

hist_fincl1 = 'TSA','TLAI','TOTVEGC','TOTSOMC','TOTECOSYSC',
'GPP','NPP','AR','HR','NEE',
'FSH','EFLX_LH_TOT','FSA','FIRA','FSDS','FLDS',
'RAIN','SNOW',
'QSOIL','QVEGE','QVEGT','QOVER','QRUNOFF',
'H2OSOI','SOILLIQ','SOILICE','TSOI','ZWT'
/
EOF
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

# ---------------- CAM output-size diagnostic tests ----------------
#
# Usage: test_diagnostics <T0|T1|T2|T3|T4|T5|T6>
#
# Determine empirically which variables are written to CAM's primary history
# tape (h0). Each test runs for one model day and writes one daily-mean h0 file.
#
#   T0  defaults                                     baseline h0 fields
#   T1  empty_htapes + PS                            clean-tape test (does it contain just 'PS'?)
#   T2  defaults + history_aerosol                   T2-T0: aerosol-history fields
#   T3  defaults + CAM_AEROCOM                       T3-T0: AEROCOM fields
#   T4  empty_htapes + history_aerosol + PS          empty_htapes vs history_aerosol interaction:
#                                                       T4 == T1  -> empty_htapes overrides history_aerosol defaults
#                                                       T4 ~= T2  -> history_aerosol repopulates the tape
#   T5  defaults - history_aerosol                   T0-T5: fields added by history_aerosol
#   T6  empty_htapes + history_aerosol + CAM_AEROCOM + PS,_DRF/CDRF     Confirms two things at once:
#                                                       (a) empty_htapes yields a clean tape with all flags ON, and
#                                                       (b) the Ghan _DRF/CDRF forcing fields are requestable.                 
#
# After the test runs, use
#   BOREAL-FOREST-EXPANSION/diagnostics/reduce-history-file-size/compare_diagnostics_tests_for_h0_size.ipynb
# to compare the resulting h0 fields (run on Betzy).
#

test_diagnostics() {
    local test_name="${1:?Usage: test_diagnostics <T0|T1|T2|T3|T4|T5|T6>}"

    # CAM_AEROCOM is a build-time flag: enabled for T3 and T6; left at default (off) otherwise.
    case "$test_name" in
        T3|T6)                ./xmlchange CAM_AEROCOM=TRUE ;;
        T0|T1|T2|T4|T5)       ;;
        *) echo "ERROR: unknown test '$test_name' (use T0|T1|T2|T3|T4|T5|T6)"; return 1 ;;
    esac

    # test-specific history flags
    case "$test_name" in
        T0) : ;;                              # pure defaults, nothing extra
        T1) cat << 'EOF' >> user_nl_cam
empty_htapes = .true.
fincl1 = 'PS'
EOF
            ;;
        T2) cat << 'EOF' >> user_nl_cam
history_aerosol = .true.
EOF
            ;;
        T3) : ;;                              # AEROCOM set via xmlchange above
        T4) cat << 'EOF' >> user_nl_cam
empty_htapes = .true.
history_aerosol = .true.
fincl1 = 'PS'
EOF
            ;;
        T5) cat << 'EOF' >> user_nl_cam
history_aerosol = .false.
EOF
            ;;
        T6) cat << 'EOF' >> user_nl_cam
empty_htapes = .true.
history_aerosol = .true.
fincl1 = 'PS','FSNT_DRF','FLNT_DRF','FSNTCDRF','FLNTCDRF'
EOF
            ;;
    esac

    # common: daily-mean, 1 sample/file, so a 1-day run writes one clean h0
    cat << 'EOF' >> user_nl_cam
mfilt = 1
nhtfrq = -24
avgflag_pertape = 'A'
EOF

    # Run each diagnostic case for exactly one model day.
    ./xmlchange STOP_OPTION=ndays,STOP_N=1
    ./xmlchange RESUBMIT=0
    ./xmlchange REST_OPTION=ndays,REST_N=1
    ./xmlchange DOUT_S_SAVE_INTERIM_RESTART_FILES=FALSE

    echo "test_diagnostics: configured ${test_name} for a one-day run"
}