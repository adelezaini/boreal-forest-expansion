#!/bin/bash
#SBATCH --job-name=create_cam_spinup_dataset
#SBATCH --account=nn9188k
#SBATCH --qos=preproc
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=8G
#SBATCH --output=create_cam_spinup_dataset.log_%j.txt

set -e

source ~/pyenv/bin/activate
pip install -e ~/BOREAL-FOREST-EXPANSION/

python create_cam_spinup_dataset.py