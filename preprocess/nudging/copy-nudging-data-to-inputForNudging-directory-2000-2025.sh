#!/bin/bash

# Build ONE nudging folder with all MET data, 2000-2025 (user 2026-11-03).
# Same idea as copy-nudging-data-to-inputForNudging-directory.sh (which made _6h_2000-2015):
# copy the 6-hourly CAM h1 files to the shared inputForNudging folder, then write the
# ordered file list.
#   - old files 2000-01-01 ... 2014-12-31: copied from the _6h_2000-2015 folder. Its
#     2015-01-01 file is NOT copied: it is the patched one (data/nudging-met-backup/).
#   - new files 2015-01-01 ... 2026-01-02: from the MET extension (12d production) in the
#     work archive. The real 2015-01-01 file replaces the patched one.
# The old _6h_2000-2015 folder is left untouched (finished runs point to it).
# Never overwrites a file (rsync --ignore-existing; then every file is cmp'd with its source).
#
# Usage: bash copy-nudging-data-to-inputForNudging-directory-2000-2025.sh [--run]
#   without --run: dry run (prints what would be copied, changes nothing)

set -euo pipefail

CASENAME=NF2000norbc_tropstratchem_met_f19_f19_20260422
FREQUENCY=6h
TIME_RANGE=2000-2025

AZ=/cluster/shared/noresm/inputdata/noresm-only/inputForNudging/AZ
OLDDIR=$AZ/${CASENAME}_${FREQUENCY}_2000-2015
NEWSRC=/cluster/work/users/$USER/archive/$CASENAME/atm/hist
NUDGDIR=$AZ/${CASENAME}_${FREQUENCY}_${TIME_RANGE}
FILELIST=$NUDGDIR/${CASENAME}.cam.h1_filelist.txt
PY=/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

RUN=0; [[ "${1:-}" == "--run" ]] && RUN=1
DRY=(--dry-run); [[ $RUN -eq 1 ]] && DRY=()

[[ -d "$OLDDIR" ]] || { echo "ERROR: missing $OLDDIR" >&2; exit 1; }
[[ -d "$NEWSRC" ]] || { echo "ERROR: missing $NEWSRC (MET extension not archived yet?)" >&2; exit 1; }
n_old=$(ls "$OLDDIR"/$CASENAME.cam.h1.20[01][0-9]-*.nc | grep -v '\.2015-01-01-00000\.nc$' | wc -l)
n_new=$(ls "$NEWSRC"/$CASENAME.cam.h1.20[12][0-9]-*.nc | wc -l)
echo "old files (2000-01-01 ... 2014-12-31): $n_old  (expected $((15*365)))"
echo "new files (2015-01-01 ... 2026-01-02): $n_new  (expected $((11*365+2)))"
echo "target: $NUDGDIR"
[[ $RUN -eq 1 ]] || echo "DRY RUN (add --run to copy)"

[[ $RUN -eq 1 ]] && mkdir -p "$NUDGDIR"
# old: everything but the patched 2015-01-01 file and the old file list
rsync -a --ignore-existing --info=stats1 "${DRY[@]}" \
    --exclude="$CASENAME.cam.h1.2015-01-01-00000.nc" --exclude='*filelist*' \
    --include="$CASENAME.cam.h1.*.nc" --exclude='*' \
    "$OLDDIR"/ "$NUDGDIR"/
# new
rsync -a --ignore-existing --info=stats1 "${DRY[@]}" \
    --include="$CASENAME.cam.h1.*.nc" --exclude='*' \
    "$NEWSRC"/ "$NUDGDIR"/
[[ $RUN -eq 1 ]] || exit 0

# Every copied file identical to its source (an existing different file would show here)
echo "cmp of every file with its source..."
for f in "$NUDGDIR"/$CASENAME.cam.h1.*.nc; do
    b=$(basename "$f")
    if [[ "$b" < "$CASENAME.cam.h1.2015-01-01" ]]; then src="$OLDDIR/$b"; else src="$NEWSRC/$b"; fi
    cmp -s "$f" "$src" || { echo "ERROR: $b differs from $src" >&2; exit 1; }
done

ls -1v "$NUDGDIR"/$CASENAME.cam.h1.*.nc > "$FILELIST"
echo "file list: $FILELIST ($(wc -l < "$FILELIST") files)"

# Coverage, records, time continuity, 2015-01-01 record 0 = old patched file record 0
$PY "$HERE/check_nudging_dir.py" "$NUDGDIR" --start 2000-01-01 --end 2026-01-02 \
    --compare-rec0 "$OLDDIR/$CASENAME.cam.h1.2015-01-01-00000.nc"
