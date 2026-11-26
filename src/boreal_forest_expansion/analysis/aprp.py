"""APRP: Approximate Partial Radiative Perturbation (Taylor et al. 2007, J. Climate 20, 3637).

Splits the change of absorbed shortwave (SW) at the top of the atmosphere between two runs into
surface albedo, cloud (amount, scattering, absorption) and non-cloud atmosphere, month by month
and cell by cell, from standard monthly 2-D output.

Single-layer model of one column (all quantities normalised by the insolation S):

    alpha = S_up_TOA / S          planetary albedo (the quantity decomposed)
    Q     = S_dn_sfc / S          fraction of the insolation reaching the surface
    a     = S_up_sfc / S_dn_sfc   surface albedo
    mu    = alpha + Q (1 - a)     1 - atmospheric absorption
    gam   = (mu - Q) / (mu - a Q) atmospheric reflectance (one pass)
    A(mu, gam, a) = mu gam + mu a (1 - gam)^2 / (1 - a gam)

The column is inverted twice: clear sky (clear-sky fluxes) and overcast, with
F_oc = (F - (1 - c) F_clr) / c for every flux F and total cloud fraction c. The cloud is the
overcast column relative to the clear one: mu_oc = mu_clr mu_cld, 1 - gam_oc = (1 - gam_clr)(1 - gam_cld).
All-sky A = (1 - c) A(mu_clr, gam_clr, a_clr) + c A(mu_oc, gam_oc, a_oc).

Each term = -S_mean x centred partial change of A: swap one group of parameters forward from the
reference run and backward from the new run, average the two. Sign: positive = more SW absorbed.

Usage
-----
    from boreal_forest_expansion.analysis.aprp import aprp
    terms = aprp(ds_lcc, ds_ctrl, flux_set="clean")   # monthly xr.Dataset, W m-2
    terms["cloud"], terms["sfc_all"], terms["mask_sfc"], ...

`ds_new` / `ds_ref` hold the monthly variables of FLUX_SETS[flux_set] (see REQUIRED_VARS) plus
CLDTOT, on the same time axis. Yearly means: fm.annual_mean(terms[k], ds_ref).
Used in analysis/cloud-masking-aprp.ipynb (same maths, written there before this module).
"""

from __future__ import annotations

import numpy as np
import xarray as xr

C_MIN = 0.02   # cloud fraction below which the column is treated as clear (overcast fluxes undefined)
S_MIN = 1.0    # W m-2: insolation below which a month carries no SW (polar night)

# Upward/downward SW fluxes per flux set (rsut = TOA up, rsds/rsus = surface down/up, *cs = clear sky).
# "clean" = aerosol-free radiation calls (_DRF, the Ghan basis): the clean clear-sky TOA upward flux adds
# the above-model-top absorption of the clear-sky call (FSNTOAC - FSNTC) to FSNTCDRF; the clean clear-sky
# surface upward flux uses the clear-sky surface albedo (FSDSC - FSNSC) / FSDSC (not in the output).
# "allsky" = standard fluxes (include aerosols, so the cloud term is SWCF-like, not Ghan).
FLUX_SETS = {
    "clean": dict(rsut=lambda d: d.FSUTADRF,
                  rsutcs=lambda d: d.SOLIN - d.FSNTCDRF - (d.FSNTOAC - d.FSNTC),
                  rsds=lambda d: d.FSDS_DRF, rsus=lambda d: d.FSUS_DRF,
                  rsdscs=lambda d: d.FSDSCDRF,
                  rsuscs=lambda d: d.FSDSCDRF * ((d.FSDSC - d.FSNSC) / d.FSDSC.where(d.FSDSC > S_MIN)).fillna(0)),
    "allsky": dict(rsut=lambda d: d.SOLIN - d.FSNTOA, rsutcs=lambda d: d.SOLIN - d.FSNTOAC,
                   rsds=lambda d: d.FSDS, rsus=lambda d: d.FSDS - d.FSNS,
                   rsdscs=lambda d: d.FSDSC, rsuscs=lambda d: d.FSDSC - d.FSNSC),
}
REQUIRED_VARS = {
    "clean": ["SOLIN", "CLDTOT", "FSUTADRF", "FSNTCDRF", "FSNTOAC", "FSNTC", "FSDS_DRF", "FSUS_DRF",
              "FSDSCDRF", "FSDSC", "FSNSC"],
    "allsky": ["SOLIN", "CLDTOT", "FSNTOA", "FSNTOAC", "FSDS", "FSNS", "FSDSC", "FSNSC"],
}

# term -> parameters swapped; all-sky terms use the full model, clear-sky terms A_clr only
TERMS_ALL = {"sfc_all": ("a_clr", "a_oc"), "cld_amt": ("c",), "cld_scat": ("gam_cld",),
             "cld_abs": ("mu_cld",), "atm_all": ("mu_clr", "gam_clr")}
TERMS_CLR = {"sfc_clr": ("a_clr",), "atm_clr": ("mu_clr", "gam_clr")}

DESCRIPTIONS = {
    "sfc_all": "surface albedo, all-sky: -S dA(a_clr, a_oc)",
    "cld_amt": "cloud amount: -S dA(c)",
    "cld_scat": "cloud scattering: -S dA(gam_cld)",
    "cld_abs": "cloud absorption: -S dA(mu_cld)",
    "atm_all": "non-cloud atmosphere, all-sky: -S dA(mu_clr, gam_clr)",
    "sfc_clr": "surface albedo, clear-sky: -S dA_clr(a_clr)",
    "atm_clr": "non-cloud atmosphere, clear-sky: -S dA_clr(mu_clr, gam_clr)",
    "dF_all": "actual change of absorbed SW at TOA, all-sky",
    "dF_clr": "actual change of absorbed SW at TOA, clear-sky",
    "ins_all": "insolation change term dS (1 - mean alpha), all-sky",
    "ins_clr": "insolation change term dS (1 - mean alpha_clr), clear-sky",
    "res_all": "residual (non-linearity) = dF_all - ins_all - sum of all-sky terms",
    "res_clr": "residual (non-linearity) = dF_clr - ins_clr - sum of clear-sky terms",
    "recon_all": "|A_model - alpha| summed over both runs (inversion check, all-sky)",
    "recon_clr": "|A_model - alpha| summed over both runs (inversion check, clear-sky)",
    "cloud": "real cloud change = cld_amt + cld_scat + cld_abs",
    "mask_sfc": "surface-albedo cloud masking = sfc_all - sfc_clr",
    "mask_atm": "non-cloud-atmosphere cloud masking = atm_all - atm_clr",
    "cre": "APRP-basis cloud term = dF_all - dF_clr",
    "other": "cre - cloud - mask_sfc - mask_atm (residuals + insolation, small)",
    "mask_atm_other": "mask_atm + other",
}
PARAMETERS = {
    "c": "total cloud fraction (0 where c < C_MIN)",
    "a_clr": "surface albedo under clear sky",
    "a_oc": "surface albedo under overcast sky",
    "mu_clr": "1 - absorption of the clear-sky atmosphere",
    "gam_clr": "reflectance of the clear-sky atmosphere",
    "mu_cld": "mu_oc / mu_clr: 1 - cloud absorption",
    "gam_cld": "1 - (1 - gam_oc) / (1 - gam_clr): cloud reflectance",
}


def _ratio(a, b, fill):
    ok = np.abs(b) > 1e-6
    return np.where(ok, a / np.where(ok, b, 1.0), fill)


def _mu_gam(alpha, qhat, a):
    mu = alpha + qhat * (1 - a)
    return mu, _ratio(mu - qhat, mu - a * qhat, 0.0)


def _A1(mu, gam, a):
    """Planetary albedo of the single-layer column."""
    return mu * gam + mu * a * (1 - gam) ** 2 / (1 - a * gam)


def _albedo_all(p):
    A_oc = _A1(p["mu_clr"] * p["mu_cld"], 1 - (1 - p["gam_clr"]) * (1 - p["gam_cld"]), p["a_oc"])
    return (1 - p["c"]) * _A1(p["mu_clr"], p["gam_clr"], p["a_clr"]) + p["c"] * A_oc


def _albedo_clr(p):
    return _A1(p["mu_clr"], p["gam_clr"], p["a_clr"])


def _dA(fun, p_ref, p_new, keys):
    """Centred partial albedo change: swap `keys` forward from the reference and backward from the new state."""
    swap = lambda p, q: {**p, **{k: q[k] for k in keys}}
    return 0.5 * ((fun(swap(p_ref, p_new)) - fun(p_ref)) + (fun(p_new) - fun(swap(p_new, p_ref))))


def _params_np(d: xr.Dataset, flux_set: str, c_min: float, s_min: float):
    """APRP parameters of one run (numpy), insolation, all-sky and clear-sky upward TOA flux."""
    missing = [v for v in REQUIRED_VARS[flux_set] if v not in d]
    if missing:
        raise KeyError(f"APRP ({flux_set}) needs {missing}")
    f = {k: np.asarray(v(d).values, dtype="float64") for k, v in FLUX_SETS[flux_set].items()}
    S = np.asarray(d.SOLIN.values, dtype="float64")
    c = np.clip(np.asarray(d.CLDTOT.values, dtype="float64"), 0, 1)
    cloudy = c >= c_min
    cc = np.where(cloudy, c, 1.0)
    oc = {k: np.where(cloudy, (f[k] - (1 - c) * f[k + "cs"]) / cc, f[k + "cs"]) for k in ("rsut", "rsds", "rsus")}
    a_clr = np.clip(_ratio(f["rsuscs"], f["rsdscs"], 0.0), 0, 0.999)
    a_oc = np.clip(np.where(oc["rsds"] > s_min, _ratio(oc["rsus"], oc["rsds"], 0.0), a_clr), 0, 0.999)
    Sx = np.where(S > s_min, S, 1.0)
    mu_clr, gam_clr = _mu_gam(f["rsutcs"] / Sx, f["rsdscs"] / Sx, a_clr)
    mu_oc, gam_oc = _mu_gam(oc["rsut"] / Sx, oc["rsds"] / Sx, a_oc)
    p = dict(c=np.where(cloudy, c, 0.0), a_clr=a_clr, a_oc=a_oc, mu_clr=mu_clr, gam_clr=gam_clr,
             mu_cld=np.where(cloudy, _ratio(mu_oc, mu_clr, 1.0), 1.0),
             gam_cld=np.where(cloudy, 1 - _ratio(1 - gam_oc, 1 - gam_clr, 1.0), 0.0))
    return p, S, f["rsut"], f["rsutcs"]


def aprp_parameters(d: xr.Dataset, flux_set: str = "clean", c_min: float = C_MIN,
                    s_min: float = S_MIN) -> xr.Dataset:
    """Single-layer parameters of one run (c, a_clr, a_oc, mu_clr, gam_clr, mu_cld, gam_cld)."""
    p, *_ = _params_np(d, flux_set, c_min, s_min)
    like = d["SOLIN"]
    return xr.Dataset({k: xr.DataArray(v, dims=like.dims, coords=like.coords, attrs=dict(long_name=PARAMETERS[k]))
                       for k, v in p.items()}, attrs=dict(flux_set=flux_set))


def aprp(ds_new: xr.Dataset, ds_ref: xr.Dataset, flux_set: str = "clean", c_min: float = C_MIN,
         s_min: float = S_MIN) -> xr.Dataset:
    """Monthly APRP terms of ds_new - ds_ref (W m-2, positive = more SW absorbed).

    Variables: sfc_all, cld_amt, cld_scat, cld_abs, atm_all (all-sky terms); sfc_clr, atm_clr
    (clear-sky terms); dF_*, ins_*, res_*, recon_* (actual change, insolation term, residual,
    inversion check); cloud, mask_sfc, mask_atm, cre, other, mask_atm_other (combinations).
    If both datasets hold SW_cloud (Ghan: FSNT_DRF - FSNTCDRF), ghan_cloud and top_diff = ghan_cloud - cre
    are added. Months with S < s_min in either run are 0.
    """
    if flux_set not in FLUX_SETS:
        raise ValueError(f"flux_set must be one of {list(FLUX_SETS)}")
    if not np.array_equal(ds_new["time"].values, ds_ref["time"].values):
        raise ValueError("ds_new and ds_ref have different time axes")
    p1, S1, up1, upc1 = _params_np(ds_ref, flux_set, c_min, s_min)
    p2, S2, up2, upc2 = _params_np(ds_new, flux_set, c_min, s_min)
    lit = (S1 > s_min) & (S2 > s_min)
    Sm, dS = 0.5 * (S1 + S2), S2 - S1
    o = {}
    for fun, terms, sfx, upa, upb in ((_albedo_all, TERMS_ALL, "all", up1, up2),
                                      (_albedo_clr, TERMS_CLR, "clr", upc1, upc2)):
        for name, keys in terms.items():
            o[name] = np.where(lit, -Sm * _dA(fun, p1, p2, keys), 0.0)
        # actual change of the absorbed SW and its exact split -S̄ ΔA + ΔS (1 - Ā)
        A1, A2 = _ratio(upa, S1, 0.0), _ratio(upb, S2, 0.0)
        o[f"dF_{sfx}"] = np.where(lit, (S2 - upb) - (S1 - upa), 0.0)
        o[f"ins_{sfx}"] = np.where(lit, dS * (1 - 0.5 * (A1 + A2)), 0.0)
        o[f"recon_{sfx}"] = np.where(lit, np.abs(fun(p1) - A1) + np.abs(fun(p2) - A2), 0.0)
    for sfx, terms in (("all", TERMS_ALL), ("clr", TERMS_CLR)):
        o[f"res_{sfx}"] = o[f"dF_{sfx}"] - o[f"ins_{sfx}"] - sum(o[k] for k in terms)
    o["cloud"] = o["cld_amt"] + o["cld_scat"] + o["cld_abs"]
    o["mask_sfc"] = o["sfc_all"] - o["sfc_clr"]
    o["mask_atm"] = o["atm_all"] - o["atm_clr"]
    o["cre"] = o["dF_all"] - o["dF_clr"]
    o["other"] = o["cre"] - o["cloud"] - o["mask_sfc"] - o["mask_atm"]
    o["mask_atm_other"] = o["mask_atm"] + o["other"]
    attrs = {}
    if "SW_cloud" in ds_new and "SW_cloud" in ds_ref:
        o["ghan_cloud"] = (ds_new["SW_cloud"] - ds_ref["SW_cloud"]).values
        o["top_diff"] = o["ghan_cloud"] - o["cre"]   # above-model-top absorption, clear-sky surface proxy
        attrs = dict(ghan_cloud="Ghan SW cloud term change, d(FSNT_DRF - FSNTCDRF)",
                     top_diff="ghan_cloud - cre")
    like = ds_ref["SOLIN"]
    return xr.Dataset(
        {k: xr.DataArray(v, dims=like.dims, coords=like.coords,
                         attrs=dict(units="W m-2", long_name=DESCRIPTIONS.get(k, attrs.get(k, k))))
         for k, v in o.items()},
        attrs=dict(flux_set=flux_set, method="APRP, Taylor et al. 2007", c_min=c_min, s_min=s_min,
                   sign="positive = more SW absorbed (warming)"))
