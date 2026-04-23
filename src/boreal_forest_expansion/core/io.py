from __future__ import annotations

import glob

import xarray as xr

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
    ds_ = ds.copy() # remove deep=True (22 April 26, long processing time) --- IGNORE ---
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


TIME_HELPERS = ["time", "time_bnds", "time_bounds"]

def open_mfdataset_selected(file_glob: str, keep_vars: list[str]) -> xr.Dataset:
    """
    Open and merge multiple NetCDF files matching a glob pattern (and sort them by time).
    """
    all_files = sorted(glob.glob(file_glob))
    if not all_files:
        raise FileNotFoundError(f"No files found for pattern: {file_glob}")

    # Inspect first file to determine which variables actually exist
    ds0 = xr.open_dataset(all_files[0], decode_times=False)
    vars_in_file = set(ds0.variables)

    keep = [v for v in keep_vars + TIME_HELPERS if v in vars_in_file]
    drop = [v for v in vars_in_file if v not in keep]

    print(f"Keeping variables: {keep}")
    print(f"Dropping {len(drop)} variables")

    ds = xr.open_mfdataset(
        all_files,
        combine="by_coords",
        drop_variables=drop,
        parallel=False,
    )

    ds = fix_cam_time(ds, timetype="DatetimeNoLeap")
    return ds