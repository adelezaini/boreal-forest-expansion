"""Sandbox: plotting the cyclical (time-slice) PD and FUT runs on a SIMULATION-YEAR axis.

The PD runs repeat year-2000 conditions and the FUT runs repeat year-2100 SSP5-8.5 conditions every year; both are
nudged to the same 2000–2025 winds. So the x-axis is "Simulation year" (1, 2, 3, …), not a calendar year, and the
prescribed conditions are named in the figure/panel titles and legends.

Figures (sandbox/test_cyclical_sim_year_outputs/):
  drift_{PD,FUT}_{global,regional}.png       absolute yearly means, full series incl. simulation year 1
                                             (spin-up, dropped in the analysis); shaded = analysis period (mean)
  drift_FUT_minus_PD_{global,regional}.png   paired FUT − PD per simulation year, same shading
  seasonal_{PD,FUT}_{global,regional}.png    Jan–Dec, each month averaged over the analysis period
                                             (band = ±1 SD across years)
Tables (same folder): yearly_absolute.csv, monthly_absolute.csv (recomputed only if missing; --recompute forces it).

Inputs: data/processed-data/postprocessing/<alias>_<comp>_<CAT>_2001-2025.nc (analysis period) and the year-2000
(simulation year 1) files in sandbox/test_fut_minus_pd_outputs/cache/proc2000/ (made with spin-up 0 by
cache/run_2000.sh + run_2000_missing.sh). Nothing in analysis/ or results/ is read or written.

Run: PYTHONPATH=src $PY sandbox/test_cyclical_sim_year.py [--recompute]   (from the repo root)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

from boreal_forest_expansion.plotting.style import set_default_style
from boreal_forest_expansion.plotting import palette as pal
from boreal_forest_expansion.plotting import forcing_maps as fm

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).with_name("test_cyclical_sim_year_outputs")
OUT.mkdir(exist_ok=True)
PROC2000 = ROOT / "sandbox/test_fut_minus_pd_outputs/cache/proc2000"
FIRST_YEAR = 2000                 # simulation year 1 = first year of every run (met/nudging year 2000)
Y0, Y1 = 2001, 2025               # analysis period (simulation years 2–26)
SIM = lambda y: y - FIRST_YEAR + 1
set_default_style()

# prescribed conditions (CLAUDE_log 2026-10-30, (a)): repeated every simulation year
CONDITIONS = {
    "PD": "PD runs: year-2000 conditions repeated every year (SST/sea ice 1995–2005 clim., CO$_2$ 369 ppm, emissions 2000)",
    "FUT": "FUT runs: year-2100 SSP5-8.5 conditions repeated every year (SST/sea ice 2090–2100 clim., CO$_2$ 1135 ppm, emissions 2100)",
}
RUNS = {
    "PD": ["CTRL_PD", "LCC_PD", "LCC_PD_fBVOCctrlPD", "LCC_PD_fBVOClccPD", "CTRL_PD_fBVOCctrlPD"],
    "FUT": ["CTRL_FUT", "LCC_FUT", "LCC_FUT_fBVOCctrlPD", "LCC_FUT_fBVOCctrlFUT", "LCC_FUT_fBVOClccPD",
            "CTRL_FUT_fBVOCctrlFUT"],
}
# FUT run, PD twin, label, colour, linestyle (as sandbox/test_fut_minus_pd.py)
PAIRS = [
    ("CTRL_FUT", "CTRL_PD", "CTRL", pal.NAVY, "-"),
    ("LCC_FUT", "LCC_PD", "LCC", pal.RED, "-"),
    ("LCC_FUT_fBVOCctrlPD", "LCC_PD_fBVOCctrlPD", "LCC_fBVOCctrlPD (same emissions)", pal.PLUM, "-"),
    ("LCC_FUT_fBVOClccPD", "LCC_PD_fBVOClccPD", "LCC_fBVOClccPD (same emissions)", pal.TEAL, "-"),
    ("CTRL_FUT_fBVOCctrlFUT", "CTRL_PD_fBVOCctrlPD", "CTRL_fBVOC (own emissions)", pal.NAVY, "--"),
]
REGIONAL = {"sfisop": "modified cells", "sfmterp": "modified cells"}   # all other panels: ≥45°N
PANELS = [(p.key, p.title, p.variable_class, p.variable, p.units, p.component) for p in fm.CONTEXT_PANELS]
PANELS += [(f"NET_{t}", fm.GHAN_TITLES[t], "RADIATIVE", f"NET_{t}", "W m$^{-2}$", "atm") for t in fm.GHAN_TERMS]
MONTHS = "JFMAMJJASOND"
SHADE = dict(color="0.94", lw=0, zorder=0)
WHERE = {"global": "global mean", "regional": "modified cells (BVOC emissions) / ≥45°N (other variables)"}


def run_style(alias):
    if alias.startswith("CTRL"):
        return pal.NAVY, ("--" if "fBVOC" in alias else "-")
    return {"ctrlPD": pal.PLUM, "ctrlFUT": pal.ORANGE, "lccPD": pal.TEAL}.get(alias.split("fBVOC")[-1], pal.RED), "-"


# ----------------------------------------------------------------------------------------------- tables
def compute():
    refs = {comp: fm.open_class("CTRL_PD", cls, Y0, Y1, comp) for comp, cls in (("atm", "RADIATIVE"), ("lnd", "ET"))}
    masks = {comp: fm.region_masks(ds) for comp, ds in refs.items()}
    for m in masks.values():
        m["global"] = m["≥45°N"] | ~m["≥45°N"]

    def on_ref(f, comp):
        assert np.allclose(f["lat"], refs[comp]["lat"]) and np.allclose(f["lon"], refs[comp]["lon"])
        return f.assign_coords(lat=refs[comp]["lat"], lon=refs[comp]["lon"])   # CAM/CLM coords differ by ~1e-13

    yearly, monthly, missing = [], [], set()
    for period, aliases in RUNS.items():
        for alias in aliases:
            opened = {}
            for key, title, cls, var, units, comp in PANELS:
                if (cls, comp) not in opened:
                    ds = fm.open_class(alias, cls, Y0, Y1, comp)
                    p0 = PROC2000 / f"{alias}_{comp}_{cls}_{FIRST_YEAR}-{FIRST_YEAR}.nc"
                    if p0.exists():
                        d0 = xr.open_dataset(p0)
                        d0 = d0.rename({v: v.replace("cre_clean", "cloud").replace("clearclean", "rest")
                                        for v in d0.data_vars if v.endswith(("_cre_clean", "_clearclean"))})
                    else:
                        d0 = None; missing.add(p0.name)
                    opened[cls, comp] = ds, d0
                ds, d0 = opened[cls, comp]
                regions = (("global", "global"), ("regional", REGIONAL.get(key, "≥45°N")))
                # yearly, simulation years 1–26
                for src in (d0, ds):
                    if src is None:
                        continue
                    f = on_ref(fm.yearly_field(src, var), comp)
                    for line, region in regions:
                        r = fm.regional(f, refs[comp], masks[comp][region])
                        yearly += [dict(period=period, run=alias, panel=key, line=line, region=region, units=units,
                                        year=int(y), value=float(v)) for y, v in zip(r["year"].values, r.values)]
                # monthly, analysis period only: per-month value of each year (same definitions as yearly_field)
                for mo in range(1, 13):
                    f = on_ref(fm.yearly_field(ds, var, months=[mo]), comp)
                    for line, region in regions:
                        r = fm.regional(f, refs[comp], masks[comp][region])
                        monthly += [dict(period=period, run=alias, panel=key, line=line, region=region, units=units,
                                         year=int(y), month=mo, value=float(v)) for y, v in zip(r["year"].values, r.values)]
            print("done", alias, flush=True)
    if missing:
        print("No simulation-year-1 file (yet):", sorted(missing))
    y, m = pd.DataFrame(yearly), pd.DataFrame(monthly)
    y.to_csv(OUT / "yearly_absolute.csv", index=False); m.to_csv(OUT / "monthly_absolute.csv", index=False)
    return y, m


def yearly_without_nird():
    """Simulation years 2–26 from the existing table (analysis/timeseries-responses.ipynb §3, same definitions),
    simulation year 1 from the year-2000 files on /cluster/work (proc2000). Needs no NIRD read (16 Nov: NIRD HDF errors)."""
    t = pd.read_csv(ROOT / "results/tables/timeseries_absolute_2001_2025.csv")
    t = t[t.year.between(Y0, Y1)].drop(columns="variable")
    refs = {comp: xr.open_dataset(PROC2000 / f"CTRL_PD_{comp}_{cls}_{FIRST_YEAR}-{FIRST_YEAR}.nc")
            for comp, cls in (("atm", "RADIATIVE"), ("lnd", "ET"))}
    masks = {comp: fm.region_masks(ds) for comp, ds in refs.items()}
    for m in masks.values():
        m["global"] = m["≥45°N"] | ~m["≥45°N"]
    rows = []
    for period, aliases in RUNS.items():
        for alias in aliases:
            for key, title, cls, var, units, comp in PANELS:
                d0 = xr.open_dataset(PROC2000 / f"{alias}_{comp}_{cls}_{FIRST_YEAR}-{FIRST_YEAR}.nc")
                d0 = d0.rename({v: v.replace("cre_clean", "cloud").replace("clearclean", "rest")
                                for v in d0.data_vars if v.endswith(("_cre_clean", "_clearclean"))})
                f = fm.yearly_field(d0, var).assign_coords(lat=refs[comp]["lat"], lon=refs[comp]["lon"])
                for line, region in (("global", "global"), ("regional", REGIONAL.get(key, "≥45°N"))):
                    r = fm.regional(f, refs[comp], masks[comp][region])
                    rows += [dict(period=period, run=alias, panel=key, line=line, region=region, units=units,
                                  year=int(y), value=float(v)) for y, v in zip(r["year"].values, r.values)]
    y = pd.concat([pd.DataFrame(rows), t], ignore_index=True)
    assert y.groupby(["run", "panel", "line"]).year.nunique().eq(Y1 - FIRST_YEAR + 1).all(), "gaps in 2000–2025"
    y.to_csv(OUT / "yearly_absolute.csv", index=False)
    return y


SEASONAL = "--seasonal" in sys.argv     # needs the monthly 2001–2025 files on NIRD
if SEASONAL:
    if "--recompute" in sys.argv or not (OUT / "monthly_absolute.csv").exists():
        yearly, monthly = compute()
    else:
        yearly, monthly = pd.read_csv(OUT / "yearly_absolute.csv"), pd.read_csv(OUT / "monthly_absolute.csv")
else:
    yearly = (pd.read_csv(OUT / "yearly_absolute.csv") if (OUT / "yearly_absolute.csv").exists()
              and "--recompute" not in sys.argv else yearly_without_nird())
yearly["sim_year"] = SIM(yearly.year)
UNITS = yearly.drop_duplicates("panel").set_index("panel").units
TITLES = {k: t for k, t, *_ in PANELS}


# ----------------------------------------------------------------------------------------------- figures
def grid(title):
    fig = plt.figure(figsize=(13, 14), constrained_layout=True)
    top, bottom = fig.subfigures(2, 1, height_ratios=[3, 1.05], hspace=0.04)
    axes = list(top.subplots(3, 3).ravel()) + list(bottom.subplots(1, 4))
    bottom.suptitle("Ghan decomposition, NET (down positive)", fontsize=11, fontweight="semibold")
    fig.suptitle(title, fontsize=12, fontweight="bold")
    return fig, axes


def sim_year_axis(ax):
    ax.axvspan(SIM(Y0) - 0.5, SIM(Y1) + 0.5, **SHADE)
    ax.set_xlim(0.5, SIM(Y1) + 0.5)
    ax.set_xticks([1] + list(range(5, SIM(Y1) + 1, 5)))
    ax.set_xlabel("Simulation year", fontsize=8)
    ax.tick_params(labelsize=7.5); ax.grid(alpha=0.25, lw=0.5)


def finish(fig, axes, xlabel, fname, extra_handles=()):
    h, l = axes[0].get_legend_handles_labels()
    h, l = h + [e[0] for e in extra_handles], l + [e[1] for e in extra_handles]
    fig.legend(h, l, loc="outside lower center", ncol=3, fontsize=8.5, frameon=False)
    fig.savefig(OUT / fname, dpi=170, bbox_inches="tight"); plt.close(fig)
    print("Saved", OUT / fname)


SHADE_HANDLE = (Patch(facecolor=SHADE["color"]), f"analysis period (simulation years {SIM(Y0)}–{SIM(Y1)}), used for means")


def drift_absolute(period, line):
    sub = yearly[(yearly.period == period) & (yearly.line == line)]
    fig, axes = grid(f"Drift / spin-up, absolute yearly means: {WHERE[line]}\n{CONDITIONS[period]}")
    for ax, (key, title, *_ , units, _c) in zip(axes, PANELS):
        d = sub[sub.panel == key]
        for alias in RUNS[period]:
            r = d[d.run == alias].sort_values("sim_year")
            c, ls = run_style(alias)
            ax.plot(r.sim_year, r.value, marker="o", ms=2.8, lw=1.2, ls=ls, color=c, label=alias)
        ax.set_title(f"{title}\n({d.region.iloc[0]})", fontsize=9.5, fontweight="semibold")
        ax.set_ylabel(f"[{units}]", fontsize=8); sim_year_axis(ax)
    finish(fig, axes, "Simulation year", f"drift_{period}_{line}.png", [SHADE_HANDLE])


def drift_difference(line):
    w = yearly[yearly.line == line].pivot_table(index=["panel", "sim_year"], columns="run", values="value")
    fig, axes = grid(f"FUT − PD per simulation year (same nudging winds each year): {WHERE[line]}\n"
                     "FUT = year-2100 SSP5-8.5 conditions, PD = year-2000 conditions, both repeated every year")
    for ax, (key, title, *_ , units, _c) in zip(axes, PANELS):
        d = w.loc[key]
        for fut, pd_, lab, c, ls in PAIRS:
            s = (d[fut] - d[pd_]).dropna()
            m = s.loc[SIM(Y0):SIM(Y1)].mean()
            ax.plot(s.index, s.values, marker="o", ms=2.8, lw=1.2, ls=ls, color=c, label=lab)
            ax.hlines(m, SIM(Y0) - 0.5, SIM(Y1) + 0.5, color=c, lw=0.8, ls=":")
        ax.axhline(0, color="black", lw=0.6)
        region = yearly[(yearly.panel == key) & (yearly.line == line)].region.iloc[0]
        ax.set_title(f"{title}\n({region})", fontsize=9.5, fontweight="semibold")
        ax.set_ylabel(f"Δ FUT − PD [{units}]", fontsize=8); sim_year_axis(ax)
    finish(fig, axes, "Simulation year", f"drift_FUT_minus_PD_{line}.png",
           [SHADE_HANDLE, (plt.Line2D([], [], color="0.3", ls=":", lw=0.8), "mean over the analysis period")])


def seasonal(period, line):
    sub = monthly[(monthly.period == period) & (monthly.line == line)]
    st = sub.groupby(["panel", "run", "month"]).value.agg(["mean", "std"])
    fig, axes = grid(f"Seasonal cycle, each month averaged over simulation years {SIM(Y0)}–{SIM(Y1)} "
                     f"(band = ±1 SD across years): {WHERE[line]}\n{CONDITIONS[period]}")
    for ax, (key, title, *_ , units, _c) in zip(axes, PANELS):
        for alias in RUNS[period]:
            r = st.loc[(key, alias)]
            c, ls = run_style(alias)
            ax.fill_between(r.index, r["mean"] - r["std"], r["mean"] + r["std"], color=c, alpha=0.10, lw=0)
            ax.plot(r.index, r["mean"], marker="o", ms=2.8, lw=1.2, ls=ls, color=c, label=alias)
        region = sub[sub.panel == key].region.iloc[0]
        ax.set_title(f"{title}\n({region})", fontsize=9.5, fontweight="semibold")
        ax.set_ylabel(f"[{units}]", fontsize=8)
        ax.set_xticks(range(1, 13), list(MONTHS)); ax.set_xlim(0.6, 12.4); ax.set_xlabel("Month", fontsize=8)
        ax.tick_params(labelsize=7.5); ax.grid(alpha=0.25, lw=0.5)
    finish(fig, axes, "Month", f"seasonal_{period}_{line}.png")


for line in ("global", "regional"):
    for period in RUNS:
        drift_absolute(period, line)
        if SEASONAL:
            seasonal(period, line)
    drift_difference(line)

# check: simulation-year-1 coverage
cov = yearly[yearly.sim_year == 1].groupby("run").panel.nunique().reindex([a for r in RUNS.values() for a in r]).fillna(0)
print("panels with simulation year 1 (of", len(PANELS), "):", cov.astype(int).to_dict())
