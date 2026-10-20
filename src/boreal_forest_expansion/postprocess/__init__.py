"""Postprocessing of NorESM2.3 (CAM + CLM) history output.

Modules
-------
variables : which variables to keep, by component and category
fileio    : find/check/open history files, validate and fix time, drop spin-up, save, load
derived   : secondary variables (Ghan, SOA columns and total, UV_meanvec, ET_veg, in-cloud)
averaging : weighted means (record length in days, cell area)
units     : unit conversion for plotting (processed files keep model units)
pipeline  : run() = the full raw -> processed chain for one case and component
"""
from . import averaging, derived, fileio, units, variables
from .pipeline import run

__all__ = ["run", "averaging", "derived", "fileio", "units", "variables"]
