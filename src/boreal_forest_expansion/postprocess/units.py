"""Unit conversion for plotting. Processed files keep model units; convert only here.

`convert(da, "mg m-2 yr-1")` looks up (current units -> target) in CONVERSIONS.
Guard against double conversion: if the DataArray is already in the target units,
it is returned unchanged.

Example
-------
>>> isop = units.convert(ds.SFISOP, "mg m-2 yr-1")     # kg/m2/s -> mg m-2 yr-1
>>> units.convert(isop, "mg m-2 yr-1") is isop          # second call: no-op
True

Changes vs the old code (old: postprocess.fix_units, functions.fix_soa/fix_cloud/fix_et)
--------------------------------------------------------------------------------------
- CHANGED conversion moved from save time to plot time; processed files keep model units.
- FIXED   CLDHGH/CLDLOW/CLDMED were multiplied by 1e3 and labelled g/kg; they are
          fractions (no conversion exists for them here, on purpose). CLDMED was listed
          twice in the condition and CLDTOT was left unconverted.
- FIXED   conversions could be applied twice (ACTNL: fix_units 1e-6, then fix_ds 1e-6,
          then functions.fix_cloud 1e-12). Now converting to the units a variable already
          has is a no-op.
- FIXED   `ds[var].values = ...` loaded every array into memory (dask); now lazy arithmetic.
- FIXED   functions.fix_soa / fix_cloud returned inside the loop (None if no match).
- REMOVED pure relabelling W/m^2 -> W/m$^2$ (LaTeX in metadata); format labels in plots.
"""
SECONDS_PER_DAY = 86400.0
DAYS_PER_YEAR = 365.0   # NorESM uses a noleap calendar

# (source units as written by the model, target units) -> multiplicative factor
CONVERSIONS = {
    # emission / deposition fluxes
    ("kg/m2/s", "mg m-2 yr-1"): 1e6 * SECONDS_PER_DAY * DAYS_PER_YEAR,
    ("kg/m2/sec", "mg m-2 yr-1"): 1e6 * SECONDS_PER_DAY * DAYS_PER_YEAR,   # MEG_* spelling
    ("kg/m2/s", "mg m-2 day-1"): 1e6 * SECONDS_PER_DAY,
    ("kg/m2/sec", "mg m-2 day-1"): 1e6 * SECONDS_PER_DAY,
    # mass mixing ratios and columns
    ("kg/kg", "ug/kg"): 1e9,
    ("kg/kg", "mg/kg"): 1e6,
    ("kg/m2", "mg m-2"): 1e6,
    ("kg/m2", "g m-2"): 1e3,
    # number concentrations
    ("m-3", "cm-3"): 1e-6,
    ("1/m2", "1e6 cm-2"): 1e-10,
    # water fluxes
    ("mm/s", "mm/day"): SECONDS_PER_DAY,
    ("mm H2O/s", "mm/day"): SECONDS_PER_DAY,
    # carbon fluxes
    ("gC/m^2/s", "gC m-2 yr-1"): SECONDS_PER_DAY * DAYS_PER_YEAR,
}

# Offsets (additive) for temperature
OFFSETS = {("K", "degC"): -273.15}


def convert(da, target):
    """Return `da` converted to `target` units (new object; attrs kept, `units` updated)."""
    source = da.attrs.get("units")
    if source == target:
        return da
    key = (source, target)
    if key in CONVERSIONS:
        out = da * CONVERSIONS[key]
    elif key in OFFSETS:
        out = da + OFFSETS[key]
    else:
        raise KeyError(f"No conversion {source!r} -> {target!r} for {da.name}; add it to CONVERSIONS")
    return out.assign_attrs(da.attrs, units=target)
