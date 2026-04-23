
import numpy as np
import xarray as xr
import glob #return all file paths that match a specific pattern

import numpy as np
import xarray as xr

from boreal_forest_expansion.datasets.datavariables_catalog import atm_always_include, lnd_always_include,pressure_variables,variables_by_component,Ghan_vars

def save_postprocessed(ds, component, processed_path, casealias, pressure_vars=True):
    """Save the postprocessed dataset by variable (ex: IDEAL-ON_BVOC_20082012.nc) """
    
    date = str(ds.time.dt.year.values[0])+str(ds.time.dt.year.values[-1])
    categories = list(variables_by_component(component).keys()) 
    #['LAND', 'BIOGEOCHEM', 'ET'] or ['BVOC', 'SOA', 'CLOUDPROP', 'RADIATIVE', 'TURBFLUXES']
    
    for cat in categories:
    
        bvoc = True # variable for adding bvoc variables in the land component, useless in atm
        if component == 'atm':
            variables = atm_always_include
            if pressure_vars: variables = variables + pressure_variables
           
        elif component == 'lnd':
            variables = lnd_always_include
            if casealias.find('OFF')>0.: bvoc = False # deactivate bvoc variables in simulation with bvoc controlled (tagged with '*-OFF')
             
        variables = variables + variables_by_component(component, bvoc)[cat]
        if cat == 'RADIATIVE': variables = variables + Ghan_vars
        file_out = casealias+'_'+cat+'_'+date+'.nc'
        ds[variables].to_netcdf(processed_path+file_out)
        print(file_out)
        
    print("\nSaving completed")
    
