#!/bin/bash
#SBATCH --job-name=bvoc-clim
#SBATCH --account=nn9188k
#SBATCH --partition=preproc
#SBATCH --time=23:59:00
#SBATCH --ntasks=1
#SBATCH --mem=16G
#SBATCH --array=0-18
#SBATCH --output=/cluster/work/users/adelez/bvoc-emissions/logs/%x_%A_%a.out
# One array task per species: concat + climatology (create_bvoc_emissions_climatology_staged.py).
# Usage (from this folder): sbatch run_bvoc_climatology_array.sh CASE START_YEAR END_YEAR
#   e.g. sbatch run_bvoc_climatology_array.sh NF2100ssp585norbc_tropstratchem_nudg_ctrl_f19_f19-20261023 2001 2014
# Subset of species: sbatch --array=0,1 ...   (index = position in VARS below)
# Work files (staged_work, purged after 42 days): $OUTPUT_PATH (default /cluster/work/users/adelez/bvoc-emissions).
# The final file is then moved (copy, never overwritten + cmp, then the work copy is deleted) to $FINAL_DIR (default /cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions),
# where the fBVOC runs read it. For FUT targets relabel there afterwards:
#   bash create_bvoc_emissions_for_year_2100.sh CASE_START-END
set -euo pipefail

CASE="$1"; START_YEAR="$2"; END_YEAR="$3"
OUTPUT_PATH="${OUTPUT_PATH:-/cluster/work/users/adelez/bvoc-emissions}"
FINAL_DIR="${FINAL_DIR:-/cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions}"
VARS=(SFISOP SFMTERP MEG_BCARY MEG_C3H6 MEG_BIGENE MEG_CH3CHO MEG_CH2O MEG_C2H4
      MEG_CH3OH MEG_C2H5OH MEG_CH3COOH MEG_CH3COCH3 MEG_HCOOH MEG_HCN MEG_CO
      MEG_C2H6 MEG_C3H8 MEG_BIGALK MEG_TOLUENE)
VAR="${VARS[$SLURM_ARRAY_TASK_ID]}"

# /nird (conda env) is not mounted on compute nodes: use the module Python (same toolchain as NCO;
# output identical to the conda env on the synthetic test, 2026-10-25).
module load NCO/5.2.9-foss-2024a netcdf4-python/1.7.1.post2-foss-2024a
cd "$SLURM_SUBMIT_DIR"
echo "$CASE $START_YEAR-$END_YEAR $VAR -> $OUTPUT_PATH"
for stage in concat climatology; do
    python3 create_bvoc_emissions_climatology_staged.py "$CASE" "$START_YEAR" "$END_YEAR" "$VAR" \
        --calendar noleap --stage "$stage" --output-path "$OUTPUT_PATH"
done
final="ems_${CASE}_${START_YEAR}-${END_YEAR}_${VAR}.nc"
cp -n "$OUTPUT_PATH/$final" "$FINAL_DIR/"
cmp "$OUTPUT_PATH/$final" "$FINAL_DIR/$final"   # set -e: stop and keep the work copy if they differ
rm "$OUTPUT_PATH/$final"
echo "Final file: $FINAL_DIR/$final"
