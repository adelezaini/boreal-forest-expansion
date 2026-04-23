from __future__ import annotations

import xarray as xr

from .metadata import get_units


def add_derived_cam_fields(ds: xr.Dataset) -> xr.Dataset:
    """
    Add derived CAM-style variables when enough source fields are present.
    """
    if "RESTOM" not in ds and "FSNT" in ds and "FLNT" in ds:
        ds["RESTOM"] = ds["FSNT"] - ds["FLNT"]
        ds["RESTOM"].attrs["units"] = get_units(ds["FSNT"])
        ds["RESTOM"].attrs["long_name"] = (
            "Top-of-atmosphere net downward radiation (FSNT - FLNT)"
        )

    return ds
