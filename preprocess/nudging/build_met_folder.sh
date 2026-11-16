#!/bin/bash

# Add the MET continuation 2026-2040 to the ONE nudging folder ..._6h_2000-2040 (user 2026-11-15).
# Record: docs/met-nudg-2026-2040.md. Successor of copy-nudging-data-to-inputForNudging-directory-2000-2025.sh
# (kept as the record of the 2015-2025 build).
#
# Folder layout since 2026-11-15:
#   ..._6h_2000-2040/            the real folder (renamed from ..._6h_2000-2025, by hand, 15 Nov 18:37)
#   ..._6h_2000-2025 -> ..._6h_2000-2040   symlink: cases and restarts written before the rename store
#                                this path; the symlink must stay
#   <MET>.cam.h1_filelist.txt    FROZEN old list (old folder name, 2000-01-01 ... 2026-01-02): never rewritten
#   <MET>.cam.h1_filelist_2000-2040.txt   NEW list (new folder name), rewritten atomically by this script;
#                                the 12 runs read it after their phase-A switch (switch_case_to_met_list)
#   superseded/                  the old one-record 2026-01-02 file (MET stopped at 2026-01-02 00 h);
#                                the full day replaces it (same record 0, checked)
#
# What it does:
#   1. regroups each new calendar day (00/06/12/18 h) from the MET continuation's h1 files in the
#      work archive (regroup_met_ext_days.py --first 2026-01-02 --last 2041-01-02: record 0 = last
#      record of the previous day's file, records 1-3 = records 0-2 of the day's file; every record
#      verified bit-identical to its source). Days whose sources are not archived yet are left for the
#      next call; existing days are skipped; --final (MET finished) also builds 2041-01-02 (record 0).
#   2. writes the new list (every day file of the folder, date order), tmp + mv;
#   3. checks: check_nudging_dir.py on the new list (continuous days, 4 records, 0.25-d steps),
#      every path of the frozen list exists, record 0 of the new 2026-01-02 = the superseded file's.
# Never overwrites a day file. Logs BUILD_OK last_day=YYYY-MM-DD.
#
# Usage: bash build_met_folder.sh [--run] [--final]      (without --run: dry run, changes nothing)
# Batch: sbatch build_met_2000-2040_job.sh [--final]

set -euo pipefail

MET=NF2000norbc_tropstratchem_met_f19_f19_20260422
AZ=/cluster/shared/noresm/inputdata/noresm-only/inputForNudging/AZ
FOLDER=$AZ/${MET}_6h_2000-2040
OLDNAME=$AZ/${MET}_6h_2000-2025                     # symlink to FOLDER
OLDLIST=$FOLDER/$MET.cam.h1_filelist.txt            # frozen
NEWLIST=$FOLDER/$MET.cam.h1_filelist_2000-2040.txt
SRC=/cluster/work/users/$USER/archive/$MET/atm/hist
FIRST=2026-01-02
LAST=2041-01-02
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
RUNFLAG=(); [[ $RUN -eq 1 ]] && RUNFLAG=(--run)

[[ -d "$FOLDER" && ! -L "$FOLDER" ]] || { echo "ERROR: $FOLDER is not a real folder" >&2; exit 1; }
[[ -L "$OLDNAME" && "$(readlink -f "$OLDNAME")" == "$FOLDER" ]] || { echo "ERROR: $OLDNAME is not a symlink to $FOLDER" >&2; exit 1; }
[[ -f "$OLDLIST" ]] || { echo "ERROR: missing frozen list $OLDLIST" >&2; exit 1; }
[[ -d "$SRC" ]] || { echo "ERROR: missing $SRC" >&2; exit 1; }
echo "folder: $FOLDER"
echo "MET continuation h1 files in archive from 2026: $(ls "$SRC"/$MET.cam.h1.20[2-4][0-9]-*-21600.nc 2>/dev/null | awk -F'h1.' '$2 >= "2026-01-01"' | wc -l)"
[[ $RUN -eq 1 ]] || echo "DRY RUN (add --run)"

# 0. the one-record 2026-01-02 -> superseded/, once its full day can be built (source 2026-01-02-21600)
D0="$FOLDER/$MET.cam.h1.$FIRST-00000.nc"
SUP="$FOLDER/superseded/$MET.cam.h1.$FIRST-00000.nc"
if [[ -f "$D0" && ! -f "$SUP" && -f "$SRC/$MET.cam.h1.$FIRST-21600.nc" ]]; then
    nrec=$($PY -c "import netCDF4,sys; print(netCDF4.Dataset(sys.argv[1]).dimensions['time'].size)" "$D0")
    [[ "$nrec" == 1 ]] || { echo "ERROR: $D0 has $nrec records, expected the old 1-record file" >&2; exit 1; }
    if [[ $RUN -eq 1 ]]; then
        mkdir -p "$FOLDER/superseded"
        mv -n "$D0" "$SUP"
        echo "moved the 1-record $FIRST file to superseded/"
    else
        echo "would move the 1-record $FIRST file to superseded/"
    fi
fi

# 1. regroup the new days
out=$($PY "$HERE/regroup_met_ext_days.py" --src "$SRC" --first "$FIRST" --last "$LAST" \
      --out-dir "$FOLDER" "${RUNFLAG[@]}" "${FINAL[@]}" | tee /dev/stderr)
LAST_DAY=$(grep '^LAST_DAY=' <<< "$out" | cut -d= -f2)
[[ -n "$LAST_DAY" ]] || { echo "ERROR: no complete new day" >&2; exit 1; }
[[ $RUN -eq 1 ]] || exit 0
[[ -f "$D0" ]] || { echo "ERROR: $D0 missing after the regroup" >&2; exit 1; }

# 2. new list, atomic replace (only grows)
tmp="$FOLDER/.$(basename "$NEWLIST").tmp"
ls -1 "$FOLDER"/$MET.cam.h1.*-00000.nc | sort > "$tmp"
if [[ -f "$NEWLIST" ]]; then
    head -n "$(wc -l < "$NEWLIST")" "$tmp" | cmp -s - "$NEWLIST" || { echo "ERROR: new list would not extend the existing one" >&2; rm -f "$tmp"; exit 1; }
fi
mv -f "$tmp" "$NEWLIST"
echo "new list: $NEWLIST ($(wc -l < "$NEWLIST") files, last day $LAST_DAY)"

# 3. checks
$PY "$HERE/check_nudging_dir.py" "$FOLDER" --start 2000-01-01 --end "$LAST_DAY" --filelist "$NEWLIST"
n=0; while read -r f; do [[ -f "$f" ]] || { echo "frozen list: MISSING $f"; n=$((n+1)); }; done < "$OLDLIST"
(( n == 0 )) || { echo "ERROR: $n paths of the frozen list do not exist" >&2; exit 1; }
echo "frozen list: all $(wc -l < "$OLDLIST") paths exist"
if [[ -f "$SUP" ]]; then
    $PY - "$D0" "$SUP" <<'EOF'
import sys, netCDF4, numpy as np
n, o = netCDF4.Dataset(sys.argv[1]), netCDF4.Dataset(sys.argv[2])
bad = [v for v in ["time", "date", "datesec", "PS", "U", "V", "T", "Q"] if not np.array_equal(n[v][0], o[v][0])]
print("record 0 of the new 2026-01-02 =", "superseded file: OK" if not bad else f"DIFFERS in {bad}")
sys.exit(1 if bad else 0)
EOF
fi
echo "BUILD_OK last_day=$LAST_DAY"
