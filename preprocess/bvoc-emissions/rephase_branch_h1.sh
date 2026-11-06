#!/bin/bash
# Re-cut the half-hourly h1 files of the LCC_FUT_HRBVOC BRANCH pieces (s2: 2005-2009, s3: 2010-2014) to the
# hybrid convention of s1 and of every CTRL source run (2026-11-06).
# Why: a branch run writes day files D-01800 = D 00:30 ... D+1 00:00; a hybrid run writes D-00000 = D 00:00 ... D 23:30.
#   create_bvoc_emissions_climatology_staged.py refuses to average years with different sampling phase
#   (climatology array 1788903 failed at 2005, 5 Nov). Values are NOT changed, only the file boundaries:
#   new D-00000 = last record of the previous day file (D 00:00) + records 0..46 of D-01800 (D 00:30 ... 23:30).
#   The 00:00 record of the first day of s2 (2005-01-01) comes from s1's one-record file 2005-01-01-00000,
#   that of s3 (2010-01-01) from s2's last file 2009-12-31-01800 (all three pieces are identical to LCC_FUT).
# Output: real files in $OUT/<case>/atm/hist/<case>.cam.h1.<D>-00000.nc (s2, s3); nothing in the archive is touched.
# Usage: bash rephase_branch_h1.sh <s1 case> <s2 case> <s3 case> [NJOBS]
set -euo pipefail
[[ $# -ge 3 ]] || { echo "Usage: $0 <s1> <s2> <s3> [NJOBS]" >&2; exit 1; }
S1=$1; S2=$2; S3=$3; NJ=${4:-8}
A=/cluster/work/users/$USER/archive
OUT=/cluster/work/users/$USER/archive_phase0
module load NCO/5.2.9-foss-2024a >/dev/null 2>&1 || true
command -v ncrcat >/dev/null || { echo "ERROR: NCO not available" >&2; exit 1; }
TMP=$(mktemp -d /cluster/work/users/$USER/rephase_tmp.XXXX)
trap 'rm -rf "$TMP"' EXIT

jobs=$TMP/jobs.txt; : > "$jobs"
prev="$A/$S1/atm/hist/$S1.cam.h1.2005-01-01-00000.nc"            # 2005-01-01 00:00
[[ -f "$prev" ]] || { echo "ERROR: missing $prev" >&2; exit 1; }
for c in "$S2" "$S3"; do
    mkdir -p "$OUT/$c/atm/hist"
    for f in "$A/$c/atm/hist/$c".cam.h1.*-01800.nc; do
        d=$(basename "$f" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}-01800' | cut -c1-10)
        echo "$prev $f $OUT/$c/atm/hist/$c.cam.h1.$d-00000.nc" >> "$jobs"
        prev=$f
    done
done
echo "$(wc -l < "$jobs") day files to build (expect 3650)"

one() {   # PREV CUR OUT: last record of PREV + records 0..46 of CUR
    local p=$1 c=$2 o=$3 t
    [[ -f "$o" ]] && return 0
    t=$(mktemp -d "$TMP/d.XXXX")
    ncks -O -d time,-1 "$p" "$t/a.nc" && ncks -O -d time,0,46 "$c" "$t/b.nc" && ncrcat -O "$t/a.nc" "$t/b.nc" "$t/o.nc" \
        && [[ $(ncks -m "$t/o.nc" | grep -oE 'time = UNLIMITED ; // \(([0-9]+)' | grep -oE '[0-9]+$') == 48 ]] \
        && mv "$t/o.nc" "$o" || { echo "FAILED $o" >&2; rm -rf "$t"; return 1; }
    rm -rf "$t"
}
export -f one; export TMP
xargs -P "$NJ" -L 1 bash -c 'one "$0" "$1" "$2"' < "$jobs"
n2=$(ls "$OUT/$S2/atm/hist/" | wc -l); n3=$(ls "$OUT/$S3/atm/hist/" | wc -l)
echo "built: $S2 $n2, $S3 $n3 (expect 1825 each)"
[[ $n2 -eq 1825 && $n3 -eq 1825 ]] || { echo "ERROR: unexpected file count" >&2; exit 1; }
echo REPHASE_OK
