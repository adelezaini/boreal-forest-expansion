#!/usr/bin/env python3
"""Print CAM/CLM h0 metadata
Knowing variable list and their metadata is useful for postprocessing

Usage: python inspect_h0_metadata.py /path/to/file.h0.nc > cam_variables_metadata_CASE.csv

"""
import csv
import sys
import xarray as xr

with xr.open_dataset(sys.argv[1], decode_times=False, mask_and_scale=False) as ds:
    attributes = list(dict.fromkeys(
        key for var in ds.data_vars.values() for key in var.attrs
    ))

    writer = csv.writer(sys.stdout)
    writer.writerow(["variable", "dtype", "dimensions", "shape", *attributes])

    for name, var in ds.data_vars.items():
        writer.writerow([
            name, str(var.dtype), ", ".join(var.dims), str(var.shape),
            *(var.attrs.get(key, "") for key in attributes)
        ])