"""Secondary variables (computed here, not written by the model).

Every secondary variable gets the attribute  secondary = "yes"  and a `derived_from`
attribute, so it is never confused with model output.

Contents
--------
1. Ghan (2013) decomposition of top-of-model fluxes      -> category RADIATIVE (atm)
2. SOA column burdens SOA_A1_cb, SOA_NA_cb, SOA_cb       -> category SOA (atm)
   and total SOA mixing ratio SOA_TOT
3. Small diagnostics: UV_meanvec -> METEO (atm), ET_veg -> ET (lnd)
4. incloud(): in-cloud averages of AREL, AWNC, ACTREL, ACTNL (analysis-time function)

Inputs: a function computing secondary variables for a REQUESTED category raises
KeyError if any input is missing (no silent skipping), and ValueError if units or the
vertical grid are not as expected.

Changes vs the old code (old: postprocess.aerosol_cloud_forcing_scomposition_Ghan,
postprocess.fix_ds; functions.fix_radiative_names, add_SOA_TOT, fix_et)
--------------------------------------------------------------------------------------
Ghan decomposition (formulas unchanged, names and labels changed):
- FIXED   the old code OVERWROTE the model's SWCF and LWCF with the Ghan clean-sky cloud
          terms; the same name then meant two different quantities. New names:
              old SWDIR / LWDIR / DIR      -> SW_dir / LW_dir / NET_dir
              old SWCF  / LWCF  / NCFT     -> SW_cre_clean / LW_cre_clean / NET_cre_clean
              old SW_rest / LW_rest / FREST -> SW_clearclean / LW_clearclean / NET_clearclean
              old FTOT                     -> NET_toa
              old SWTOT / LWTOT            -> removed (copies of FSNT and -FLNT)
- FIXED   long_names said "forcing"; these are fluxes/effects of ONE run. Forcing is the
          difference between runs.
- FIXED   LW_rest and LWTOT lost their units attribute (unary minus drops attrs).
- ADDED   attribute secondary="yes" on every term.
SOA:
- ADDED   SOA_A1_cb, SOA_NA_cb, SOA_cb computed offline (cb_SOA_* are no longer output).
          Old cb_SOA_dry / cb_SOA_TOT used model fields that no longer exist.
- NOT REPLACED  the old cloud-water burdens cb_SOA_*_OCW: cloud-borne SOA is not in the
          current output and cannot be rebuilt offline (would need fincl in new runs).
- ADDED   (review round 2) SOA_TOT = SOA_A1 + SOA_NA (old functions.add_SOA_TOT).
- FIXED   (review round 2) column sum uses skipna=False: an all-NaN profile gives NaN,
          not 0 (xarray's default skips NaN; tested). Units of P0, PS, SOA_* and the
          sign of every layer thickness are now checked.
Other diagnostics:
- ADDED   (review round 2) ET_veg = QVEGE + QVEGT. The old functions.fix_et computed
          QFLX_EVAP_TOT - QSOIL, which equals this sum only if no other term enters
          QFLX_EVAP_TOT (not verified); the explicit sum says what it is.
- ADDED   (review round 2) UV_meanvec = sqrt(U^2 + V^2) of the MONTHLY-MEAN wind
          components: magnitude of the mean wind vector at model levels. It is NOT the mean
          wind speed (lower when wind direction varies) and NOT U10 (10 m wind speed).
          Replaces the old WIND_SPEED, which also wrote its units on the dataset.
- REMOVED T_C (use units.convert(ds.T, "degC")).
In-cloud values:
- FIXED   ACTNL_incld was 1e6 too small: fix_units had already converted ACTNL to cm-3
          and fix_ds multiplied by 1e-6 again (functions.fix_cloud applied another 1e-12).
- CHANGED in-cloud values are no longer stored; incloud() computes them at analysis time
          as a ratio of means, with low cloud fraction masked (old: per-month ratio, only
          exact zeros masked).
- CHANGED (review round 2) averages inside incloud() are weighted: by record length in
          days over time and by cell area over lat/lon (see averaging.py).
"""
import logging

import numpy as np

from .averaging import weighted_mean

log = logging.getLogger(__name__)

GRAVITY = 9.80616   # m s-2, CESM shared constant SHR_CONST_G (used by CAM for column burdens)


def _secondary(da, name, units, long_name, derived_from, **extra):
    return da.rename(name).assign_attrs(
        units=units, long_name=long_name, secondary="yes",
        derived_from=derived_from, **extra)


def _require(ds, names, what):
    """Raise KeyError naming the missing inputs of `what`."""
    missing = [v for v in names if v not in ds]
    if missing:
        raise KeyError(f"{what} needs {', '.join(missing)}, which are not in the history files. "
                       "Process the other categories with --categories, or add the fields to fincl.")


def _check_units(ds, expected):
    """Raise ValueError if any variable's `units` attribute differs from `expected`."""
    wrong = {v: ds[v].attrs.get("units") for v, u in expected.items() if ds[v].attrs.get("units") != u}
    if wrong:
        raise ValueError(f"Unexpected units {wrong}; expected {expected}")


# ----------------------------------------------------------------------------- 1. Ghan
GHAN_INPUTS = ["FSNT", "FLNT", "FSNT_DRF", "FLNT_DRF", "FSNTCDRF", "FLNTCDRF"]


def ghan_decomposition(ds):
    """Ghan (2013, ACP 13, 9971) decomposition of the net top-of-model flux of ONE run.

    Sign: positive = downward (energy into the system). FLNT is positive upward.
    The *_DRF fields come from an extra radiation call with aerosol optical depth = 0
    ("clean"), made on the same radiation timesteps as FSNT/FLNT (verified in OsloAero
    radiation.F90), so the terms below are consistent and close exactly:

        NET_dir + NET_cre_clean + NET_clearclean == NET_toa

    Differences between two runs give:
        d(NET_dir)        -> ERFari  (aerosol-radiation interactions)
        d(NET_cre_clean)  -> cloud term (ERFaci + cloud adjustments)
        d(NET_clearclean) -> surface albedo and other clear-sky, aerosol-free changes
    """
    _require(ds, GHAN_INPUTS, "Ghan decomposition")
    src = "Ghan (2013) decomposition of " + ", ".join(GHAN_INPUTS)
    sw_dir = ds.FSNT - ds.FSNT_DRF
    lw_dir = -(ds.FLNT - ds.FLNT_DRF)
    sw_cre = ds.FSNT_DRF - ds.FSNTCDRF
    lw_cre = -(ds.FLNT_DRF - ds.FLNTCDRF)
    sw_clr = ds.FSNTCDRF
    lw_clr = -ds.FLNTCDRF
    terms = {
        "SW_dir": (sw_dir, "SW aerosol direct radiative effect (all-sky)"),
        "LW_dir": (lw_dir, "LW aerosol direct radiative effect (all-sky)"),
        "NET_dir": (sw_dir + lw_dir, "Net aerosol direct radiative effect (all-sky)"),
        "SW_cre_clean": (sw_cre, "SW cloud radiative effect without aerosol (clean)"),
        "LW_cre_clean": (lw_cre, "LW cloud radiative effect without aerosol (clean)"),
        "NET_cre_clean": (sw_cre + lw_cre, "Net cloud radiative effect without aerosol (clean)"),
        "SW_clearclean": (sw_clr, "SW net flux, clear-sky and aerosol-free"),
        "LW_clearclean": (lw_clr, "LW net flux (down positive), clear-sky and aerosol-free"),
        "NET_clearclean": (sw_clr + lw_clr, "Net flux, clear-sky and aerosol-free"),
        "NET_toa": (ds.FSNT - ds.FLNT, "Net flux at top of model (down positive)"),
    }
    return {name: _secondary(da, name, "W/m2", long_name, src, sign_convention="positive down")
            for name, (da, long_name) in terms.items()}


# ------------------------------------------------------------------------------ 2. SOA
SOA_SPECIES = ["SOA_A1", "SOA_NA"]
_GRID = ["P0", "PS", "hyai", "hybi"]


def layer_thickness(ds):
    """Pressure thickness of each model layer [Pa], dims (time, lev, lat, lon).

    p_interface = hyai * P0 + hybi * PS ;  dp_k = p(k+1/2) - p(k-1/2)

    Checked (ValueError if not met): P0 and PS in Pa; ilev has one more level than lev;
    dp > 0 in every layer. Because dp_k is linear in PS, checking it at the minimum and
    maximum PS in the data proves it for every grid cell and month.

    Convention: uses the full (moist) surface pressure, as CAM does for its own cb_*
    column burdens (chm_diags receives state%pdel, OsloAero chemistry.F90).
    """
    _require(ds, _GRID, "Layer thickness")
    _check_units(ds, {"P0": "Pa", "PS": "Pa"})
    if ds.sizes["ilev"] != ds.sizes["lev"] + 1:
        raise ValueError(f"Expected len(ilev) = len(lev) + 1, got {ds.sizes['ilev']} and {ds.sizes['lev']}")

    d_a = np.diff(ds.hyai.values) * float(ds.P0)
    d_b = np.diff(ds.hybi.values)
    ps_range = [float(ds.PS.min()), float(ds.PS.max())]
    for ps in ps_range:
        bad = np.flatnonzero(d_a + d_b * ps <= 0)
        if bad.size:
            raise ValueError(f"Non-positive layer thickness at PS = {ps:.0f} Pa in layers {bad.tolist()}: "
                             "check the order of hyai/hybi (top to bottom expected)")

    p_int = (ds.hyai * ds.P0 + ds.hybi * ds.PS).drop_vars("ilev", errors="ignore")
    below = p_int.isel(ilev=slice(1, None)).rename(ilev="lev")
    above = p_int.isel(ilev=slice(None, -1)).rename(ilev="lev")
    dp = (below - above).assign_coords(lev=ds.lev)    # stays lazy (dask)
    return dp.assign_attrs(units="Pa", long_name="layer pressure thickness")


def soa_columns(ds):
    """Column burdens SOA_A1_cb, SOA_NA_cb and their sum SOA_cb  [kg m-2].

    Formula: sum_k q_k * dp_k / g, from MONTHLY MEANS of q and PS.

    Conventions and limits (documented, not corrected):
    - Mass basis: q is multiplied by the moist layer thickness, the same convention as
      CAM's own cb_* fields, so values are comparable with the old cb_SOA_*. CAM registers
      chemistry tracers as 'dry' mixing ratios; a strictly dry-air column would use
      dp * (1 - Q). Expected difference: of the order of the water-vapour mixing ratio,
      roughly <= 1-2 % (inference, not computed).
    - Monthly means: misses the within-month covariance of q and dp; expected small
      (not quantified).
    - NaN: an incomplete or all-NaN profile gives NaN (skipna=False), never a partial sum.
    - Cloud-borne SOA (old cb_SOA_*_OCW) is not included; it is not in the output.
    """
    _require(ds, SOA_SPECIES, "SOA column burdens")
    _check_units(ds, {sp: "kg/kg" for sp in SOA_SPECIES})
    for sp in SOA_SPECIES:
        if "lev" not in ds[sp].dims:
            raise ValueError(f"{sp} has no 'lev' dimension: {ds[sp].dims}")
    dp = layer_thickness(ds)
    note = ("offline from monthly means of q and PS, moist dp (CAM cb_ convention); "
            "not the model cb_ diagnostic; excludes cloud-borne SOA")
    out = {}
    for sp in SOA_SPECIES:
        col = (ds[sp] * dp).sum("lev", skipna=False) / GRAVITY
        out[f"{sp}_cb"] = _secondary(col, f"{sp}_cb", "kg/m2", f"{sp} column burden",
                                     f"sum({sp} * dp) / g", comment=note)
    total = out["SOA_A1_cb"] + out["SOA_NA_cb"]
    out["SOA_cb"] = _secondary(total, "SOA_cb", "kg/m2", "SOA column burden (A1 + NA)",
                               "SOA_A1_cb + SOA_NA_cb", comment=note)
    return out


def soa_total(ds):
    """SOA_TOT = SOA_A1 + SOA_NA  [kg/kg] (mixing ratio, interstitial aerosol)."""
    _require(ds, SOA_SPECIES, "SOA_TOT")
    _check_units(ds, {sp: "kg/kg" for sp in SOA_SPECIES})
    return {"SOA_TOT": _secondary(ds.SOA_A1 + ds.SOA_NA, "SOA_TOT", "kg/kg",
                                  "total SOA mixing ratio (A1 + NA)", "SOA_A1 + SOA_NA")}


# ---------------------------------------------------------------------- 3. other
def wind_meanvec(ds):
    """UV_meanvec = sqrt(U^2 + V^2) of the monthly-mean wind components [m/s].

    This is the magnitude of the MEAN horizontal wind vector at model levels. It is
    smaller than the mean wind speed whenever the wind direction varies within the month,
    and it is a different quantity from U10 (10 m wind speed).
    """
    _require(ds, ["U", "V"], "UV_meanvec")
    _check_units(ds, {"U": "m/s", "V": "m/s"})
    return {"UV_meanvec": _secondary(np.sqrt(ds.U ** 2 + ds.V ** 2), "UV_meanvec", "m/s",
                                     "magnitude of the monthly-mean horizontal wind vector",
                                     "sqrt(U**2 + V**2) of monthly means",
                                     comment="not the mean wind speed; not U10")}


def et_veg(ds):
    """ET_veg = QVEGE + QVEGT: canopy evaporation + transpiration [same units as inputs]."""
    _require(ds, ["QVEGE", "QVEGT"], "ET_veg")
    units = ds.QVEGE.attrs.get("units")
    _check_units(ds, {"QVEGT": units})
    return {"ET_veg": _secondary(ds.QVEGE + ds.QVEGT, "ET_veg", units,
                                 "vegetation evapotranspiration (canopy evaporation + transpiration)",
                                 "QVEGE + QVEGT")}


# Secondary variables computed by the pipeline, and the category file they go into.
DERIVED_BY_CATEGORY = {
    "atm": {"RADIATIVE": [ghan_decomposition],
            "SOA": [soa_columns, soa_total],
            "METEO": [wind_meanvec]},
    "lnd": {"ET": [et_veg]},
}


def add_derived(ds, component, categories):
    """Compute the secondary variables for the requested categories.

    Returns (ds, {category: [new variable names]}). Raises if inputs are missing.
    """
    added = {}
    for cat in categories:
        for func in DERIVED_BY_CATEGORY[component].get(cat, []):
            new = func(ds)
            ds = ds.assign(new)
            added.setdefault(cat, []).extend(new)
    return ds, added


# ---------------------------------------------------------------------- 4. in-cloud
# Model output (micro_mg_cam.F90): AREL = r_eff * f_liq, AWNC = N_incloud * f_liq,
# FREQL = f_liq  (only where f_liq > 0.01 and in-cloud liquid > 5e-5 kg/kg, else 0).
# Cloud top (ACTREL, ACTNL, FCTL): first level from the top with liquid OR ice cloud;
# ice-topped columns give 0.
INCLOUD_PAIRS = {
    "AREL": "FREQL", "AWNC": "FREQL",
    "ACTREL": "FCTL", "ACTNL": "FCTL",
}


def incloud(ds, var, dim=None, min_frac=0.01, weights=None):
    """In-cloud value of `var`, weighted by liquid cloud fraction.

    With `dim`, numerator and denominator are averaged separately, then divided:
        weighted_mean(AREL) / weighted_mean(FREQL)
    This is the cloud-fraction-weighted in-cloud value: each month (and grid cell)
    counts in proportion to how much liquid cloud it had. It is the consistent way to
    aggregate, and comparable with cloud-weighted satellite products.

    The mean of per-month ratios, weighted_mean(incloud(ds, var), "time", ds), answers a
    different question (typical in-cloud value of a single month, every month equal);
    use it deliberately if that is what you need.

    Weights: by default record length in days (time) and cell area (lat/lon), from `ds`
    (see averaging.default_weights); pass `weights` to override.
    Points where the (mean) cloud fraction is below `min_frac` are set to NaN.

    Example
    -------
    >>> reff_djf = incloud(ds.sel(time=ds.time.dt.season == "DJF"), "AREL", dim="time")
    >>> nd_monthly = incloud(ds, "ACTNL")            # dim=None: month by month
    """
    frac_name = INCLOUD_PAIRS[var]
    num, frac = ds[var], ds[frac_name]
    if dim is not None:
        num = weighted_mean(num, dim, ds, weights)
        frac = weighted_mean(frac, dim, ds, weights)
    out = (num / frac).where(frac >= min_frac)
    how = (f"weighted_mean({var}) / weighted_mean({frac_name}) over {dim}" if dim is not None
           else f"{var} / {frac_name}")
    return out.rename(f"{var}_incld").assign_attrs(
        units=ds[var].attrs.get("units"),
        long_name=f"in-cloud {var} (liquid-cloud-fraction weighted)",
        secondary="yes", derived_from=f"{how}; {frac_name} >= {min_frac}")
