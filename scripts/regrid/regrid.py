###### This python file collects fuctions to modify PFT configuration, such as in surfdata_map file

####### Import packages
import numpy as np
import xarray as xr; xr.set_options(display_style='html')
import xesmf as xe

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def regrid(dset_in, dset_target, method='bilinear', mask=True):
    """ Regrid using xesmf Regrider with a mask, based on https://pavics-sdi.readthedocs.io/en/latest/notebooks/regridding.html#Third-example-:-Regridding-and-masks
    Args:
    - dset_in (Dataset/DataArray): dataset to be regrided
    - dset_target (Dataset/DataArray): dataset with the target grid
    - method (string): interpolation method. Default: 'bilinear'. See https://xesmf.readthedocs.io/en/latest/notebooks/Compare_algorithms.html and https://earthsystemmodeling.org/regrid/#regridding-methods
    - mask (bool): mask to regrid to coarser. Default: True.
    """
    # Check if they are DataArray convert to Dataset
    if type(dset_in) == xr.DataArray: ds_in = dset_in.to_dataset()
    else: ds_in = dset_in.copy()
        
    if type(dset_target) == xr.DataArray: ds_tgt = dset_target.to_dataset()
    else: ds_tgt = dset_target.copy()
        
    if mask:
        in_mask = ds_in[list(ds_in.data_vars)[0]].isel(natpft=0).notnull()
        ds_in = ds_in.assign(mask=in_mask)

        tgt_mask = ds_tgt[list(ds_tgt.data_vars)[0]].isel(natpft=0).notnull()
        ds_tgt = ds_tgt.assign(mask=tgt_mask)

    regridder = xe.Regridder(ds_in, ds_tgt, method)
    ds_out = regridder(ds_in, keep_attrs=True)
    
    if type(dset_in) == xr.DataArray: ds_out = ds_out[list(ds_out.data_vars)[0]]
    
    return ds_out
