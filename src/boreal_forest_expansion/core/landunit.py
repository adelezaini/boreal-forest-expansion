######

import numpy as np
import netCDF4 as nc
import xarray as xr; xr.set_options(display_style='html', keep_attrs=True)
import pandas as pd
import os

def convert_landunit_to_gridcell(da_lndunit, lnd_frac, attrs={}):
    """Covert Data variable from being over the landunit to be renormalized over the whole gridcell.
    Args:
    - da_lndunit (DataArray): variable evaluated over the landunit
    - lnd_frac (DataArray): land fraction - fraction of land in the gridcell. Same lonxlat dimensions as da_lndunit
    - attrs (dict): dictionary gathering attributes. Needed if the previous attributes mentioned the normalization. Optional.
    """
    xr.set_options(keep_attrs=True)
    da_gridcell = da_lndunit * lnd_frac
    if attrs: da_gridcell = da_gridcell.assign_attrs(attrs)
    return da_gridcell
    
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def convert_gridcell_to_landunit(da_gridcell, lnd_frac, attrs={}):
    """Covert Data variable from being over the gridcell to be renormalized over the landunit.
    Args:
    - da_gridcell (DataArray): variable evaluated over the gridcell
    - lnd_frac (DataArray): land fraction - fraction of land in the gridcell. Same lonxlat dimensions as da_gridcell
    - attrs (dict): dictionary gathering attributes. Needed if the previous attributes mentioned the normalization. Optional.
    """
    xr.set_options(keep_attrs=True)
    da_lndunit = da_gridcell/lnd_frac
    if attrs: da_lndunit = da_lndunit.assign_attrs(attrs)
    return da_lndunit
