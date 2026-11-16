#!/bin/bash
#SBATCH --job-name=met2000-2040
#SBATCH --account=nn9188k
#SBATCH --partition=preproc
#SBATCH --time=08:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=8G
#SBATCH --output=/cluster/work/users/adelez/met-nudg-2040/build_met_2000-2040_%j.log

# Batch wrapper of build_met_folder.sh (2026-2040 days into ..._6h_2000-2040), submitted by
# cases-scripts/run_when_done/met_nudg_2026-2040_when_done.sh after each archived MET segment
# (--final after the last one). ~1 s per regrouped day + ~10 min for the folder check.
set -euo pipefail
cd /cluster/home/adelez/BOREAL-FOREST-EXPANSION/preprocess/nudging
bash build_met_folder.sh --run "$@"
