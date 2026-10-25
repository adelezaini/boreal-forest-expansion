#!/bin/bash
# Usage: bash create_bvoc_emissions_climatology.sh [CASE] [VAR ...]
#   CASE default: latest CTRL_PD (keep up to date: CLAUDE.md "When a run version changes")
#   VAR  default: all 19 MEGAN-fed species (needs a CTRL run with cam_diagnostics HR_BVOC_ALL)
# Half-hourly species are read from h1, monthly ones from h0 (MONTHLY_VARS in the .py).
# Work files in /cluster/work/users/adelez/bvoc-emissions; final files moved (cp -n + cmp, then the work copy is deleted) to
# FINAL_DIR (default /cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions), where the fBVOC runs read them.

module load NCO/5.2.9-foss-2024a

CASE="${1:-NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20261023}"
START_YEAR=2001
END_YEAR=2014
WORK_DIR=/cluster/work/users/adelez/bvoc-emissions
FINAL_DIR="${FINAL_DIR:-/cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions}"
shift
VARS=("$@")
[[ ${#VARS[@]} -eq 0 ]] && VARS=(SFISOP SFMTERP MEG_BCARY MEG_C3H6 MEG_BIGENE MEG_CH3CHO MEG_CH2O MEG_C2H4
                                MEG_CH3OH MEG_C2H5OH MEG_CH3COOH MEG_CH3COCH3 MEG_HCOOH MEG_HCN MEG_CO
                                MEG_C2H6 MEG_C3H8 MEG_BIGALK MEG_TOLUENE)

for VAR in "${VARS[@]}"; do
    echo -e "\n${VAR}:\n------------"
    python create_bvoc_emissions_climatology_staged.py   "$CASE" "$START_YEAR" "$END_YEAR" "$VAR" --calendar noleap   --stage concat
    python create_bvoc_emissions_climatology_staged.py   "$CASE" "$START_YEAR" "$END_YEAR" "$VAR" --calendar noleap   --stage climatology
    final="ems_${CASE}_${START_YEAR}-${END_YEAR}_${VAR}.nc"
    cp -n "$WORK_DIR/$final" "$FINAL_DIR/" && cmp "$WORK_DIR/$final" "$FINAL_DIR/$final" && rm "$WORK_DIR/$final"
done
