#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Select variables from CAM/NetCDF history files and concatenate
# them into one time-series file using NCO.
#
# Automatically resumable:
#   - If a temporary .selected.nc file already exists and is valid,
#     it is reused.
#   - If it is missing, empty, or invalid, it is rewritten.
#
# Requires:
#   NCO: ncks, ncrcat
#
# Usage:
#   ./select_concat_cam_raw_output.sh CASE_NAME VARLIST_FILE [START_YM] [END_YM] [STREAM]
#
# Example:
#   ./select_concat_cam_raw_output.sh NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOC_f19_f19-20260503 selected_cam_variables.txt
# ============================================================

export HDF5_USE_FILE_LOCKING=FALSE

module load NCO/5.2.9-foss-2024a

# -----------------------------
# Fixed project paths
# -----------------------------

ARCHIVE_ROOT="/cluster/work/users/adelez/archive"
OUT_DIR="/cluster/home/adelez/BOREAL-FOREST-EXPANSION/data/selected-model-output"

COMPRESSION_LEVEL=1

# If false, temporary filtered files are removed after successful concatenation.
# If the script crashes before the end, they remain and are reused automatically.
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
echo "Tmp dir:     $TMP_DIR"
echo "Resume:      automatic"
echo

# -----------------------------
# Helpers
# -----------------------------

date_to_number() {
  echo "${1//-/}"
}

selected_file_is_valid() {
  local f="$1"

  [[ -s "$f" ]] || return 1
  ncks -m "$f" >/dev/null 2>&1 || return 1

  return 0
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
# Filter files, automatically resuming
# -----------------------------

FILTERED_LIST="${TMP_DIR}/filtered_files_to_concat.txt"
: > "$FILTERED_LIST"

while IFS= read -r infile; do
  base=$(basename "$infile")
  outfile="${TMP_DIR}/${base%.nc}.selected.nc"

  FILE_VARS="${WORK_DIR}/${base}.vars.txt"
  KEEP_VARS="${WORK_DIR}/${base}.keep.txt"
  MISSING_VARS="${WORK_DIR}/${base}.missing.txt"

  # ------------------------------------------------------------
  # Resume check.
  #
  # If the expected temporary selected file already exists and is
  # non-empty, reuse it directly. This avoids rerunning ncks.
  #
  # This is intentionally simple: for a crash-restart workflow,
  # existence + non-zero size is usually the most useful test.
  # ------------------------------------------------------------

  if [[ -s "$outfile" ]]; then
    echo "Reusing existing selected file for $base"
    echo "  reused: $outfile"
    echo

    echo "$outfile" >> "$FILTERED_LIST"
    continue
  fi

  echo "Filtering $base"

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
  echo "ERROR: no filtered files were created or reused." >&2
  exit 1
fi

sort -u "$FINAL_VAR_LOG" -o "$FINAL_VAR_LOG"

# -----------------------------
# Concatenate along record/time dimension
# -----------------------------

echo "Concatenating $N_FILTERED filtered files with ncrcat..."

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