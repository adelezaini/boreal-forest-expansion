#!/bin/bash

module load NCO/5.2.9-foss-2024a

cd /cluster/shared/noresm/inputdata/atm/cam/prescribed_data/bvoc_emissions

for sp in SFISOP SFMTERP
do
    in=ems_NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20260429_2002-2011_${sp}.nc
    out=ems_NF2000norbc_tropstratchem_nudg_ctrl_f19_f19-20260429_2002-2011_on_yr2100_${sp}.nc

    cp "$in" "$out"

    ncap2 -O -s 'date=date+1000000' "$out" "$out"

    ncatted -O \
      -a units,time,o,c,"days since 2100-01-01 00:00:00" \
      -a fake_year_note,global,o,c,"Created by relabelling year 2000 climatological BVOC emissions as year 2100; emissions values unchanged." \
      "$out"

    echo "==== $out ===="
    ncdump -h "$out" | grep -E "time = UNLIMITED|time:units|time:calendar|fake_year_note"
    ncdump -v date "$out" | grep -o '[0-9]\{8\}' | cut -c1-4 | sort -u
done