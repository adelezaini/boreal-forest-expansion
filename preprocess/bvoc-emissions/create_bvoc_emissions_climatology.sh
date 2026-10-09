#!/bin/bash

module load NCO/5.2.9-foss-2024a

CASE="NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20260925"
START_YEAR=2001
END_YEAR=2009

echo -e "\nSFISOP:\n------------"
python create_bvoc_emissions_climatology_staged.py   "$CASE" "$START_YEAR" "$END_YEAR" SFISOP --calendar noleap   --stage concat
python create_bvoc_emissions_climatology_staged.py   "$CASE" "$START_YEAR" "$END_YEAR" SFISOP --calendar noleap   --stage climatology

echo -e "\nSFMTERP:\n------------"
python create_bvoc_emissions_climatology_staged.py   "$CASE" "$START_YEAR" "$END_YEAR" SFMTERP --calendar noleap   --stage concat
python create_bvoc_emissions_climatology_staged.py   "$CASE" "$START_YEAR" "$END_YEAR" SFMTERP --calendar noleap   --stage climatology
