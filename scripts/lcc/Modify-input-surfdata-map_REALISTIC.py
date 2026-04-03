#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Converted from Jupyter notebook: Modify-input-surfdata-map_REALISTIC.ipynb
"""

import subprocess

# %% [markdown]
# # Modify surface data map - REALISTIC CASE

# %%
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib as mpl
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

import sys; sys.path.append("..")
from dataset_manipulation import *
from surfdatamaplib import *
from lpjguess import *

# %%
# Bigger fonts to save figures for printing
plt.rcParams['font.size'] = 14
#plt.rcParams['figure.facecolor'] = 'none'
plt.rcParams['figure.titlesize'] = 16
fig_folder = '../../figures/modify_surfdata/'

# %% [markdown]
# ## Import data

# %%
# Import original surfdata file
fn_in='surfdata_1.9x2.5_hist_78pfts_CMIP6_simyr2000_c190304'
fn = '../../data/surfdatamap/'+fn_in + '.nc'
dset_in = xr.open_dataset(fn)

# Load pfts in CLM (from previous analysis)
folder_out='/Users/adelezaini/Desktop/master-thesis/processed-data/input/'
pfts_CLM = xr.open_dataset(folder_out+'IDEALIZED/pfts_CLM.nc'); pfts_CLM = pfts_CLM.PCT_NAT_PFT

# Filter DataArray by the land cover (to have ocean grid cells marked as NaN instead of 0)
lnd_frac = xr.open_dataset(folder_out+'IDEALIZED/lndfrac_CLM.nc'); lnd_frac = lnd_frac.LANDFRAC_PFT
lnd_frac = lnd_frac.where(lnd_frac<=1.,1.) # There are values above 1. -> replace with 1.
pfts_CLM = pfts_CLM#.where(lnd_frac>0.)

titles = ["1 – TeNET","2 – BoNET","3 – BoNDT", "5 – TeBET", "7 – TeBDT", "8 – BoBDT", "11 – BoBDS","12 – aC3"]
pftnames_CLM = {0:'Bare Ground', 1:'TeNET', 2:'BoNET', 3:'BoNDT', 4:'TrBET', 5:'TeBET', 6:'TrBDT', 
             7:'TeBDT', 8:'BoBDT', 9:'TeBES', 10:'TeBDS', 11:'BoBDS', 12:'arcticC3', 13:'C3', 14:'C4'}
plot_title('Overview of PFT distribution in the different models')
plot_boreal_pfts(pfts_CLM, col_wrap=4, title = "CLM PFTs", titles=dict_to_legend(pftnames_CLM))

# Future veg distribution from LPJGUESS - under SSP85 and as GCM GFDL-ESM4
fn = 'GFDL-ESM4_SSP585_fpc2071to2100.txt'
fn_path = '../../data/LPJ-GUESS/FPC/'+fn
pfts_GFDL = DataArray_from_LPJGUESS(fn_path, name='FPC_PFT', colnames=False, da_attrs=pfts_CLM,
                               main_attrs = {'long_name': 'foliage projective cover (fraction of gridcell)'})
pftnames = pftnames_LPJGUESS('../../data/LPJ-GUESS/FPC/fpc1971to2000.txt')

#Select just natural PFTs and not peatland ones
pfts_GFDL = pfts_GFDL.isel(natpft=slice(0,16))

plot_boreal_pfts(pfts_GFDL*100, titles = pftnames, col_wrap=4, title = "LPJGUESS PFTs", lat=1., extra_cbar_axis=True)

# %% [markdown]
# ## Convert LPJGUESS data into CLM format: regrid, normalize over landunit, convert PFTs

# %%
# Regrid LPJGUESS
pfts_GFDL.load().to_netcdf(folder_out+'REALISTIC/pfts_GFDL.nc')
pfts_CLM.load().to_netcdf(folder_out+'REALISTIC/pfts_CLM_real.nc')

# %%
subprocess.run(
    r"""eval "$(conda shell.bash hook)"
conda activate xesmf_env
python3 xe_regrid.py pfts_GFDL.nc pfts_CLM_real.nc ../../processed-data/input/REALISTIC/ pfts_GFDL_regridded.nc conservative_normed
#rm ../../processed-data/input/IDEALIZED/pfts_CLM_real.nc
rm ../../processed-data/input/REALISTIC/pfts_GFDL.nc
conda activate base""",
    shell=True,
    executable="/bin/bash",
    check=True,
)

# %%
pfts_GFDL_coarse = xr.open_dataset(folder_out+'REALISTIC/pfts_GFDL_regridded.nc')
pfts_GFDL_coarse = pfts_GFDL_coarse.FPC_PFT

# %%
subprocess.run(
    r"""eval "$(conda shell.bash hook)"
rm ../../processed-data/input/REALISTIC/pfts_GFDL_regridded.nc""",
    shell=True,
    executable="/bin/bash",
    check=True,
)

# %%
plot_boreal_pfts(pfts_GFDL_coarse, titles = pftnames, col_wrap=4, 
                 title = "LPJGUESS PFTs", lat=1., extra_cbar_axis=True)

# %%
########### OPERATIONS CORRECTED AFTERWARDS #################

# Regrid LPJGUESS
#pfts_GFDL_coarse = match_coord(pfts_GFDL, pfts_CLM)
#plot_boreal_pfts(pfts_GFDL_coarse,title = "PFTs in LPJGUESS - coarse", col_wrap=4, extra_cbar_axis=True)

# Rescale on landunit (CLM is in landunit)
#pfts_GFDL_lndunit = convert_gridcell_to_landunit(pfts_GFDL_coarse, lnd_frac, attrs=dict(long_name = pfts_CLM.long_name))

#pfts_GFDL_lndunit = pfts_GFDL_lndunit.where(pfts_GFDL_lndunit<=1., 1.).where(pfts_GFDL_coarse.notnull())

# Plot the difference: hard to see but there are some differences in the coastline. 
# Since LPJGUESS area cover just land, hard that when converted it has values on the coastline, 
#it's then hard to find the different gridcell on the map
#diff = pfts_GFDL_coarse - pfts_GFDL_lndunit
#plot_boreal_pfts(diff.where(diff!=0.),title = "PFTs in LPJGUESS - landunit",  figsize=[12,15],
                 #col_wrap=4, cmap='burd', vmin=-0.05, vmax = 0.05, levels=11)

# %%
# Convert PFT from LPJGUESS to CLM
pfts_GFDL_converted = PFT_convert_LPJGUESS_to_CLM(CLM_pfts = pfts_CLM, LPJGUESS_pfts = pfts_GFDL_coarse) #landunit
# There is value >100. ->100.
pfts_GFDL_converted = pfts_GFDL_converted.where(pfts_GFDL_converted<=100., 100.).where(pfts_GFDL_converted.notnull())
plot_boreal_pfts(pfts_GFDL_converted,title = "PFTs in LPJGUESS - converted into CLM", col_wrap=4, vmax = 100.,
                 extra_cbar_axis=True, titles = titles)

# %% [markdown]
# ### Change in LPJGUESS_SSP85 - CLM_2000

# %%
plot_boreal_pfts(pfts_GFDL_converted - pfts_CLM.sel(natpft = pfts_GFDL_converted.natpft).where(pfts_GFDL_converted>=0.),
                 title = "Change in PFT distribution: \nLPJGUESS_SSP85 - CLM_2000", cmap='burd',
                 col_wrap=4, extra_cbar_axis=True, titles = titles)
#plot_boreal_pfts(pfts_CLM.sel(natpft = pfts_GFDL_converted.natpft).where(pfts_GFDL_converted>=0.),
                 #title = "CLM PFTs - selected", titles = titles, col_wrap=4, extra_cbar_axis=True)

# %% [markdown]
# First of all, we need to remember that the two distributions come from two different models, so the plotted change takes into count differences in modelling (ex: the negative change in TeNET is simply due to this, there is no real decrease). A solution could be the following. Instead of replacing the values from LPJGUESS onto CLM configuration - just in the area of interested -, we **apply the change** observed in LPJGUESS on CLM configuration.

# %% [markdown]
# ### Change in LPJGUESS_SSP85 - LPJGUESS_hist

# %%
# Import historical data from LPJGUESS (sliced 1971-2000)
fn = 'fpc1971to2000.txt'
fn_path = '../../data/LPJ-GUESS/FPC/'+fn
pfts_hist = DataArray_from_LPJGUESS(fn_path, name='FPC_PFT', colnames=False, da_attrs=pfts_CLM,
                               main_attrs = {'long_name': 'foliage projective cover (fraction of gridcell)'})
#Select just natural PFTs and not peatland ones
pfts_hist= pfts_hist.isel(natpft=slice(0,16))

# Regrid LPJGUESS
pfts_hist.load().to_netcdf(folder_out+'REALISTIC/pfts_hist.nc')

# %%
subprocess.run(
    r"""eval "$(conda shell.bash hook)"
conda activate xesmf_env
python3 xe_regrid.py pfts_hist.nc pfts_CLM_real.nc ../../processed-data/input/REALISTIC/ pfts_hist_regridded.nc conservative
rm ../../processed-data/input/REALISTIC/pfts_hist.nc
rm ../../processed-data/input/REALISTIC/pfts_CLM_real.nc
conda activate base""",
    shell=True,
    executable="/bin/bash",
    check=True,
)

# %%
pfts_hist_coarse = xr.open_dataset(folder_out+'REALISTIC/pfts_hist_regridded.nc')
pfts_hist_coarse = pfts_hist_coarse.FPC_PFT

# %%
subprocess.run(
    r"""eval "$(conda shell.bash hook)"
rm ../../processed-data/input/REALISTIC/pfts_hist_regridded.nc""",
    shell=True,
    executable="/bin/bash",
    check=True,
)

# %%
# Regrid LPJGUESS
#pfts_hist_coarse = match_coord(pfts_hist, pfts_CLM)
# Rescale on landunit (CLM is in landunit)
#pfts_hist_lndunit = convert_gridcell_to_landunit(pfts_hist_coarse, lnd_frac,
                                                 #attrs=dict(long_name = pfts_CLM.long_name))
# Convert PFT from LPJGUESS to CLM
pfts_hist_converted = PFT_convert_LPJGUESS_to_CLM(CLM_pfts = pfts_CLM, LPJGUESS_pfts = pfts_hist_coarse)#lndunit)
# There is value >100. ->100.
#pfts_hist_converted = pfts_GFDL_converted.where(pfts_hist_converted<=100., 100.).where(pfts_hist_converted.notnull())

# Plot the change
change = pfts_GFDL_converted-pfts_hist_converted
plot_boreal_pfts(change, title = "Realistic change in PFT distribution\n(LPJGUESS_SSP85 - LPJGUESS_hist)", levels=10,
                 cmap='burd', col_wrap=4, extra_cbar_axis=True, vmax=50, vmin=-50,titles = titles, show=False)
plt.savefig(fig_folder+'realistic_change.pdf'); plt.show()

# %% [markdown]
# ## Add difference of LPJGUESS to CLM

# %%
pfts_CLM_GFDL = pfts_CLM.copy()

# Apply the change
for n in [1,2,3,5,7,8,11,12]:
    pfts_CLM_GFDL.loc[dict(natpft=n)] = pfts_CLM_GFDL.sel(natpft=n) + change.fillna(0.).sel(natpft=n)

# Set to 0 where it's negative (some areas in BoNET, BoBDS, aC3)
# plot_boreal_pfts(pfts_CLM_GFDL, title = "", cmap='burd', col_wrap=4, titles = dict_to_legend(pftnames_CLM), vmax=50, vmin=-50)
pfts_CLM_GFDL = pfts_CLM_GFDL.where(pfts_CLM_GFDL>=0., 0.).where(lnd_frac>0.)

# Renomalize with adding the change the sum is not 100. anymore...
#da_norm = pfts_CLM_GFDL.where(pfts_CLM_GFDL.sum('natpft')>100.00000001)
#da_norm = da_norm/da_norm.sum('natpft')*100.
#pfts_CLM_GFDL = pfts_CLM_GFDL.where(pfts_CLM_GFDL.sum('natpft')<100.00000001, da_norm)
pfts_CLM_GFDL = pfts_CLM_GFDL/pfts_CLM_GFDL.sum('natpft')*100.
#pfts_CLM_GFDL.sum('natpft').where(pfts_CLM_GFDL.sum('natpft')>100.).plot()

plot_boreal_pfts(pfts_CLM_GFDL, title = "Final configuration", cmap='Greens', 
                 col_wrap=4, titles = dict_to_legend(pftnames_CLM))

plot_boreal_pfts((pfts_CLM_GFDL-pfts_CLM).sel(natpft=[1,2,3,5,7,8,11,12]), extra_cbar_axis=True,
                 title = "Change in PFT distribution", cmap='burd', col_wrap=4, titles = titles)

# %% [markdown]
# ## Save edited surfdata_map_LPJGUESS

# %%
# Import original file
fn_in='surfdata_1.9x2.5_hist_78pfts_CMIP6_simyr2000_c190304'
fn = '../../data/surfdatamap/'+fn_in + '.nc'
#Open original file
dset_in = xr.open_dataset(fn)
pfts = convert360_180(convert_lsmcoord(dset_in)).PCT_NAT_PFT

# Apply modification to the original surfdata map
ds = surfdatamap_modification(original_ds = dset_in, pfts_tot = pfts, edited_pfts = pfts_CLM_GFDL, method='irregular_area')
ds.load().to_netcdf(folder_out+'REALISTIC/'+fn_in+'_GFDL.nc')
# Plot difference
#a = dset_in.PCT_NAT_PFT.sel(natpft=[2,3,8,11,12]); a.plot(col='natpft'); plt.show()
#b = ds.PCT_NAT_PFT.sel(natpft=[2,3,8,11,12]); b.plot(col='natpft'); plt.show()
#c= (b-a)#;c.plot(col='natpft', col_wrap=3); plt.show()
d = convert180_360(convert_lsmcoord(dset_in)).PCT_NAT_PFT.sel(natpft=[2,3,8,11,12])
e = convert180_360(convert_lsmcoord(ds)).PCT_NAT_PFT.sel(natpft=[2,3,8,11,12])
basic_pft_map((e-d), title ="Change in boreal PFT configuration -in the original format-", col_wrap=5,cmap='burd', figsize=(12,3))

# %%
basic_pft_map((pfts_CLM_GFDL-pfts_CLM).sel(natpft=[2,3,8,11,12]), 
              title ="Change in boreal PFT configuration -in the original format-", 
              col_wrap=5,cmap='burd', figsize=(12,3))

# %%

# %%

# %%

# %%

# %%

# %%
# Import original file
fn_in='surfdata_1.9x2.5_hist_78pfts_CMIP6_simyr2000_c190304'
fn = '../../data/surfdatamap/'+fn_in + '.nc'
dset_in = xr.open_dataset(fn)
# Load a CLM DataArray (from previous analysis)
pfts_CLM = xr.open_dataset(folder_out+'IDEALIZED/pfts_CLM.nc'); pfts_CLM = pfts_CLM.PCT_NAT_PFT

# Apply modification to the original surfdata map
ds = surfdatamap_modification(original_ds = dset_in, pfts_tot = pfts_CLM, edited_pfts = pfts_converted_lndunit, method = 'irregular_area')
# Save the new edited surfdatafile
ds.load().to_netcdf(folder_out+'REALISTIC/'+fn_in+'_historical.nc')

# %%

# %%

# %%


#Note there is a single value that after the regriding exceed 100 (natpft=2, lat=69.16, lon=35.)
#Pribably linked all the manipulation: 1. regrid LPJ grid to CLM grid, 
#2. sum of BNE+BINE in a single pft 3. convert into lndgrid
#Fix manually
pfts_converted_lndunit = pfts_converted_lndunit.where(pfts_converted_lndunit<=100., 100.).where(pfts_converted_lndunit>=0.)


# Apply modification to the original surfdata map
ds = surfdatamap_modification(original_ds = dset_in, pfts_tot = pfts_CLM, edited_pfts = pfts_converted_lndunit, method = 'irregular_area')
# Save the new edited surfdatafile
ds.load().to_netcdf(folder_out+'REALISTIC/'+fn_in+'_historical.nc')

# %%
e = convert180_360(convert_lsmcoord(ds)).PCT_NAT_PFT.sel(natpft=[1,2,3,5,7,8,11,12])
plot_boreal_pfts(e, title ="New configuration in CLM", col_wrap=3)
d = convert180_360(convert_lsmcoord(dset_in)).PCT_NAT_PFT.sel(natpft=[1,2,3,5,7,8,9,11,12])
plot_boreal_pfts((e-d), title ="Change in boreal PFT configuration -in the original format-", 
                 cmap='burd',col_wrap=3)
