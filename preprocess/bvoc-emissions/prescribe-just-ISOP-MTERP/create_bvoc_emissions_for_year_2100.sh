#!/bin/bash
set -euo pipefail

module load NCO/5.2.9-foss-2024a

cd /cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions

CASE_YEARS="NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20260925_2001-2009"

for sp in SFISOP SFMTERP; do
    echo "Processing species: $sp"

    in="ems_${CASE_YEARS}_${sp}.nc"
    out="ems_${CASE_YEARS}_on_yr2100_${sp}.nc"

    echo "  Checking calendar and time origin"

    header=$(ncdump -h "$in")

    if ! grep -Eq 'time:calendar = "(noleap|365_day)"' <<< "$header"; then
        echo "ERROR: expected a noleap calendar in $in" >&2
        exit 1
    fi

    if ! grep -Fq 'time:units = "days since 2000-01-01 00:00:00"' <<< "$header"; then
        echo "ERROR: unexpected time origin in $in" >&2
        exit 1
    fi

    bounds=$(sed -n 's/.*time:bounds = "\([^"]*\)".*/\1/p' <<< "$header")

    echo "  Relabelling dates from year 2000 to 2100"
    ncap2 -O -s 'date=date+1000000' "$in" "$out"

    # Update time and optional bounds metadata in a single file-editing pass.
    attrs=(
        -a "units,time,o,c,days since 2100-01-01 00:00:00"
        -a "fake_year_note,global,o,c,Year-2000 noleap climatology relabelled as year 2100; emission values unchanged."
    )

    if [[ -n "$bounds" ]]; then
        attrs+=(-a "units,${bounds},o,c,days since 2100-01-01 00:00:00")
    fi

    echo "  Updating time metadata"
    ncatted -O "${attrs[@]}" "$out"

    echo "  Finished: $out"
    ncdump -h "$out" | grep -E \
        'time = UNLIMITED|:units = "days since|time:calendar|fake_year_note'
done