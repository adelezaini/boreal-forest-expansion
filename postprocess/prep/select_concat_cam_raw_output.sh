#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Select variables from CAM/NetCDF history files and concatenate
# them into one time-series file using NCO.
#
# What this script does:
#   1. Takes the CAM case name as an external argument.
#   2. Reads a variable keep-list from a txt file.
#   3. Finds CAM history files for the selected case and stream.
#   4. Restricts files to a YYYY-MM date range.
#   5. For each file, keeps only variables that are both:
#        - requested in the keep-list
#        - actually present in that file
#   6. Writes temporary filtered files.
#   7. Concatenates them with ncrcat.
#   8. Writes simple logs for reproducibility.
#
# Requires:
#   NCO: ncks, ncrcat
#
# Usage:
#   ./select_concat_cam_raw_output.sh CASE_NAME VARLIST_FILE [START_YM] [END_YM] [STREAM]
#
# Example:
#   ./select_concat_cam_raw_output.sh \
#     NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20260429 \
#     aggregated_keep_variables_present_only_ncks_with_depletion.txt
#
# Optional arguments:
#   START_YM defaults to 2000-01
#   END_YM   defaults to 2009-12
#   STREAM   defaults to h0
# ============================================================

# -----------------------------
# Fixed project paths
# -----------------------------

ARCHIVE_ROOT="/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive"
OUT_DIR="/cluster/home/adelez/BOREAL-FOREST-EXPANSION/data/selected-model-output"

# Compression level. 1 is light and usually a good compromise.
# Increase to 2-4 if you need smaller files and can accept slower processing.
COMPRESSION_LEVEL=1

# Set to true if you want to keep temporary filtered monthly files after concatenation.
KEEP_TMP=false

# -----------------------------
# Inputs
# -----------------------------

if [[ $# -lt 2 || $# -gt 5 ]]; then
  echo "Usage: $0 CASE_NAME VARLIST_FILE [START_YM] [END_YM] [STREAM]" >&2
  echo >&2
  echo "Example:" >&2
  echo "  $0 NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20260429 keep_variables_list.txt" >&2
  exit 1
fi

CASE_NAME="$1"
VARLIST_FILE="$2"
START_YM="${3:-2000-01}"
END_YM="${4:-2009-12}"
STREAM="${5:-h0}"

IN_DIR="${ARCHIVE_ROOT}/${CASE_NAME}/atm/hist"
FILE_GLOB="${CASE_NAME}.cam.${STREAM}.*.nc"

OUT_FILE="${OUT_DIR}/${CASE_NAME}.cam.${STREAM}.${START_YM}_${END_YM}.nc"
TMP_DIR="${OUT_DIR}/tmp_selected_${CASE_NAME}_${STREAM}_${START_YM}_${END_YM}"

# Logs
LOG_DIR="${OUT_DIR}/logs/${CASE_NAME}"
mkdir -p "$LOG_DIR"

FILE_LIST="${LOG_DIR}/${CASE_NAME}.cam.${STREAM}.files_used_${START_YM}_${END_YM}.txt"
USED_LOG="${LOG_DIR}/${CASE_NAME}.cam.${STREAM}.variables_used_by_file_${START_YM}_${END_YM}.log"
MISSING_LOG="${LOG_DIR}/${CASE_NAME}.cam.${STREAM}.variables_missing_by_file_${START_YM}_${END_YM}.log"
FINAL_VAR_LOG="${LOG_DIR}/${CASE_NAME}.cam.${STREAM}.variables_in_final_selection_${START_YM}_${END_YM}.txt"

# -----------------------------
# Checks
# -----------------------------

if [[ ! -f "$VARLIST_FILE" ]]; then
  echo "ERROR: variable list not found: $VARLIST_FILE" >&2
  exit 1
fi

if [[ ! -d "$IN_DIR" ]]; then
  echo "ERROR: input directory not found: $IN_DIR" >&2
  exit 1
fi

if ! command -v ncks >/dev/null 2>&1; then
  echo "ERROR: ncks not found. Load NCO first, for example: module load NCO" >&2
  exit 1
fi

if ! command -v ncrcat >/dev/null 2>&1; then
  echo "ERROR: ncrcat not found. Load NCO first, for example: module load NCO" >&2
  exit 1
fi

mkdir -p "$OUT_DIR" "$TMP_DIR"

: > "$FILE_LIST"
: > "$USED_LOG"
: > "$MISSING_LOG"
: > "$FINAL_VAR_LOG"

# -----------------------------
# Normalize keep-list
# -----------------------------
# Accepts one variable per line, comma-separated, whitespace-separated,
# and quoted lists such as 'VAR1','VAR2'.

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

MASTER_VARS="${WORK_DIR}/master_vars.txt"

tr ',[:space:]' '\n' < "$VARLIST_FILE" \
  | sed "s/[\"']//g" \
  | sed '/^$/d' \
  | sort -u > "$MASTER_VARS"

N_MASTER=$(wc -l < "$MASTER_VARS" | tr -d ' ')

if [[ "$N_MASTER" -eq 0 ]]; then
  echo "ERROR: no variables found in keep-list: $VARLIST_FILE" >&2
  exit 1
fi

echo "Case:        $CASE_NAME"
echo "Stream:      $STREAM"
echo "Period:      $START_YM to $END_YM"
echo "Input:       ${IN_DIR}/${FILE_GLOB}"
echo "Varlist:     $VARLIST_FILE ($N_MASTER requested variables)"
echo "Output:      $OUT_FILE"
echo

# -----------------------------
# Helper for YYYY-MM comparison
# -----------------------------

date_to_number() {
  echo "${1//-/}"
}

# -----------------------------
# Find files in date range
# -----------------------------

shopt -s nullglob
ALL_FILES=("$IN_DIR"/$FILE_GLOB)

if [[ ${#ALL_FILES[@]} -eq 0 ]]; then
  echo "ERROR: no files found matching: ${IN_DIR}/${FILE_GLOB}" >&2
  exit 1
fi

START_NUM=$(date_to_number "$START_YM")
END_NUM=$(date_to_number "$END_YM")

SELECTED_FILES=()

for f in "${ALL_FILES[@]}"; do
  base=$(basename "$f")

  # Extract first date in the filename, e.g. 2000-01 from:
  # case.cam.h0.2000-01.nc
  # case.cam.h0.2000-01-01-00000.nc
  ym=$(echo "$base" | grep -oE '[0-9]{4}-[0-9]{2}' | head -n 1 || true)

  if [[ -z "$ym" ]]; then
    continue
  fi

  ym_num=$(date_to_number "$ym")

  if [[ "$ym_num" -ge "$START_NUM" && "$ym_num" -le "$END_NUM" ]]; then
    SELECTED_FILES+=("$f")
  fi
done

if [[ ${#SELECTED_FILES[@]} -eq 0 ]]; then
  echo "ERROR: no files found between ${START_YM} and ${END_YM}" >&2
  exit 1
fi

printf '%s\n' "${SELECTED_FILES[@]}" | sort > "$FILE_LIST"
N_FILES=$(wc -l < "$FILE_LIST" | tr -d ' ')

echo "Found $N_FILES files in the selected period."
echo "File list: $FILE_LIST"
echo

# -----------------------------
# Filter files
# -----------------------------

FILTERED_LIST="${TMP_DIR}/filtered_files_to_concat.txt"
: > "$FILTERED_LIST"

while IFS= read -r infile; do
  base=$(basename "$infile")
  outfile="${TMP_DIR}/${base%.nc}.selected.nc"

  FILE_VARS="${WORK_DIR}/${base}.vars.txt"
  KEEP_VARS="${WORK_DIR}/${base}.keep.txt"
  MISSING_VARS="${WORK_DIR}/${base}.missing.txt"

  echo "Filtering $base"

  # Extract variable names from file metadata.
  # This avoids failure when a requested variable is missing from a file.
  ncks -m "$infile" \
    | awk '/^[[:space:]]*(byte|char|short|int|int64|float|double|ubyte|ushort|uint|uint64|string)[[:space:]]+[A-Za-z_][A-Za-z0-9_]*[[:space:]]*\(/ {gsub(/\(.*/,"",$2); print $2}' \
    | sort -u > "$FILE_VARS"

  comm -12 "$MASTER_VARS" "$FILE_VARS" > "$KEEP_VARS"
  comm -23 "$MASTER_VARS" "$FILE_VARS" > "$MISSING_VARS"

  N_KEEP=$(wc -l < "$KEEP_VARS" | tr -d ' ')
  N_MISSING=$(wc -l < "$MISSING_VARS" | tr -d ' ')

  if [[ "$N_KEEP" -eq 0 ]]; then
    echo "  WARNING: no requested variables found; skipping."
    {
      echo "============================================================"
      echo "$base"
      echo "No requested variables found."
    } >> "$MISSING_LOG"
    continue
  fi

  VARS_CSV=$(paste -sd, "$KEEP_VARS")

  {
    echo "============================================================"
    echo "$base"
    echo "Variables kept: $N_KEEP"
    cat "$KEEP_VARS"
    echo
  } >> "$USED_LOG"

  {
    echo "============================================================"
    echo "$base"
    echo "Variables requested but absent in this file: $N_MISSING"
    cat "$MISSING_VARS"
    echo
  } >> "$MISSING_LOG"

  # Main selection command.
  # Do NOT use -C: without -C, NCO keeps associated coordinate variables
  # such as time, lat, lon, lev, ilev, hyam, hybm, and P0 when needed.
  ncks -O -L "$COMPRESSION_LEVEL" -v "$VARS_CSV" "$infile" "$outfile"

  echo "$outfile" >> "$FILTERED_LIST"
  cat "$KEEP_VARS" >> "$FINAL_VAR_LOG"

  echo "  kept:   $N_KEEP variables"
  echo "  absent: $N_MISSING requested variables"
  echo "  wrote:  $outfile"
  echo

done < "$FILE_LIST"

N_FILTERED=$(wc -l < "$FILTERED_LIST" | tr -d ' ')

if [[ "$N_FILTERED" -eq 0 ]]; then
  echo "ERROR: no filtered files were created." >&2
  exit 1
fi

sort -u "$FINAL_VAR_LOG" -o "$FINAL_VAR_LOG"

# -----------------------------
# Concatenate along record/time dimension
# -----------------------------

echo "Concatenating $N_FILTERED filtered files with ncrcat..."

# xargs avoids problems with very long command lines.
xargs ncrcat -O -L "$COMPRESSION_LEVEL" -o "$OUT_FILE" < "$FILTERED_LIST"

echo
echo "Done."
echo "Final file:        $OUT_FILE"
echo "Files used:        $FILE_LIST"
echo "Variables kept:    $FINAL_VAR_LOG"
echo "Per-file used log: $USED_LOG"
echo "Per-file missing:  $MISSING_LOG"
echo

if [[ "$KEEP_TMP" == "true" ]]; then
  echo "Temporary filtered files kept in: $TMP_DIR"
else
  echo "Removing temporary filtered files: $TMP_DIR"
  rm -rf "$TMP_DIR"
fi
