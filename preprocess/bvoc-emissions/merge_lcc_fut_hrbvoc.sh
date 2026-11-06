#!/bin/bash
# Merge LCC_FUT_HRBVOC (24f: 3 output-only segments of LCC_FUT -20261028) into one history
# folder that create_bvoc_emissions_climatology_staged.py reads as if LCC_FUT itself had
# written the HR_BVOC_ALL h1 tape. Symlinks only; nothing is copied or modified.
#   h0 (11 monthly MEG_*) -> LCC_FUT's own h0
#   h1 (8 half-hourly)    -> s1 files dated 2000-2004 (hybrid, phase 0; its one-record
#                            2005-01-01-00000 file is excluded: 2005 comes from s2),
#                            all of s2 (2005-2009) and s3 (2010-2014) (branch, phase 1800:
#                            files YYYY-MM-DD-01800, 00:30 ... next day 00:00)
# PHASE0_ROOT (2026-11-06): take s2/s3 h1 from rephase_branch_h1.sh output (D-00000 files, hybrid convention);
#   the raw branch files (D-01800) made the climatology fail (phase 1800 vs 0, array 1788903).
# Usage: [PHASE0_ROOT=/cluster/work/users/$USER/archive_phase0] bash merge_lcc_fut_hrbvoc.sh <s1 case> <s2 case> <s3 case>
# Then:  NORESM_ARCHIVE=$MERGE_ROOT sbatch run_bvoc_climatology_array.sh $LCC_FUT 2001 2014
set -euo pipefail
[[ $# -eq 3 ]] || { echo "Usage: $0 <s1 case> <s2 case> <s3 case>" >&2; exit 1; }
ARCH=/cluster/work/users/$USER/archive
LCC_FUT=NF2100ssp585norbc_tropstratchem_nudg_lcc_f19_f19-20261028
MERGE_ROOT=/cluster/work/users/$USER/archive_merged
OUT="$MERGE_ROOT/$LCC_FUT/atm/hist"
[[ ! -e "$OUT" ]] || { echo "ERROR: $OUT exists; move it first" >&2; exit 1; }
mkdir -p "$OUT"

link() {  # link <source file> <case prefix to replace>
    local f="$1" pre="$2" dst
    dst="$OUT/$LCC_FUT${f##*/$pre}"
    [[ ! -e "$dst" ]] || { echo "ERROR: duplicate target $dst" >&2; exit 1; }
    ln -s "$f" "$dst"
}
n0=0; for f in "$ARCH/$LCC_FUT"/atm/hist/"$LCC_FUT".cam.h0.20{01..14}-*.nc; do link "$f" "$LCC_FUT"; n0=$((n0+1)); done
n1=0; for f in "$ARCH/$1"/atm/hist/"$1".cam.h1.200[0-4]-*.nc; do link "$f" "$1"; n1=$((n1+1)); done
for c in "$2" "$3"; do
    for f in "${PHASE0_ROOT:-$ARCH}/$c"/atm/hist/"$c".cam.h1.*.nc; do link "$f" "$c"; n1=$((n1+1)); done
done
echo "Linked $n0 h0 (expect 168) and $n1 h1 files (expect 5 x 365 x 3 = 5475) in $OUT"
[[ $n0 -eq 168 && $n1 -eq 5475 ]] || { echo "ERROR: unexpected file count" >&2; exit 1; }
