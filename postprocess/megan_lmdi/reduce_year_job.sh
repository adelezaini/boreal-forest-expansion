#!/bin/bash
#SBATCH --job-name=megan-lmdi
#SBATCH --account=nn9188k
#SBATCH --partition=preproc
#SBATCH --time=10:00:00
#SBATCH --ntasks=1
#SBATCH --mem=16G
# One year pair of the MEGAN exact split (analysis/MEGAN_ATTRIBUTION.md, steps 3-5), submitted by
# cases-scripts/megan-lmdi/watch_megan_lmdi.sh once both runs' tape-2 files of YEAR are archived:
#   3. identity check of each branch against its parent (check_identity.py)        -> stop if it fails
#   4. LMDI reduction of YEAR (reduce_megan_lmdi.py --year)                         -> stop if a check fails
#      test mode: also the replay validation (megan_replay.py) around the job restart and the month boundaries
#   5. delete the year's raw tape-2 files: DELETE=yes (only if every check passed), dry (list only), no,
#      only (spin-up year 2000: identity check, then delete, no reduction)
# Result: $STATE/<label>.ok or <label>.failed; output $OUT/megan_lmdi_<label>.nc (copied to NIRD by the watcher,
# /nird is not mounted on compute nodes).
# Usage: sbatch -o LOG reduce_year_job.sh LABEL YEAR CTRL_CASE CTRL_PARENT LCC_CASE LCC_PARENT DELETE OUT STATE [test]
set -uo pipefail
LABEL="$1"; YEAR="$2"; CTRL="$3"; CTRL_PARENT="$4"; LCC="$5"; LCC_PARENT="$6"; DELETE="$7"; OUT="$8"; STATE="$9"
TEST="${10:-}"
HERE=/cluster/home/adelez/BOREAL-FOREST-EXPANSION/postprocess/megan_lmdi
ARCHIVE=/cluster/work/users/adelez/archive

module load netcdf4-python/1.7.1.post2-foss-2024a     # /nird (conda env) is not mounted on compute nodes
python3 -c "import netCDF4" 2>/dev/null || { echo "module python broken on $(hostname)"; echo "no netCDF4 on $(hostname)" > "$STATE/$1.failed"; exit 1; }
fail() { echo "FAILED: $*"; echo "$*" > "$STATE/$LABEL.failed"; exit 1; }
echo "$(date '+%F %T') $LABEL: CTRL $CTRL, LCC $LCC, year $YEAR, delete=$DELETE ${TEST:+(test)}"

python3 "$HERE/check_identity.py" --branch "$CTRL" --parent "$CTRL_PARENT" --year "$YEAR" || fail "identity CTRL"
python3 "$HERE/check_identity.py" --branch "$LCC" --parent "$LCC_PARENT" --year "$YEAR" || fail "identity LCC"

if [[ -n "$TEST" ]]; then
    # replay of the gammas on new-chain data, on the last day of the first month and the first day of the next
    for c in "$CTRL" "$LCC"; do
        # around the job restart (31 Jan) and the two month boundaries (Jan/Feb, Feb/Mar)
        files=$(ls "$ARCHIVE/$c/lnd/hist/$c".clm2.h1.$YEAR-{01-30,01-31,02-01,02-28,03-01}-*.nc 2>/dev/null)
        [[ $(echo "$files" | wc -w) -eq 5 ]] || fail "replay: expected 5 tape-2 files (30-31 Jan, 1 Feb, 28 Feb, 1 Mar) of $c"
        echo "replay validation, $c:"
        python3 "$HERE/megan_replay.py" $files || fail "replay $c"
    done
fi

if [[ "$DELETE" == only ]]; then
    # spin-up year 2000: no split; after the identity check delete both runs' tape-2 files of the year
    n=0
    for c in "$CTRL" "$LCC"; do
        for f in "$ARCHIVE/$c/lnd/hist/$c".clm2.h1.$YEAR-*.nc; do [[ -f "$f" ]] && rm "$f" && n=$((n + 1)); done
    done
    echo "$(date '+%F %T') identity passed, $n raw tape-2 files of $YEAR deleted (no split)" | tee "$STATE/$LABEL.ok"
    exit 0
fi
case "$DELETE" in
    yes) DEL=--delete-raw ;;
    dry) DEL=--delete-dry-run ;;
    no)  DEL= ;;
    *)   fail "DELETE must be yes, dry or no" ;;
esac
python3 "$HERE/reduce_megan_lmdi.py" --ctrl "$CTRL" --lcc "$LCC" --label "$LABEL" --year "$YEAR" --out "$OUT" $DEL \
    || fail "reduction"
echo "$(date '+%F %T') done" | tee "$STATE/$LABEL.ok"
