###### This python file collects fuctions to manipulate Xarray Dataset/DataArray

####### Import packages
import numpy as np
import netCDF4 as nc
import xarray as xr; xr.set_options(display_style='html')
import pandas as pd
import os
from scipy.special import erf


################ Fitting in Xarray
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def polynomial_fit(ds, dim, deg=3):
    out = ds.polyfit(dim=dim, deg=deg, full=True)
    polyfit = xr.polyval(coord=ds[dim], coeffs=out.polyfit_coefficients).rename('polyfit')
    return polyfit

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def gaussian_fit(ds, dim, p0={'A':45, 'xc':55, 'sig':5}, asym_gauss=False, fixed_extremes=False):
    
    names=None
    
    def gaussian(x, A, xc, sig):
        return A*np.exp(-np.power((x - xc),2.) / (2 * np.power(sig,2.)))
    
    def asym_gaussian(x, *p):
        amp = (p[0] / (p[2] * np.sqrt(2 * np.pi)))
        spread = np.exp((-(x - p[1]) ** 2.0) / (2 * p[2] ** 2.0))
        skew = (1 + erf((p[3] * (x - p[1])) / (p[2] * np.sqrt(2))))
        return amp * spread * skew
    
    if asym_gauss:
        gaussian=asym_gaussian
        p0['p3']=1
        names=['A', 'xc', 'sig', 'p3']
        
    if fixed_extremes==True:
        sigma = np.ones(len(ds[dim].values))
        sigma[[0, -1]] = 0.01
        fit_params=ds.curvefit(coords=dim, func=gaussian, p0=p0, param_names=names, kwargs={'sigma': sigma})
    else:
        fit_params=ds.curvefit(coords=dim, func=gaussian, p0=p0, param_names=names)#, kwargs={'sigma': sigma})
    popt=fit_params.curvefit_coefficients # NO! .values
    gaussfit = gaussian(ds[dim], *popt.T).drop('param').rename('gaussfit')
    return gaussfit
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
