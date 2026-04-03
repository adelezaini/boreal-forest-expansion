###### This python file collects fuctions to read LPJGUESS files

####### Import packages
import numpy as np
import pandas as pd
import xarray as xr

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def dataframe_from_LPJGUESS(filename, total = False):
    """Import data as pandas dataframe from LPJGUESS .txt file,
    Columns are [Lat, Lon, [16 NAT PFTs], [7 PETLAND PFTs], Total, Natural_sum, Petland_sum]
        Args:
        - filename (string): path to txt file where data is
        - total (bool): include total amounts. These files have the last three columns as 'Total', 'Natural_sum', 'Petland_sum'.
        
        Return:
        - dataframe with indexes [Lat, Lon] and columns [16 NAT PFTs], [7 PETLAND PFTs], Total*, Natural_sum*, Petland_sum*.
        """
    if not total:
        df = pd.read_csv(filename, delim_whitespace=True, usecols=range(25))#, index_col=[0,1])
    else:
        df = pd.read_csv(filename, delim_whitespace=True)
    df.set_index(['Lat', 'Lon'], inplace=True)
    return df

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def DataArray_from_LPJGUESS(filename, total = False, colnames=True, name=None, da_attrs=xr.DataArray(None), main_attrs = None):#, peatland=False):
    """Import data as xarray DataArray from LPJGUESS .txt file,
    Columns are [Lat, Lon, [16 NAT PFTs], [7 PETLAND PFTs], Total, Natural_sum, Petland_sum]
        Args:
        - filename (string): path to txt file where data is
        - total (bool): include total amounts. These files have the last three columns as 'Total', 'Natural_sum', 'Petland_sum'.
        - colnames (bool): import 'natpft' coord as pft indexes (False) or proper pft names (True) - aka name of the columns.
        - name (string): how to name the DataArray.
        
        Return:
        - DataArray, named 'name' with coords/dims=(natpft, lat, lon).
        """
    df = dataframe_from_LPJGUESS(filename, total = total)
    if not colnames:
        pft_names = list(df.columns.values)
        df.columns = [i for i in range(len(pft_names))]
    #if not peatland:
    da = xr.DataArray(df.values, coords={'lonlat':df.index,'natpft':df.columns.values})
    #else:
        #print(df.iloc[:,0:19].columns.values)
        #da = xr.DataArray(df.values, coords={'lonlat':df.index,'natpft':df.iloc[:,0:19].columns.values, 'petpft':df.iloc[:,19:25].columns.values})
    
    da = da.unstack().rename({'Lat': 'lat', 'Lon': 'lon'}).rename(name)
    
    if da_attrs.any():
      da = da.assign_attrs(da_attrs.attrs)
      da['lat'] = da['lat'].assign_attrs(da_attrs['lat'].attrs)
      da['lon'] = da['lon'].assign_attrs(da_attrs['lon'].attrs)
      da['natpft'] = da['natpft'].assign_attrs(da_attrs['natpft'].attrs)
      # If column names is True, the units [='index'] is deleted from the attributes
      if colnames: del da['natpft'].attrs['units']
    if main_attrs: da = da.assign_attrs(main_attrs)
      
    return da

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def pftnames_LPJGUESS(filename, total = False, dict_format=False):
    """Return list of pftnames from txt file
    Columns are [Lat, Lon, [16 NAT PFTs], [7 PETLAND PFTs], Total, Natural_sum, Petland_sum]
        Args:
        - filename (string): path to txt file where data is
        - total (bool): include total amounts. These files have the last three columns as 'Total', 'Natural_sum', 'Petland_sum'.
        - dict_format (bool): return the pftnames as a dict with {pft_index: pft_name}
    """
    df = dataframe_from_LPJGUESS(filename, total=total)
    pftnames_list = list(df.columns)
    if not dict_format:
        return pftnames_list
    else:
        pftnames_dict = {}
        for i in range(len(pftnames_list)):
            pftnames_dict[i] = pftnames_list[i]
        return pftnames_dict
