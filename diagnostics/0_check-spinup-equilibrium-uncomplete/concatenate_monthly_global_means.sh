#!/bin/bash
# ============================================================
# Purpose:
#   Create monthly global-mean CAM or CLM history files using NCO
#   If gas variables are present, it caclulates also the column burden
#   Raw files in /cluster/work/users/adelez/archive/CASENAME/COMP/hist/ (COMP = atm, lnd)
#   Store the output in equilibrium_output/
#
# Usage:
#   ./concatenate_monthly_global_means.sh cam CASENAME
#   ./concatenate_monthly_global_means.sh clm CASENAME
#
# Examples: ./concatenate_monthly_global_means.sh clm NF2000norbc_tropstratchem_spinup_f19_f19
#
# Note: This script was developed with assistance from an AI language model
# ============================================================

set -euo pipefail
module load NCO/5.2.9-foss-2024a

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/compute_cam_column_burdens_nco.sh"

if ! declare -F compute_cam_column_burdens >/dev/null; then
    echo "Error: compute_cam_column_burdens function not found after sourcing helper file."
    exit 1
fi

if ! declare -p CAM_BURDEN_GASES >/dev/null 2>&1; then
    echo "Error: CAM_BURDEN_GASES array not found after sourcing helper file."
    exit 1
fi

# Check input arguments
if [[ $# -ne 2 ]]; then
    echo "Usage: $0 cam/clm CASENAME"
    exit 1
fi

COMP="$1"
CASENAME="$2"
# ============================================================

ARCHIVE_BASE="/cluster/work/users/adelez/archive/${CASENAME}"
CANDIDATE_FILE="${SCRIPT_DIR}/${COMP}_equilibrium_variables.txt"

# ============================================================

OUTDIR="${SCRIPT_DIR}/equilibrium_output/equilibrium_${CASENAME}"
TMPDIR="${OUTDIR}/tmp"
OUTFILE="${OUTDIR}/${COMP}_monthly_globalmean.nc"

mkdir -p "$OUTDIR" "$TMPDIR"

# ============================================================
# Helper functions:

is_valid_nc() {
    local f="$1"
    [[ -s "$f" ]] && ncks -m "$f" >/dev/null 2>&1
}

var_exists() {
    local var="$1"
    local file="$2"

    ncks -m -v "$var" "$file" >/dev/null 2>&1
}

CANDIDATE_VARS=()

AVAILABLE_BURDEN_GASES=()
BURDEN_VARS=()

read_candidate_file() {
    local file="$1"

    if [[ ! -f "$file" ]]; then
        echo "Error: candidate variable file not found:"
        echo "  $file"
        exit 1
    fi

    while IFS= read -r line; do
        line="${line%%#*}" # Remove comments
        line="$(echo "$line" | xargs)" # Trim whitespace
        [[ -z "$line" ]] && continue # Skip empty lines

        # First field is the variable name
        var="$(echo "$line" | awk '{print $1}')"

        CANDIDATE_VARS+=( "$var" )

    done < "$file"
}
# ============================================================

# -------------------------
# Component-specific settings
# -------------------------

if [[ "$COMP" == "cam" ]]; then

    INDIR="${ARCHIVE_BASE}/atm/hist"
    PATTERN="${CASENAME}.cam.h0.*.nc"

elif [[ "$COMP" == "clm" ]]; then

    INDIR="${ARCHIVE_BASE}/lnd/hist"
    PATTERN="${CASENAME}.clm2.h0.*.nc"

else
    echo "Error: first argument must be either 'cam' or 'clm'"
    exit 1
fi

AVG_DIMS="lat,lon"
read_candidate_file "$CANDIDATE_FILE"

# -------------------------
# Collect files
# -------------------------

FILES=( $(ls "${INDIR}"/${PATTERN} 2>/dev/null | sort) )

if [[ ${#FILES[@]} -eq 0 ]]; then
    echo "Error: no files found"
    echo "  Directory: $INDIR"
    echo "  Pattern:   $PATTERN"
    exit 1
fi

SAMPLE_FILE="${FILES[0]}"

# -------------------------
# Select available variables
# -------------------------

AVAILABLE_VARS=()
NEED_RESTOM=false

for VAR in "${CANDIDATE_VARS[@]}"; do

    if [[ "$VAR" == "RESTOM" ]]; then
        NEED_RESTOM=true
        continue
    fi

    if var_exists "$VAR" "$SAMPLE_FILE"; then
        AVAILABLE_VARS+=( "$VAR" )
        echo "Found variable: $VAR"
    else
        echo "Warning: variable not found in sample file, skipping: $VAR"
    fi

done

# If RESTOM is requested, FSNT and FLNT need to be included temporarily even if they are not included in the list
if [[ "$COMP" == "cam" && "$NEED_RESTOM" == true ]]; then

    if var_exists "FSNT" "$SAMPLE_FILE" && var_exists "FLNT" "$SAMPLE_FILE"; then

        if [[ ! " ${AVAILABLE_VARS[*]} " =~ " FSNT " ]]; then
            AVAILABLE_VARS+=( "FSNT" )
        fi

        if [[ ! " ${AVAILABLE_VARS[*]} " =~ " FLNT " ]]; then
            AVAILABLE_VARS+=( "FLNT" )
        fi

    else
        echo "Warning: RESTOM requested but FSNT and/or FLNT missing. Skipping RESTOM."
        NEED_RESTOM=false
    fi

fi

if [[ ${#AVAILABLE_VARS[@]} -eq 0 ]]; then
    echo "Error: no requested variables found."
    exit 1
fi


# -------------------------
# Add temporary weight variables
# -------------------------

EXTRACT_VARS=( "${AVAILABLE_VARS[@]}" )

if [[ "$COMP" == "cam" ]]; then

    if var_exists "gw" "$SAMPLE_FILE"; then
        EXTRACT_VARS+=( "gw" )
    else
        echo "Error: CAM weight variable 'gw' not found."
        exit 1
    fi

    # Needed for physically correct CAM column burdens before horizontal averaging.
    for AUXVAR in PS hyai hybi P0; do
        if var_exists "$AUXVAR" "$SAMPLE_FILE"; then
            EXTRACT_VARS+=( "$AUXVAR" )
            echo "Adding CAM auxiliary variable for burden calculation: $AUXVAR"
        else
            echo "Warning: CAM auxiliary variable not found: $AUXVAR"
        fi
    done

    # Identify requested gases for column-burden calculation.
    for GAS in "${CAM_BURDEN_GASES[@]}"; do
        if [[ " ${CANDIDATE_VARS[*]} " =~ " ${GAS} " ]] && var_exists "$GAS" "$SAMPLE_FILE"; then
            AVAILABLE_BURDEN_GASES+=( "$GAS" )
            BURDEN_VARS+=( "${GAS}_COLBURDEN" )
            echo "Will calculate CAM column burden for: $GAS"
        fi
    done

elif [[ "$COMP" == "clm" ]]; then

    if var_exists "area" "$SAMPLE_FILE" && var_exists "landfrac" "$SAMPLE_FILE"; then
        EXTRACT_VARS+=( "area" "landfrac" )
    else
        echo "Error: CLM needs both 'area' and 'landfrac' for land-area weighting."
        exit 1
    fi

fi

# -------------------------

VAR_LIST=$(IFS=, ; echo "${EXTRACT_VARS[*]}")

echo
echo "Variables extracted:"
echo "  $VAR_LIST"

# -------------------------
# Process monthly files one by one
# -------------------------

MONTHLY_MEAN_FILES=()

echo "Processing monthly files..."

for FILE in "${FILES[@]}"; do

    BASENAME=$(basename "$FILE" .nc)

    GMEAN="${TMPDIR}/${BASENAME}_globalmean.nc"

    if is_valid_nc "$GMEAN"; then
        echo "Reusing existing temporary monthly mean:"
        echo "  $(basename "$GMEAN")"

        MONTHLY_MEAN_FILES+=( "$GMEAN" )
        continue
    fi

    echo "Processing: $(basename "$FILE")"

    SMALL="${TMPDIR}/${BASENAME}_small.nc"
    WITH_RESTOM="${TMPDIR}/${BASENAME}_with_restom.nc"
    WEIGHTED="${TMPDIR}/${BASENAME}_weighted.nc"
    GMEAN_WORK="${GMEAN}.work.$$"

    rm -f "$GMEAN_WORK"

    if [[ "$COMP" == "cam" ]]; then

        if is_valid_nc "$SMALL"; then
            echo "  Reusing extracted file: $(basename "$SMALL")"
        else
            #echo "  Extracting selected CAM variables..."
            ncks -O \
                -v "time,lat,lon,lev,ilev,${VAR_LIST}" \
                "$FILE" \
                "$SMALL"
        fi

        if [[ "$NEED_RESTOM" == true ]]; then

            if is_valid_nc "$WITH_RESTOM"; then
                echo "  Reusing RESTOM file: $(basename "$WITH_RESTOM")"
            else
                #echo "  Computing RESTOM = FSNT - FLNT..."
                ncap2 -O \
                    -s 'RESTOM=FSNT-FLNT' \
                    "$SMALL" \
                    "$WITH_RESTOM"

                ncatted -O \
                    -a long_name,RESTOM,o,c,"Net radiative flux at TOA" \
                    -a units,RESTOM,o,c,"W/m2" \
                    "$WITH_RESTOM"
            fi

            MEAN_INPUT="$WITH_RESTOM"

        else
            MEAN_INPUT="$SMALL"
        fi

        WITH_BURDEN="${TMPDIR}/${BASENAME}_with_burden.nc"

        if [[ ${#AVAILABLE_BURDEN_GASES[@]} -gt 0 ]]; then
            if is_valid_nc "$WITH_BURDEN"; then
                echo "  Reusing burden file: $(basename "$WITH_BURDEN")"
            else
                echo "  Calculating CAM gas column burdens..."
                compute_cam_column_burdens "$MEAN_INPUT" "$WITH_BURDEN" "${AVAILABLE_BURDEN_GASES[@]}"
            fi

            MEAN_INPUT="$WITH_BURDEN"
        fi

        #echo "  Computing CAM weighted global mean..."
        ncwa -O \
            -w gw \
            -a "$AVG_DIMS" \
            "$MEAN_INPUT" \
            "$GMEAN_WORK"

    elif [[ "$COMP" == "clm" ]]; then

        if is_valid_nc "$SMALL"; then
            echo "  Reusing extracted file: $(basename "$SMALL")"
        else
            #echo "  Extracting selected CLM variables..."
            ncks -O \
                -v "time,lat,lon,${VAR_LIST}" \
                "$FILE" \
                "$SMALL"
        fi

        if is_valid_nc "$WEIGHTED"; then
            echo "  Reusing weighted file: $(basename "$WEIGHTED")"
        else
            #echo "  Creating landarea = area * landfrac..."
            ncap2 -O \
                -s 'landarea=area*landfrac' \
                "$SMALL" \
                "$WEIGHTED"
        fi

        #echo "  Computing CLM land-area-weighted global mean..."
        ncwa -O \
            -w landarea \
            -a "$AVG_DIMS" \
            "$WEIGHTED" \
            "$GMEAN_WORK"

    fi

    if ! is_valid_nc "$GMEAN_WORK"; then
        echo "Error: failed to create valid monthly mean:"
        echo "  $GMEAN_WORK"
        exit 1
    fi

    mv -f "$GMEAN_WORK" "$GMEAN"

    MONTHLY_MEAN_FILES+=( "$GMEAN" )

done

# -------------------------
# Concatenate monthly global means
# -------------------------

echo
echo "Concatenating monthly global means..."

if [[ ${#MONTHLY_MEAN_FILES[@]} -eq 0 ]]; then
    echo "Error: no monthly global-mean files available for concatenation."
    exit 1
fi

OUTFILE_WORK="${OUTFILE}.work.$$"
rm -f "$OUTFILE_WORK"

ncrcat -O "${MONTHLY_MEAN_FILES[@]}" "$OUTFILE_WORK"

if ! is_valid_nc "$OUTFILE_WORK"; then
    echo "Error: failed to create valid output:"
    echo "  $OUTFILE_WORK"
    exit 1
fi

mv -f "$OUTFILE_WORK" "$OUTFILE"


# -------------------------
# Keep only requested final variables
# -------------------------

FINAL_VARS=()

for VAR in "${CANDIDATE_VARS[@]}"; do

    if var_exists "$VAR" "$OUTFILE"; then
        FINAL_VARS+=( "$VAR" )
    fi

done

# Also keep calculated CAM column burdens.
if [[ "$COMP" == "cam" ]]; then
    for VAR in "${BURDEN_VARS[@]}"; do
        if var_exists "$VAR" "$OUTFILE"; then
            FINAL_VARS+=( "$VAR" )
        fi
    done
fi

if [[ ${#FINAL_VARS[@]} -eq 0 ]]; then
    echo "Error: none of the requested final variables are present in output."
    exit 1
fi

# Keep only the requested final variables.
# This removes temporary helper variables such as gw, area, landfrac...
# Write first to a temporary file, check that it is valid, then replace OUTFILE

FINAL_VAR_LIST=$(IFS=, ; echo "${FINAL_VARS[*]}")

FINAL_WORK="${OUTFILE}.final.work.$$"
rm -f "$FINAL_WORK"

ncks -O -v "$FINAL_VAR_LIST" "$OUTFILE" "$FINAL_WORK"

if ! is_valid_nc "$FINAL_WORK"; then
    echo "Error: failed to create final cleaned output:"
    echo "  $FINAL_WORK"
    exit 1
fi

mv -f "$FINAL_WORK" "$OUTFILE"

# -------------------------
# Clean up temporary checkpoint files
# -------------------------

if is_valid_nc "$OUTFILE"; then
    echo
    echo "Final output successfully created."
    echo "Removing temporary files:"
    echo "  $TMPDIR"

    rm -rf "$TMPDIR"
else
    echo
    echo "Error: final output is not valid. Keeping temporary files:"
    echo "  $TMPDIR"
    exit 1
fi

echo
echo "Done."
echo "Final output:"
echo "  $OUTFILE"