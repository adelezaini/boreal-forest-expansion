#!/bin/bash
# Postprocess one archived run of the new (CO2-fix) chain (user 2026-10-29). Started in the background by
# cases-scripts/auto_launch_new_chain.sh; runs one at a time (flock).
#   1. Move the old processed files of ALIAS out of the current folder (CLAUDE.md rule iii):
#      <ALIAS>_{atm,lnd}_*_2001-2009.nc -> 2001-2009-pre-co2-fix/, all other spans -> 2001-2014-all-bvoc-pre-co2-fix/;
#      their logs/<ALIAS>_{atm,lnd}_*.log go to <target>/logs/. Never overwrites (stops if a target exists).
#   2. run_all_parallel.sh for this case only (all atm + lnd categories, first 12 months dropped, work archive).
#   3. Check: 19 output files (10 atm + 9 lnd) and no FAILED line.
# Result: <STATE_PREFIX>.ok or <STATE_PREFIX>.err; log <STATE_PREFIX>.log.
# Usage: bash postprocess_new_chain_run.sh ALIAS CASENAME STATE_PREFIX [NJOBS]
set -uo pipefail

ALIAS=$1 CASE=$2 PREFIX=$3 NJOBS=${4:-10}
HERE=/cluster/home/adelez/BOREAL-FOREST-EXPANSION/postprocess
OUT=/cluster/home/adelez/BOREAL-FOREST-EXPANSION/data/processed-data/postprocessing
exec >> "$PREFIX.log" 2>&1
fail() { echo "$(date '+%F %T') ERROR: $*"; touch "$PREFIX.err"; exit 1; }

exec 9> "$(dirname "$PREFIX")/postprocess.lock"
echo "$(date '+%F %T') $ALIAS $CASE: waiting for lock"
flock 9
echo "$(date '+%F %T') $ALIAS $CASE: start"

# 1. Move old files (exact <ALIAS>_atm_/<ALIAS>_lnd_ prefix: CTRL_PD never matches CTRL_PD_fBVOCctrlPD)
shopt -s nullglob
for f in "$OUT/${ALIAS}"_{atm,lnd}_*.nc; do
    case "$f" in *_2001-2009.nc) dest=2001-2009-pre-co2-fix ;; *) dest=2001-2014-all-bvoc-pre-co2-fix ;; esac
    [[ -e "$OUT/$dest/$(basename "$f")" ]] && fail "$OUT/$dest/$(basename "$f") exists, not overwritten"
    mv -n "$f" "$OUT/$dest/" || fail "mv $f"
    echo "moved $(basename "$f") -> $dest/"
    for l in "$OUT/logs/$(basename "${f%_*.nc}").log"; do
        [[ -e $l ]] || continue
        mkdir -p "$OUT/$dest/logs"
        [[ -e "$OUT/$dest/logs/$(basename "$l")" ]] && fail "$OUT/$dest/logs/$(basename "$l") exists"
        mv -n "$l" "$OUT/$dest/logs/" || fail "mv $l"
    done
done
left=("$OUT/${ALIAS}"_{atm,lnd}_*.nc)
(( ${#left[@]} == 0 )) || fail "old files left: ${left[*]}"

# 2. Postprocess
out=$(CASES="$ALIAS $CASE" bash "$HERE/run_all_parallel.sh" "$NJOBS")
echo "$out"

# 3. Check
n=$(ls "$OUT/${ALIAS}"_{atm,lnd}_*.nc 2>/dev/null | wc -l)
grep -q '^FAILED' <<< "$out" && fail "some categories failed (n=$n)"
(( n == 19 )) || fail "expected 19 output files, found $n"
echo "$(date '+%F %T') $ALIAS $CASE: done, $n files"
touch "$PREFIX.ok"
