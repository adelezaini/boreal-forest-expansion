"""Sandbox: how to name the analysis period in titles (the years are nudging-met labels, not calendar years).

The nudging winds come from MET, a free-running NorESM NF2000 (present-day) run (cases-scripts/run_aliases.csv),
so "2001–2025" are model-calendar labels of that run, for PD and FUT alike.

Same figure (yearly responses of one contrast, from the existing table; no model data read) in 3 versions:
  A_current.png   as analysis/timeseries-responses.ipynb: "(2001–2025)", x = 2001…2025
  B_small_fix.png title "(25-yr mean)"; x ticks unchanged, x label "Nudging year (present-day winds)"
  C_proposal.png  title "(25-yr mean)" + subtitle naming the conditions and the shared nudged winds;
                  x = "Simulation year" 2–26 (year 1 = spin-up, dropped)
+ titles.png: the 3 wordings applied to 4 real map/figure titles of forcing_maps.py.
Outputs: sandbox/test_period_wording_outputs/.  Run: PYTHONPATH=src $PY sandbox/test_period_wording.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

from boreal_forest_expansion.plotting.style import set_default_style
from boreal_forest_expansion.plotting import palette as pal
from boreal_forest_expansion.plotting import forcing_maps as fm

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).with_name("test_period_wording_outputs"); OUT.mkdir(exist_ok=True)
set_default_style()
Y0, Y1 = 2001, 2025
N = Y1 - Y0 + 1
CONTRAST = "LCC-CTRL_FUT"
COLORS = {"global": pal.NAVY, "regional": pal.RED}

PERIOD = {"A": f"{Y0}–{Y1}", "B": f"{N}-yr mean", "C": f"{N}-yr mean"}
SUBTITLE_C = ("FUT = year-2100 SSP5-8.5 conditions repeated every year; winds nudged to the same "
              f"{N}-yr sequence of a free-running present-day simulation (first year dropped as spin-up)")

t = pd.read_csv(ROOT / f"results/tables/timeseries_regional_means_{Y0}_{Y1}.csv")
sub = t[t.contrast == CONTRAST]
name = sub.name.iloc[0]
PANELS = [(p.key, p.title, p.units) for p in fm.CONTEXT_PANELS] + \
         [(f"NET_{k}", fm.GHAN_TITLES[k], "W m$^{-2}$") for k in fm.GHAN_TERMS]


def mean_ci(v):
    v = np.asarray(v)
    return v.mean(), stats.t.ppf(0.975, v.size - 1) * v.std(ddof=1) / np.sqrt(v.size)


def figure(version):
    fig = plt.figure(figsize=(13, 13.5), constrained_layout=True)
    top, bottom = fig.subfigures(2, 1, height_ratios=[3, 1.05], hspace=0.04)
    axes = list(top.subplots(3, 3).ravel()) + list(bottom.subplots(1, 4))
    bottom.suptitle("Ghan decomposition, NET (positive = warming)", fontsize=11, fontweight="semibold")
    for ax, (key, title, units) in zip(axes, PANELS):
        for line in ("global", "regional"):
            d = sub[(sub.panel == key) & (sub.line == line)].sort_values("year")
            x = d.year - Y0 + 2 if version == "C" else d.year       # C: simulation year 2–26
            m, h = mean_ci(d.value)
            ax.plot(x, d.value, "o-", ms=3.5, lw=1.4, color=COLORS[line],
                    label=f"{'global' if line == 'global' else d.region.iloc[0]}: {m:+.3g} ± {h:.2g}")
            ax.axhline(m, color=COLORS[line], lw=0.9, ls="--", alpha=0.8)
        ax.axhline(0, color="black", lw=0.6)
        ax.set_title(title, fontsize=9.5, fontweight="semibold")
        ax.set_ylabel(f"Δ [{units}]", fontsize=8)
        if version == "C":
            ax.set_xticks([2] + list(range(5, N + 2, 5))); ax.set_xlim(1.5, N + 1.5)
            ax.set_xlabel("Simulation year", fontsize=8)
        else:
            ax.set_xticks(range(Y0, Y1 + 1, 4))
            if version == "B":
                ax.set_xlabel("Nudging year (present-day winds)", fontsize=8)
        ax.tick_params(labelsize=7.5); ax.legend(fontsize=7, loc="best", frameon=False); ax.grid(alpha=0.25, lw=0.5)
    line1 = f"Yearly responses (interactive): {name} ({PERIOD[version]})"
    line2 = ("global mean and modified cells (BVOC emissions) / ≥45°N (other variables); legend = mean ± 95 % CI over years"
             if version != "C" else SUBTITLE_C + "\nglobal mean and modified cells (BVOC emissions) / ≥45°N (other variables); "
             "legend = mean ± 95 % CI over years")
    fig.suptitle(f"{line1}\n{line2}", fontsize=12, fontweight="bold")
    path = OUT / {"A": "A_current.png", "B": "B_small_fix.png", "C": "C_proposal.png"}[version]
    fig.savefig(path, dpi=150, bbox_inches="tight"); plt.close(fig); print("Saved", path)


for v in "ABC":
    figure(v)

# the same wordings on real titles of forcing_maps.py (strings only)
real = [("LCC_FUT − LCC_PD", "Ghan decomposition, ≥45°N: {c}"),
        ("[LCC − CTRL]_FUT", "BVOC/SOA/cloud maps: {c}"),
        ("[LCC − CTRL]_PD", "Zonal-mean cloud change, JJA, 45–90°N, all longitudes"),
        ("CTRL_FUT − CTRL_PD", "Radiative forcing decomposition, ≥45°N: {c}")]
fig, ax = plt.subplots(figsize=(13, 5.2)); ax.axis("off")
yy = 0.97
for v, lab in (("A", "A  current"), ("B", "B  small fix"), ("C", "C  proposal")):
    ax.text(0, yy, lab, fontsize=11, fontweight="bold", va="top", color=pal.RED if v == "C" else "black"); yy -= 0.07
    for c, tpl in real:
        ax.text(0.03, yy, f"{tpl.format(c=c)} ({PERIOD[v]})", fontsize=10, va="top"); yy -= 0.055
    if v == "C":
        ax.text(0.03, yy, "caption / subtitle: " + SUBTITLE_C.replace("FUT = year-2100 SSP5-8.5 conditions repeated every year; w", "W"),
                fontsize=9, style="italic", va="top", color="0.35"); yy -= 0.055
    yy -= 0.03
fig.savefig(OUT / "titles.png", dpi=150, bbox_inches="tight"); plt.close(fig); print("Saved", OUT / "titles.png")
