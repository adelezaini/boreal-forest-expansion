
import xarray as xr
import numpy as np
import pandas as pd
import glob
import os

from boreal_forest_expansion.core import open_mfdataset_selected, add_derived_cam_fields

path_to_archive = "/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive/NF2000norbc_tropstratchem_spinup_f19_f19/atm/hist/"
CAM_GLOB = path_to_archive + "NF2000norbc_tropstratchem_spinup_f19_f19.cam.h0.*.nc"
CAM_VARS = ["RESTOM","TREFHT","PRECT","FSNT","FLNT","PSL","CLDTOT"]

# For debugging: check if the path exists
print("path exists:", os.path.exists(path_to_archive))

cam_ds = open_mfdataset_selected(CAM_GLOB, CAM_VARS)
cam_ds = add_derived_cam_fields(cam_ds)

cam_ds["time"].encoding["units"] = "days since 0001-01-01"
cam_ds["time"].encoding["calendar"] = "noleap"  # or "gregorian", depending on data

cam_ds.to_netcdf("/nird/datapeak/NS9188K/adelez/BRL-FRST-XPSN_archive/cam_spinup_dataset.nc")