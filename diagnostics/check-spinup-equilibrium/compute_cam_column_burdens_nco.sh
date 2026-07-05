#!/bin/bash

# Helper function for concatenate_monthly_global_means.sh

set -euo pipefail

# CAM tracers for which we calculate column burden if present/requested.
# Assumes tracer units are mol mol-1.
CAM_BURDEN_GASES=(SF6 CFC115 N2O CO2 CH4)

compute_cam_column_burdens() {
    local infile="$1"
    local outfile="$2"

    shift 2
    local gases=( "$@" )

    if [[ ${#gases[@]} -eq 0 ]]; then
        cp "$infile" "$outfile"
        return
    fi

    for AUXVAR in PS hyai hybi P0; do
        if ! var_exists "$AUXVAR" "$infile"; then
            echo "Warning: cannot calculate CAM column burdens because $AUXVAR is missing."
            cp "$infile" "$outfile"
            return
        fi
    done

    local work="${outfile}.work.$$"
    local nco_script="${outfile}.dp_script.$$"
    local gas_tmp="${outfile}.gas_tmp.$$"
    local burden_tmp="${outfile}.burden_tmp.$$"

    rm -f "$work" "$nco_script" "$gas_tmp" "$burden_tmp"

    cp "$infile" "$work"

    local nlev

    nlev=$(ncks -m "$infile" | awk '
        /^[[:space:]]*lev[[:space:]]*=/ {
            for (i=1; i<=NF; i++) {
                gsub(";", "", $i)
                if ($i ~ /^[0-9]+$/) {
                    print $i
                    exit
                }
            }
        }
    ')

    if [[ -z "$nlev" || "$nlev" -le 0 ]]; then
        echo "Warning: could not determine number of lev levels. Skipping burdens."
        cp "$infile" "$outfile"
        rm -f "$work" "$nco_script" "$gas_tmp" "$burden_tmp"
        return
    fi

    echo "  Number of CAM lev levels detected: $nlev"

    {
        echo 'dp[time,lev,lat,lon]=0.0f;'
        for (( k=0; k<nlev; k++ )); do
            kp1=$(( k + 1 ))
            echo "dp(:,$k,:,:)=((hyai($kp1)-hyai($k))*P0)+((hybi($kp1)-hybi($k))*PS);"
        done
        echo 'dp=abs(dp);'
        echo 'dp@long_name="hybrid pressure layer thickness";'
        echo 'dp@units="Pa";'
    } > "$nco_script"

    local dp_tmp="${outfile}.dp_tmp.$$"

    ncap2 -O -S "$nco_script" "$work" "$dp_tmp"
    mv -f "$dp_tmp" "$work"

    local G="9.80665"
    local MAIR="0.0289647"

    for GAS in "${gases[@]}"; do

        if ! var_exists "$GAS" "$work"; then
            echo "Warning: burden gas not found after extraction, skipping: $GAS"
            continue
        fi

        echo "  Calculating column burden for $GAS"

        rm -f "$gas_tmp" "$burden_tmp"

        ncap2 -O \
            -s "${GAS}_BURDEN_LEV=${GAS}*dp/(${G}*${MAIR}); ${GAS}_BURDEN_LEV@units=\"mol m-2\"; ${GAS}_BURDEN_LEV@long_name=\"${GAS} column burden contribution by model layer\";" \
            "$work" \
            "$gas_tmp"

        ncwa -O \
            -y ttl \
            -a lev \
            -v "${GAS}_BURDEN_LEV" \
            "$gas_tmp" \
            "$burden_tmp"

        ncrename -O \
            -v "${GAS}_BURDEN_LEV,${GAS}_COLBURDEN" \
            "$burden_tmp"

        ncatted -O \
            -a long_name,"${GAS}_COLBURDEN",o,c,"${GAS} column burden" \
            -a units,"${GAS}_COLBURDEN",o,c,"mol m-2" \
            "$burden_tmp"

        ncks -A "$burden_tmp" "$work"

    done

    ncks -O -x -v dp "$work" "$outfile"

    rm -f "$work" "$nco_script" "$gas_tmp" "$burden_tmp"
}