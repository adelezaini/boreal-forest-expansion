###### This python file collects fuctions to manipulate Xarray Dataset/DataArray

# Import packages
import numpy as np
import netCDF4 as nc
import xarray as xr; xr.set_options(display_style='html', keep_attrs=True)
import pandas as pd
import os

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
# Miscellaneous
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def check_da_equal(da1, da2):
    p = da1-da2
    check = p.where(p!=0.,drop=True).squeeze()
    if not len(check.values): print("The DataArrays are equal")
    else: print("The DataArrays are different. Check NaN values")
  
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
# Operations over coordinates
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def convert360_180(ds):
    """Convert the longitude of the given xr:Dataset from [0-360] to [-180-180] deg"""
    _ds = ds.copy()
    if np.min(_ds['lon'].values) >= 0: # check if already
        attrs = _ds['lon'].attrs
        _ds.coords['lon'] = (_ds.coords['lon'] + 180) % 360 - 180
        _ds = _ds.sortby(_ds.lon)
        _ds['lon'].attrs = attrs
        _ds.lon.attrs['valid_max'] = 180.0
        _ds.lon.attrs['valid_min'] = -180.0
    return _ds
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def convert180_360(ds):
    """Convert the longitude of the given xr:Dataset from [-180-180] to [0-360] deg"""
    _ds = ds.copy()
    if np.min(_ds['lon'].values) <= 0: # check if already
        attrs = _ds['lon'].attrs
        _ds.coords['lon'] = _ds.coords['lon'] % 360
        _ds = _ds.sortby(_ds.lon)
        _ds['lon'].attrs = attrs
        _ds.lon.attrs['valid_max'] = 0.0
        _ds.lon.attrs['valid_min'] = 360.0
    return _ds
    
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def convert_lsmcoord(ds):
    """ When default coordinate are in Land Surface coord.
    Convert them in lon-lat. """
    
    _ds = ds.copy()
    #Set the longitude and latitude
    _ds['lsmlat'] = _ds['LATIXY'].isel(lsmlon=0) #or dset_in['lsmlat'] = dset_in['lat']
    _ds['lsmlon'] = _ds['LONGXY'].isel(lsmlat=0)
    #Rename coord
    _ds = _ds.rename({'lsmlat':'lat','lsmlon':'lon'})
    return _ds
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def convert_to_lsmcoord(ds):
    """ Convert lon-lat into Land Surface Model coordinates. """
    print("Allert convert_to_lsmcoord! Changing from coord to dim means loosing information and changing from values to indexes")
    _ds = ds.copy()
    _ds = _ds.rename({'lat':'lsmlat','lon':'lsmlon'})
    #From coordinate to dimensions (as original)
    _ds = _ds.drop_vars('lsmlat').drop_vars('lsmlon')

    return _ds
    
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
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
    
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def match_coord(original_coord_da, coord_to_match_da, method='linear'):
    """Return DataArray with matching coordinates (lon/lat) with another given DataArray.
    The method used is the interp() of xarray. Different options of interpolation are available.
    Args:
    - original_coord_da (DataArray): variable with coordinates to be matched
    - coord_to_match_da (DataArray): variable with coordinates to match
    - method ({"linear", "nearest", "zero", "slinear", "quadratic", "cubic", "polynomial"},
    default: "linear"): the method used to interpolate.
    """
    new_da = original_coord_da.copy()
    new_da = new_da.interp(lat=coord_to_match_da['lat'], method = method)
    new_da = new_da.interp(lon=coord_to_match_da['lon'], method = method)
    return new_da
    
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
  
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def filter_lonlat(df, lonlat):
    """Filter lon-lat pair in df with the list in lonlat
    Args:
    - df (Pandas dataframe): dataframe to filter with first columns longitude and latitude
    - lonlat (Pandas dataframe): dataframe with the longitude and latitude for filtering
    Return:
    - Filtered Pandas dataframe
    """
    
    dflonlat = df.iloc[:,[0,1]]
    
    new_coords = pd.MultiIndex.from_frame(lonlat)
    existing_coords = pd.MultiIndex.from_frame(dflonlat)
    filter_coord = existing_coords.isin(new_coords)
    
    df_new=df.copy()
    df_new.iloc[:,0] = df_new.iloc[:,0][filter_coord]
    return df_new.dropna()


