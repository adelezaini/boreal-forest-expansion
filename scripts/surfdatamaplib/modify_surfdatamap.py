###### This python file collects fuctions to modify PFT configuration, such as in surfdata_map file

####### Import packages
import numpy as np
import xarray as xr; xr.set_options(display_style='html')
import sys; sys.path.append(".")
from dataset_manipulation import *

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def apply_replacement_perc(config_init, replecement_perc, lnd_frac):
    """
    Given a percentage of replacement, this function applies the percentage over the initial configuration.
    The replacement is meant trees -> shrubs, shrubs -> grass. It can be expanded for grass-> bg.
    This means that the replacement_perc should have 2 natpft instead of 3, as the initial configuration.
    This first draft of func works on replacement_perc with 3 natpft to make it simple.
    The function than ignores the replacement_perc.natpft[0].
    In order to work properly the order of natpft is important: 3 natpfts in order trees-shrubs-grass
        Args:
            - config_init (DataArray - lon, lat, natpft): initial PFT configuration
            - replecement_perc (DataArray - lon, lat, natpft): percentage of replecement, spanning over lat-lon.It needs to have same natpfts as config_init to work
            - lnd_frac (DataArray): DataArray.LAND_FRAC, needed for filter some DataArray on the scheme lnd=0, nan=ocean
    """
    
    # Evaluate the ammount to subtract to shrubs+grass and to add to trees+shrubs
    diff = config_init * replecement_perc
    # Apply the difference to shrubs and grass
    d = config_init - diff
    ## Remember to ignore the first one: tree_pft = d.natpft[0]
    subtracted = d.where(d.natpft!= d.natpft[0], config_init.isel(natpft=0))
    # Apply the sum to trees and shrubs
    add = diff.roll(natpft=-1)
    added = subtracted+add
    added = added.where(added>0., 0.).where(lnd_frac>0.) #problem with negative 10^-5 values
    config_edited = added.where(added.natpft!=added.natpft[-1], subtracted.isel(natpft=-1)) # ignore the last one
    return config_edited

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def tree_aggregation(pfts, tree_indexes, tree_macro_index = 15, lnd_frac=xr.DataArray(None)):
    """Transform a PFT DataArray into a new one with tree PFTs aggregated into one single 'macro PFT'
        Return a DataArray with natpft index order [tree_indexes, other_indexes]. Change in adding index_order=list of indexes
        Args:
        - pfts (DataArray): original PFT DataArray
        - tree_indexes (list): list of the 'natpft' indexes corresponding to the tree PFTs
        - tree_macro_index (int): new 'macro PFT' index for the aggregated trees
        - lnd_frac (DataArray, also array): the sample is da.LAND_FRAC. It is needed because in the operation of the
        sum we loose the division 0=lnd vs nan=ocean.
        Return:
        - pfts_macro (DatArray): same as pfts but with (fewer and) different indexes, in the order [tree_macro_index, others]
    """
    ds = pfts.copy()
    dt = pfts.sel(natpft=tree_indexes).sum('natpft')
    if lnd_frac.any(): dt = dt.where(lnd_frac>0.)
    else: dt = dt.where(ds.isel(natpft=0)>=0.)
    dt = dt.assign_coords({"natpft":tree_macro_index}).expand_dims('natpft')
    old_indexes = ds['natpft'].values
    new_indexes = np.append(tree_macro_index, old_indexes[~np.isin(old_indexes,tree_indexes)])
    pfts_macro = xr.concat((dt, ds), dim='natpft').sel(natpft=new_indexes)
    pfts_macro = pfts_macro.assign_attrs(pfts.attrs)
    pfts_macro['natpft']=pfts_macro['natpft'].assign_attrs(pfts['natpft'].attrs)
    return pfts_macro

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def tree_separation(tree_macro, original_tree_pfts, lat_shift):
    """
    Disaggregation method for tree PFTs based on the original with a latitude shift applied
    Args:
    - tree_macro (DataArray): edited tree configuration - aggregated in one "macro" PFT
    - original_tree_pfts (DataArray): original tree configuration - disaggregated
    - lat_shift (float): latitude shift (north degree)
    Return:
    - tree_pfts (DataArray): disaggregated tree configuration
    """
    
    # Find percentage of tree occurrance [0-1]
    tree_perc_original = original_tree_pfts/original_tree_pfts.sum('natpft')
    
    # Apply the shift
    tree_perc = tree_perc_original.copy()
    tree_perc = tree_perc.assign_coords({'lat': tree_perc_original.lat+lat_shift})
    tree_perc = tree_perc.interp(lat=original_tree_pfts.lat)#.fillna(0.)
    
    # In applying the shift (and filtering where there is land), some gridcells are left NaN
    #-> just fill with previous values (approximation)
    tree_perc = tree_perc.where(tree_macro>0.).fillna(tree_perc_original)
    
    # Smooth it a bit to avoid topography dependence
    tree_perc = tree_perc.rolling(dict(lat=3, lon=3), center=True).mean().fillna(tree_perc)
    
    # In these operationations the overall normalisation to 1 is lost...
    tree_perc = tree_perc/tree_perc.sum('natpft')
    
    # From the sum, divide into the different pfts according to the percentage
    tree_pfts = tree_macro * tree_perc
    
    """
    # Let's keep normalization as much as possible
    a = tree_macro.copy()
    b = tree_pfts.sum('natpft')
    errata_diff = a-b
    # Add the difference to the first tree PFT
    tree_pfts[dict(natpft=0)] = tree_pfts[dict(natpft=0)].where(a != b, tree_pfts[dict(natpft=0)]+errata_diff)
    """
    return tree_pfts
    
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def tree_separation_longitude(pft_macro, tree_lon_perc, prod_along_dim, tree_indexes = [2,3,8], tree_macro_index=15, index_order=None, attrs=None):
    """Disaggregation method of the tree PFTs based on the longitude occurance percentage.
        Return a DataArray with natpft index order [tree_indexes, other_indexes]. Change in adding index_order=list of indexes
        Args:
        - pfts_macro (DataArray): PFT DataArray with 'macro PFTs' (e.g. tree PFTs aggregated into one 'macro PFT')
        - tree_lon_perc (DataArray): dim=['natpft, 'lon'] with the occurance percentage over longitude of the tree PFTs on the 'macro PFT'
        - tree_indexes (list): list of the 'natpft' indexes corresponding to the tree PFTs
        - tree_macro_index (int): new 'macro PFT' index for the aggregated trees
        Return:
        - pfts (DatArray): same as pfts but with indexes restored as previous aggregation, in the order [tree_indexes, others]
    """

    for t in tree_indexes:
        if t == 2:
            edited_trees = pft_macro.sel(natpft=tree_macro_index).assign_coords({"natpft":t}).expand_dims('natpft')
        else:
            et = pft_macro.sel(natpft=tree_macro_index).assign_coords({"natpft":t}).expand_dims('natpft')
            edited_trees = xr.concat((edited_trees, et), dim='natpft')

    edited_trees = prod_along_dim(edited_trees, tree_lon_perc, 'lon')

    # Let's keep normalization as much as possible
    a = pft_macro.sel(natpft=tree_macro_index)
    b = edited_trees.sum('natpft')
    errata_diff = a-b
    # Add the difference to the first tree PFT
    edited_trees = edited_trees.where(edited_trees.natpft != edited_trees.natpft[0],
                                      edited_trees.isel(natpft=0)+errata_diff)
    
    # Merge with the rest of the DataArray (shrubs & grass)
    if not index_order: old_indexes = pft_macro['natpft'].values; index_order = np.append(tree_indexes, old_indexes[~np.isin(old_indexes,tree_macro_index)])
    pfts = xr.concat((edited_trees, pft_macro), dim='natpft').sel(natpft=index_order)
    if attrs: pfts =pfts.assign_attrs(attrs)
    return pfts

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––#
def surfdatamap_modification(original_ds, pfts_tot, edited_pfts, method = None):
    """Apply the edited PFT configuration to the original surface data map
    Args:
    - original_ds (Dataset): original surface data map with all data varables and
    original coordinate sistem (lsmcoord)
    - pfts_tot (DataArray): data variable PCT_NAT_PFT of original_ds with coordinate convertion
    (lsmcoord -> lon/lat, 0-360 -> -180-180)
    - edited_pfts (DataArray): sub-DataArray of pfts_tot with just the edited (lat,lon, natpft)
    - method (string): if 'irregular_area' suitable for irregular area of edited_pfts to substitute.
    Otherwise, a basic approach replace a rectangular shape.
    
    Return:
    - edited_ds (Dataset): same as original_ds, but with edited
    """
    # Add modification to original PFT lon-lat range
    edited_config = pfts_tot.copy(deep=True)
    # Substitute area covered by non-NaN value of edited_pfts
    if method == 'irregular_area':
        # Idea: sum of 1. pfts_tot to which mask irreg. area covered by edited_pfts + 2. edited_pfts
        edited_config = pfts_tot.where(edited_pfts.isnull()).fillna(0.)+edited_pfts.fillna(0.)
    else: # Classical method: if area to substitute is rectangular
        edited_config.loc[dict(lat=edited_pfts.lat, lon=edited_pfts.lon, natpft=edited_pfts.natpft)] = edited_pfts

    """ Test: # first attempt, but way too slow and little elegant
    for n in edited_pfts.natpft.values:
        for lat in edited_pfts.lat.values:
            for lon in edited_pfts.lon.values:
                replacement_cell = edited_pfts.sel(natpft = n, lat = lat, lon = lon)
                if replacement_cell.values>=0.:
                    edited_config.loc[dict(lat=lat, lon=lon, natpft = n)] = replacement_cell
    """
    # Let's keep normalization as much as possible
    errata_diff = 100. - edited_config.sum('natpft')
    # Add the difference to the first tree PFT
    edited_config[dict(natpft=1)] = edited_config[dict(natpft=1)].where(edited_config.sum('natpft')==100., edited_config[dict(natpft=1)]+errata_diff)
    
    # Convert to orginal format
    ep = convert180_360(edited_config)
    ep = convert_to_lsmcoord(ep.fillna(0.))
    # Apply the change
    edited_ds = original_ds.copy(deep=True)
    edited_ds.PCT_NAT_PFT.loc[dict(lsmlat=ep.lsmlat, lsmlon=ep.lsmlon, natpft=ep.natpft)] = ep
    return edited_ds
