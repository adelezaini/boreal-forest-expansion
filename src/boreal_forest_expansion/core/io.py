from __future__ import annotations

import glob

import xarray as xr


def open_mfdataset_sorted(file_glob: str) -> xr.Dataset:
    """
    Open multiple NetCDF files matching a glob pattern and sort them by time.

    Parameters
    ----------
    file_glob
        Glob pattern matching one or more NetCDF files.

    Returns
    -------
    xr.Dataset
        Combined dataset, sorted along the time coordinate if present.

    Raises
    ------
    FileNotFoundError
        If no files match the provided glob pattern.

    Notes
    -----
    - Files are combined using xarray's 'by_coords' logic.
    - Time decoding is enabled.
    - `use_cftime=False` assumes the dataset can be decoded into standard datetime-like
      objects. This may need to be changed for model calendars such as 'noleap'.
    """
    files = sorted(glob.glob(file_glob))
    if not files:
        raise FileNotFoundError(f"No files found for pattern: {file_glob}")

    ds = xr.open_mfdataset(
        files,
        combine="by_coords",
        decode_times=True,
        parallel=False,
        use_cftime=False,
    )

    if "time" in ds.coords:
        ds = ds.sortby("time")

    return ds
