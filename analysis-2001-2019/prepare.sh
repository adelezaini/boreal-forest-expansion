#!/usr/bin/env bash
# Self-contained 2001-2019 set (meeting Mon 9 Nov 2026). Everything it writes stays in this folder:
#   raw-links/   symlinks to the 2000-01..2019-12 h0 files in the work archive (the runs keep writing
#                2020+ files there; the pipeline reads every h0 file in hist/, so it gets only these)
#   processed/   postprocessed files <ALIAS>_<atm|lnd>_<CAT>_2001-2019.nc (+ logs/), first 12 months dropped
#   results/     figures and tables of radiative_forcing_2001-2019.ipynb
#   logs/        this script's log
# Uses the repo code unchanged (postprocess/run_all_parallel.sh with RAW_PATH/OUT_PATH/CASES overrides).
# Usage: bash prepare.sh [NJOBS]      (rerun-safe: existing processed files are skipped)
# Delete everything afterwards: rm -rf analysis-2001-2019
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(dirname "$HERE")"
ARCHIVE=/cluster/work/users/adelez/archive
PYTHON=/nird/datapeak/NS9188K/adelez/.conda/envs/lcc-env/bin/python
NJOBS="${1:-16}"
mkdir -p "$HERE"/{raw-links,processed,results/figures,results/tables,logs}
echo "$(date '+%F %T') start on $(hostname), pid $$"

# 1. link tree: exactly 240 h0 files (2000-01..2019-12) per case and component
while read -r alias case; do
    for comp in atm lnd; do
        model=$([ $comp = atm ] && echo cam || echo clm2)
        dst="$HERE/raw-links/$case/$comp/hist"; mkdir -p "$dst"
        for y in $(seq 2000 2019); do
            for f in "$ARCHIVE/$case/$comp/hist/$case.$model.h0.$y-"[01][0-9].nc; do
                [ -e "$f" ] && ln -sfn "$f" "$dst/"
            done
        done
        n=$(ls "$dst" | wc -l)
        [ "$n" -eq 240 ] || { echo "ERROR $alias $comp: $n h0 files (need 240)"; exit 1; }
    done
done < "$HERE/cases.txt"
echo "$(date '+%F %T') links OK (11 cases x atm/lnd x 240)"

# 2. postprocess all categories (repo script, outputs redirected here)
RAW_PATH="$HERE/raw-links" OUT_PATH="$HERE/processed" CASES="$(cat "$HERE/cases.txt")" PYTHON="$PYTHON" \
    bash "$REPO/postprocess/run_all_parallel.sh" "$NJOBS"
nfiles=$(ls "$HERE"/processed/*_2001-2019.nc | wc -l)
echo "$(date '+%F %T') processed files: $nfiles (expected 11 x 19 = 209, fewer if a category does not exist)"

# 3. run the notebook in place (outputs saved in the .ipynb)
"$PYTHON" "$REPO/results/tables/logs/run_nb_inplace.py" "$HERE/radiative_forcing_2001-2019.ipynb" --timeout 7200
echo "$(date '+%F %T') DONE"
