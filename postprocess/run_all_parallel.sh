#!/usr/bin/env bash
# Parallel version of run_all_postprocessing.sh: one process per (case, component, category),
# NJOBS at a time. Categories whose output already exists are skipped.
# Logs: $OUT_PATH/logs/<alias>_<component>_<category>.log
# Usage: [RAW_PATH=...] [CASES="ALIAS CASENAME..."] bash run_all_parallel.sh [NJOBS]
cd "$(dirname "$0")"

PYTHON="${PYTHON:-/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python}"
RAW_PATH="${RAW_PATH:-/cluster/work/users/adelez/archive}"   # work archive: postprocess as soon as a run is done (user 2026-10-28); NIRD copy = ~/BRL-FRST-XPSN_archive
OUT_PATH="/cluster/home/adelez/BOREAL-FOREST-EXPANSION/data/processed-data/postprocessing"
SPINUP_MONTHS=12
NJOBS="${1:-24}"
LOG_DIR="$OUT_PATH/logs"
mkdir -p "$LOG_DIR"

# One process reads with one thread (HDF5 serialises reads anyway); parallelism is across processes.
export DASK_SCHEDULER=synchronous OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1

# Aliases: <VEG>_<PERIOD>[_fBVOC<source run>[_IM]], e.g. LCC_FUT_fBVOCctrlPD = emissions from CTRL_PD;
# All fBVOC runs prescribe all 19 MEGAN species (the ISOP+MTERP-only _IM runs are dropped, 2026-10-28).
# Current set (2026-10-28): 2000-2014 runs of the all-species fBVOC setup, before the CO2 fix (CTRL -20261023, LCC -20261005, fBVOC -20261025).
# Raw files are read from the work archive by default (purged after 42 days); RAW_PATH=~/BRL-FRST-XPSN_archive reads the NIRD copy.
# Case names: keep up to date (CLAUDE.md "When a run version changes"; move old processed files first).
CASES="${CASES:-CTRL_PD NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20261023
LCC_PD NF2000norbc_tropstratchem_nudg_lcc_f19_f19-20261005
CTRL_FUT NF2100ssp585norbc_tropstratchem_nudg_ctrl_f19_f19-20261023
LCC_FUT NF2100ssp585norbc_tropstratchem_nudg_lcc_f19_f19-20261005
LCC_PD_fBVOCctrlPD NF2000norbc_tropstratchem_nudg_lcc_fBVOCctrlPD_f19_f19-20261025
LCC_FUT_fBVOCctrlPD NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOCctrlPD_f19_f19-20261025
LCC_FUT_fBVOCctrlFUT NF2100ssp585norbc_tropstratchem_nudg_lcc_fBVOCctrlFUT_f19_f19-20261025}"

# Largest categories first, so the slowest jobs do not start last.
ATM_CATS="AERSIZE SOA METEO CHEM CLOUDPROP BVOCOX SULFATE BVOC AEROPT RADIATIVE"
LND_CATS="BVOC LAND ENERGY BIOGEOCHEM SNOW SURFEXCH ET QA HYDRO"

jobs_list() {
    for cat in $ATM_CATS; do
        while read -r alias casename; do echo "$alias $casename atm $cat"; done <<< "$CASES"
    done
    for cat in $LND_CATS; do
        while read -r alias casename; do echo "$alias $casename lnd $cat"; done <<< "$CASES"
    done
}

run_one() {
    alias=$1 casename=$2 component=$3 cat=$4
    if ls "$OUT_PATH/${alias}_${component}_${cat}_"*.nc >/dev/null 2>&1; then return 0; fi
    log="$LOG_DIR/${alias}_${component}_${cat}.log"
    start=$(date +%s)
    if "$PYTHON" run_postprocess.py "$casename" "$alias" "$component" --categories "$cat" \
        --raw-path "$RAW_PATH" --out-path "$OUT_PATH" --spinup-months "$SPINUP_MONTHS" \
        --skip-existing > "$log" 2>&1; then
        echo "OK     $alias $component $cat ($(( $(date +%s) - start )) s)"
    else
        echo "FAILED $alias $component $cat ($(( $(date +%s) - start )) s) -> $log"
    fi
}
export -f run_one
export PYTHON RAW_PATH OUT_PATH SPINUP_MONTHS LOG_DIR

jobs_list | xargs -P "$NJOBS" -L 1 bash -c 'run_one "$@"' _
echo "All done."
