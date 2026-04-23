######

import numpy as np
import netCDF4 as nc
import xarray as xr; xr.set_options(display_style='html', keep_attrs=True)
import pandas as pd
import os

def check_da_equal(da1, da2):
    p = da1-da2
    check = p.where(p!=0.,drop=True).squeeze()
    if not len(check.values): print("The DataArrays are equal")
    else: print("The DataArrays are different. Check NaN values")
    
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def xr_prod_along_dim(ds, weights, dim):
    """
    Product along a specific dimension. Particularly suitable for weighting
    Edited code from https://www.reddit.com/r/learnpython/comments/g45f2u/multiplying_xarray_dataarrays/
    """
    
    assert ds[dim].size == weights[dim].size

    old_order = ds.dims
    new_order = tuple(list(set(old_order) - set([dim])) + [dim])

    ds_t = ds.transpose(*new_order)
    ds_weighted = ds_t * weights
    ds_weighted = ds_weighted.transpose(*old_order)

    return ds_weighted
