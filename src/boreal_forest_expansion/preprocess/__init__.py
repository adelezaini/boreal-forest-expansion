"""
Preprocessing / vegetation manipulation utilities.

This module provides functions to:
- manipulate forest/PFT configurations
- convert LPJ-GUESS PFTs to CLM
- apply modifications to surfdata maps
"""

# Forest / PFT operations
from .forest_operations import (
    apply_replacement_perc,
    tree_aggregation,
    tree_separation,
    tree_separation_longitude,
)

# PFT conversion
from .pft_conversion import (
    convert_lpjguess_to_clm_pfts,
    convert_lpjguess_to_clm_pfts_finegrid,
)

# Surfdata editing
from .surfdata_edit import (
    surfdatamap_modification,
)

__all__ = [
    # forest operations
    "apply_replacement_perc",
    "tree_aggregation",
    "tree_separation",
    "tree_separation_longitude",

    # PFT conversion
    "PFT_convert_LPJGUESS_to_CLM",
    "PFT_convert_LPJGUESS_to_CLM_finegrid",

    # surfdata
    "surfdatamap_modification",
]
