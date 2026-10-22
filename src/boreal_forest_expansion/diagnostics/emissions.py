"""D2 - how large are the MEGAN emissions other than ISOP and MTERP, and how much does
the land-cover change alter them?

  Q1  size of the other compounds' emissions (CTRL)          -> size of the fBVOC artifact
  Q2  Delta E (LCC - CTRL) of the others vs of ISOP + MTERP   -> what an ISOP/MTERP-only
                                                                 definition of BVOC misses

Input: CLM h0 MEG_<compound> (kg compound m-2 s-1, per unit land area of the grid cell),
default-active in CLM release-clm5.0.14-Nor_v1.0.7 (a, VOCEmissionMod.F90 registers them
without default='inactive'; all 46 present in the production h0 files). Totals = MEG x
area (km2 -> m2) x landfrac (a: CLM history writes area and landfrac; gridcell values
are land-area averages (a, subgridAveMod.F90)).

Three weightings (they answer different questions, so all three are reported):
  mass    Tg(compound) yr-1        literature comparison
  carbon  Tg C yr-1                proxy for the TOTAL OH demand and CO/O3 production once
                                   a compound is fully oxidised (each C ends as CO -> CO2,
                                   CO + OH consumes one OH) (b). Relevant for the global OH
                                   budget and the CH4 lifetime.
  koh     Tmol(CO-eq) yr-1         emission x k_OH(T_ref) / k_OH(CO, T_ref): INSTANTANEOUS
                                   OH reactivity near the source. Relevant for local
                                   oxidant levels and SOA formation rates over the boreal
                                   region (b). Long-lived compounds (CO, CH3OH, acetone)
                                   score low here although their total OH demand is large.

Only ISOP and MTERP form SOA in pp_tropstrat_mam_oslo (a); the other compounds can
affect aerosol and clouds only through oxidants.

Caveat (a, case scripts): LCC and CTRL start from different land spin-ups, so LCC - CTRL
also contains an emission offset outside the modified cells (largest in the tropics,
FUT). Read Q2 for the `modified_cells` region; `global` and `tropics` show the offset.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import xarray as xr

from . import megan
from boreal_forest_expansion.analysis.loading import annual_mean, open_cam_monthly
from boreal_forest_expansion.analysis.regions import band_mask, load_modified_cells
from boreal_forest_expansion.analysis.stats import paired_summary

log = logging.getLogger(__name__)

SECONDS_PER_YEAR = 365 * 86400.0          # noleap calendar
WEIGHTINGS = {
    "mass": "Tg yr-1",
    "carbon": "Tg C yr-1",
    "koh": "Tmol(CO-eq) yr-1",
}


@dataclass
class EmissionContrast:
    """minuend - subtrahend, both CLM h0 globs."""
    name: str
    minuend: str
    subtrahend: str
    label: str = ""
    note: str = ""


@dataclass
class D2Result:
    totals: pd.DataFrame        # per member, region, species, weighting, year
    q1: pd.DataFrame            # group shares per member/region/weighting
    q2: pd.DataFrame            # Delta E per contrast/region/group/weighting with intervals
    q2_summary: pd.DataFrame    # others vs ISOP+MTERP per contrast/region/weighting
    maps: dict[str, xr.Dataset]  # contrast -> time-mean Delta carbon flux, g C m-2 yr-1
    meta: dict = field(default_factory=dict)


def meg_variables(spec: str = megan.MEGAN_SPECIFIER) -> list[str]:
    return [f"MEG_{r['compound']}" for r in megan.compound_table(spec)]


def species_fluxes(ds: xr.Dataset, spec: str = megan.MEGAN_SPECIFIER, T_ref: float = 298.0) -> dict[str, xr.Dataset]:
    """Per-grid-cell fluxes per CAM species in the three weightings (per second, not per year).

    Returns {'mass': kg s-1, 'carbon': kg C s-1, 'koh': mol(CO-eq) s-1}, each a Dataset with one
    variable per CAM species, dims (time, lat, lon).
    """
    land_m2 = (ds["area"] * 1e6 * ds["landfrac"]).fillna(0.0)
    if "time" in land_m2.dims:
        land_m2 = land_m2.isel(time=0, drop=True)
    k_co = megan.k_oh("CO", T_ref)
    out = {w: {} for w in WEIGHTINGS}
    for r in megan.compound_table(spec):
        v = f"MEG_{r['compound']}"
        if v not in ds:
            continue
        kg_s = ds[v].fillna(0.0) * land_m2 * r["coeff"]
        mol_s = kg_s / (r["mw"] * 1e-3)
        s = r["cam_species"]
        add = {
            "mass": kg_s,
            "carbon": mol_s * r["nC"] * megan.ATOMIC_MASS["C"] * 1e-3,
            "koh": mol_s * megan.k_oh(s, T_ref) / k_co,
        }
        for w in WEIGHTINGS:
            out[w][s] = out[w][s] + add[w] if s in out[w] else add[w]
    return {w: xr.Dataset(d) for w, d in out.items()}


def load_annual_meg(pattern: str, spec: str = megan.MEGAN_SPECIFIER, spinup_months: int = 12) -> xr.Dataset:
    """Annual means (month-length weighted) of all MEG_* fields of one CLM case, in memory.

    Everything downstream works on these (year, lat, lon) arrays: fluxes are linear in
    MEG_*, so annual totals of the weighted sums equal weighted sums of annual means.
    """
    ds = open_cam_monthly(pattern, meg_variables(spec), spinup_months, strict=False)
    for v in ("area", "landfrac"):
        if v not in ds:
            raise KeyError(f"{ds.attrs['case']}: CLM '{v}' missing; is this a CLM h0 file?")
    meg = [v for v in ds.data_vars if v.startswith("MEG_")]
    ann = annual_mean(ds[meg], ds["days_in_interval"]).load()
    for v in ("area", "landfrac"):
        a = ds[v]
        ann[v] = (a.isel(time=0, drop=True) if "time" in a.dims else a).load()
    ann.attrs.update(case=ds.attrs["case"], missing=ds.attrs.get("missing", ""))
    return ann


def annual_totals(ann: xr.Dataset, regions: dict[str, xr.DataArray], spec: str = megan.MEGAN_SPECIFIER,
                  T_ref: float = 298.0) -> pd.DataFrame:
    """Annual regional totals per CAM species and weighting, in WEIGHTINGS units.
    `ann` = output of load_annual_meg (dims year, lat, lon)."""
    flux = species_fluxes(ann, spec, T_ref)
    scale = {"mass": 1e-9, "carbon": 1e-9, "koh": 1e-12}     # kg -> Tg ; mol -> Tmol
    rows = []
    for w, fds in flux.items():
        for rname, mask in regions.items():
            tot = fds.where(mask, 0.0).sum(("lat", "lon")) * SECONDS_PER_YEAR * scale[w]
            df = tot.to_dataframe().reset_index().melt(id_vars="year", var_name="species", value_name="value")
            df["region"], df["weighting"] = rname, w
            rows.append(df)
    out = pd.concat(rows, ignore_index=True)
    out["group"] = out["species"].map(megan.group_of)
    out["case"] = ann.attrs.get("case", "")
    return out


def _regions(ds: xr.Dataset, modified_path: str) -> dict[str, xr.DataArray]:
    mod = load_modified_cells(modified_path, ds)
    return {
        "global": xr.ones_like(mod, dtype=bool),
        "modified_cells": mod,
        "NH_45_90": band_mask(ds, 45, 90),
        "tropics": band_mask(ds, -30, 30),
    }


def _group_totals(totals: pd.DataFrame) -> pd.DataFrame:
    g = totals.groupby(["member", "region", "weighting", "group", "year"], as_index=False)["value"].sum()
    others = (g[g.group != megan.PRESCRIBED_GROUP]
              .groupby(["member", "region", "weighting", "year"], as_index=False)["value"].sum())
    others["group"] = "ALL OTHERS"
    allg = g.groupby(["member", "region", "weighting", "year"], as_index=False)["value"].sum()
    allg["group"] = "ALL MEGAN"
    return pd.concat([g, others, allg], ignore_index=True)


def q1_table(gt: pd.DataFrame) -> pd.DataFrame:
    """Mean annual total per group and its share of all MEGAN emissions (%)."""
    m = gt.groupby(["member", "region", "weighting", "group"], as_index=False)["value"].mean()
    tot = m[m.group == "ALL MEGAN"].set_index(["member", "region", "weighting"])["value"]
    m["share_pct"] = 100 * m["value"] / m.set_index(["member", "region", "weighting"]).index.map(tot)
    m["units"] = m["weighting"].map(WEIGHTINGS)
    return m


def gross_share(totals: pd.DataFrame, contrasts: list[EmissionContrast]) -> pd.DataFrame:
    """Share of the others in the GROSS change, sum over species of |mean Delta E|.

    Robust to cancellation: if isoprene decreases while monoterpenes increase, the net
    Delta E(ISOP+MTERP) can be ~0 and the ratio others/ISOP+MTERP meaningless, but the
    gross change is not. Species level = CAM species (19).
    """
    rows = []
    m = totals.groupby(["member", "region", "weighting", "species", "group"], as_index=False)["value"].mean()
    for c in contrasts:
        a = m[m.member == c.name + "::minuend"]
        b = m[m.member == c.name + "::subtrahend"]
        mg = a.merge(b, on=["region", "weighting", "species", "group"], suffixes=("_a", "_b"))
        mg["absd"] = (mg["value_a"] - mg["value_b"]).abs()
        for (reg, w), g in mg.groupby(["region", "weighting"]):
            tot = g["absd"].sum()
            oth = g.loc[g.group != megan.PRESCRIBED_GROUP, "absd"].sum()
            rows.append({"contrast": c.name, "region": reg, "weighting": w,
                         "others_share_of_gross_change": oth / tot if tot else np.nan})
    return pd.DataFrame(rows)


def q2_tables(gt: pd.DataFrame, contrasts: list[EmissionContrast]) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows, summ = [], []
    for c in contrasts:
        a = gt[gt.member == c.name + "::minuend"]
        b = gt[gt.member == c.name + "::subtrahend"]
        mg = a.merge(b, on=["region", "weighting", "group", "year"], suffixes=("_a", "_b"))
        mg["delta"] = mg["value_a"] - mg["value_b"]
        for (reg, w, grp), g in mg.groupby(["region", "weighting", "group"]):
            s = paired_summary(g["delta"].to_numpy())
            rows.append({"contrast": c.name, "region": reg, "weighting": w, "group": grp,
                         "E_minuend": g["value_a"].mean(), "E_subtrahend": g["value_b"].mean(),
                         "delta": s["mean"], "ci_lo": s["ci_lo"], "ci_hi": s["ci_hi"], "p": s["p"],
                         "rel_change_pct": 100 * s["mean"] / g["value_b"].mean() if g["value_b"].mean() else np.nan,
                         "units": WEIGHTINGS[w], "n_years": s["n"]})
    q2 = pd.DataFrame(rows)
    for (cn, reg, w), g in q2.groupby(["contrast", "region", "weighting"]):
        gi = g.set_index("group")
        d_pre = gi.loc[megan.PRESCRIBED_GROUP, "delta"]
        d_oth = gi.loc["ALL OTHERS", "delta"]
        e_oth = gi.loc["ALL OTHERS", "E_subtrahend"]
        pre_sig = bool(gi.loc[megan.PRESCRIBED_GROUP, "ci_lo"] > 0 or gi.loc[megan.PRESCRIBED_GROUP, "ci_hi"] < 0)
        summ.append({
            "contrast": cn, "region": reg, "weighting": w, "units": WEIGHTINGS[w],
            "dE_ISOP_MTERP": d_pre, "dE_others": d_oth,
            "ISOP_MTERP_ci_excludes_0": pre_sig,
            # only meaningful when the ISOP+MTERP change itself is distinguishable from 0
            "others_over_ISOP_MTERP": d_oth / d_pre if (pre_sig and d_pre) else np.nan,
            # fraction of the others' emissions changed by LCC: scales the D1 artifact (b)
            "f_others_changed": d_oth / gi.loc["ALL OTHERS", "E_subtrahend"] if e_oth else np.nan,
            "others_ci_excludes_0": bool(gi.loc["ALL OTHERS", "ci_lo"] > 0 or gi.loc["ALL OTHERS", "ci_hi"] < 0),
        })
    return q2, pd.DataFrame(summ)


def delta_carbon_maps(a: xr.Dataset, b: xr.Dataset, spec: str = megan.MEGAN_SPECIFIER) -> xr.Dataset:
    """Time-mean Delta carbon flux, g C m-2 (grid-cell area) yr-1, for ISOP+MTERP and the others.
    a, b = outputs of load_annual_meg."""
    out = {}
    years = np.intersect1d(a["year"].values, b["year"].values)
    for ds, key in ((a, "a"), (b, "b")):
        f = species_fluxes(ds.sel(year=years), spec)["carbon"]
        cell_m2 = ds["area"] * 1e6
        ann = f.mean("year")
        pre = sum(ann[s] for s in megan.GROUPS[megan.PRESCRIBED_GROUP] if s in ann)
        oth = sum(ann[s] for s in ann.data_vars if s not in megan.GROUPS[megan.PRESCRIBED_GROUP])
        out[key] = xr.Dataset({"ISOP+MTERP": pre, "others": oth}) / cell_m2 * 1e3 * SECONDS_PER_YEAR
    d = (out["a"] - out["b"]).load()
    for v in d.data_vars:
        d[v].attrs["units"] = "g C m-2 yr-1"
    return d


def run_d2(members: dict[str, str], contrasts: list[EmissionContrast], modified_cells_path: str,
           spinup_months: int = 12, T_ref: float = 298.0, spec: str = megan.MEGAN_SPECIFIER) -> D2Result:
    """members: alias -> CLM h0 glob, used for Q1. contrasts: for Q2 (their members are loaded too)."""
    variables = meg_variables(spec)
    opened: dict[str, xr.Dataset] = {}

    def _open(pattern):
        if pattern not in opened:
            opened[pattern] = load_annual_meg(pattern, spec, spinup_months)
        return opened[pattern]

    first = _open(next(iter(members.values())) if members else contrasts[0].minuend)
    regions = _regions(first, modified_cells_path)

    frames, missing = [], {}
    for alias, pat in members.items():
        ds = _open(pat)
        t = annual_totals(ds, regions, spec, T_ref)
        t["member"] = alias
        frames.append(t)
        missing[alias] = ds.attrs.get("missing", "")
    for c in contrasts:
        for role, pat in (("minuend", c.minuend), ("subtrahend", c.subtrahend)):
            ds = _open(pat)
            t = annual_totals(ds, regions, spec, T_ref)
            t["member"] = f"{c.name}::{role}"
            frames.append(t)
            missing[f"{c.name}::{role}"] = ds.attrs.get("missing", "")
    totals = pd.concat(frames, ignore_index=True)
    gt = _group_totals(totals)
    q1 = q1_table(gt[~gt.member.str.contains("::")])
    q2, q2s = q2_tables(gt, contrasts)
    q2s = q2s.merge(gross_share(totals, contrasts), on=["contrast", "region", "weighting"], how="left")
    maps = {c.name: delta_carbon_maps(_open(c.minuend), _open(c.subtrahend), spec) for c in contrasts}
    meta = {"T_ref": T_ref, "spinup_months": spinup_months, "n_compounds": len(variables),
            "missing_MEG": {k: v for k, v in missing.items() if v}, "modified_cells": int(regions["modified_cells"].sum()),
            "k_OH_ref_CO": megan.k_oh("CO", T_ref)}
    if meta["missing_MEG"]:
        log.warning("Some MEG_ fields are missing; totals of their groups are incomplete: %s", meta["missing_MEG"])
    return D2Result(totals, q1, q2, q2s, maps, meta)


def cam_clm_crosscheck(clm_pattern: str, cam_pattern: str, spinup_months: int = 12) -> pd.DataFrame:
    """Global ISOP/MTERP totals from CLM MEG_* (summed to CAM species) vs CAM MEG_ISOP/MEG_MTERP.

    CAM MEG_<species> is kg(CAM species) m-2 s-1 per grid-cell area (a, chemistry.F90).
    ISOP: same molecule on both sides, totals should agree within regridding/coupling
    differences (b). MTERP: CAM mass uses the MTERP molar mass, so compare in moles.
    """
    from boreal_forest_expansion.analysis.regions import area_weights
    R_EARTH = 6.37122e6
    clm = open_cam_monthly(clm_pattern, meg_variables(), spinup_months, strict=False)
    cam = open_cam_monthly(cam_pattern, ["MEG_ISOP", "MEG_MTERP"], spinup_months)
    cell_m2 = area_weights(cam) * 4 * np.pi * R_EARTH ** 2
    mw_cam = {"ISOP": megan.molar_mass("C5H8"), "MTERP": megan.molar_mass("C10H16")}
    rows = []
    rows_mol_clm = {}
    for r in megan.compound_table():
        v = f"MEG_{r['compound']}"
        if r["cam_species"] in ("ISOP", "MTERP") and v in clm:
            land_m2 = (clm["area"] * 1e6 * clm["landfrac"]).fillna(0.0)
            mol = (clm[v].fillna(0.0) * land_m2 / (r["mw"] * 1e-3)).mean("time").sum()
            rows_mol_clm[r["cam_species"]] = rows_mol_clm.get(r["cam_species"], 0.0) + float(mol)
    for s in ("ISOP", "MTERP"):
        cam_mol = float((cam[f"MEG_{s}"] * cell_m2).mean("time").sum()) / (mw_cam[s] * 1e-3)
        rows.append({"species": s, "CLM_Tmol_yr": rows_mol_clm.get(s, np.nan) * SECONDS_PER_YEAR * 1e-12,
                     "CAM_Tmol_yr": cam_mol * SECONDS_PER_YEAR * 1e-12})
    df = pd.DataFrame(rows)
    df["CAM/CLM"] = df["CAM_Tmol_yr"] / df["CLM_Tmol_yr"]
    return df
