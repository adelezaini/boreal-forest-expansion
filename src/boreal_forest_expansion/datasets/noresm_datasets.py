
import sys
import numpy as np
import xarray as xr
import glob #return all file paths that match a specific pattern

from boreal_forest_expansion.datasets.datavariables_catalog import atm_always_include, lnd_always_include,pressure_variables,variables_by_component


def fix_cam_time(ds, timetype = 'datetime64'):
    # Inspired by Marte Sofie Buraas / Ada Gjermundsen
    # Adampted for cam and clm output and to have time in DatetimeNoLeap or in 'datetime64' types (default)
    
    """ NorESM raw h0 files has incorrect time variable output,
    thus it is necessary to use time boundaries to get the correct time
    If the time variable is not corrected, none of the functions involving time
    e.g. yearly_avg, seasonal_avg etc. will provide correct information
    Source: https://noresm-docs.readthedocs.io/en/latest/faq/postp_plotting_faq.html
    
    Parameters
    ----------
    ds : xarray.DaraSet
    type: string, type of ds.time
    
    Returns
    -------
    ds : xarray.DaraSet with corrected time
    """

    # Make compatible variable names for CAM and CLM (CLM names converted to CAM)
    ds_ = ds.copy(deep=False) # for large files, this can become expensive
    if 'time_bounds' in list(ds_.data_vars): 
        ds_ = ds_.rename_vars(dict(time_bounds='time_bnds'))
        ds_ = ds_.rename_dims(dict(hist_interval='nbnd'))

    # monthly data: refer data to the 15th of the month
    if timetype == 'DatetimeNoLeap':
        from cftime import DatetimeNoLeap

        months = ds_.time_bnds.isel(nbnd=0).dt.month.values
        years = ds_.time_bnds.isel(nbnd=0).dt.year.values
        dates = [DatetimeNoLeap(year, month, 15) for year, month in zip(years, months)]
      
    elif timetype == 'datetime64':
        dates = list(ds_.time_bnds.isel(nbnd=0).values + np.timedelta64(14, 'D'))
      
    else:
        raise ValueError("time type not supported. Choose 'DatetimeNoLeap' or 'datetime64'")
      
    ds = ds.assign_coords({'time':('time', dates, ds.time.attrs)})
    return ds

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

def create_dataset(raw_path, casename, comp, history_field='h0', vars=None, full_dset = False,
                   fix_timestamp = 'datetime64', spinup_months = 12, pressure_vars=False):
    """Given a list of raw netcdf files, convert them into a Xarray Dataset with merged time
    Args:
    - raw_path (string): path to the dictory with the files
    - casename (string): case name to identify the files
    - comp (string): component to analyse ('atm' or 'lnd')
    - history_field (string): code for the history files type. Default:'h0' (main - monthly)
    - full_dset (bool): return full dataset with no variable selection, else a variable selection will be performed by component. Default: False
    - fix_timestamp (string): fix dates in h0 raw files (shifted of one month). 
    Value of fix_timestamp passed as timetype in fix_cam_time. If no fixing pass None. Default: 'datetime64'.
    - spinup_months (int): number of month to neglect because of spin up. Dafault: 12
    - pressure_vars (bool): include pressure variables ('P0', 'hyam', 'hybm', 'PS', 'hyai', 'hybi', 'ilev'). Default: False
    
    Return:
    - xarray Dataset 
    """

    # Set model name by comp
    if comp == 'atm': model = 'cam'
    elif comp == 'lnd': model = 'clm2'
    else: raise ValueError("component not supported. Choose 'atm' or 'lnd'")
    
    # Import all dataset   
    fp = raw_path+casename+'/'+comp+'/hist/'+casename+'.'+model+'.'+history_field+'.*.nc'

    all_files = glob.glob(fp)

    if len(all_files) == 0:
        print(f"No files found matching: {fp}", file=sys.stderr)
        sys.exit(1)
    
    all_files.sort()
    print("Files found")

    ds = xr.open_mfdataset(all_files)
    print("Dataset created")
    
    # Fix timestamp of model data
    if fix_timestamp and history_field == 'h0': 
        ds = fix_cam_time(ds, timetype = fix_timestamp)

    # Remove spinup months of data set
    ds = ds.isel(time=slice(spinup_months,len(ds.time)))
    print("Postprocessing completed")
    
    if full_dset: 
        return ds
    
    else: # Select variables
        bvoc = True # variable for adding bvoc variables in the land component, useless in atm
        if comp == 'atm':
            variables = atm_always_include
            if pressure_vars: variables = variables + pressure_variables
        elif comp == 'lnd': 
            variables = lnd_always_include
            if casename.find('OFF')>0.: bvoc = False # deactivate bvoc variables in simulation with bvoc controlled (tagged with '*-OFF')

        if not vars: variables = variables + sum([*variables_by_component(comp, bvoc).values()], []) # from dict to flat list
        else: variables = variables + variables_by_component(comp, bvoc)[vars]
        
        present = [v for v in variables if v in ds.variables]
        missing = sorted(set(variables) - set(present))

        if missing:
            print(f"Warning: {len(missing)} requested variables missing:")
            print(missing)

        return ds[present]
    
