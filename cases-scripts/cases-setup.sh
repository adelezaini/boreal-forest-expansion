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

##------ extend an existing case (continue run)
# Continues a finished case for NYEARS more years from its last restart.
# Keeps casename, namelists, SourceMods and archive continuous (no rebuild).
# Usage: extend_case "$CASENAME" 5 "2010-01-01-00000"
# Optional env:
#   MET_END_YEAR=2026         nudging data end year (default 2015: ..._6h_2000-2015)
#   SUBMIT_BATCH_ARGS="--exclude=..."   passed to case.submit --batch-args= (kept for resubmits)
#   CHECK_ONLY=1              run the checks, change nothing, do not submit

extend_case() {
    local casename="$1"        # existing case name (with date suffix)
    local nyears="$2"          # years to add
    local restdate="$3"        # restart date the run dir must point to
    local met_end_year="${MET_END_YEAR:-2015}"   # nudging data end (last file <year>-01-01-00000)

    local caseroot="$HOME/cases/BRL_FRST_XPSN/$casename"
    [[ -d "$caseroot" ]] || { echo "ERROR: missing case directory: $caseroot" >&2; return 1; }
    cd "$caseroot" || return 1

    # Do not touch a case that is still queued/running
    if squeue -u "$USER" -h -o %j | grep -q -- "$casename"; then
        echo "ERROR: a job for $casename is still in the queue." >&2
        return 1
    fi

    # Previous segment must have completed and been archived
    tail -n 3 CaseStatus | grep -q 'st_archive success' || {
        echo "ERROR: last CaseStatus entry is not 'st_archive success' for $casename." >&2
        return 1
    }

    # Run dir must point to the expected restart
    local rundir
    rundir=$(./xmlquery --value RUNDIR)
    grep -q -- "$restdate" "$rundir/rpointer.atm" || {
        echo "ERROR: $rundir/rpointer.atm does not point to $restdate:" >&2
        cat "$rundir/rpointer.atm" >&2
        return 1
    }

    # Stay inside the nudging data period
    local end_year=$(( 10#${restdate:0:4} + nyears ))
    (( end_year <= met_end_year )) || {
        echo "ERROR: run would end in $end_year, after nudging data end ($met_end_year-01-01)." >&2
        return 1
    }

    if [[ -n "${CHECK_ONLY:-}" ]]; then
        echo "CHECK OK: $casename can be extended from $restdate by $nyears years (to $end_year-01-01)"
        return 0
    fi

    ./xmlchange CONTINUE_RUN=TRUE
    ./xmlchange STOP_OPTION=nyears,STOP_N="$nyears"
    ./xmlchange RESUBMIT=0
    ./xmlchange REST_OPTION=nyears,REST_N=1

    echo "Extending $casename from $restdate by $nyears years (to $end_year-01-01)"
    if [[ -n "${SUBMIT_BATCH_ARGS:-}" ]]; then
        ./case.submit --batch-args="$SUBMIT_BATCH_ARGS"
    else
        ./case.submit
    fi
}

##------ switch a nudged case to the 2000-2025 MET folder (extension past 2015)
# The 2015-01-01 restart of every nudged run stores the met file it is reading as a
# FULL PATH (global attribute current_metdata_filename of cam.r, metdata.F90
# read_met_restart_pio); on restart CAM ignores met_data_file and looks this exact
# path up in met_filenames_list. So both must move to the new folder:
#   1. user_nl_cam met_data_file / met_filenames_list: _6h_2000-2015 -> _6h_2000-2025
#      (backup user_nl_cam.before_met2025); preview_namelists; atm_in checked;
#   2. cam.r.<restdate> in the RUN DIR: current/next_metdata_filename -> new folder
#      (same path length). The archived restart is the untouched original.
# Idempotent. Log: <caseroot>/met2025_switch.log.
# Usage: switch_case_to_met_2000_2025 <casename> <restdate YYYY-MM-DD-00000> <last met day needed YYYY-MM-DD>
# CHECK_ONLY=1: checks only.
switch_case_to_met_2000_2025() {
    local casename="$1" restdate="$2" need_day="$3"
    local met=NF2000norbc_tropstratchem_met_f19_f19_20260422
    local az=/cluster/shared/noresm/inputdata/noresm-only/inputForNudging/AZ
    local olddir="$az/${met}_6h_2000-2015" newdir="$az/${met}_6h_2000-2025"
    local newlist="$newdir/${met}.cam.h1_filelist.txt"
    local caseroot="$HOME/cases/BRL_FRST_XPSN/$casename"
    cd "$caseroot" || return 1
    local rundir; rundir=$(./xmlquery --value RUNDIR)
    local rfile="$rundir/$casename.cam.r.$restdate.nc"
    local log="$caseroot/met2025_switch.log"

    [[ -f "$newlist" ]] || { echo "ERROR: missing $newlist (MET folder not built yet)" >&2; return 1; }
    local last; last=$(tail -n 1 "$newlist" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}-00000\.nc$' | cut -c1-10)
    [[ -n "$last" && ! "$last" < "$need_day" ]] || {
        echo "ERROR: $newlist ends at '$last', run needs $need_day" >&2; return 1; }
    [[ -f "$rfile" ]] || { echo "ERROR: missing run-dir restart $rfile" >&2; return 1; }
    grep -q "_6h_2000-20[12]5/" user_nl_cam || { echo "ERROR: no met paths in user_nl_cam" >&2; return 1; }

    module load NCO/5.2.9-foss-2024a >/dev/null 2>&1 || true
    command -v ncks >/dev/null || { echo "ERROR: NCO not available" >&2; return 1; }
    local cur nxt
    cur=$(ncks -M "$rfile" | sed -n 's/.*current_metdata_filename = "\(.*\)".*/\1/p')
    nxt=$(ncks -M "$rfile" | sed -n 's/.*next_metdata_filename = "\(.*\)".*/\1/p')
    case "$cur" in
        "$olddir"/*|"$newdir"/*) ;;
        *) echo "ERROR: unexpected current_metdata_filename '$cur' in $rfile" >&2; return 1 ;;
    esac
    local cur_new="${cur/$olddir/$newdir}" nxt_new="${nxt/$olddir/$newdir}"
    [[ -f "$cur_new" ]] || { echo "ERROR: $cur_new not in the new folder" >&2; return 1; }
    [[ -z "$nxt_new" || -f "$nxt_new" ]] || { echo "ERROR: $nxt_new not in the new folder" >&2; return 1; }
    if [[ -n "${CHECK_ONLY:-}" ]]; then
        echo "CHECK OK: $casename met switch possible (restart reads $(basename "$cur"); list ends $last)"
        return 0
    fi

    {
        echo "== $(date '+%F %T') switch to $newdir (restart $restdate)"
        echo "restart before: current='$cur' next='$nxt'"
    } >> "$log"
    [[ -f user_nl_cam.before_met2025 ]] || cp -p user_nl_cam user_nl_cam.before_met2025
    sed -i "/^ *met_\(data_file\|filenames_list\)/ s|_6h_2000-2015/|_6h_2000-2025/|" user_nl_cam
    ./preview_namelists > /dev/null || return 1
    grep -q "_6h_2000-2015" CaseDocs/atm_in && { echo "ERROR: atm_in still has the old folder" >&2; return 1; }
    [[ $(grep -c "_6h_2000-2025/" CaseDocs/atm_in) -eq 2 ]] || { echo "ERROR: atm_in met paths not switched" >&2; return 1; }

    if [[ "$cur" != "$cur_new" || "$nxt" != "$nxt_new" ]]; then
        local att=(-a current_metdata_filename,global,o,c,"$cur_new")
        [[ -n "$nxt" ]] && att+=(-a next_metdata_filename,global,o,c,"$nxt_new")
        ncatted -h "${att[@]}" "$rfile" || return 1
    fi
    local cur_chk; cur_chk=$(ncks -M "$rfile" | sed -n 's/.*current_metdata_filename = "\(.*\)".*/\1/p')
    [[ "$cur_chk" == "$cur_new" ]] || { echo "ERROR: restart attribute not updated ($cur_chk)" >&2; return 1; }
    echo "restart after:  current='$cur_new' next='$nxt_new'" >> "$log"
    echo "Switched $casename to $newdir"
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

cam_met_diagnostics(){
# MET extension (12d) and its reproduction test: the nudging tape h1 of
# cam_generate_nudging_data, plus a minimal h0 with the cam_spinup_diagnostics
# fields (user 2026-11-03). The two functions can't be called together: both set
# mfilt/nhtfrq. History output only, no effect on the model state.
cat << EOF >> user_nl_cam
empty_htapes = .true.
mfilt = 1, 4
nhtfrq = 0, -6
avgflag_pertape = 'A','I'

fincl1 = 'TREFHT','PSL','PRECT','PS','U10','V10','FSNT','FLNT','FSNS','FLNS','FSNSC','FLNSC',
    'FLUTC','FSNT_DRF','FLNT_DRF','FSNTCDRF','FLNTCDRF','CLOUD','CLDTOT','LANDFRAC', 'TS', 'FLUT',
    'SF6', 'CFC115', 'N2O', 'CO2', 'CH4'
fincl2 = 'PS','U','V','T','Q'
EOF
}

stage_branch_restart(){
# Copy and unzip only the restart files (+ rpointers) of an archived restart
# folder, no history files (a staged h1 with the same name as the new run's
# output would be linked into the run dir).
# Usage: stage_branch_restart <archived rest/YYYY-MM-DD-00000> <local dir>
    local src="$1" dst="$2"
    [[ -d "$src" ]] || { echo "ERROR: missing restart folder: $src" >&2; return 1; }
    mkdir -p "$dst" || return 1
    rsync -havP --exclude='*.h0.*' --exclude='*.h1.*' --exclude='*.h0[a-z]*' "$src"/ "$dst"/ || return 1
    if find "$dst" -maxdepth 1 -name '*.gz' -print -quit | grep -q .; then
        gunzip -fv "$dst"/*.gz || return 1
    fi
    echo "Restart files staged in $dst:"; ls "$dst"
}

compare_xml_to_archived_case(){
# Compare case XML settings that change the model (build, PEs, forcing) with an
# archived case. Returns 1 on any difference. Call from the case dir after case.setup.
# Usage: compare_xml_to_archived_case <archived case dir>
    local ref="$1" v a b bad=0
    for v in COMPSET COMPILER MPILIB DEBUG CAM_CONFIG_OPTS CAM_NAMELIST_OPTS CAM_AEROCOM \
             CLM_BLDNML_OPTS CLM_NAMELIST_OPTS CLM_CONFIG_OPTS CCSM_CO2_PPMV \
             SSTICE_DATA_FILENAME SSTICE_YEAR_ALIGN SSTICE_YEAR_START SSTICE_YEAR_END OCN_FLUX_SCHEME \
             ATM_NCPL LND_NCPL NTASKS NTHRDS ROOTPE PSTRID; do
        a=$(./xmlquery --caseroot "$ref" --value "$v" 2>/dev/null || echo "<n/a>")
        b=$(./xmlquery --value "$v" 2>/dev/null || echo "<n/a>")
        if [[ "$a" != "$b" ]]; then
            echo "XML DIFF $v:"; echo "  archived: $a"; echo "  this case: $b"; bad=1
        fi
    done
    [[ $bad -eq 0 ]] && echo "XML build/PE/forcing settings match $ref."
    return $bad
}

_flat_namelist(){
# One "key = value" per line (continuation lines joined, whitespace squeezed), sorted.
    awk '
        /^[[:space:]]*[&\/!]/ { next }
        /^[[:space:]]*[A-Za-z0-9_%()]+[[:space:]]*=/ { if (line != "") print line; line = $0; next }
        NF { line = line " " $0 }
        END { if (line != "") print line }
    ' "$1" | sed -E 's/[[:space:]]+/ /g; s/^ //; s/ = /=/' | sort
}

compare_namelists_to_archived_case(){
# Compare this case's CaseDocs/*_in with an archived case's CaseDocs, key by key.
# Keys matching the allowed ERE (expected differences, e.g. history output,
# restart/branch settings) are listed but don't count. Returns 1 if any other key
# differs. Call after ./preview_namelists, from the case dir.
# Usage: compare_namelists_to_archived_case <archived CaseDocs> <allowed key ERE>
    local ref="$1" allowed="$2" f bad=0 d hard
    for f in atm_in lnd_in ice_in docn_in drv_in drv_flds_in mosart_in; do
        [[ -f "$ref/$f" ]] || continue
        [[ -f "CaseDocs/$f" ]] || { echo "MISSING CaseDocs/$f"; bad=1; continue; }
        d=$(diff <(_flat_namelist "$ref/$f") <(_flat_namelist "CaseDocs/$f") | grep -E '^[<>]' || true)
        [[ -z "$d" ]] && continue
        hard=$(echo "$d" | grep -v -E "^[<>] ($allowed)=" || true)
        echo "== $f: expected differences:"; echo "$d" | grep -E "^[<>] ($allowed)=" | cut -c1-200 || true
        if [[ -n "$hard" ]]; then
            echo "== $f: UNEXPECTED differences:"; echo "$hard" | cut -c1-300; bad=1
        fi
    done
    [[ $bad -eq 0 ]] && echo "Namelists match $ref except the expected keys."
    return $bad
}

setup_nudging_data () {
    # $1 (optional) = run start date YYYY-MM-DD (default 2000-01-01). A startup/hybrid/branch
    # run must point met_data_file to the file of its OWN start date, otherwise FIND_TIMES
    # aborts ("Failed to find dates bracketing", 24f s2/s3, 2026-11-04).
    local START_DATE="${1:-2000-01-01}"
    local CASENAME=NF2000norbc_tropstratchem_met_f19_f19_20260422

    local NUDGDIR="/cluster/shared/noresm/inputdata/noresm-only/inputForNudging/AZ/${CASENAME}_6h_2000-2015"
    local FILELIST="${NUDGDIR}/${CASENAME}.cam.h1_filelist.txt"
    local METFILE="${NUDGDIR}/${CASENAME}.cam.h1.${START_DATE}-00000.nc"

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
bypass_isoprene_diurnal_adjustment() {
    # Disable CAM's extra isoprene diurnal adjustment in fBVOC cases because the
    # prescribed half-hourly total ISOP climatology already includes that cycle.
    # Call before case.build.
    local src="${NORESM_ROOT}/components/cam/src/chemistry/oslo_aero/src_cam/mo_srf_emissions.F90"
    local dst="SourceMods/src.cam/mo_srf_emissions.F90"

    [[ -f env_case.xml ]] || {
        echo "ERROR: run this function from the case directory." >&2
        return 1
    }

    mkdir -p SourceMods/src.cam || return 1

    if [[ ! -f "$dst" ]]; then
        cp "$src" "$dst" || return 1
    fi

    python3 "$HOME/BOREAL-FOREST-EXPANSION/cases-scripts/bypass_isoprene_diurnal_adjustment.py" "$dst"
}

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
         'MEK -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_MEK_anthrosurfgasALL_surface_1849-2015_1.9x2.5_version20211124.nc',
         'MEK -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20211124/emissions_cmip6_noresm2_MEK_bbsurfALL_surface_1849-2015_1.9x2.5_version20211124.nc',
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
         'ISOP -> /cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions/ems_NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20260925_2001-2009_SFISOP.nc',
         'MTERP -> /cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions/ems_NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20260925_2001-2009_SFMTERP.nc'
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
         'MEK -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_MEK_anthrosurfgasALL_surface_2014-2301_1.9x2.5_version20230630.nc',
         'MEK -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20230630/emissions_cmip6_noresm2_ScenarioMIP_IAMC-REMIND-MAGPIE-ssp585-1-1_MEK_bbsurfALL_surface_2014-2301_1.9x2.5_version20230630.nc',
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
         'NO -> /cluster/shared/noresm/inputdata/atm/cam/chem/emis/emissions_ssp585_2deg/emissions-cmip6_NO_other_surface_1750-2015-2101_1.9x2.5_c20170322.nc',
         'ISOP -> /cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions/ems_NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20260925_2001-2009_on_yr2100_SFISOP.nc',
         'MTERP -> /cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions/ems_NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20260925_2001-2009_on_yr2100_SFMTERP.nc'
/
EOF
}

prescribed_bvoc_emissions_all(){
    # All 19 MEGAN-fed species prescribed, MEGAN off (fBVOC<source> runs, e.g. LCC_FUT_fBVOCctrlFUT).
    # Usage: prescribed_bvoc_emissions_all <2000|2100> <prefix>
    #   2000/2100 -> anthropogenic/BB file list of prescribed_bvoc_emissions / _2100 (single source, unchanged)
    #   prefix    -> <dir>/ems_<source case>_<y0>-<y1>[_on_yr2100]; files <prefix>_SFISOP.nc, <prefix>_MEG_<SP>.nc
    # ISOP/MTERP come from SF* (MEGAN + biomass burning), so their BB files stay out of the list, as in
    # the _IM runs. The other 17 come from MEG_* (biogenic only), so their anthro/BB files stay in.
    local period="$1" prefix="$2" sp extra=""
    local others=(BCARY C3H6 BIGENE CH3CHO CH2O C2H4 CH3OH C2H5OH CH3COOH CH3COCH3 HCOOH HCN CO
                  C2H6 C3H8 BIGALK TOLUENE)
    for sp in SFISOP SFMTERP "${others[@]/#/MEG_}"; do
        [[ -f "${prefix}_${sp}.nc" ]] || { echo "ERROR: missing ${prefix}_${sp}.nc" >&2; return 1; }
    done
    case "$period" in
        2000) prescribed_bvoc_emissions ;;
        2100) prescribed_bvoc_emissions_2100 ;;
        *) echo "ERROR: period must be 2000 or 2100" >&2; return 1 ;;
    esac
    # Point the ISOP/MTERP entries to the new files and add the 17 other species after MTERP.
    for sp in "${others[@]}"; do extra+=",\n         '${sp} -> ${prefix}_MEG_${sp}.nc'"; done
    sed -i -E -e "s|^( *'ISOP -> ).*\.nc',$|\1${prefix}_SFISOP.nc',|" \
              -e "s|^( *'MTERP -> ).*\.nc'$|\1${prefix}_SFMTERP.nc'${extra}|" user_nl_cam
    local n
    n=$(grep -c -- "-> ${prefix}_" user_nl_cam)
    [[ "$n" -eq 19 ]] || { echo "ERROR: expected 19 prescribed BVOC entries in user_nl_cam, found $n" >&2; return 1; }
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
    # optional arg:
    #   "HR_BVOC"     -> h1 tape of 30-min SFISOP, SFMTERP (CTRL only; original workflow)
    #   "HR_BVOC_ALL" -> h1 tape of 30-min SFISOP, SFMTERP + the short-lived MEGAN species
    #                    (CTRL reruns that feed the all-species fixed-BVOC files)
    #   "HR_BVOC_ONLY" -> ONLY the HR_BVOC_ALL h1 tape + a 2-field monthly h0 (SFISOP, SFMTERP)
    #                    for the bit-identity check. For output-only reruns of a finished run
    #                    whose h0 already has everything else (24f, LCC_FUT_HRBVOC; user 2026-11-04)
    # for tests: set nhtfrq = -24
    ./xmlchange CAM_AEROCOM=TRUE

    if [[ "${1:-}" == "HR_BVOC_ONLY" ]]; then
        cat << 'EOF' >> user_nl_cam
empty_htapes    = .true.
history_aerosol = .true.
docosp          = .false.
mfilt           = 1, 48
nhtfrq          = 0, 1
avgflag_pertape = 'A', 'I'
fincl1 = 'SFISOP','SFMTERP'
fincl2 = 'SFISOP','SFMTERP',
       'MEG_BCARY','MEG_C3H6','MEG_BIGENE','MEG_CH3CHO','MEG_CH2O','MEG_C2H4'
/
EOF
        return 0
    fi

    if [[ "${1:-}" == "HR_BVOC" || "${1:-}" == "HR_BVOC_ALL" ]]; then
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
       'PS',
       'SF6', 'CFC115', 'N2O', 'CO2',
       'MEG_CH3OH','MEG_C2H5OH','MEG_CH2O','MEG_CH3CHO','MEG_CH3COOH','MEG_CH3COCH3',
       'MEG_HCOOH','MEG_HCN','MEG_CO','MEG_C2H6','MEG_C2H4','MEG_C3H8',
       'MEG_C3H6','MEG_BIGALK','MEG_BIGENE','MEG_TOLUENE',
       'QFLX','PBLH','RELHUM','TMQ',
       'cb_SOA_NA','cb_SOA_A1','cb_SOA_NA_OCW','cb_SOA_A1_OCW',
       'cb_SO4_NA','cb_SULFATE','cb_CH4','cb_O3',
       'NO3','N2O5','HNO3','PAN','H2O2','CH2O',
       'MACR','MVK','ISOPOOH','IEPOX','ISOPNO3',
       'TERPNIT','TERPROD1','TERPROD2','DMS','SO2',
       'SFCH2O','SFCH3OH','SFCO','SFNO','SFNO2',
       'DF_O3','DF_HNO3','DF_PAN','DF_SO2','DF_ISOPNO3',
       'WD_HNO3','WD_SO2','WD_A_PAN','WD_A_ISOPNO3',
       'SOA_NAGVF','SOA_NATBF','SOA_A1GVF','SOA_A1TBF',
       'SOA_NA_OCWDDF','SOA_A1_OCWDDF','SOA_NA_OCWSFWET','SOA_A1_OCWSFWET',
       'SOA_NA_OCWGVF','SOA_A1_OCWGVF','SOA_NA_OCWTBF','SOA_A1_OCWTBF',
       'NCONC01','NCONC02','NCONC03','NCONC04','NCONC05','NCONC06','NCONC07',
       'NCONC08','NCONC09','NCONC10','NCONC11','NCONC12','NCONC13','NCONC14',
       'NMR01','NMR02','NMR03','NMR04','NMR05','NMR06','NMR07',
       'NMR08','NMR09','NMR10','NMR11','NMR12','NMR13','NMR14'
EOF
    # Added 2026-10-28 for the new nudged chain (all names checked in the CTRL_PD -20261023
    # atm.log master list): humidity/PBL, oxidants and BVOC oxidation products, sulfur,
    # gas dry/wet deposition, SOA dry deposition split into GVF (gravitational) and TBF
    # (turbulent) -- DDF already = GVF + TBF, do not sum them -- cloud-borne SOA removal,
    # and per-mode number (NCONC) and number-median radius (NMR). SIGMA*/HYGRO* left out (size).
    # 20:27 same day: + cb_SOA_A1 (only cb_SOA_NA was listed) and the cloud-borne SOA burdens
    # cb_SOA_NA_OCW, cb_SOA_A1_OCW (model column burdens, every timestep); 14a/23a/24a relaunched.
    # The last 16 MEG_* fields = biogenic (MEGAN) flux of every other CAM species in
    # megan_specifier, kg m-2 s-1 per grid-cell area (chemistry.F90). Monthly means feed the
    # fixed-BVOC files of the long-lived species. In fBVOC runs (megan_specifier = '') they
    # do not exist: CAM drops unknown fincl fields with a log line, no abort
    # (cam_history.F90: the abort flag is a .false. parameter).

    # --- h1 30-min BVOC tape (CTRL only), feeds the emission-climatology script ---
    if [[ "${1:-}" == "HR_BVOC" ]]; then
        cat << 'EOF' >> user_nl_cam
fincl2 = 'SFISOP','SFMTERP'
EOF
    elif [[ "${1:-}" == "HR_BVOC_ALL" ]]; then
        # SFISOP, SFMTERP first and in the same order as HR_BVOC, so position-based
        # readers keep working. Then MEG_* (biogenic only; NOT SF*, which would include the
        # anthropogenic and biomass-burning file emissions that stay active in fBVOC runs)
        # for the species with lifetime <~ 1 day, whose diurnal cycle matters:
        # BCARY, C3H6, BIGENE, CH3CHO, CH2O, C2H4.
        cat << 'EOF' >> user_nl_cam
fincl2 = 'SFISOP','SFMTERP',
       'MEG_BCARY','MEG_C3H6','MEG_BIGENE','MEG_CH3CHO','MEG_CH2O','MEG_C2H4'
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
       'TOTVEGC', 'TOTVEGN', 'TWS',
       'Z0M','Z0MV','Z0MG','DISPLA','Z0HV','Z0HG','Z0QV','Z0QG',
       'RAM1','RSSUN','RSSHA','RH2M','FCTR','FCEV','FGEV',
       'ALBD','ALBI','ALBGRD','ALBGRI','SABV','SABG','FSRVI','FSRNI',
       'SNOFSDSVD','SNOFSDSVI','SNOFSDSND','SNOFSDSNI',
       'SNOFSRVD','SNOFSRVI','SNOFSRND','SNOFSRNI',
       'H2OCAN','HBOT','TOTSOMC','TOTECOSYSC'

EOF
# Added 2026-10-28 (checked in the CTRL_PD -20261023 lnd.log master list): roughness,
# resistances, latent-heat split, albedo and snow radiation. CLM aborts on an unknown
# hist_fincl name (histFileMod.F90), so Z0M_TO_COUPLER, RAH1, RAW1, RB, VPD_CAN, ALBDSF,
# ALBISF are left out: they do not exist in this build.
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

    # Both configurations require the SourceMod, so that paired experiments
    # are compiled from identical CLM source.
    local sourcemod="$CASEROOT/SourceMods/src.clm/VOCEmissionMod.F90"
    if [[ ! -f "$sourcemod" ]]; then
        echo "ERROR: CLM SourceMod not installed: $sourcemod" >&2
        echo "Call install_clm_sourcemods before clm_diagnostics." >&2
        return 1
    fi
    # Catch a stale copy (repo version edited after installation)
    if ! cmp -s "$sourcemod" "$REPO_ROOT/model/SourceMods/src.clm/VOCEmissionMod.F90"; then
        echo "ERROR: installed SourceMod differs from repo version — re-run install_clm_sourcemods" >&2
        return 1
    fi

    # Add the common surface, hydrology and carbon-cycle fields.
    _clm_diagnostics_base

    # Fixed-BVOC runs do not need the extended MEGAN history fields.
    if [[ "$configuration" == "fBVOC" ]]; then
        return 0
    fi

    cat <<'EOF' >> user_nl_clm

hist_fincl1 += 'MEG_isoprene','MEG_carene_3','MEG_limonene','MEG_myrcene',
    'MEG_pinene_a','MEG_pinene_b','MEG_ocimene_t_b','MEG_sabinene',
    'MEG_acetaldehyde','MEG_acetic_acid','MEG_acetone','MEG_ethanol',
    'MEG_formaldehyde','MEG_methanol',
    'GAMMAL','GAMMAS','GAMMAC_isoprene',
    'EPS_isoprene','GAMMA_isoprene','GAMMAP_isoprene','GAMMAT_isoprene','GAMMAA_isoprene',
    'EPS_pinene_a','GAMMA_pinene_a','GAMMAP_pinene_a','GAMMAT_pinene_a','GAMMAA_pinene_a',
    'EPS_carene_3','GAMMA_carene_3','GAMMAP_carene_3','GAMMAT_carene_3','GAMMAA_carene_3',
    'EPS_pinene_b','GAMMA_pinene_b','GAMMAP_pinene_b','GAMMAT_pinene_b','GAMMAA_pinene_b',
    'EPS_myrcene','GAMMA_myrcene','GAMMAP_myrcene','GAMMAT_myrcene','GAMMAA_myrcene',
    'EPS_limonene','GAMMA_limonene','GAMMAP_limonene','GAMMAT_limonene','GAMMAA_limonene',
    'EPS_ocimene_t_b','GAMMA_ocimene_t_b','GAMMAP_ocimene_t_b','GAMMAT_ocimene_t_b','GAMMAA_ocimene_t_b',
    'EPS_sabinene','GAMMA_sabinene','GAMMAP_sabinene','GAMMAT_sabinene','GAMMAA_sabinene',
    'EPS_methanol','GAMMA_methanol','GAMMAP_methanol','GAMMAT_methanol','GAMMAA_methanol',
    'EPS_acetone','GAMMA_acetone','GAMMAP_acetone','GAMMAT_acetone','GAMMAA_acetone'

EOF
}

cam_spinup_diagnostics(){
# To check if reached equilibrium in the spinup
# NB: Added GASES = 'SF6', 'CFC115', 'N2O', 'CO2', 'CH4' after running the simulations (for equilibrium check)
cat << EOF >> user_nl_cam
empty_htapes = .true.
mfilt = 1
nhtfrq = 0
avgflag_pertape = 'A'

fincl1 = 'TREFHT','PSL','PRECT','PS','U10','V10','FSNT','FLNT','FSNS','FLNS','FSNSC','FLNSC',
    'FLUTC','FSNT_DRF','FLNT_DRF','FSNTCDRF','FLNTCDRF','CLOUD','CLDTOT','LANDFRAC', 'TS', 'FLUT',
    'SF6', 'CFC115', 'N2O', 'CO2', 'CH4'
/
EOF
}

clm_spinup_diagnostics(){
# To check if reached equilibrium in the spinup
# Monthly average output, each file has 1 month
# NB: Added CLM_VARS = ('TOTVEGN', 'TWS') after running the simulations (for equilibrium check)
# NB: added 'TSAI','HTOP' (canopy structure -> albedo), 'PCO2','PBOT' (CO2 seen by CLM:
#   PCO2/PBOT*1e6 = ppm, catches the land-only CO2 bug), 'FSNO','SNOWDP' (snow, TWS drift at >45N)
cat << EOF >> user_nl_clm
hist_empty_htapes = .true.
hist_mfilt = 1
hist_nhtfrq = 0

hist_fincl1 = 'TSA','TLAI','LAISHA','LAISUN','TSAI','HTOP',
'TOTVEGC','TOTSOMC','TOTECOSYSC',
'TOTVEGN', 'TWS',
'PCO2','PBOT','FSNO','SNOWDP',
'GPP','NPP','AR','HR','NEE',
'FSH','EFLX_LH_TOT','FSA','FIRA','FSDS','FLDS', 'FSR','FGR',
'RAIN','SNOW', 'H2OSNO',
'QSOIL','QVEGE','QVEGT','QOVER','QRUNOFF',
'H2OSOI','SOILLIQ','SOILICE','TSOI','ZWT'
EOF
}

clm_long_spinup_diagnostics(){
# Yearly average output, everyfile have 10 years
# NB: Added CLM_VARS = ('TOTVEGN', 'TWS') after running the simulations (for equilibrium check)
# NB added 'TSAI','HTOP','PCO2','PBOT','FSNO','SNOWDP' (see clm_spinup_diagnostics)

cat << EOF >> user_nl_clm
hist_empty_htapes = .true.
hist_mfilt  = 10
hist_nhtfrq = -8760

hist_fincl1 = 'TSA','TLAI','TSAI','HTOP','TOTVEGC','TOTSOMC','TOTECOSYSC',
'GPP','NPP','AR','HR','NEE',
'TOTVEGN', 'TWS',
'PCO2','PBOT','FSNO','SNOWDP',
'FSH','EFLX_LH_TOT','FSA','FIRA','FSDS','FLDS','FSR','FGR',
'RAIN','SNOW', 'H2OSNO',
'QSOIL','QVEGE','QVEGT','QOVER','QRUNOFF',
'H2OSOI','SOILLIQ','SOILICE','TSOI','ZWT'
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