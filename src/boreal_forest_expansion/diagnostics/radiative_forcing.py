
import numpy as np
import xarray as xr
from boreal_forest_expansion.datasets.datavariables_catalog import Ghan_vars

def aerosol_cloud_forcing_scomposition_Ghan(ds):
    # Author: Sara Marie Blichner
    
    """Apply Ghan's scomposition of the aerosol-cloud radiative forcing:
    https://acp.copernicus.org/articles/13/9971/2013/acp-13-9971-2013.pdf"""
    
    ds_ = ds.copy(deep=True)

    # If the dataset is provided of the exential variables to perfom the Ghan's scomposition...
    if all(elem in list(ds.data_vars) for elem in ['FLNT', 'FSNT', 'FLNT_DRF', 'FLNTCDRF', 'FSNTCDRF', 'FSNT_DRF']):
        
        for var in Ghan_vars:
            
        
            if 'SWDIR' == var:
                ds_[var] = ds_['FSNT'] - ds_['FSNT_DRF']
                ds_[var].attrs['units'] = ds_['FSNT_DRF'].attrs['units']
                ds_[var].attrs['long_name'] = "Shortwave aerosol direct radiative flux - Ghan's scomposition"

            if 'LWDIR' == var:
                ds_[var] = -(ds_['FLNT'] - ds_['FLNT_DRF'])
                ds_[var].attrs['units'] = ds_['FLNT_DRF'].attrs['units']
                ds_[var].attrs['long_name'] = "Longwave aerosol direct radiative flux - Ghan's scomposition"


            if 'DIR' == var:
                ds_[var] = ds_['LWDIR'] + ds_['SWDIR']
                ds_[var].attrs['units'] = ds_['LWDIR'].attrs['units']
                ds_[var].attrs['long_name'] = "Net aerosol direct radiative flux - Ghan's scomposition"


            if 'SWCF' == var: # this will overwrite the existing one
                ds_[var] = ds_['FSNT_DRF'] - ds_['FSNTCDRF']
                ds_[var].attrs['units'] = ds_['FSNT_DRF'].attrs['units']
                ds_[var].attrs['long_name'] = "Shortwave cloud radiative flux - Ghan's scomposition"


            if 'LWCF' == var: # this will overwrite the existing one
                ds_[var] = -(ds_['FLNT_DRF'] - ds_['FLNTCDRF'])
                ds_[var].attrs['units'] = ds_['FLNT_DRF'].attrs['units']
                ds_[var].attrs['long_name'] = "Longwave cloud radiative flux - Ghan's scomposition"


            if 'NCFT' == var:
                ds_[var] = ds_['FSNT_DRF'] - ds_['FSNTCDRF'] - (ds_['FLNT_DRF'] - ds_['FLNTCDRF'])
                ds_[var].attrs['units'] = ds_['FLNT_DRF'].attrs['units']
                ds_[var].attrs['long_name'] = "Net cloud radiative flux - Ghan's scomposition"


            if 'SW_rest' == var:
                ds_[var] = ds_['FSNTCDRF']
                ds_[var].attrs['long_name'] = "Shortwave surface change radiative flux - Ghan's scomposition"


            if 'LW_rest' == var:
                ds_[var] = -ds_['FLNTCDRF']
                ds_[var].attrs['long_name'] = "Longwave surface change radiative flux - Ghan's scomposition"#Clear sky total column longwave flux - Ghan's scomposition"
                
            if 'FREST' == var:
                ds_[var] = ds_['FSNTCDRF'] - ds_['FLNTCDRF']
                ds_[var].attrs['units'] = ds_['FSNTCDRF'].attrs['units']
                ds_[var].attrs['long_name'] = "Net surface change radiative flux - Ghan's scomposition"
                
            if 'FTOT' == var:
                ds_[var] = ds_['FSNT'] - ds_['FLNT']
                ds_[var].attrs['units'] = ds_['FLNT'].attrs['units']
                ds_[var].attrs['long_name'] = "Net radiative flux at top of the model"
                
            if 'SWTOT' == var:
                ds_[var] = ds_['FSNT']

            if 'LWTOT' == var:
                ds_[var] = -(ds_['FLNT'])
                
            #print(var, "-", ds_[var].attrs["long_name"])
                
        # Add attributes based on Ghan scomposition
        
        for var in list(ds_.keys()):
            
            if var == "FSNT":
                ds_[var].attrs["Ghan_name"] = 'SWTOT'
                ds_[var].attrs["Ghan_long_name"] = 'Shortwave total forcing at TOA'
            elif var == "FLNT":
                ds_[var].attrs["Ghan_name"] = 'LWTOT'
                ds_[var].attrs["Ghan_long_name"] = 'Longwave total forcing at TOA'
            elif var == "FSNT_DRF":
                ds_[var].attrs["Ghan_name"] = 'SW_clean'
                ds_[var].attrs["Ghan_long_name"] = 'Shortwave without direct aerosol forcing (scattering, absorbing)'
            elif var == "FSNTCDRF":
                ds_[var].attrs["Ghan_name"] = 'SW_clean_clear'
                ds_[var].attrs["Ghan_long_name"] = 'Shortwave without direct aerosol and cloud forcing'
            elif var == "FLNT_DRF":
                ds_[var].attrs["Ghan_name"] = 'LW_clean'
                ds_[var].attrs["Ghan_long_name"] = 'Longwave without direct aerosol forcing (scattering, absorbing)'
            elif var == "FLNTCDRF":
                ds_[var].attrs["Ghan_name"] = 'LW_clean_clear'
                ds_[var].attrs["Ghan_long_name"] = 'Longwave without direct aerosol and cloud forcing'
            else:
                continue
            #print(var, "->", ds_[var].attrs["Ghan_name"], "-", ds_[var].attrs["Ghan_long_name"])
            
        print("Ghan's scomposition completed")

    return ds_
