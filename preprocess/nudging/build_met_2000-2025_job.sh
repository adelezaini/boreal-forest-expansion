#!/bin/bash
#SBATCH --job-name=met2000-2025
#SBATCH --account=nn9188k
#SBATCH --partition=preproc
#SBATCH --time=08:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=8G
#SBATCH --output=/cluster/work/users/adelez/met-ext/build_met_2000-2025_%j.log

# Batch wrapper: fill the 2000-2025 nudging folder from what the MET extension has archived.
# After segment 1 (user 2026-11-04): sbatch --dependency=afterok:<st_archive job> build_met_2000-2025_job.sh
# After the last segment:            sbatch build_met_2000-2025_job.sh --final
# ~1 s per regrouped day (2015-01-04 test), + rsync/cmp of the 104 GB old files on first run.
set -euo pipefail
cd /cluster/home/adelez/BOREAL-FOREST-EXPANSION/preprocess/nudging
bash copy-nudging-data-to-inputForNudging-directory-2000-2025.sh --run "$@"
