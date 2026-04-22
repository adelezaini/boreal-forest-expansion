from __future__ import annotations

import xarray as xr

from .metadata import get_units


def maybe_convert_units(da: xr.DataArray, varname: str) -> xr.DataArray:
    """
    Convert selected variables into more interpretable units when possible.
    """
    units = get_units(da).lower()

    if varname.upper() == "PRECT":
        if units in {"m/s", "m s-1"}:
            out = da * 1000.0 * 86400.0
            out.attrs["units"] = "mm/day"
            return out

        if units in {"kg/m2/s", "kg m-2 s-1"}:
            out = da * 86400.0
            out.attrs["units"] = "mm/day"
            return out

    if varname.upper() in {"PSL", "PS"} and units == "pa":
        out = da / 100.0
        out.attrs["units"] = "hPa"
        return out

    return da
