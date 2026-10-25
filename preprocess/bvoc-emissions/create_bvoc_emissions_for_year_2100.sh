#!/bin/bash
set -euo pipefail

module load NCO/5.2.9-foss-2024a

# Usage: [EMS_DIR=dir] bash create_bvoc_emissions_for_year_2100.sh [CASE_YEARS] [VAR ...]
#   EMS_DIR    default: /cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions
#              (final files read by the fBVOC runs; run_bvoc_climatology_array.sh copies them there)
#   CASE_YEARS default: latest CTRL_PD, 2001-2014 (keep up to date: CLAUDE.md "When a run version changes")
#   VAR        default: all 19 MEGAN-fed species
# The ISOP/MTERP-only version (CTRL_PD -20260925, shared inputdata) is in prescribe-just-ISOP-MTERP/.
cd "${EMS_DIR:-/cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions}"

CASE_YEARS="${1:-NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20261023_2001-2014}"
shift || true
VARS=("$@")
[[ ${#VARS[@]} -eq 0 ]] && VARS=(SFISOP SFMTERP MEG_BCARY MEG_C3H6 MEG_BIGENE MEG_CH3CHO MEG_CH2O MEG_C2H4
                                MEG_CH3OH MEG_C2H5OH MEG_CH3COOH MEG_CH3COCH3 MEG_HCOOH MEG_HCN MEG_CO
                                MEG_C2H6 MEG_C3H8 MEG_BIGALK MEG_TOLUENE)

for sp in "${VARS[@]}"; do
    echo "Processing species: $sp"

    in="ems_${CASE_YEARS}_${sp}.nc"
    out="ems_${CASE_YEARS}_on_yr2100_${sp}.nc"
    [[ -e "$out" ]] && { echo "ERROR: $out exists; not overwriting" >&2; exit 1; }

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