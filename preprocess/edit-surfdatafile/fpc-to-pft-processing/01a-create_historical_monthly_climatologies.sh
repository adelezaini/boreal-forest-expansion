#!/usr/bin/env bash
set -euo pipefail

# Convert the 1971–2000 monthly LPJ-GUESS time series into 12-month
# climatologies for each grid cell. Run from the data directory, or pass it
# as the first argument:
#
#   bash create_historical_monthly_climatologies.sh
#   bash create_historical_monthly_climatologies.sh /path/to/LPJ-GUESS
#   bash create_historical_monthly_climatologies.sh ~/BOREAL-FOREST-EXPANSION/data/edit-surfdata/LPJ-GUESS
#
# Existing outputs are protected. Set FORCE=1 only when replacement is wanted:
#
#   FORCE=1 bash create_historical_monthly_climatologies.sh

data_dir="${1:-.}"

make_climatology() {
    local input="$1"
    local output="$2"
    local temporary="${output}.tmp.$$"

    [[ -f "$input" ]] || { echo "ERROR: input not found: $input" >&2; return 1; }
    if [[ -e "$output" && "${FORCE:-0}" != "1" ]]; then
        echo "ERROR: output already exists: $output" >&2
        echo "Rename it, remove it, or rerun with FORCE=1." >&2
        return 1
    fi

    echo "Creating: $output"

    if ! LC_ALL=C awk '
    function flush(    m,i) {
        for (m=1; m<=12; m++) {
            if (!(m in count)) {
                printf "ERROR: lon=%s lat=%s month=%d is missing\n", lon, lat, m > "/dev/stderr"
                errors++
                continue
            }

            if (count[m] != 30) {
                printf "ERROR: lon=%s lat=%s month=%d has %d years\n", lon, lat, m, count[m] > "/dev/stderr"
                errors++
            }

            printf "%.2f %.2f %d", lon, lat, m
            for (i=5; i<=ncol; i++) printf " %.6f", sum[m,i] / count[m]
            print ""
        }

        delete sum
        delete count
    }

    NR==1 {
        ncol=NF
        printf "%s %s %s", $1, $2, $4
        for (i=5; i<=NF; i++) printf " %s", $i
        print ""
        next
    }

    $1=="Lon" {next}

    {
        if (started && ($1 != lon || $2 != lat)) flush()

        if (!started || $1 != lon || $2 != lat) {
            lon=$1
            lat=$2
            started=1
        }

        month=$4
        count[month]++
        for (i=5; i<=ncol; i++) sum[month,i]+=$i
    }

    END {
        if (started) flush()
        if (errors) exit 1
    }
    ' "$input" > "$temporary"; then
        rm -f -- "$temporary"
        echo "ERROR: climatology creation failed for $input" >&2
        return 1
    fi

    local lines data_rows cells
    lines=$(wc -l < "$temporary")
    data_rows=$((lines - 1))

    if ((data_rows <= 0 || data_rows % 12 != 0)); then
        rm -f -- "$temporary"
        echo "ERROR: output has $data_rows data rows, not a multiple of 12." >&2
        return 1
    fi

    cells=$((data_rows / 12))
    mv -f -- "$temporary" "$output"
    echo "Finished: $cells grid cells, $data_rows data rows, $lines lines including header."
}

fpc_input="$data_dir/mfpc_pft_avg_1971_2000.out"
lai_input="$data_dir/mlai_pft_avg_1971_2000.out"
fpc_output="$data_dir/mfpc_pft_avg_1971_2000_monthly_mean.out"
lai_output="$data_dir/mlai_pft_avg_1971_2000_monthly_mean.out"

make_climatology "$fpc_input" "$fpc_output"
make_climatology "$lai_input" "$lai_output"

echo "Both historical monthly climatologies were created successfully."
