"""Ghan (2013) TOA flux decomposition, split into SW, LW and net.

Same definitions and sign convention as postprocess.derived.ghan_decomposition (a):
all terms are DOWNWARD POSITIVE at the top of the model, so a positive difference
warms the system. CAM: FSNT is net SW down, FLNT is net LW up (a).

    F         = all-sky flux                      (FSNT, FLNT)
    F_clean   = all-sky without aerosol (_DRF)     (FSNT_DRF, FLNT_DRF)
    F_cc      = clear-sky without aerosol (CDRF)   (FSNTCDRF, FLNTCDRF)

    ari   = F       - F_clean      aerosol-radiation interaction (direct)
    cloud = F_clean - F_cc         cloud radiative effect, aerosol removed
    clear = F_cc                   clean clear-sky: surface albedo, gases, temperature
    total = ari + cloud + clear = F

Differences of these terms between two runs give Delta-ari, Delta-cloud (aci plus any
other cloud change), Delta-clear (SW: albedo; LW: surface temperature, water vapour,
ozone ...). Names in postprocess.derived -> here:
    SW_dir -> ari_SW         LW_dir -> ari_LW         NET_dir -> ari_net
    SW_cre_clean -> cloud_SW LW_cre_clean -> cloud_LW NET_cre_clean -> cloud_net
    SW_clearclean -> clear_SW LW_clearclean -> clear_LW NET_clearclean -> clear_net
    NET_toa -> total_net
"""

from __future__ import annotations

import xarray as xr

GHAN_INPUTS = ["FSNT", "FLNT", "FSNT_DRF", "FLNT_DRF", "FSNTCDRF", "FLNTCDRF"]
COMPONENTS = ["ari", "cloud", "clear", "total"]
BANDS = ["SW", "LW", "net"]

COMPONENT_LABELS = {
    "ari": "ari (direct)",
    "cloud": "cloud",
    "clear": "clean clear-sky",
    "total": "total",
}


def term_name(component: str, band: str) -> str:
    return f"{component}_{band}"


def ghan_terms(ds: xr.Dataset) -> xr.Dataset:
    """Return the 12 terms (4 components x SW/LW/net), downward positive, W m-2."""
    missing = [v for v in GHAN_INPUTS if v not in ds]
    if missing:
        raise KeyError(f"Ghan decomposition needs {missing}")

    sw = {
        "ari": ds.FSNT - ds.FSNT_DRF,
        "cloud": ds.FSNT_DRF - ds.FSNTCDRF,
        "clear": ds.FSNTCDRF,
        "total": ds.FSNT,
    }
    lw = {  # minus sign: FLNT is upward positive
        "ari": -(ds.FLNT - ds.FLNT_DRF),
        "cloud": -(ds.FLNT_DRF - ds.FLNTCDRF),
        "clear": -ds.FLNTCDRF,
        "total": -ds.FLNT,
    }
    out = xr.Dataset()
    for c in COMPONENTS:
        out[term_name(c, "SW")] = sw[c]
        out[term_name(c, "LW")] = lw[c]
        out[term_name(c, "net")] = sw[c] + lw[c]
        for b in BANDS:
            out[term_name(c, b)].attrs = {
                "units": "W m-2",
                "long_name": f"{COMPONENT_LABELS[c]} {b}, TOA, downward positive (Ghan 2013)",
            }
    return out
