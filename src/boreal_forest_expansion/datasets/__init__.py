"""
Datasets utilities for boreal_forest_expansion.

This module provides:
- readers for LPJ-GUESS data
- redears for NorESM dataset
- variable catalogs
- export helper
"""

# LPJ-GUESS readers
from .lpjguess import (
    dataframe_from_LPJGUESS,
    DataArray_from_LPJGUESS,
    pftnames_LPJGUESS,
)

# NorESM datasets
from .noresm_datasets import (
    fix_cam_time,
    create_dataset,
)

# Variable catalog
from .datavariables_catalog import (
    atm_always_include,
    lnd_always_include,
    pressure_variables,
    Ghan_vars,
    variables_by_component,
)

# Export
from .export import (
    save_postprocessed,
)

__all__ = [
    # lpjguess
    "dataframe_from_LPJGUESS",
    "DataArray_from_LPJGUESS",
    "pftnames_LPJGUESS",

    # noresm datasets
    "fix_cam_time",
    "create_dataset",

    # variable catalog
    "atm_always_include",
    "lnd_always_include",
    "pressure_variables",
    "Ghan_vars",
    "variables_by_component",

    # export
    "save_postprocessed",
]
