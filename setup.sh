#!/bin/bash
set -e

module purge
module load netCDF/4.9.2-gompi-2023a

python3 -m venv .brl_frst_venv
source .brl_frst_venv/bin/activate
# BUT I have 3 environments!

python --version
python -m pip install --upgrade pip
python -m pip install .

echo "Setup complete!"
echo "Activate later with: source .brl_frst_venv/bin/activate"