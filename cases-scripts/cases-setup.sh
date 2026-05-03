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
avgflag_pertape = 'A','I'
history_aerosol = .true.

fincl1 = 'NNAT_0','FSNT','FLNT','FSNT_DRF','FLNT_DRF','FSNTCDRF','FLNTCDRF','FLNS','FSNS','FLNSC','FSNSC',
'FSDSCDRF','FSDS_DRF','FSUTADRF','FLUTC','FSUS_DRF','FLUS','CLOUD','FCTL','FCTI','NUCLRATE','FORMRATE',
'GRH2SO4','GRSOA','GR','COAGNUCL','H2SO4','SOA_LV','PS','LANDFRAC','SOA_NA','SO4_NA',

'NCONC01','NCONC02','NCONC03','NCONC04','NCONC05','NCONC06','NCONC07','NCONC08','NCONC09','NCONC10','NCONC11','NCONC12','NCONC13','NCONC14',
'SIGMA01','SIGMA02','SIGMA03','SIGMA04','SIGMA05','SIGMA06','SIGMA07','SIGMA08','SIGMA09','SIGMA10','SIGMA11','SIGMA12','SIGMA13','SIGMA14',
'NMR01','NMR02','NMR03','NMR04','NMR05','NMR06','NMR07','NMR08','NMR09','NMR10','NMR11','NMR12','NMR13','NMR14',

'CCN1','CCN2','CCN3','CCN4','CCN5','CCN6','CCN7','CCN_B','TGCLDCWP','cb_H2SO4','cb_SOA_LV','cb_SOA_NA','cb_SO4_NA',
'CLDTOT','CDNUMC','SO2','ISOP','MTERP','SOA_SV','OH_vmr','AOD_VIS','CAODVIS','CLDFREE',
'CDOD550','CDOD440','CDOD870','AEROD_v','CABS550','CABS550A',

'SOA_SEC01','SOA_SEC02','SOA_SEC03','SOA_SEC04','SOA_SEC05',
'SO4_SEC01','SO4_SEC02','SO4_SEC03','SO4_SEC04','SO4_SEC05',
'nrSOA_SEC01','nrSOA_SEC02','nrSOA_SEC03','nrSOA_SEC04','nrSOA_SEC05',
'nrSO4_SEC01','nrSO4_SEC02','nrSO4_SEC03','nrSO4_SEC04','nrSO4_SEC05',
'cb_SOA_SEC01','cb_SOA_SEC02','cb_SOA_SEC03','cb_SOA_SEC04','cb_SOA_SEC05',
'cb_SO4_SEC01','cb_SO4_SEC02','cb_SO4_SEC03','cb_SO4_SEC04','cb_SO4_SEC05',

'SST','PRECC','PRECL','PRECT','ozone','O3','TROP_P','TROP_T','TROP_Z','VT100',
'MEG_CH3COCH3','MEG_CH3CHO','MEG_CH2O','MEG_CO','MEG_C2H6','MEG_C3H8','MEG_C2H4','MEG_C3H6',
'MEG_C2H5OH','MEG_MTERP','MEG_ISOP','MEG_CH3OH',
'SFISOP','SFMTERP','emis_ISOP','emis_MTERP','cb_ISOP','cb_MTERP'
EOF

if [[ "${1:-}" == "HR_BVOC" ]]; then # hourly BVOC surface fluxes/emissions
cat << EOF >> user_nl_cam

fincl2 = 'SFISOP','SFMTERP'
EOF
fi

cat << EOF >> user_nl_cam
/
EOF
}

clm_diagnostics(){
cat << EOF >> user_nl_clm 
hist_mfilt = 1
hist_nhtfrq = 0
hist_avgflag_pertape='A'

hist_fincl1 = 'TSA','TLAI','LAISHA','LAISUN','FSH','EFLX_LH_TOT','FSA','FIRA','FSDS','FLDS',
'RAIN','SNOW',
'QSOIL','QVEGE','QVEGT','QOVER','QRUNOFF','H2OSOI','SOILLIQ','SOILICE','TSOI',
'GPP','NPP','AR','HR','NEE','WIND', 'ZWT', 
'MEG_acetaldehyde','MEG_acetic_acid','MEG_acetone','MEG_carene_3', 'MEG_ethanol',
'MEG_formaldehyde','MEG_isoprene','MEG_methanol', 'MEG_pinene_a','MEG_thujene_a'
/
EOF
}

clm_diagnostics_fBVOC(){
cat << EOF >> user_nl_clm 
hist_mfilt = 1
hist_nhtfrq = 0
hist_avgflag_pertape='A'

hist_fincl1 = 'TSA','TLAI','LAISHA','LAISUN','FSH','EFLX_LH_TOT','FSA','FIRA','FSDS','FLDS',
'RAIN','SNOW',
'QSOIL','QVEGE','QVEGT','QOVER','QRUNOFF','H2OSOI','SOILLIQ','SOILICE','TSOI',
'GPP','NPP','AR','HR','NEE','WIND', 'ZWT'
/
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
/
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