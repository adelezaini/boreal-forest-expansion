"""
Core utilities for boreal_forest_expansion.

This module provides generic, reusable functions for:
- coordinate transformations
- xarray operations
- fitting
- landunit/gridcell conversions
"""

# Coordinates
from .coordinates import (
    convert360_180,
    convert180_360,
    convert_lsmcoord,
    convert_to_lsmcoord,
    match_coord,
    filter_lonlat,
)

# Landunit / normalization
from .landunit import (
    convert_landunit_to_gridcell,
    convert_gridcell_to_landunit,
)

# Xarray operations
from .xr_operations import (
    check_da_equal,
    xr_prod_along_dim,
)

# Fitting
from .fitting import (
    polynomial_fit,
    gaussian_fit,
)

__all__ = [
    # coordinates
    "convert360_180",
    "convert180_360",
    "convert_lsmcoord",
    "convert_to_lsmcoord",
    "match_coord",
    "filter_lonlat",

    # landunit
    "convert_landunit_to_gridcell",
    "convert_gridcell_to_landunit",

    # xarray ops
    "check_da_equal",
    "xr_prod_along_dim",

    # fitting
    "polynomial_fit",
    "gaussian_fit",
]
