#!/bin/bash
# ============================================================
# check_spinup_equilibrium.sh
#
# Purpose:
#   Compute simple spinup-equilibrium diagnostics for NorESM/CESM
#   CAM or CLM history files using NCO only.
#
# Usage:
#   ./check_spinup_equilibrium.sh cam CASENAME
#   ./check_spinup_equilibrium.sh clm CASENAME
#
# Examples:
#   ./check_spinup_equilibrium.sh cam NF2000norbc_tropstratchem_spinup_f19_f19
#   ./check_spinup_equilibrium.sh clm NF2000norbc_tropstratchem_spinup_f19_f19
#
# Resume behavior:
#   If interrupted, rerun the same command.
#   Existing valid intermediate/output files will be skipped.
#
# Optional:
#   FORCE_REDO=1 ./check_spinup_equilibrium.sh cam CASENAME
#   KEEP_TMP_ON_SUCCESS=1 ./check_spinup_equilibrium.sh cam CASENAME
#
# Assumed archive structure:
#   /cluster/work/users/adelez/archive/CASENAME/atm/hist/
#   /cluster/work/users/adelez/archive/CASENAME/lnd/hist/
#
# Output structure:
#   ./equilibrium_output/equilibrium_CASENAME_cam/
#   ./equilibrium_output/equilibrium_CASENAME_clm/
#
# Main outputs:
#   cam_monthly.nc / clm_monthly.nc   monthly global/land means
#   cam_annual.nc  / clm_annual.nc    annual global/land means
#   summary.txt                       first, last, drift, slope
#   VARIABLE.txt                      annual time series per variable
#
# Requirements:
#   ncks, ncwa, ncrcat, ncra, ncap2
# ============================================================

set -euo pipefail

# -------------------------
# Timing
# -------------------------
START_TIME=$(date +%s)

module load NCO/5.2.9-foss-2024a

# -------------------------
# Resume / checkpoint options
# -------------------------
# Set FORCE_REDO=1 to recompute everything even if outputs exist.
FORCE_REDO="${FORCE_REDO:-0}"

# Set KEEP_TMP_ON_SUCCESS=1 to keep temporary checkpoint files after success.
KEEP_TMP_ON_SUCCESS="${KEEP_TMP_ON_SUCCESS:-0}"

# -------------------------
# Resume / checkpoint helpers
# -------------------------
is_valid_nc() {
    local f="$1"
    [[ -s "$f" ]] && ncks -m "$f" >/dev/null 2>&1
}

time_count() {
    local f="$1"

    ncks -m "$f" 2>/dev/null | awk '
        /time = UNLIMITED/ {
            if (match($0, /\(([0-9]+) currently\)/, a)) {
                print a[1]
                exit
            }
        }
        /time = [0-9]+/ {
            gsub(";", "", $3)
            print $3
            exit
        }
    '
}

same_time_count() {
    local f="$1"
    local expected="$2"
    local n

    n="$(time_count "$f" || true)"
    [[ -n "$n" && "$n" -eq "$expected" ]]
}

# -------------------------
# Check input arguments
# -------------------------
if [[ $# -ne 2 ]]; then
    echo "Usage:"
    echo "  ./check_spinup_equilibrium.sh cam CASENAME"
    echo "  ./check_spinup_equilibrium.sh clm CASENAME"
    exit 1
fi

COMP="$1"        # cam or clm
CASENAME="$2"

# -------------------------
# Basic paths
# -------------------------
ARCHIVE_BASE="/cluster/work/users/adelez/archive/${CASENAME}"

SCRIPT_DIR="$(pwd)"

OUTROOT="${SCRIPT_DIR}/equilibrium_output"
OUTDIR="${OUTROOT}/equilibrium_${CASENAME}_${COMP}"
TMPDIR="${OUTDIR}/tmp"

mkdir -p "$OUTDIR" "$TMPDIR"

# -------------------------
# Component-specific settings
# -------------------------
if [[ "$COMP" == "cam" ]]; then

    INDIR="${ARCHIVE_BASE}/atm/hist"
    PATTERN="${CASENAME}.cam.h0.*.nc"

    # CAM Gaussian-grid latitude weights
    AVG_DIMS="lat,lon"

    # Candidate CAM variables for atmosphere equilibrium
    CANDIDATES=(
        TREFHT     # 2 m air temperature
        PRECT      # total precipitation
        FSNT       # net solar flux at TOA
        FLNT       # net longwave flux at TOA
        PSL        # sea-level pressure
        CLDTOT     # total cloud fraction
        TS         # surface temperature
        FSNS       # net solar flux at surface
        FLNS       # net longwave flux at surface
        LHFLX      # latent heat flux
        SHFLX      # sensible heat flux
    )

elif [[ "$COMP" == "clm" ]]; then

    INDIR="${ARCHIVE_BASE}/lnd/hist"
    PATTERN="${CASENAME}.clm2.h0.*.nc"

    AVG_DIMS="lat,lon"

    # Candidate CLM variables for land equilibrium
    CANDIDATES=(
        TOTSOMN     # total soil organic matter nitrogen
        TOTECOSYSN  # total ecosystem nitrogen

        TOTVEGC     # total vegetation carbon
        TOTECOSYSC  # total ecosystem carbon
        TOTSOMC     # total soil organic matter carbon
        TOTLITC     # total litter carbon

        NPP         # net primary productivity
        GPP         # gross primary productivity
        HR          # heterotrophic respiration
        NEE         # net ecosystem exchange
        NBP         # net biome production

        TWS         # total water storage
        H2OSOI      # soil water
        SOILLIQ     # soil liquid water
        SOILICE     # soil ice
        H2OSNO      # snow water

        TSOI        # soil temperature
    )

else
    echo "Error: first argument must be either 'cam' or 'clm'"
    exit 1
fi

# ============================================================
# Locate files
# ============================================================

if [[ ! -d "$INDIR" ]]; then
    echo "Error: input directory does not exist:"
    echo "  $INDIR"
    exit 1
fi

cd "$INDIR"

mapfile -t FILES < <(ls -1 ${PATTERN} 2>/dev/null | sort)

if [[ ${#FILES[@]} -eq 0 ]]; then
    echo "Error: no files found with pattern:"
    echo "  ${INDIR}/${PATTERN}"
    exit 1
fi

SAMPLE="${FILES[0]}"
EXPECTED_MONTHS="${#FILES[@]}"

echo "============================================"
echo "Component: $COMP"
echo "Case:      $CASENAME"
echo "Input dir: $INDIR"
echo "Files:     ${#FILES[@]}"
echo "Sample:    $SAMPLE"
echo "Output:    $OUTDIR"
echo "Resume:    FORCE_REDO=$FORCE_REDO"
echo "============================================"

# ============================================================
# Select only variables that exist
# ============================================================

VARS=()

for v in "${CANDIDATES[@]}"; do

    TESTFILE="${TMPDIR}/test_${v}.nc"

    if ncks -O -v "$v" "$SAMPLE" "$TESTFILE" >/dev/null 2>&1; then
        VARS+=("$v")
        echo "Found variable: $v"
        rm -f "$TESTFILE"
    else
        echo "Skipping missing variable: $v"
    fi

done

if [[ "$COMP" == "cam" ]]; then
    if [[ ! " ${VARS[*]} " =~ " FSNT " || ! " ${VARS[*]} " =~ " FLNT " ]]; then
        echo "Error: CAM requires FSNT and FLNT to compute RESTOM = FSNT - FLNT."
        exit 1
    fi
fi

if [[ ${#VARS[@]} -eq 0 ]]; then
    echo "Error: none of the candidate variables were found."
    exit 1
fi

VARLIST=$(IFS=, ; echo "${VARS[*]}")

echo ""
echo "Variables extracted:"
echo "  $VARLIST"

if [[ "$COMP" == "cam" ]]; then
    echo "Derived variable:"
    echo "  RESTOM = FSNT - FLNT"
fi

echo ""

# ============================================================
# Process monthly files
# ============================================================

MONTHLY_OUT="${OUTDIR}/${COMP}_monthly.nc"
MONTHLY_FILES=()

if [[ "$FORCE_REDO" != "1" ]] && is_valid_nc "$MONTHLY_OUT" && same_time_count "$MONTHLY_OUT" "$EXPECTED_MONTHS"; then

    echo ""
    echo "Monthly output already exists and looks complete:"
    echo "  $MONTHLY_OUT"
    echo "Skipping monthly processing."

else

    echo ""
    echo "Processing monthly files..."

    for f in "${FILES[@]}"; do

        base=$(basename "$f" .nc)

        GMEAN="${TMPDIR}/${base}_gmean.nc"

        if [[ "$FORCE_REDO" != "1" ]] && is_valid_nc "$GMEAN"; then
            echo "Skipping completed monthly mean: $base"
            MONTHLY_FILES+=( "$GMEAN" )
            continue
        fi

        echo "Processing $f"

        WORKTAG="work.$$"

        SMALL="${TMPDIR}/${base}_small.${WORKTAG}.nc"
        WITH_RESTOM="${TMPDIR}/${base}_with_restom.${WORKTAG}.nc"
        WEIGHTED="${TMPDIR}/${base}_weighted.${WORKTAG}.nc"
        GMEAN_WORK="${GMEAN}.${WORKTAG}"

        rm -f "$SMALL" "$WITH_RESTOM" "$WEIGHTED" "$GMEAN_WORK"

        if [[ "$COMP" == "cam" ]]; then

            # Extract selected CAM variables plus grid weights.
            ncks -O \
                -v time,lat,lon,gw,$VARLIST \
                "$f" \
                "$SMALL"

            # Compute TOA net radiative imbalance.
            # Positive RESTOM means net energy gain by the climate system.
            ncap2 -O \
                -s 'RESTOM=FSNT-FLNT' \
                "$SMALL" \
                "$WITH_RESTOM"

            # Area-weighted global mean using CAM Gaussian latitude weights.
            ncwa -O \
                -w gw \
                -a "$AVG_DIMS" \
                "$WITH_RESTOM" \
                "$GMEAN_WORK"

        elif [[ "$COMP" == "clm" ]]; then

            # Extract selected CLM variables plus land-area fields.
            ncks -O \
                -v time,lat,lon,area,landfrac,$VARLIST \
                "$f" \
                "$SMALL"

            # Construct land-area weights.
            ncap2 -O \
                -s 'landarea=area*landfrac' \
                "$SMALL" \
                "$WEIGHTED"

            # Land-area-weighted mean.
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

        rm -f "$SMALL" "$WITH_RESTOM" "$WEIGHTED"

        MONTHLY_FILES+=( "$GMEAN" )

    done

fi

# ============================================================
# Concatenate monthly means
# ============================================================

if [[ "$FORCE_REDO" != "1" ]] && is_valid_nc "$MONTHLY_OUT" && same_time_count "$MONTHLY_OUT" "$EXPECTED_MONTHS"; then

    echo ""
    echo "Monthly concatenated file already complete:"
    echo "  $MONTHLY_OUT"
    echo "Skipping monthly concatenation."

else

    echo ""
    echo "Concatenating monthly means..."

    if [[ ${#MONTHLY_FILES[@]} -eq 0 ]]; then
        echo "Error: no monthly mean files available for concatenation."
        exit 1
    fi

    MONTHLY_WORK="${MONTHLY_OUT}.work.$$"
    rm -f "$MONTHLY_WORK"

    ncrcat -O "${MONTHLY_FILES[@]}" "$MONTHLY_WORK"

    if ! is_valid_nc "$MONTHLY_WORK"; then
        echo "Error: failed to create valid monthly output:"
        echo "  $MONTHLY_WORK"
        exit 1
    fi

    if ! same_time_count "$MONTHLY_WORK" "$EXPECTED_MONTHS"; then
        echo "Error: monthly output has unexpected number of time records."
        echo "Expected: $EXPECTED_MONTHS"
        echo "Found:    $(time_count "$MONTHLY_WORK" || echo unknown)"
        exit 1
    fi

    mv -f "$MONTHLY_WORK" "$MONTHLY_OUT"

fi

# ============================================================
# Compute annual means
# ============================================================

ANNUAL_OUT="${OUTDIR}/${COMP}_annual.nc"
ANNUAL_TMPDIR="${OUTDIR}/tmp_annual"

mkdir -p "$ANNUAL_TMPDIR"

echo ""
echo "Computing annual means..."

NMONTHS="$(time_count "$MONTHLY_OUT" || true)"

if [[ -z "$NMONTHS" ]]; then
    echo "Error: could not determine number of monthly time records."
    exit 1
fi

NYEARS=$((NMONTHS / 12))

if [[ "$NYEARS" -lt 1 ]]; then
    echo "Error: less than 12 monthly records found in $MONTHLY_OUT"
    exit 1
fi

echo "Monthly records: $NMONTHS"
echo "Complete years:  $NYEARS"

ANNUAL_FILES=()

if [[ "$FORCE_REDO" != "1" ]] && is_valid_nc "$ANNUAL_OUT" && same_time_count "$ANNUAL_OUT" "$NYEARS"; then

    echo ""
    echo "Annual output already exists and looks complete:"
    echo "  $ANNUAL_OUT"
    echo "Skipping annual averaging."

else

    for ((yr=0; yr<NYEARS; yr++)); do

        start=$((yr * 12))
        end=$((start + 11))
        yearnum=$(printf "%04d" $((yr + 1)))

        outfile="${ANNUAL_TMPDIR}/${COMP}_annual_${yearnum}.nc"

        if [[ "$FORCE_REDO" != "1" ]] && is_valid_nc "$outfile"; then
            echo "  Skipping completed annual mean: year $((yr + 1))"
            ANNUAL_FILES+=( "$outfile" )
            continue
        fi

        echo "  Year $((yr + 1)): averaging time indices ${start}-${end}"

        outfile_work="${outfile}.work.$$"
        rm -f "$outfile_work"

        ncra -O \
            -d time,$start,$end \
            "$MONTHLY_OUT" \
            "$outfile_work"

        ncks -O --mk_rec_dmn time "$outfile_work" "$outfile_work"

        if ! is_valid_nc "$outfile_work"; then
            echo "Error: failed to create valid annual file:"
            echo "  $outfile_work"
            exit 1
        fi

        mv -f "$outfile_work" "$outfile"

        ANNUAL_FILES+=( "$outfile" )

    done

    echo ""
    echo "Concatenating annual means..."

    ANNUAL_WORK="${ANNUAL_OUT}.work.$$"
    rm -f "$ANNUAL_WORK"

    ncrcat -O "${ANNUAL_FILES[@]}" "$ANNUAL_WORK"

    if ! is_valid_nc "$ANNUAL_WORK"; then
        echo "Error: failed to create valid annual output:"
        echo "  $ANNUAL_WORK"
        exit 1
    fi

    if ! same_time_count "$ANNUAL_WORK" "$NYEARS"; then
        echo "Error: annual output has unexpected number of time records."
        echo "Expected: $NYEARS"
        echo "Found:    $(time_count "$ANNUAL_WORK" || echo unknown)"
        exit 1
    fi

    mv -f "$ANNUAL_WORK" "$ANNUAL_OUT"

fi

# ============================================================
# Compute drift and linear trends
# ============================================================

SUMMARY="${OUTDIR}/summary.txt"

echo ""
echo "Computing drift and linear trend..."

echo "var first last drift slope_per_year" > "$SUMMARY"

SUMMARY_VARS=("${VARS[@]}")

if [[ "$COMP" == "cam" ]]; then
    SUMMARY_VARS+=(RESTOM)
fi

for v in "${SUMMARY_VARS[@]}"; do

    TXT="${OUTDIR}/${v}.txt"

    ncks -H -C -v "$v" "$ANNUAL_OUT" \
        | awk -F'[= ]+' '/'"$v"'/ {print NR, $NF}' \
        > "$TXT"

    awk -v var="$v" '
    {
        x[NR]=$1
        y[NR]=$2
        n=NR
    }
    END {
        if (n < 2) {
            print var, "NA", "NA", "NA", "NA"
            exit
        }

        sx=sy=sxx=sxy=0

        for (i=1; i<=n; i++) {
            sx  += x[i]
            sy  += y[i]
            sxx += x[i]*x[i]
            sxy += x[i]*y[i]
        }

        denom = n*sxx - sx*sx

        if (denom == 0) {
            slope = "NA"
        } else {
            slope = (n*sxy - sx*sy) / denom
        }

        drift = y[n] - y[1]

        print var, y[1], y[n], drift, slope
    }' "$TXT" >> "$SUMMARY"

done

# ============================================================
# Finish
# ============================================================

echo ""

if [[ "$KEEP_TMP_ON_SUCCESS" == "1" ]]; then
    echo "Keeping temporary files:"
    echo "  $TMPDIR"
    echo "  $ANNUAL_TMPDIR"
else
    echo "Removing temporary files..."
    rm -rf "$TMPDIR" "$ANNUAL_TMPDIR"
fi

echo ""
echo "Done."
echo ""

END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))

printf "\nTotal runtime: %02d:%02d:%02d (hh:mm:ss)\n" \
    $((TOTAL_TIME/3600)) \
    $(((TOTAL_TIME%3600)/60)) \
    $((TOTAL_TIME%60))

echo ""
echo "Outputs written to:"
echo "  $OUTDIR"
echo ""
echo "Main files:"
echo "  ${COMP}_monthly.nc"
echo "  ${COMP}_annual.nc"
echo "  summary.txt"
echo ""
echo "Interpretation reminder:"
echo "  - CAM: check RESTOM, TREFHT, PRECT, PSL, CLDTOT."
echo "  - CLM: check storage variables more than fluxes."
echo "  - CLM equilibrium cannot be proven from NPP alone."
echo ""