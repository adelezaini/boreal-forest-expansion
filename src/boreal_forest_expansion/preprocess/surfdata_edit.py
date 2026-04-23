###### 

####### Import packages
import numpy as np
import xarray as xr; xr.set_options(display_style='html')
import sys; sys.path.append(".")
from boreal_forest_expansion.core.coordinates import convert180_360, convert_to_lsmcoord


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
