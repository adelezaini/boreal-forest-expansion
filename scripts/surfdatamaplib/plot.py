###### This python file collects fuctions to make some plotting

####### Import packages
import numpy as np
import math
from textwrap import wrap
import xarray as xr; xr.set_options(display_style='html')
from scipy.optimize import curve_fit
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import transforms
from matplotlib.colors import ListedColormap
import matplotlib.path as mpath
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import proplot as pplt
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.mpl.ticker as cticker
from cartopy.util import add_cyclic_point
from owslib.wms import WebMapService
import warnings; warnings.filterwarnings('ignore')
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = 'STIXGeneral'
#'Ubuntu'#'Times New Roman'#'Source Sans Pro'#'Noto Sans'#'AppleMyungjo'#'STIXGeneral'
#plt.rcParams['font.size'] = 14
#plt.rcParams['figure.facecolor'] = 'none'
#plt.rcParams['figure.titlesize'] = '16'

import sys; sys.path.append("..")
from plot import *


################ GridSpec: PlanteCaree Map with Lat_lon distributions ################
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def map_lonlatdistribution(ds, lnd_frac=xr.DataArray(None), title=None, cbar_label=None, figsize=(10,6), cmap='Greens', color='g'):
    """
    Plot a map in PlateCaree projection with side Lat and Lon distribution.
    Distribution evaluated over the mean, considering the input as a percentage.
    
    Args:
    - ds (DataArray): PFT distribution with only dimensions lat-lon
    - lnd_frac (DataArray): land fraction - mandatory argument as a control
                            over the input dataset (0 over land, NaN over ocean)
    - *args: intuitive
    """
    if not cbar_label:
        cbar_label = ds.long_name
        
    ds = ds.copy()
    if lnd_frac.any(): ds = ds.where(lnd_frac>0.)
        
    fig = plt.figure(figsize=figsize)
    grid = plt.GridSpec(4, 4, hspace=0.2, wspace=0.2, right=0.85)

    ####### Main map:
    main_ax = fig.add_subplot(grid[:-1, 1:], projection=ccrs.PlateCarree())
    main_ax.set_global()
    main_ax.coastlines()
    main_ax.set_aspect('auto')
    im = ds.plot(ax=main_ax, add_colorbar=False, cmap=cmap, vmin = 0, vmax =100)
    plt.suptitle(title, weight='bold', size='x-large', y=0.95)

    ####### Latitude plot:
    # It was hard to have an area but orientated vertically (hist has orientation, line is easy, area is hell)
    lat_ax = fig.add_subplot(grid[:-1, 0], sharey=main_ax, ylabel='Latitude [°]') #xticklabels=[],
    ### Rotate axis
    base = plt.gca().transData
    rot = transforms.Affine2D().rotate_deg(90)
    reflect_vertical = transforms.Affine2D(np.array([[1, 0, 0], [0, -1, 0], [0, 0, 1]]))

    ds_lat = ds.mean('lon').rename('Latitude [°]')
    ds_lat.to_series().rename_axis('').plot(kind='area', ax=plt.gca(),transform= reflect_vertical + rot + base, stacked=False, color=color,xlim=(0, ds_lat.max()+3), ylim=(-90,90))
    plt.gca().invert_xaxis() #same as lat_ax.invert_xaxis()

    ####### Longitude plot:
    lon_ax = fig.add_subplot(grid[-1, 1:], sharex=main_ax) #yticklabels=[],
    ds_lon = ds.mean('lat')
    ds_lon.to_series().rename_axis('Longitude [°]').plot(kind='area', ax=lon_ax, stacked=False, color=color, ylim=(0, ds_lon.max()+3))
    lon_ax.invert_yaxis()

    ####### Colorbar:
    axins = inset_axes(lon_ax, # here using axis of the lowest plot
               width="5%",  # width = 5% of parent_bbox width
               height="340%",  # height : 340% good for a (4x4) Grid
               loc='lower left',
               bbox_to_anchor=(1.05, 1.2, 1, 1),
               bbox_transform=lon_ax.transAxes,
               borderpad=0
               )

    cb = fig.colorbar(im, cax=axins,format='%.0f%%', label = cbar_label)

    plt.tight_layout()
    plt.show()
    
    
################ Boreal PFTs plots ################
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def basic_pft_map(da, title, extent_lat=45, figsize=None, proj=ccrs.PlateCarree(), col_wrap=None, cmap='Greens', contourf = False, titles = None, cbar_label=None, show=True, **kwargs):
    """Analogous plot of da.plot(col='natpft'), but prettier (coastlines, proper colormap...)"""
    npft=len(da.natpft.values)
    if not col_wrap: col_wrap = npft
    
    # Gather all the arguments of the plot
    plot_args = dict(col='natpft', figsize=figsize, cmap=cmap, col_wrap=col_wrap, transform=ccrs.PlateCarree(), subplot_kws={"projection": proj}, add_colorbar=False, **kwargs)

    # If not plot.contourf -> plot.pcolormesh
    if not contourf: p = da.plot(**plot_args) #pcolormesh
    else: p = da.plot.contourf(**plot_args)

    for i, ax in enumerate(p.axes.flat):
        ax_map_properties(ax, gridlines=False, rivers=False, borders=False)
        ax.set_extent([-180,180, extent_lat,90], crs = ccrs.PlateCarree())
        #if col_wrap == npft: ax.set_position([0.025+i*(1/npft+0.01), 0.15, 1/npft, 0.66])
        if titles and i<len(titles): ax.set_title(titles[i])
            
        if proj== ccrs.PlateCarree():
            ax.set_aspect('auto')
            ax.set_xticks(ax.get_xticks()[abs(ax.get_xticks())<=180])
            ax.set_yticks(ax.get_yticks()[abs(ax.get_yticks())<=90])
            
    p.fig.subplots_adjust(left =0.05, right=1.04, wspace =0.03, hspace=0.2, bottom=0.16, top=0.75)

    if not cbar_label: cbar_label="\n".join(wrap(da.long_name+" ["+da.units+"]", 30))
    p.add_colorbar(label=cbar_label)
    p.fig.suptitle(title)
    #p.fig.suptitle(title, size=max(figsize)) if figsize else p.fig.suptitle(title)
    p.fig.tight_layout()
    if show: plt.show()
    
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def single_pft_map(da, title, figsize = [10,8], ax=None, extent_lat = None, projection=ccrs.Orthographic(0, 90), grid=True, earth=False, contourf=False, cmap='Greens', show=True, **kwargs):
    """Plot for a single PFT"""
    
    # Add axis if it not given - useful to plot multiple subplots in one figure
    if not ax:
        fig = plt.figure(1, figsize=figsize)#,dpi=100)
        ax = plt.axes(projection=projection)

    # Zoom on the map according to boreal_lat
    # Opposite of ax.set_global()
    if extent_lat: cut_extent_Orthographic(ax, extent_lat)

    # Gather all the arguments of the plot
    plot_args = dict(ax=ax, x='lon', y='lat', cmap = cmap, transform=ccrs.PlateCarree(), add_colorbar=False, **kwargs)
    
    # If not plot.contourf -> plot.pcolormesh
    if not contourf: p = da.plot(**plot_args) #pcolormesh
    else: p = da.plot.contourf(**plot_args)
        
    # Add common colorbar
    cbar = plt.colorbar(p,ax = [ax], location = 'top', shrink=0.6, aspect=40, label=da.long_name)#'PTF on the natveg landunit [% of landunit]')

    # Costum axis features
    ax_map_properties(ax, gridlines=grid, earth=earth)
    if projection==ccrs.PlateCarree(): ax.set_aspect('auto')
    ax.set_title(title,y=1.2, weight='bold') #size='x-large'
    if not ax or show: plt.show()
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def plot_boreal_pfts_CLM(boreal_pfts, col_wrap=2, contourf = True):
    """ Ah hoc plotting for the 5 boreal PFTs of CLM.
        Args:
        - boreal_pfts (DataArray): (lat, lon, natpft) with natpft = '2 - BoNET','3 - BoNDT','8 - BoBDT', '11 - BoBDS','12 - artic C3 grass'
    """
    
    titles=['2 - BoNET','3 - BoNDT','8 - BoBDT','11 - BoBDS','12 - artic C3 grass']
    #plt.tight_layout()
    
    # Gather all the arguments of the plot
    plot_args = dict(x='lon', y='lat', col='natpft', col_wrap=col_wrap,
                                  cmap='Greens', transform=ccrs.PlateCarree(),
                                  subplot_kws={'projection': ccrs.Orthographic(0, 90)},
                                  add_colorbar=False,figsize=(15, 15), robust=False)
    # If not plot.contourf -> plot.pcolormesh
    if contourf: p = boreal_pfts.plot.contourf(**plot_args)
    else: p = boreal_pfts.plot(**plot_args)

    for i, ax in enumerate(p.axes.flat):
        ax_map_properties(ax, borders=False, rivers=False)
        if i<5:
            ax.set_title(titles[i])
            data,lons=add_cyclic_point(boreal_pfts.isel(natpft=i).values,coord=boreal_pfts['lon'])
            cs=ax.contourf(lons,boreal_pfts['lat'],data, transform = ccrs.PlateCarree(),
                                cmap ='Greens', extend='both', levels = np.linspace(0,100, 11) )
        ax.title.set_size(15)
        ax.title.set_position([0.5,1.5])

    plt.tight_layout()
    # Add colorbar in the remaining axis
    plt.subplots_adjust(bottom=0.1, top=0.9, left=0.1, right=0.9, wspace=0.1, hspace=0.1)
    cbar_ax = p.fig.add_axes([0.5, 0.25, 0.4, 0.03]) #[left, bottom, width, height]
    cbar=p.fig.colorbar(cs,cax=cbar_ax ,orientation='horizontal')
    cbar.ax.set_title(boreal_pfts.long_name, size = 14 )

    plt.suptitle("Boreal PFTs", size=20, y = 0.95, fontweight = 'bold')
    plt.show()
    
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def plot_boreal_pfts(boreal_pfts, figsize=None, col_wrap=2, title=None, titles=None, cmap='Greens', auto_aspect=False, cbar_label=None, perc_label=True, extra_cbar_axis=False, lat=None, contourf = False, robust=False, show=True, cbar_kwargs={}, **kwargs):
    """ Orthographic projection plot of boreal PFTs.
        Args:
        - boreal_pfts (DataArray): DataArray of the boreal pfts with (lat, lon, natpft) as coordinates
        - figsize (list/tuple): set figure size of the plot - useful to adjust when pft total number changes
        - col_wrap (int): number of subplots in each row
        - title (string): title of the plot. If None, boreal_pfts.name will set as title
        - titles (list of string): titles for the subplots - meant to give proper names to the pfts (ex: boreal needleaf deciduous tree)
        - auto_aspect (bool): set automatically aspect ratio in each subplot
        - cbar_label (string): set colorbar label, if None boreal_pfts.long_name is the label
        - lat (float): latitude at which to cut the plot in ax.extent()
        - vmin, vmax (float): range values for colormap
        - contourf (bool): kind of plot
        - robust (bool): argument to optimise the plot colours by clipping extreme values or outliers
        - cbar_kwargs (dict): colorbar arguments (ex: shrink, aspect, orientation...)
        - **kwargs (Any): keyword-arguments to pass to xr.DataArray.plot().
    """
    
    rows = math.ceil(len(boreal_pfts.natpft.values)/col_wrap)
    # If 'figsize' is not given: set it automatically considering the total number of PFTs
    if not figsize: figsize = [col_wrap*3.5, rows*3.5]

        
    # Just for a nicer plot: extra_cbar_axis=True move the (eventual) big colorbar from the side to an extra axis
    # If the number of PFTs fits a multiple of 'col_wrap', then xarray.DataArray.plot() will automatically add a side colorbar, rearranging the axes position and width ('add_colorbar=True')
    # Else, we silence the automatic colorbar ('add_colorbar=False') to add an extra axis on the last available from the arrange of subplots
    if extra_cbar_axis or len(boreal_pfts.natpft.values)%col_wrap and not robust:
        add_colorbar=False
    else:
        add_colorbar=True
        
    # Gather all the arguments of the plot
    if not cbar_kwargs:
        if rows<2: cbar_kwargs=dict(shrink=0.6)
        else: cbar_kwargs=dict(orientation='horizontal', shrink=0.6)
            
    # If vmin and vmax are not assigned -> 'ceiling tens' are choosen for extremes (-91->-100, 84->100)
    if not robust: # in contrast with robust
        if not any(x=='vmin' for x in kwargs.keys()):
            if boreal_pfts.min().values:
                kwargs['vmin'] = 10**(math.ceil(math.log(abs(boreal_pfts.min().values), 10)))*np.sign(boreal_pfts.min().values)
            else: #in case it's 0.
                kwargs['vmin'] = boreal_pfts.min().values
        if not any(x=='vmax' for x in kwargs.keys()):
            if boreal_pfts.max().values:
                kwargs['vmax'] = 10**(math.ceil(math.log(abs(boreal_pfts.max().values), 10)))*np.sign(boreal_pfts.max().values)
            else: #in case it's 0.
                kwargs['vmax'] = boreal_pfts.min().values
            
    plot_args = dict(x='lon', y='lat', col='natpft', col_wrap=col_wrap,
                     cmap=cmap, transform=ccrs.PlateCarree(), robust=robust,
                     subplot_kws={'projection': ccrs.Orthographic(0, 90)},
                     add_colorbar=add_colorbar,figsize=figsize, **kwargs,
                     cbar_kwargs=cbar_kwargs)
    # If not plot.contourf -> plot.pcolormesh
    if not contourf: p = boreal_pfts.plot.pcolormesh(**plot_args)
    else: p = boreal_pfts.plot.contourf(**plot_args)
        

    for i, ax in enumerate(p.axes.flat):
        ax_map_properties(ax, borders=False, rivers=False)
        if auto_aspect: ax.set_aspect('auto')
        if lat:
            #cut_extent_Orthographic(ax, lat=lat) # it doesn't work with FacedGrid: https://github.com/pydata/xarray/issues/4137
            ax.set_extent([-180,180, lat,90], crs = ccrs.PlateCarree())
        if titles and i<len(titles): ax.set_title(titles[i])

    # If automatic colorbar is silenced (see above), add colorbar in the last axis
    if not add_colorbar:
        # If there is no "last axis", add an extra one
        if extra_cbar_axis:
            nrows = int(len(boreal_pfts.natpft.values)/col_wrap) #number of rows in the subplots
            n = len(p.fig.axes) #number of axis
            # Change geometry to fit an extra line of axes
            for i in range(n):
                p.fig.axes[i].change_geometry(nrows+1, col_wrap, i+1)
            # Add extra axis and remove all the "decorations" (facecolor, grid, axes, ...)
            ax = p.fig.add_subplot(nrows+1, 1, nrows+1)
            ax.remove() #ax.grid(False) #ax.set_facecolor('none')
            # Adjust the figsize (height) with the new extra row of subplots
            p.fig.set_figheight(figsize[1]/nrows*(nrows+1))
            
        #plt.subplots_adjust(bottom=0.1, top=0.9, left=0.1, right=0.9, wspace=0.1, hspace=0.1)
        #Get last axis position
        l,b,w,h = ax.get_position().bounds
        #Create a rectangle for the colorbar (horizontal stripe, narrower than the total original axis size)
          # if an extra row is added for the colorbar, shrink the axis containining the colorbar and center it
        if extra_cbar_axis: sec = w/6.; w = sec*4.; l = l + sec
        rect = [l,b+h*0.5,w,h*0.05]
        cbar_ax = p.fig.add_axes(rect)
        #cbar_ax.set_aspect(w/h)
        # Create a colormap within [vmin, vmax] in 'Greens'
        # If levels: create colorbar with levels
        if any(x=='levels' for x in kwargs.keys()): cmap = mpl.cm.get_cmap(cmap,kwargs['levels'])
        cs=mpl.cm.ScalarMappable(mpl.colors.Normalize(vmin=kwargs['vmin'], vmax=kwargs['vmax']), cmap=cmap)
        #Add colorbar and title
        cbar=p.fig.colorbar(cs,cax=cbar_ax , extend='both', orientation='horizontal')
        if cbar_label: cbar.set_label(cbar_label)
        else: cbar.set_label("\n".join(wrap(boreal_pfts.long_name, 30))) #, size = 14 )
        if perc_label: cbar_ax.set_xticklabels(['{0:g}%'.format(x) for x in cbar_ax.get_xticks()])
        
    #Set title
    if title : plt.suptitle(title, y = 0.97, fontweight = 'bold') #size=13,
    else: plt.suptitle(boreal_pfts.name, y = 0.97, fontweight = 'bold') #size=13,
    plt.tight_layout()
    if show: plt.show()

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def basic_line_plot(ds, title, alpha=None, colors=None, legend = {15:'15 - Boreal trees', 11:'11 - Boreal schrubs', 12:'12 - arctic C3 grass'}, ytick_perc=True, show=True):
    """Simple line plot for lat/lon distribution of different natpft together"""
    
    if not alpha: alpha=np.ones(len(ds.natpft.values))

    fig, ax = plt.subplots(figsize=[7,3])
    for i, n in enumerate(ds.natpft.values):
        if not colors:
            ds.sel(natpft=n).plot(ax=ax, label=legend[n], alpha=alpha[i])
        else:
            ds.sel(natpft=n).plot(ax=ax, label=legend[n], alpha=alpha[i], color=colors[i])

    if ytick_perc:
        ax.set_yticklabels(['{0:g}%'.format(x) for x in ax.get_yticks()])
    ax.set_xlim(40,90)
    plt.legend()
    plt.title(title)
    plt.tight_layout()
    if show: plt.show()
    
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def plot_individual_cumulative(ds_x, ds_y, col, title=None, legend=None, figname=None):
    """Distribution plots – 1. individual curves 2. cumulative contribution"""
    
    figsize=(13, 5)
    fig, axes = plt.subplots(1,2,figsize=figsize)
    series = ds_y.to_series().unstack() #series.plot.bar(ax=ax, stacked=True)
    p=series.plot.area(ax=axes[0], stacked=False, title="Individual", color=col)
    if legend:
        axes[0].legend(legend, fancybox=True)
    
    if not legend:
        Legend = axes[0].get_legend()
        leg=[]; [leg.append(t.get_text()) for t in Legend.texts]

    axes[1].stackplot(ds_x, ds_y.T, colors = col)
    axes[1].legend(leg, title = Legend.get_title().get_text()) if not legend else axes[1].legend(legend, fancybox=True)
    axes[1].set_title("Cumulative")

    for b, ax in enumerate(axes.flat):
        vals = ax.get_yticks()
        ax.set_yticklabels(['{0:g}%'.format(x) for x in vals])
        ax.set_xlim(40,90)

    plt.suptitle(title, size=max(figsize))

    plt.tight_layout()
    if figname: plt.savefig(figname)
    plt.show()
    


    
    
################ Dominant vegetation plot ################
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def dominant_vegetation(veg_ds):
    """
    Create DataArray with .values() as the corresponding dominant PFTs number
    Args:
      - pft_list: select the PFTs to consider among the all in the DataArray. Default: None, that means all PFTs in the DataArray
      Each cell will evaluate the dominant PFT among the ones given in the DatArray. Given a larger number, it will show a different dominant veg
    """
    
    pft_list = list(veg_ds.natpft.values)
    # Start copying the first PFT, fill the array of respective PFT number and filter by lnd_frac
    dominant_veg = veg_ds.isel(natpft=0).copy()
    dominant_veg[:] = pft_list[0]
    dominant_veg = dominant_veg.where(veg_ds.isel(natpft=0)>0.).drop('natpft')

    # Building the dominant veg rappresentation:
    # find max PFT value in each grid cell and compare to each "layer" of PFT
    # -> if equal to the max, then substitute the PFT number with the new max PFT number
    pfts_max = veg_ds.max(dim='natpft')
    pfts_max=pfts_max.where(pfts_max>0.) #not to consider cell=0, that in the next step could cause misleading results

    for pft_index in pft_list:
        pft_filter=veg_ds.sel(natpft=pft_index) == pfts_max
        # pft_filter is a True-False array (where -lat/lon- is equal to max values)
        dominant_veg = xr.where(pft_filter, pft_index, dominant_veg)
        # where True, PFT number. Otherwise keep dominant veg value

        dominant_veg = dominant_veg.drop('natpft').rename('PFTs')
    return dominant_veg

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def discrete_mapping_elements(col_dict, labels):
    """Return colormap, normalizer, format and ticks for colorbar in order to plot a discrete map
        Args:
            - col_dict (dictionary): dictionary with values as .keys() and respective color as .items()
            - labels (list of strings): names relative to values
      Code taken from [...]"""
    # Create a colormap
    cm = ListedColormap([col_dict[x] for x in col_dict.keys()])
    # Normalizer:
    ## Prepare bins for the normalizer
    norm_bins = np.sort([*col_dict.keys()]) + 0.5
    norm_bins = np.insert(norm_bins, 0, np.min(norm_bins) - 1.0)
    ## Make normalizer and formatter
    norm = mpl.colors.BoundaryNorm(norm_bins, len(labels), clip=True)
    fmt = mpl.ticker.FuncFormatter(lambda x, pos: labels[norm(x)])
    # Create ticks to have equidistance between ticks
    diff = norm_bins[1:] - norm_bins[:-1]
    tickz = norm_bins[:-1] + diff / 2
    return cm, norm, fmt, tickz

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def plot_dominant_vegetation(da_pfts, title, col_dict, labels, pft_list = None, projection = ccrs.PlateCarree(), extent=None, figsize=[12,8], alpha=0.8, contourf=False, show=True, **kwargs):
    """ Plot dominant vegetation on the base on dominant PFT percentage.
        Args:
            - da_pfts (DataArray): PFTs DataArray with dim (lon, lat, natpft)
            - title (string): title of the plot
            - col_dict (dict): keys are PFTs number (int) and values are color names (string)
            - labels (list of string): legend label - PFT names
            - pft_list (list of pft indexes): PFTs to plot among the analysis over all of the PFTs. Each cell will evaluate the dominant PFT among the ones given in the DatArray. Default: None, that means all PFTs in the DataArray
            - projection (ccrs object): projection of the map. Default: ccrs.PlateCarree()
            - extent (list of float): list of coordinate to zoom on [lon_min, lon_max, lat_min, lat_max]. Default None.
            - alpha (float): opacity of land-ocean background
            - contourf (bool): kind of plot
            - **kwargs (Any): keyword-arguments to pass to xr.DataArray.plot().
    """
    
    if not pft_list: pft_list = list(da_pfts.natpft.values)
    
    dominant_boreal = dominant_vegetation(da_pfts)
    dominant_boreal = xr.where(np.isin(dominant_boreal.values,pft_list), dominant_boreal, float("nan"))

    ############# Preparation for plotting:
    cm, norm, fmt, tickz = discrete_mapping_elements(col_dict, labels)

    ############# Plotting:
    
    fig = plt.figure(1, figsize=figsize)#, dpi=300)
    ax = plt.axes(projection=projection)
    
    if extent:
        if projection == ccrs.PlateCarree():
            ax.set_extent(extent, crs = ccrs.PlateCarree())
        else:
            cut_extent_Orthographic(ax, extent=extent)
            
    # Gather all the arguments of the plot
    plot_args = dict(ax=ax, x='lon', y='lat', cmap=cm, norm=norm, transform=ccrs.PlateCarree(), add_colorbar=False, **kwargs)
    # If not plot.contourf -> plot.pcolormesh
    if not contourf: p = dominant_boreal.plot.pcolormesh(**plot_args)
    else: p = dominant_boreal.plot.contourf(**plot_args)
    
    cb = fig.colorbar(p, ax=[ax], format=fmt, ticks=tickz, location = 'top', shrink=1/10*len(pft_list), aspect=len(pft_list)*5)

    ax_map_properties(ax, alpha=alpha)
    ax.gridlines(draw_labels=True, alpha=0.5)

    if projection == ccrs.PlateCarree():
        ax.set_aspect('auto')
        plt.title(title, y=1.25, weight='bold') #size='xx-large',
    else:
        plt.title(title, y=1.15, weight='bold') #size='xx-large',
        plt.tight_layout()
    if show: plt.show()

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
