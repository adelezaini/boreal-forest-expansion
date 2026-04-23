######
import numpy as np
import pandas as pd
import xarray as xr

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as colors

import cartopy
import cartopy.feature as cfeature
import cartopy.crs as ccrs
import warnings; warnings.filterwarnings('ignore')
import matplotlib.path as mpath
from textwrap import wrap

# import style
from boreal_forest_expansion.plotting.common import (
    ax_map_properties,
    cut_extent_Orthographic,
    MidpointNormalize,
)


fig_folder = '../../figures/results/'
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def boreal_map(da, title, figsize = [10,8], ax=None, projection=ccrs.Orthographic(0, 90), extent_lat = None,
                   grid=True, earth=False, contourf=False, units=None, text_wrap=30, cbar_kwargs={}, **kwargs):
    """Plot a spatial distribution of 'da', specially adapted for boreal and artic area.
    Args:
        - da (xr.DataArray): variable to plot with dimension [lat,lon]
        - ax (matplotlib.axes.Axes): axis to plot on. Optional. If None, a figure is created.
        - figsize (tuple): figure size (if ax=None)
        - projection (ccrs.): geographical projection
        - extent_lat (float): latitude over which the distribution will be depicted
        - grid (bool): display grid lines
        - earth (bool): display earth background
        - contourf (bool): contourf plot type. Default: pcolormesh
        - units (string): units for the colorbar label
        - cbar_kwargs (dict): colorbar arguments
        - kwargs (dict): arguments to pass to the xr.da.plot()
    """
    
    
    # Add axis if it not given - useful to plot multiple subplots in one figure
    if not ax:
        fig = plt.figure(1, figsize=figsize)#,dpi=100)
        ax = plt.axes(projection=projection)

    # Zoom on the map according to boreal_lat
    # Opposite of ax.set_global()
    if extent_lat: cut_extent_Orthographic(ax, extent_lat)

    # Gather all the arguments of the plot
    plot_args = dict(ax=ax, x='lon', y='lat', transform=ccrs.PlateCarree(), add_colorbar=False, **kwargs)
    
    # If not plot.contourf -> plot.pcolormesh
    if not contourf: p = da.plot(**plot_args) #pcolormesh
    else: p = da.plot.contourf(**plot_args)
        
    # Add common colorbar
    for arg in ['location', 'pad', 'shrink', 'aspect', 'extend']:
        if not arg in list(cbar_kwargs.keys()):
            if arg == 'location': cbar_kwargs[arg] = 'bottom'
            if arg == 'pad': cbar_kwargs[arg] =  0.05
            if arg == 'shrink': cbar_kwargs[arg] = 0.8
            if arg == 'aspect': cbar_kwargs[arg] = 35
            if arg == 'extend': cbar_kwargs[arg] = 'both'
            #if arg == 'label': cbar_kwargs[arg] = da.long_name+'\n['+da.units+']'
    cbar = plt.colorbar(p, ax = [ax], **cbar_kwargs)
    if not units: units = da.units
    cbar.set_label("\n".join(wrap(da.long_name+'\n['+units+']', text_wrap)), size=14)
    cbar.ax.tick_params(labelsize=13)
    #cbar = plt.colorbar(p, ax = [ax], location = 'bottom', pad=0.05,shrink=0.8, aspect=40, extend='both', **cbar_kwargs, label=da.long_name+'\n['+da.units+']')#'PTF on the natveg landunit [% of landunit]')

    # Costum axis features
    ax_map_properties(ax, gridlines=grid, earth=earth, rivers=False)
    if projection==ccrs.PlateCarree(): ax.set_aspect('auto')
    ax.set_title(title)#, weight='bold') #size='x-large'
    if not ax: plt.show()
    
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def set_colorbar(ds, kwargs, cbar_ticks=True):
    if 'vmax' in list(kwargs.keys()):
        vmax = kwargs['vmax']
        kwargs['vmin'] = - vmax
    if cbar_ticks and 'vmax' in list(kwargs.keys()):
        if not 'cbar_kwargs' in list(kwargs.keys()): kwargs=dict(cbar_kwargs={}, **kwargs)
        kwargs['cbar_kwargs']['ticks'] = [-vmax, -vmax*0.5, 0, vmax*0.5, vmax]
    #if not 'norm' in list(): kwargs['norm'] = MidpointNormalize(midpoint=0.)
    if 'norm' not in kwargs:
        kwargs['norm'] = MidpointNormalize(midpoint=0.)
    #if 'levels' in list(kwargs.keys()):
        #ds = ds.where(ds!=0.)
        
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def plot_difference_map(da_dict, case1, case2, variable, ax = None, relative=False, cmap='RdBu_r', boreal_lat=45., **kwargs):
    
    da1 = da_dict[case1][variable].mean('time')
    da2 = da_dict[case2][variable].mean('time')
    if variable=='ACTNL' or variable=='ACTREL':
        da1 = da_dict[case1][variable].mean('time')/da_dict[case1]['FCTL'].mean('time')
        da2 = da_dict[case2][variable].mean('time')/da_dict[case2]['FCTL'].mean('time')
    diff = (da1-da2)
    if relative:
        diff = diff/da2*100
        if not 'vmax' in list(kwargs.keys()): kwargs = dict(vmax=100, **kwargs)
    if variable =='N_AER': diff=diff.isel(lev=-1)
        
    set_colorbar(diff, kwargs, cbar_ticks=False)

    boreal_map(diff, ax = ax, title=case1+' – '+case2, cmap=cmap, extent_lat = boreal_lat, units = '%' if relative else None, **kwargs)
    
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def spatial_averages(ds_dict, variable, title, relative = False, vmax_mid = None, vmax_bot = None, savefig=None, **kwargs):
    
    fig, axes = plt.subplots(3,2, figsize=[12,16], subplot_kw={'projection':ccrs.Orthographic(0, 90)})

    #plot_args = dict(cbar_kwargs={'extend':'both'}, **kwargs)

    if kwargs['vmax']: vmax = kwargs['vmax']
    for i, cases in enumerate([['IDEAL-ON', 'CTRL'], ['REAL-ON', 'CTRL'], ['IDEAL-ON', 'IDEAL-OFF'], ['REAL-ON', 'REAL-OFF'], ['IDEAL-OFF', 'CTRL'], ['REAL-OFF', 'CTRL']]):
        if vmax_mid and (i==2 or i ==3): kwargs['vmax'] = vmax_mid
        if vmax_bot and (i==4 or i ==5): kwargs['vmax'] = vmax_bot
        plot_difference_map(ds_dict, cases[0], cases[1], variable, ax=axes.flat[i], relative=relative, **kwargs)
        if vmax: kwargs['vmax'] = vmax
        else: kwargs['vmax'] = None
        
    plt.suptitle(title)
    if not savefig:
        figtitle = fig_folder+variable
    else: figtitle = fig_folder+savefig
    if relative: figtitle=figtitle+'_relative'
    plt.savefig(figtitle+'.pdf', pad_inches=0.5, bbox_inches='tight')
    plt.show()

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def plot_difference_map_winter_summer(axes, da_dict, case1, case2, variable, seasons = ['DJF', 'JJA'], boreal_lat=45., relative = False, **kwargs):
    
    da1 = da_dict[case1][variable].groupby('time.season').mean('time')
    da2 = da_dict[case2][variable].groupby('time.season').mean('time')
    
    if variable=='ACTNL' or variable=='ACTREL':
        da1 = da_dict[case1][variable].groupby('time.season').mean('time')/da_dict[case1]['FCTL'].groupby('time.season').mean('time')
        da2 = da_dict[case2][variable].groupby('time.season').mean('time')/da_dict[case2]['FCTL'].groupby('time.season').mean('time')
    diff = (da1-da2)
    if relative:
        diff = diff/da2*100
        if not 'vmax' in list(kwargs.keys()): kwargs = dict(vmax=100, **kwargs)
    
    if variable=='N_AER': diff=diff.isel(lev=-1)
        
    kwargs=dict(cmap='RdBu_r', extent_lat = boreal_lat, units = '%' if relative else None, cbar_kwargs=dict(shrink=1.1, aspect=25), **kwargs)
    set_colorbar(diff, kwargs)

    for i, season in enumerate(seasons):
        boreal_map(diff.sel(season=season), ax=axes.flat[i],title=season, **kwargs)
    plt.subplots_adjust(bottom=0.3, top=0.8)
    plt.suptitle(case1+' – '+case2, y=0.9,size=18)
    plt.tight_layout()
    
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def spatial_averages_winter_summer(ds_dict, variable, title, figsize=[20,30], dpi=300, relative = False, savefig=None, **kwargs):
    backend = mpl.get_backend()
    mpl.use('agg')

    plot_args = dict(nrows=1, ncols=2, figsize=[figsize[0]/4.*1.3, figsize[1]/6.], dpi=dpi, subplot_kw={'projection':ccrs.Orthographic(0, 90)})
    
    figs = []
    axes = []
    for i, cases in enumerate([['IDEAL-ON', 'CTRL'], ['REAL-ON', 'CTRL'], ['IDEAL-ON', 'IDEAL-OFF'], ['REAL-ON', 'REAL-OFF'], ['IDEAL-OFF', 'CTRL'], ['REAL-OFF', 'CTRL']]):
        fig, ax = plt.subplots(**plot_args)
        axes.append(ax)
        plot_difference_map_winter_summer(axes[i], ds_dict, *cases, variable, relative = relative, **kwargs)
        figs.append(fig)
    
    a_list = []
    for fig in figs:
        c = fig.canvas
        c.draw()
        a_list.append(np.array(c.buffer_rgba()))
        
    a_top = np.hstack(a_list[:2])
    a_middle = np.hstack(a_list[2:4])
    a_bottom = np.hstack(a_list[4:])
    a = np.vstack((a_top, a_middle, a_bottom))
        
    mpl.use(backend)
    fig,ax = plt.subplots(figsize=figsize)
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set_axis_off()
    ax.matshow(a)
    plt.suptitle(title, size=33, y=0.9)
    if not savefig:
        figtitle = fig_folder+variable+'_seasons'
    else: figtitle = fig_folder+savefig+'_seasons'
    if relative: figtitle=figtitle+'_relative'
    plt.savefig(figtitle+'.pdf', pad_inches=0.3, bbox_inches='tight')
    plt.show()







#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def plot_difference_map_4seasons(da_dict, case1, case2, variable, title, relative=True, figsize=[17,6], **kwargs):
    seasons = ['DJF', 'MAM','JJA', 'SON']
    
    da1 = da_dict[case1][variable].groupby('time.season').mean('time')
    da2 = da_dict[case2][variable].groupby('time.season').mean('time')
    
    if variable=='ACTNL' or variable=='ACTREL':
        da1 = da_dict[case1][variable].groupby('time.season').mean('time')/da_dict[case1]['FCTL'].groupby('time.season').mean('time')
        da2 = da_dict[case2][variable].groupby('time.season').mean('time')/da_dict[case2]['FCTL'].groupby('time.season').mean('time')
        #ds_[var] = ds_[var].where((ds_['FCTL'] != 0))
    diff = (da1-da2)
    if relative:
        diff = diff/da2*100
        if not 'vmax' in list(kwargs.keys()): kwargs = dict(vmax=100, **kwargs)
    if variable=='N_AER': diff=diff.isel(lev=-1)
    
    set_colorbar(diff, kwargs)
        
    fig, axes = plt.subplots(1,4, figsize=figsize, subplot_kw={'projection':ccrs.Orthographic(0, 90)})#,dpi=100)
    
    for i, season in enumerate(seasons):
        boreal_map(diff.sel(season=season), ax=axes.flat[i], title=season, cmap='RdBu_r', extent_lat =45.,**kwargs)
    plt.suptitle(title+':\n'+case1+' – '+case2)
    plt.show()
    return fig
    
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def spatial_averages_4seasons(ds_dict, variable, title, figsize=[20,60], dpi=300, relative = False, savefig=None, **kwargs):
    seasons = ['DJF', 'MAM','JJA', 'SON']
    
    backend = mpl.get_backend()
    mpl.use('agg')

    plot_args = dict(nrows=1, ncols=4, figsize=[figsize[0]/2.*1.3, figsize[1]/12.], dpi=dpi, subplot_kw={'projection':ccrs.Orthographic(0, 90)})
    
    figs = []
    axes = []
    for i, cases in enumerate([['IDEAL-ON', 'CTRL'], ['IDEAL-ON', 'IDEAL-OFF'], ['IDEAL-OFF', 'CTRL'], ['REAL-ON', 'CTRL'], ['REAL-ON', 'REAL-OFF'], ['REAL-OFF', 'CTRL']]):
        fig, ax = plt.subplots(**plot_args)
        axes.append(ax)
        plot_difference_map_winter_summer(axes[i], ds_dict, *cases, variable, seasons = seasons, relative = relative, **kwargs)
        figs.append(fig)
    
    a_list = []
    for fig in figs:
        c = fig.canvas
        c.draw()
        a_list.append(np.array(c.buffer_rgba()))
        
    a = np.vstack(a_list)
        
    mpl.use(backend)
    fig,ax = plt.subplots(figsize=figsize)
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set_axis_off()
    ax.matshow(a)
    plt.suptitle(title, size=33, y=0.9)
    if not savefig:
        figtitle = fig_folder+variable+'_4seasons'
    else: figtitle = fig_folder+savefig+'_4seasons'
    if relative: figtitle=figtitle+'_relative'
    plt.savefig(figtitle+'.pdf', pad_inches=0.3, bbox_inches='tight')
    plt.show()
