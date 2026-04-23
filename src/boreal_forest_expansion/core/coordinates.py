######

import numpy as np
import netCDF4 as nc
import xarray as xr; xr.set_options(display_style='html', keep_attrs=True)
import pandas as pd
import os

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
    print("Alert convert_to_lsmcoord! Changing from coord to dim means loosing information and changing from values to indexes")
    _ds = ds.copy()
    _ds = _ds.rename({'lat':'lsmlat','lon':'lsmlon'})
    #From coordinate to dimensions (as original)
    _ds = _ds.drop_vars('lsmlat').drop_vars('lsmlon')

    return _ds
    
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
