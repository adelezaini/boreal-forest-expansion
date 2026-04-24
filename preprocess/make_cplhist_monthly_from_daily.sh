#!/bin/bash

module load NCO/5.2.9-foss-2024a

CPLHIST_DIR=NF2000norbc_tropstratchem_spinup_f19_f19_20260421_01-20
CASENAME=NF2000norbc_tropstratchem_spinup_f19_f19

SRC_DIR=/cluster/home/adelez/work/archive/$CASENAME/cpl/hist
CPLHIST_PATH=/cluster/shared/noresm/inputdata/cplhist

make_monthly_cplhist_from_daily () {
    # Created with ChatGTP (25.04.26)

    # INPUTS
    # $1 = source directory (daily files)
    # $2 = output directory (monthly files)
    # $3 = case name (prefix of files)
    # $4 = start year (default 0001)
    # $5 = end year   (default 0020)

    local src_dir="$1"
    local out_dir="$2"
    local case="$3"
    local ystart="${4:-0001}"
    local yend="${5:-0020}"

    # Ensure output directory exists
    mkdir -p "$out_dir" || return 1

    # Streams that follow normal calendar grouping:
    # monthly file = all daily files within the same month
    local normal_streams=("ha2x" "ha2x1h" "ha2x1hi" "ha2x3h") #"hl2x"

    # Streams that are time-shifted (daily mean stamped at next day):
    # monthly file = YYYY-MM-02 ... next-month-01
    local shifted_streams=("ha2x1d" "hr2x")

    # Helper: compute next month (YYYY-MM)
    _month_next () {
        local y="$1"
        local m="$2"

        if [ "$m" = "12" ]; then
            printf "%04d-01" $((10#$y + 1))
        else
            printf "%04d-%02d" $((10#$y)) $((10#$m + 1))
        fi
    }

    # Create monthly file for "normal" streams
    _make_normal_month () {
        local stream="$1"
        local y="$2"
        local m="$3"

        # Output filename (must match DATM expectations exactly)
        local out="${out_dir}/${case}.cpl.${stream}.${y}-${m}.nc"

        # All daily files for this month (01..lastday)
        local files=( "${src_dir}/${case}.cpl.${stream}.${y}-${m}-"??.nc )

        # Skip if already exists
        [ -f "$out" ] && { echo "skip existing $out"; return 0; }

        # Skip if no input files
        [ ! -e "${files[0]}" ] && { echo "missing normal input: $stream $y-$m"; return 0; }

        echo "creating $out"

        # Concatenate daily → monthly
        ncrcat -O "${files[@]}" "$out" || return 1
    }

    # Create monthly file for "shifted" streams
    _make_shifted_month () {
        local stream="$1"
        local y="$2"
        local m="$3"

        local next
        next=$(_month_next "$y" "$m")

        local out="${out_dir}/${case}.cpl.${stream}.${y}-${m}.nc"

        # Build shifted list explicitly:
        # current month day 02..lastday + next month day 01
        local files=()

        for f in "${src_dir}/${case}.cpl.${stream}.${y}-${m}-"??.nc; do
            [ -e "$f" ] || continue

            # Skip day 01 of the current month
            [[ "$f" == *"-01.nc" ]] && continue

            files+=( "$f" )
        done

        # Add day 01 of next month
        files+=( "${src_dir}/${case}.cpl.${stream}.${next}-01.nc" )

        [ -f "$out" ] && { echo "skip existing $out"; return 0; }

        if [ "${#files[@]}" -eq 0 ]; then
            echo "missing shifted input: $stream $y-$m"
            return 0
        fi

        if [ ! -e "${files[-1]}" ]; then
            echo "missing next-month day 01: $stream ${next}-01"
            return 1
        fi

        echo "creating shifted $out"
        ncrcat -O "${files[@]}" "$out" || return 1
    }

    # Main loop over years and months
    for y in $(seq -f "%04g" "$ystart" "$yend"); do
        for m in $(seq -f "%02g" 1 12); do

            # Process normal streams
            for stream in "${normal_streams[@]}"; do
                _make_normal_month "$stream" "$y" "$m" || return 1
            done

            # Process shifted streams
            for stream in "${shifted_streams[@]}"; do
                _make_shifted_month "$stream" "$y" "$m" || return 1
            done

        done
    done
}

make_monthly_cplhist_from_daily "$SRC_DIR" "$CPLHIST_PATH/$CPLHIST_DIR" "$CASENAME"