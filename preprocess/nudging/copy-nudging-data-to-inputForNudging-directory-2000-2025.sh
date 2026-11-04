#!/bin/bash

# Build ONE nudging folder with all MET data, 2000-2025 (user 2026-11-03).
#   - old files 2000-01-01 ... 2014-12-31: copied from the _6h_2000-2015 folder. Its
#     2015-01-01 file is NOT copied: it is the patched one (data/nudging-met-backup/).
#   - new days 2015-01-01 ... : REGROUPED from the MET extension (12d production) in the
#     work archive by regroup_met_ext_days.py. The extension is a branch run, so its h1
#     files are cut 06 h -> next day 00 h (`-21600.nc`); the folder needs calendar days
#     (`-00000.nc`, 00/06/12/18 h). 2015-01-01 = record 0 of the old file (original) +
#     06-18 h of the extension (real data, replaces the patched copies).
#   - can run while the extension is still going (user 2026-11-04: fill the folder after
#     the first segment): builds every day whose sources are archived, skips existing
#     days; rerun after the next segment. `--final` (run finished) also builds 2026-01-02.
# The old _6h_2000-2015 folder is left untouched (finished runs point to it).
# Never overwrites a file. The file list is rewritten atomically (tmp + mv): runs that
# read it never see a half-written list; it only grows.
#
# Usage: bash copy-nudging-data-to-inputForNudging-directory-2000-2025.sh [--run] [--final]
#   without --run: dry run (prints what would be done, changes nothing)
# Batch: sbatch build_met_2000-2025_job.sh [--final]

set -euo pipefail

CASENAME=NF2000norbc_tropstratchem_met_f19_f19_20260422
AZ=/cluster/shared/noresm/inputdata/noresm-only/inputForNudging/AZ
OLDDIR=$AZ/${CASENAME}_6h_2000-2015
NEWSRC=/cluster/work/users/$USER/archive/$CASENAME/atm/hist
NUDGDIR=$AZ/${CASENAME}_6h_2000-2025
FILELIST=$NUDGDIR/${CASENAME}.cam.h1_filelist.txt
PY=${PY:-python3}     # needs numpy + netCDF4 (user site); works on compute nodes
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export HDF5_USE_FILE_LOCKING=FALSE

RUN=0; FINAL=()
for a in "$@"; do
    case "$a" in
        --run) RUN=1 ;;
        --final) FINAL=(--final) ;;
        *) echo "Usage: $0 [--run] [--final]" >&2; exit 1 ;;
    esac
done
DRY=(--dry-run); [[ $RUN -eq 1 ]] && DRY=()
RUNFLAG=(); [[ $RUN -eq 1 ]] && RUNFLAG=(--run)

[[ -d "$OLDDIR" ]] || { echo "ERROR: missing $OLDDIR" >&2; exit 1; }
[[ -d "$NEWSRC" ]] || { echo "ERROR: missing $NEWSRC (MET extension not archived yet?)" >&2; exit 1; }
n_old=$(ls "$OLDDIR"/$CASENAME.cam.h1.20[01][0-9]-*.nc | grep -v '\.2015-01-01-00000\.nc$' | wc -l)
echo "old files (2000-01-01 ... 2014-12-31): $n_old  (expected $((15*365)))"
(( n_old == 15*365 )) || { echo "ERROR: unexpected number of old files" >&2; exit 1; }
echo "new h1 files in archive: $(ls "$NEWSRC"/$CASENAME.cam.h1.*-21600.nc 2>/dev/null | wc -l)"
echo "target: $NUDGDIR"
[[ $RUN -eq 1 ]] || echo "DRY RUN (add --run)"

[[ $RUN -eq 1 ]] && mkdir -p "$NUDGDIR"
# 1. old: everything but the patched 2015-01-01 file and the old file list
rsync -a --ignore-existing --info=stats1 "${DRY[@]}" \
    --exclude="$CASENAME.cam.h1.2015-01-01-00000.nc" --exclude='*filelist*' \
    --include="$CASENAME.cam.h1.*.nc" --exclude='*' \
    "$OLDDIR"/ "$NUDGDIR"/

# 2. new: regroup into calendar days (each day verified against its sources)
out=$($PY "$HERE/regroup_met_ext_days.py" --src "$NEWSRC" --old-dir "$OLDDIR" \
      --out-dir "$NUDGDIR" "${RUNFLAG[@]}" "${FINAL[@]}" | tee /dev/stderr)
LAST_DAY=$(grep '^LAST_DAY=' <<< "$out" | cut -d= -f2)
[[ -n "$LAST_DAY" ]] || { echo "ERROR: no complete new day" >&2; exit 1; }
[[ $RUN -eq 1 ]] || exit 0

# 3. old copies identical to their source
echo "cmp of the old files with their source..."
for f in "$NUDGDIR"/$CASENAME.cam.h1.20[01][0-9]-*-00000.nc; do
    b=$(basename "$f")
    [[ "$b" < "$CASENAME.cam.h1.2015-01-01" ]] || continue
    cmp -s "$f" "$OLDDIR/$b" || { echo "ERROR: $b differs from $OLDDIR/$b" >&2; exit 1; }
done

# 4. file list up to LAST_DAY, atomic replace
tmp="$NUDGDIR/.$(basename "$FILELIST").tmp"
ls -1 "$NUDGDIR"/$CASENAME.cam.h1.*-00000.nc | sort > "$tmp"
mv -f "$tmp" "$FILELIST"
echo "file list: $FILELIST ($(wc -l < "$FILELIST") files, last day $LAST_DAY)"

# 5. coverage, records, time continuity, 2015-01-01 record 0 = old (original) record 0
$PY "$HERE/check_nudging_dir.py" "$NUDGDIR" --start 2000-01-01 --end "$LAST_DAY" \
    --compare-rec0 "$OLDDIR/$CASENAME.cam.h1.2015-01-01-00000.nc"
echo "BUILD_OK last_day=$LAST_DAY"
