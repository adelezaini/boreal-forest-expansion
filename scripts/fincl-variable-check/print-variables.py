#!/usr/bin/env python3
import netCDF4
import glob
import datetime

date = datetime.datetime.now().strftime("%Y-%m-%d")

comp = 'cam' # [cam,clm2]
casename ='NF2000norbc_f19_f19_test'

# --- Function to collect variable names from a list of NetCDF files ---
def collect_vars(files):
    varnames = set()
    for nc_file in files:
        with netCDF4.Dataset(nc_file, "r") as nc:
            varnames.update(nc.variables.keys())
    return sorted(varnames)

for h in ['h0', 'h1']:
    h_file = f"/cluster/home/adelez/work/noresm/{casename}/run/{casename}.{comp}.{h}*.nc"
    h_files = glob.glob(h_file)
    if not h_files:
        print(f"No {h} files found for pattern: {h_file}")
    else:
        vars_in_h = collect_vars(h_files)
        out_file = f"{comp}_{h}_variables_{date}.txt"
        with open(out_file, "w") as f:
            for v in vars_in_h:
                 f.write(v + "\n")
        print(f"Saved {len(vars_in_h)} unique variables from {h} files to {out_file}")
