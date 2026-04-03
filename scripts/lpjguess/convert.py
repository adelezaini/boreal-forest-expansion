###### This python file collects fuctions to convert LPJGUESS pfts to CLM ones

####### Import packages
import numpy as np
import xarray as xr
import sys; sys.path.append(".")
from dataset_manipulation import *

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def PFT_convert_LPJGUESS_to_CLM(CLM_pfts, LPJGUESS_pfts, convertion_scheme = {}):
    """Convert PFTs from LPJGUESS into PFTs of CLM.
    Args:
    - CLM_pfts (DataArray): original DataArray with CLM PFTs (lat, lon, natpft)
    - LPJGUESS_pfts (DataArray): natural PFTs from LPJGUESS classification (lat, lon, natpft)
    - convertion_scheme (dict): dictionary with items = LPJGUESS PFTs and amount = CLM PFTs following the correspondance. If no convertion_scheme is passed, the boreal one will be applied (see below).
    
    Return:
    - DataArray with the same distribution of LPJGUESS_pfts, but with the PFT classification beloging to CLM
    
    The boreal convertion scheme is (L->C):
    3 -> 1
    0,1 -> 2
    2 -> 3
    4 -> 5
    6 -> 7* in the boreal area
    5 -> 8
    8,10 -> 11* in the boreal area
    9, 11,12,13,14,15 -> 11* in the boreal area
    7 -> 12
    """
    
    # Convertion scheme is (C<-L):
    if not convertion_scheme:
        convertion_scheme = {1:3, 2:[0,1], 3:2, 5:4, 7:6, 8: 5, #9:[8,10],
                            11:[8,10,9,11, 12, 13, 14, 15], 12:7}

    # Create scheleton to fill with LPJGUESS data (selecting just the natpft consider in the convertion
    #(not tropical for instance))
    LPJGUESS_converted = CLM_pfts.sel(natpft=list(convertion_scheme.keys()))
    LPJGUESS_converted[:] = np.nan
    # Regrid LPJGUESS grid to the CLM one (percentage unit)
    LPJGUESS_pfts_coarse = match_coord(LPJGUESS_pfts, CLM_pfts)*100.
    # Patch some interpolation "typo" of estimating a bit under zero (10^-15)
    LPJGUESS_pfts_coarse = LPJGUESS_pfts_coarse.where(LPJGUESS_pfts_coarse>=0., 0.).where(LPJGUESS_pfts_coarse.notnull())
    
    for n in list(convertion_scheme.keys()):
        # If the LPJGUESS pft is a list -> sum the elements to obtain a new single DataArray with summed elements
        if type(convertion_scheme[n])==list:
            da_n = LPJGUESS_pfts_coarse.sel(natpft=convertion_scheme[n]).sum('natpft', keep_attrs=True).where(LPJGUESS_pfts_coarse.sel(natpft=0)>=0.)
        else:
            da_n = LPJGUESS_pfts_coarse.sel(natpft=convertion_scheme[n])
        
        # Assign the new single pft DataArray to the scheleton in the respective pft
        LPJGUESS_converted.loc[dict(lat=LPJGUESS_pfts_coarse.lat, lon=LPJGUESS_pfts_coarse.lon, natpft=n)] = da_n
    return LPJGUESS_converted

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def PFT_convert_LPJGUESS_to_CLM_finegrid(CLM_pfts, LPJGUESS_pfts, convertion_scheme = {}):
    """Convert PFTs from LPJGUESS into PFTs of CLM - on the finer grid of LPJGUESS.
    Args:
    - CLM_pfts (DataArray): original DataArray with CLM PFTs (lat, lon, natpft)
    - LPJGUESS_pfts (DataArray): natural PFTs from LPJGUESS classification (lat, lon, natpft)
    
    Return:
    - DataArray with the same distribution of LPJGUESS_pfts, but with the PFT classification beloging to CLM
    
    The boreal convertion scheme is (L->C):
    3 -> 1
    0,1 -> 2
    2 -> 3
    4 -> 5
    6 -> 7* in the boreal area
    5 -> 8
    8,10 -> 11* in the boreal area
    9, 11,12,13,14,15 -> 11* in the boreal area
    7 -> 12
    """
    
    # Convertion scheme is (C<-L):
    if not convertion_scheme:
        convertion_scheme = {1:3, 2:[0,1], 3:2, 5:4, 7:6, 8: 5, #9:[8,10],
                            11:[8, 10, 9,11, 12, 13, 14, 15], 12:7}

    CLM_pfts_fine = match_coord(original_coord_da = CLM_pfts, coord_to_match_da = LPJGUESS_pfts)
    # Patch some interpolation "typo" of estimating a bit under zero (10^-15)
    CLM_pfts_fine = CLM_pfts_fine.where(CLM_pfts>=0., 0.).where(CLM_pfts_fine.notnull())
    # Create scheleton to fill with LPJGUESS data (selecting just the natpft consider in the convertion
    #(not tropical for instance))
    LPJGUESS_converted = CLM_pfts_fine.sel(natpft=list(convertion_scheme.keys()))
    LPJGUESS_converted[:] = np.nan
    
    for n in list(convertion_scheme.keys()):
        # If the LPJGUESS pft is a list -> sum the elements to obtain a new single DataArray with summed elements
        if type(convertion_scheme[n])==list:
            da_n = LPJGUESS_pfts.sel(natpft=convertion_scheme[n]).sum('natpft', keep_attrs=True).where(LPJGUESS_pfts.sel(natpft=0)>=0.)
        else:
            da_n = LPJGUESS_pfts.sel(natpft=convertion_scheme[n])
        
        # Assign the new single pft DataArray to the scheleton in the respective pft
        LPJGUESS_converted.loc[dict(lat=LPJGUESS_pfts.lat, lon=LPJGUESS_pfts.lon, natpft=n)] = da_n
    
    # Convert to same percentage unit
    return LPJGUESS_converted*100.
