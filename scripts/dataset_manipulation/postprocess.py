
import numpy as np
import xarray as xr
import glob #return all file paths that match a specific pattern

atm_always_include = ['LANDFRAC', 'GRIDAREA', 'gw', 'date', 'time_bnds', 'T', 'TS', 'U', 'V']
lnd_always_include = ['area', 'landfrac', 'landmask', 'pftmask', 'PCT_LANDUNIT']
pressure_variables = ['P0', 'hyam', 'hybm', 'PS', 'hyai', 'hybi', 'ilev']
Ghan_vars = ['SWDIR', 'LWDIR', 'DIR', 'SWCF', 'LWCF', 'NCFT', 'SW_rest', 'LW_rest', 'FREST', 'FTOT', 'SWTOT', 'LWTOT']

    
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
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
    ds_ = ds.copy(deep=True)
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

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def variables_by_component(comp, bvoc=True):
    """Return dict of selected variables per cathegory given the respective component"""

    if comp == 'atm':

        variables = \
            {'BVOC': ['SFisoprene', 'SFmonoterp'],
             'SOA': ['N_AER', 'DOD550', 'SOA_A1','SOA_NA','cb_SOA_A1','cb_SOA_NA', 'cb_SOA_A1_OCW', 'cb_SOA_NA_OCW', 'NUCLRATE', 'FORMRATE', 'CCN1','CCN2','CCN3','CCN4','CCN5','CCN6','CCN7','CCN_B', 'cb_H2SO4','cb_SOA_LV', 'H2SO4', 'SOA_LV'],
             'CLOUDPROP': ['ACTNL', 'ACTREL','AREL', 'AWNC', 'CDNUMC', 'CLDHGH', 'CLDLOW', 'CLDMED', 'CLDTOT', 'CLDLIQ', 'CLOUD',
                           'CLOUDCOVER_CLUBB', 'FCTL', 'FREQL', 'NUMLIQ', 'TGCLDCWP', 'TGCLDLWP', 'TGCLDIWP'],
             'RADIATIVE': ['FSDS','FSNS','FLNT', 'FSNT', 'FLNT_DRF', 'FLNTCDRF', 'FSNTCDRF', 'FSNT_DRF', 'LWCF', 'SWCF', 'LHFLX', 'SHFLX'], #, 'OMEGAT'
             }
        """
        FSDS = “Downwelling solar flux at surface”
        FSDSC = “Clearsky downwelling solar flux at surface”
        FSDSCDRF = “SW downwelling clear sky flux at surface”
        FSDS_DRF = “SW downelling flux at surface”
        FSNS = “Net solar flux at surface”
        FSNSC = “Clearsky net solar flux at surface”
        FSNT = “Net solar flux at top of model”
        FSNTC = “Clearsky net solar flux at top of model”
        FSNTOA = “Net solar flux at top of atmosphere”
        FSNTOAC = “Clearsky net solar flux at top of atmosphere”
        FSUS_DRF = “SW upwelling flux at surface”
        FSUTADRF = “SW upwelling flux at TOA”
        FSUTOA
        """

    elif comp =='lnd':

        lnd_vars = ['TSA', 'Q2M', 'RH2M', 'PCT_NAT_PFT', 'TLAI']
        biogeochem_vars = ['GPP', 'NPP', 'NEE', 'NEP', 'STORVEGN', 'TOTPFTN', 'TOTVEGN',
                'TOTCOLC', 'TOTECOSYSC', 'TOTPFTC', 'TOTVEGC', 'STORVEGC']
        evap_vars = ['QFLX_EVAP_TOT', 'FCEV', 'FCTR', 'FGEV', 'QSOIL', 'QVEGE', 'QVEGT']

        if bvoc: #casename.find('OFF')<0.:
            variables = {'LAND': lnd_vars,
                        'BIOGEOCHEM': ['MEG_isoprene', 'MEG_limonene', 'MEG_myrcene', 'MEG_ocimene_t_b',
                                  'MEG_pinene_a', 'MEG_pinene_b', 'MEG_sabinene'] + biogeochem_vars,
                        'ET': evap_vars}
        else:
            variables = {'LAND': lnd_vars,
                        'BIOGEOCHEM': biogeochem_vars,
                        'ET': evap_vars}
            
    return variables

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
        
        return ds[variables]

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

def fix_units(ds):
    """ Convert some units to have a more meaningful representation """
    
    ds_ = ds.copy(deep=True)
    
    for var in list(ds_.keys()):
        
        if var == "SFisoprene" or var == "SFmonoterp":
            ds_[var].values = ds_[var].values*(1e+6*(60.*60.*24.*365.)) # Change unit from kg/m2/s to mg/m2/y
            #Note: this unit makes sense when a yearly value is shown, remember the output is monthly -> mean over the year or convert into month/day (/12, /365)
            ds_[var].attrs["units"] = "mg/m$^2$/y"
            
        elif var == "SOA_A1" or var == "SOA_NA":
            ds_[var].values = ds_[var].values*1e+9 # Change unit from kg/kg to $\mu$g/kg
            ds_[var].attrs["units"] = "$\mu$g/kg"
            
        elif var == "cb_SOA_A1" or var == "cb_SOA_NA" or var == "cb_SOA_A1_OCW" or var == "cb_SOA_NA_OCW":
            ds_[var].values = ds_[var].values*1e+6 # Change unit from kg/m2 to mg/m2
            ds_[var].attrs["units"] = "mg/m$^2$"
            
        elif var == "ACTNL":
            ds_[var].values = ds_[var].values*1e-6 # Change unit from m-3 to cm-3
            ds_[var].attrs["units"] = "cm$^{-3}$"
            
        elif var == "N_AER":
            ds_[var].attrs["units"] = "cm$^{-3}$" # Set unit to cm-3
            
        elif var == "CDNUMC":
            ds_[var].values = ds_[var].values*1e-10 # Change unit from 1/m2 to 1e6 cm-2
            ds_[var].attrs["units"] = "1e6 cm$^{-2}$"
            
        elif var == "CLDHGH" or var == "CLDLOW" or var == "CLDMED" or var == "CLDMED":
            ds_[var].values = ds_[var].values*1e+3 # Change unit from fraction to g/kg
            ds_[var].attrs["units"] = "g/kg"
            
        elif var == "CLDLIQ":
            ds_[var].values = ds_[var].values*1e+6 # Change unit from kg/kg to mg/kg
            ds_[var].attrs["units"] = "mg/kg"
            
        elif var == "TGCLDLWP":
            ds_[var].values = ds_[var].values*1e+3 # Change unit from kg/m2 to g/m2
            ds_[var].attrs["units"] = "g/m$^2$"
            
        elif var == "QFLX_EVAP_TOT":
            ds_[var].values = ds_[var].values*60*60*24 # Change unit from mm H2O/s to mm H2O/day
            ds_[var].attrs["units"] = "mm/day"
            
        elif var == "FLNT" or var == "FSNT" or var == "FLNT_DRF" or var == "FLNTCDRF" or var == "FSNT_DRF" or var == "FSNTCDRF" or var =="LHFLX" or var =="SHFLX":
            ds_[var].attrs["units"] = "W/m$^2$" # Change unit from W/m^2 to W/m2, like the other radiative fluxes
         
        else:
            continue
            
        #print(var, "-", ds_[var].attrs["long_name"], ":")
        #print(ds_[var].attrs["units"])
    print("Fix units completed")
            
    return ds_
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

def fix_ds(ds):
    """Assign clearer and more meaningful names"""
    
    ds_ = ds.copy(deep=True)
    
    for var in list(ds_.keys()):
        
        """
        if var == "SOA_A1":
            ds_[var].attrs["long_name"] = "SOA_A1 concentration - SOA condensate on existing particles from SOAGSV (gas)"
        elif var == "SOA_NA":
            ds_[var].attrs["long_name"] = "SOA_NA concentration - SOA formed by co-nucleation with SO4"
        elif var == "cb_SOA_A1":
            ds_[var].attrs["long_name"] = "SOA_A1 burden column - SOA condensate on existing particles from SOAGSV (gas)"
        elif var == "cb_SOA_NA":
            ds_[var].attrs["long_name"] = "SOA_NA burden column - SOA formed by co-nucleation with SO4"
        elif var == "cb_SOA_A1_OCW":
            ds_[var].attrs["long_name"] = "SOA_A1 burden column in cloud water - SOA condensate on existing particles from SOAGSV (gas)"
        elif var == "cb_SOA_NA_OCW":
            ds_[var].attrs["long_name"] = "SOA_NA burden column in cloud water - SOA formed by co-nucleation with SO4"
    
        elif var == "TGCLDLWP":
            ds_[var] = ds_[var].rename('LWP')
            ds_[var].attrs["CLM5_name"] = 'TGCLDLWP'
            
        elif var == "TGCLDCWP":
            ds_[var] = ds_[var].rename('CWP')
            ds_[var].attrs["CLM5_name"] = 'TGCLDCWP'
            
        elif var == "TGCLDIWP":
            ds_[var] = ds_[var].rename('IWP')
            ds_[var].attrs["CLM5_name"] = 'TGCLDIWP'
            
        elif var == "QFLX_EVAP_TOT":
            ds_[var] = ds_[var].rename('ET')
            ds_[var].attrs["CLM5_name"] = 'QFLX_EVAP_TOT'
            
        else:
            continue
            
        #print(var, "-", ds_[var].attrs["long_name"])
        """
        """
        if var == "FSNT":
            ds_[var].rename('SWTOT')
            ds_[var].assign_attrs["CLM5_name"] = "FSNT"
        if var == "FLNT":
            ds_[var].rename('LWTOT')
            ds_[var].assign_attrs["CLM5_name"] = "FLNT"
        if var == "FSNT_DRF":
            ds_[var].rename('SW_clean')
            ds_[var].assign_attrs["CLM5_name"] = "FSNT_DRF"
        if var == "FSNTCDRF":
            ds_[var].rename('SW_clean_clear')
            ds_[var].assign_attrs["CLM5_name"] = "FSNTCDRF"
        if var == "FLNT_DRF":
            ds_[var].rename('LW_clean')
            ds_[var].assign_attrs["CLM5_name"] = "FLNT_DRF"
        if var == "FLNTCDRF":
            ds_[var].rename('LW_clean_clear')
            ds_[var].assign_attrs["CLM5_name"] = "FLNTCDRF"
        """
    for var in ['cb_SOA_dry', 'AREL_incld', 'AWNC_incld', 'ACTNL_incld', 'ACTREL_incld']:
        ## Author: Sara M. Blichner
        if var == 'cb_SOA_dry':
            ds_[var] = ds_['cb_SOA_NA'] + ds_['cb_SOA_A1']
            ds_[var].attrs['long_name'] = "dry SOA burden column (cb_SOA_NA+cb_SOA_A1)"
            ds_[var].attrs['units'] = ds_['cb_SOA_NA'].attrs['units']
        if var == 'AREL_incld':
            ds_[var] = ds_['AREL'] / ds_['FREQL']
            ds_[var] = ds_[var].where((ds_['FREQL'] != 0))
            ds_[var].attrs['units'] = ds_['AREL'].attrs['units']
        if var == 'AWNC_incld':
            ds_[var] = ds_['AWNC'] / ds_['FREQL'] * 1.e-6
            ds_[var] = ds_[var].where((ds_['FREQL'] != 0))
            ds_[var].attrs['units'] = '#/cm$^3$'
        if var == 'ACTNL_incld':
            ds_[var] = ds_['ACTNL'] / ds_['FCTL'] * 1.e-6
            ds_[var] = ds_[var].where((ds_['FCTL'] != 0))
            ds_[var].attrs['units'] = '#/cm$^3$'
        if var == 'ACTREL_incld':
            ds_[var] = ds_['ACTREL'] / ds_['FCTL']  # *1.e-6
            ds_[var] = ds_[var].where((ds_['FCTL'] != 0))
            ds_[var].attrs['units'] = ds_['ACTREL'].attrs['units']
            
    for var in ['T_C', 'WIND_SPEED']:
        if var == 'T_C':
            ds_[var] = ds_['T']-273.15
            ds_[var].attrs['long_name'] = ds_['T'].attrs['long_name']
            ds_[var] = ds_[var].assign_attrs({'units': '$^\circ$C'})
        if var == 'WIND_SPEED':
            ds_[var] = np.sqrt(ds_['V']**2 + ds_['U']**2)
            ds_.attrs['long_name'] = 'Wind speed'
            ds_.attrs['units'] = 'm/s'
        
        
    print("Fix names and variables completed")
    return ds_

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

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

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

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
            if casename.find('OFF')>0.: bvoc = False # deactivate bvoc variables in simulation with bvoc controlled (tagged with '*-OFF')
             
        variables = variables + variables_by_component(component, bvoc)[cat]
        if cat == 'RADIATIVE': variables = variables + Ghan_vars
        file_out = casealias+'_'+cat+'_'+date+'.nc'
        ds[variables].to_netcdf(processed_path+file_out)
        print(file_out)
        
    print("\nSaving completed")
    
