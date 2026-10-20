"""
Postprocessing utilities for boreal_forest_expansion.

This package provides tools to:
- open selected NorESM/CAM output
- fix CAM/CLM monthly timestamps
- select available variables safely
- compute annual means and climatologies
- add general derived/display variables
- compute CAM-chem CH4/BVOC/O3 diagnostics
- compute Ghan-style radiative decomposition diagnostics
"""

from .transform import (
    fix_cam_time,
    open_selected_dataset,
    present_vars,
    missing_vars,
    select_present,
    month_length_weights,
    annual_mean,
    climatology,
    add_display_unit_variables,
    add_general_derived_variables,
    transform_dataset,
)

from .chemistry_postprocess import (
    add_pressure_diagnostics,
    add_ch4_diagnostics,
    add_bvoc_diagnostics,
    add_ozone_diagnostics,
    make_monthly_diagnostics,
    make_map_diagnostics,
    make_annual_diagnostics,
    make_climatology,
    difference,
    relative_difference_percent,
    paired_comparison,
)

from .ghan_decomposition import (
    REQUIRED_GHAN_VARS,
    has_ghan_inputs,
    missing_ghan_inputs,
    add_ghan_decomposition,
    aerosol_cloud_forcing_scomposition_Ghan,
)

__all__ = [
    # transform
    "fix_cam_time",
    "open_selected_dataset",
    "present_vars",
    "missing_vars",
    "select_present",
    "month_length_weights",
    "annual_mean",
    "climatology",
    "add_display_unit_variables",
    "add_general_derived_variables",
    "transform_dataset",

    # chemistry_postprocess
    "add_pressure_diagnostics",
    "add_ch4_diagnostics",
    "add_bvoc_diagnostics",
    "add_ozone_diagnostics",
    "make_monthly_diagnostics",
    "make_map_diagnostics",
    "make_annual_diagnostics",
    "make_climatology",
    "difference",
    "relative_difference_percent",
    "paired_comparison",

    # ghan_decomposition
    "REQUIRED_GHAN_VARS",
    "has_ghan_inputs",
    "missing_ghan_inputs",
    "add_ghan_decomposition",
    "aerosol_cloud_forcing_scomposition_Ghan",
]