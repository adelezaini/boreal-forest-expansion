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
# CASENAME = NF2000norbc_tropstratchem_spinup_f19_f19, NF2100ssp585_tropstratchem_spinup_f19_f19
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
# ===========================NF2000norbc_tropstratchem_spinup_f19_f19=================================

set -euo pipefail

# -------------------------
# Timing
# -------------------------
START_TIME=$(date +%s)

module load NCO/5.2.9-foss-2024a

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
    WEIGHT_VAR="gw"
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

FILES=( $(ls -1 ${PATTERN} 2>/dev/null | sort) )

if [[ ${#FILES[@]} -eq 0 ]]; then
    echo "Error: no files found with pattern:"
    echo "  ${INDIR}/${PATTERN}"
    exit 1
fi

SAMPLE="${FILES[0]}"

echo "============================================"
echo "Component: $COMP"
echo "Case:      $CASENAME"
echo "Input dir: $INDIR"
echo "Files:     ${#FILES[@]}"
echo "Sample:    $SAMPLE"
echo "Output:    $OUTDIR"
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

MONTHLY_FILES=()

for f in "${FILES[@]}"; do

    base=$(basename "$f" .nc)

    echo "Processing $f"

    if [[ "$COMP" == "cam" ]]; then

        # Extract selected CAM variables plus grid weights.
        # This avoids working with thousands of unnecessary variables.
        
        ncks -O \
            -v time,lat,lon,gw,$VARLIST \
            "$f" \
            "$TMPDIR/${base}_small.nc"

        # Compute TOA net radiative imbalance.
        # Positive RESTOM means net energy gain by the climate system.
        ncap2 -O \
            -s 'RESTOM=FSNT-FLNT' \
            "$TMPDIR/${base}_small.nc" \
            "$TMPDIR/${base}_with_restom.nc"

        # Area-weighted global mean using CAM Gaussian latitude weights.
        ncwa -O \
            -w gw \
            -a "$AVG_DIMS" \
            "$TMPDIR/${base}_with_restom.nc" \
            "$TMPDIR/${base}_gmean.nc"

    elif [[ "$COMP" == "clm" ]]; then

        # Extract selected CLM variables plus land-area fields.
        ncks -O \
            -v time,lat,lon,area,landfrac,$VARLIST \
            "$f" \
            "$TMPDIR/${base}_small.nc"

        # Construct land-area weights.
        ncap2 -O \
            -s 'landarea=area*landfrac' \
            "$TMPDIR/${base}_small.nc" \
            "$TMPDIR/${base}_weighted.nc"

        # Land-area-weighted mean.
        ncwa -O \
            -w landarea \
            -a "$AVG_DIMS" \
            "$TMPDIR/${base}_weighted.nc" \
            "$TMPDIR/${base}_gmean.nc"
    fi

    MONTHLY_FILES+=( "$TMPDIR/${base}_gmean.nc" )

done

# ============================================================
# Concatenate monthly means
# ============================================================

MONTHLY_OUT="${OUTDIR}/${COMP}_monthly.nc"

echo ""
echo "Concatenating monthly means..."
ncrcat -O "${MONTHLY_FILES[@]}" "$MONTHLY_OUT"

# ============================================================
# Compute annual means
# ============================================================

ANNUAL_OUT="${OUTDIR}/${COMP}_annual.nc"
ANNUAL_TMPDIR="${OUTDIR}/tmp_annual"

rm -rf "$ANNUAL_TMPDIR"
mkdir -p "$ANNUAL_TMPDIR"

echo "Computing annual means..."

# Extract number of monthly records from a line like:
#   time = UNLIMITED ; // (240 currently)
TIME_LINE=$(ncks -m "$MONTHLY_OUT" | grep "time =" || true)

NMONTHS=$(echo "$TIME_LINE" | sed -n 's/.*(\([0-9][0-9]*\) currently).*/\1/p')

if [[ -z "$NMONTHS" ]]; then
    echo "Error: could not determine number of monthly time records."
    echo "Detected time line:"
    echo "$TIME_LINE"
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

for ((yr=0; yr<NYEARS; yr++)); do

    start=$((yr * 12))
    end=$((start + 11))
    yearnum=$(printf "%04d" $((yr + 1)))

    outfile="${ANNUAL_TMPDIR}/${COMP}_annual_${yearnum}.nc"

    echo "  Year $((yr + 1)): averaging time indices ${start}-${end}"

    ncra -O \
        -d time,$start,$end \
        "$MONTHLY_OUT" \
        "$outfile"

    # Make each annual file concatenatable along time
    ncks -O --mk_rec_dmn time "$outfile" "$outfile"

    ANNUAL_FILES+=( "$outfile" )

done

ncrcat -O "${ANNUAL_FILES[@]}" "$ANNUAL_OUT"

rm -rf "$ANNUAL_TMPDIR"

# ============================================================
# Compute drift and linear trends
# ============================================================

SUMMARY="${OUTDIR}/summary.txt"

echo "var first last drift slope_per_year" > "$SUMMARY"

echo "Computing drift and linear trend..."

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

# -------------------------
# Clean temporary files
# -------------------------
echo "Removing temporary files..."
rm -rf "$TMPDIR"

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