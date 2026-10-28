#!/bin/bash

module load NCO/5.2.9-foss-2024a

CASE="NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20260925"
# Moved on NIRD 2026-10-28 (pre-all-BVOC runs)
ARCHIVE="/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive/c-before-all-bvoc"
START_YEAR=2001
END_YEAR=2009

echo -e "\nSFISOP:\n------------"
python create_bvoc_emissions_climatology_staged.py   "$CASE" "$START_YEAR" "$END_YEAR" SFISOP --calendar noleap --path "$ARCHIVE" --stage concat
python create_bvoc_emissions_climatology_staged.py   "$CASE" "$START_YEAR" "$END_YEAR" SFISOP --calendar noleap --path "$ARCHIVE" --stage climatology

echo -e "\nSFMTERP:\n------------"
python create_bvoc_emissions_climatology_staged.py   "$CASE" "$START_YEAR" "$END_YEAR" SFMTERP --calendar noleap --path "$ARCHIVE" --stage concat
python create_bvoc_emissions_climatology_staged.py   "$CASE" "$START_YEAR" "$END_YEAR" SFMTERP --calendar noleap --path "$ARCHIVE" --stage climatology
