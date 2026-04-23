###### 
import numpy as np
import pandas as pd
import xarray as xr

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as colors

import warnings; warnings.filterwarnings('ignore')
import matplotlib.path as mpath
from textwrap import wrap

#### import style

################ Miscellaneous ################
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def dict_to_legend(dct):
    """Support function for legend display.
      Convert a dict in the format {item1: amount1, item2:amount2...}
      into a list of strings in the format ['item1 - amount1', 'item2 - amount2', ...]
    """
    return ["{} – {}".format(item, amount) for item, amount in dct.items()]
    
def plot_title(title):
    """Plot the give title. Useful if plotting multiple figures, gathered under a same main title."""
    fig, ax = plt.subplots(1,1, figsize=(10, 0.5))
    ax.axis('off')
    plt.suptitle(title, weight='bold', size='xx-large', y=0.5)
    plt.show()
    
class MidpointNormalize(colors.Normalize):
#https://matplotlib.org/3.2.2/gallery/userdemo/colormap_normalizations_custom.html
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))

################ Projections ################
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def ax_map_properties(ax, alpha=0.3, coastlines=True, gridlines=True, earth = False, ocean=True, land=True, borders=True, rivers=True, provinces=False):
    """Set default map properties on the axis"""
    import cartopy.feature as cfeature
    
    if coastlines: ax.coastlines()
    if gridlines: ax.gridlines(alpha=0.3)
    if ocean: ax.add_feature(cfeature.OCEAN, zorder=0, alpha=alpha)
    if land: ax.add_feature(cfeature.LAND, zorder=0, edgecolor='black', alpha=alpha)
    if borders: ax.add_feature(cfeature.BORDERS, alpha=0.3)
    if rivers: ax.add_feature(cfeature.RIVERS)
    if earth: ax.stock_img()

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def cut_extent_Orthographic(ax, lat=None, extent=None):
    """Return circle where to cut the circular plot, given the latitude"""
    import cartopy.crs as ccrs
        
    if extent:
        ax.set_extent(extent, crs = ccrs.PlateCarree())
    elif lat:
        ax.set_extent([-180,180, lat,90], crs = ccrs.PlateCarree())
    else:
        ax.set_extent([-180,180,-90,90], crs = ccrs.PlateCarree())
    # Compute a circle in axes coordinates, which we can use as a boundary for the map.
    theta = np.linspace(0, 2*np.pi, 100)
    center, radius = [0.5, 0.5], 0.5
    verts = np.vstack([np.sin(theta), np.cos(theta)]).T
    circle = mpath.Path(verts * radius + center)
    ax.set_boundary(circle, transform=ax.transAxes)
        
