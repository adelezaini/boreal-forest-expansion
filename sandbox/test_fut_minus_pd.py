"""Sandbox: FUT − PD yearly differences ("then − now"), paired by nudging/met year.

The PD and FUT runs are time slices driven by the same nudging years (2000–2025), so year Y of a FUT run
is compared with year Y of its PD twin. Input = the absolute yearly table written by
analysis/timeseries-responses.ipynb §3 (results/tables/timeseries_absolute_2001_2025.csv): no model data read.

Outputs (sandbox/test_fut_minus_pd_outputs/):
  fut_minus_pd_{global,regional}_2001_2025.png   one line per run pair
  forest_effect_change_{global,regional}_2001_2025.png   [LCC − CTRL]_FUT − [LCC − CTRL]_PD
  fut_minus_pd_2001_2025.csv
Run: PYTHONPATH=src $PY sandbox/test_fut_minus_pd.py   (from the repo root)
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
OUT = Path(__file__).with_name("test_fut_minus_pd_outputs")
OUT.mkdir(exist_ok=True)
Y0, Y1 = 2001, 2025
set_default_style()

a = pd.read_csv(ROOT / "results/tables/timeseries_absolute_2001_2025.csv")

# FUT run, PD twin, label, colour, linestyle (palette rule: CTRL navy, LCC red, fBVOC by emission source)
PAIRS = [
    ("CTRL_FUT", "CTRL_PD", "CTRL", pal.NAVY, "-"),
    ("LCC_FUT", "LCC_PD", "LCC", pal.RED, "-"),
    ("LCC_FUT_fBVOCctrlPD", "LCC_PD_fBVOCctrlPD", "LCC_fBVOCctrlPD (same emissions)", pal.PLUM, "-"),
    ("LCC_FUT_fBVOClccPD", "LCC_PD_fBVOClccPD", "LCC_fBVOClccPD (same emissions)", pal.TEAL, "-"),
    ("CTRL_FUT_fBVOCctrlFUT", "CTRL_PD_fBVOCctrlPD", "CTRL_fBVOC (own emissions)", pal.NAVY, "--"),
]
PANELS = list(dict.fromkeys(a.panel))
TITLES = {p.key: p.title for p in fm.CONTEXT_PANELS} | {f"NET_{t}": fm.GHAN_TITLES[t] for t in fm.GHAN_TERMS}
UNITS = a.drop_duplicates("panel").set_index("panel").units

wide = a.pivot_table(index=["panel", "line", "region", "year"], columns="run", values="value")
assert wide.index.get_level_values("year").min() == Y0 and wide.index.get_level_values("year").max() == Y1
assert not wide.isna().any().any()

d = pd.DataFrame({lab: wide[fut] - wide[pd_] for fut, pd_, lab, *_ in PAIRS})
d["[LCC − CTRL]_FUT − [LCC − CTRL]_PD"] = (wide.LCC_FUT - wide.CTRL_FUT) - (wide.LCC_PD - wide.CTRL_PD)
d.stack().rename("value").rename_axis(index={None: "pair"}).reset_index().to_csv(OUT / "fut_minus_pd_2001_2025.csv", index=False)


def mean_ci(v):
    v = np.asarray(v)
    return v.mean(), stats.t.ppf(0.975, v.size - 1) * v.std(ddof=1) / np.sqrt(v.size)


def figure(line, series, fname, title):
    fig = plt.figure(figsize=(13, 14), constrained_layout=True)
    top, bottom = fig.subfigures(2, 1, height_ratios=[3, 1.05], hspace=0.04)
    axes = list(top.subplots(3, 3).ravel()) + list(bottom.subplots(1, 4))
    bottom.suptitle("Ghan decomposition, NET (positive = warming)", fontsize=11, fontweight="semibold")
    for ax, key in zip(axes, PANELS):
        sub = d.xs((key, line), level=("panel", "line"))
        region = sub.index.get_level_values("region")[0]
        for lab, color, ls in series:
            s = sub[lab].droplevel("region")
            m, h = mean_ci(s)
            ax.plot(s.index, s.values, marker="o", ms=3, lw=1.3, ls=ls, color=color, label=f"{lab}: {m:+.3g} ± {h:.2g}")
            ax.axhline(m, color=color, lw=0.8, ls=":", alpha=0.9)
        ax.axhline(0, color="black", lw=0.6)
        ax.set_title(f"{TITLES[key]}\n({region})", fontsize=9.5, fontweight="semibold")
        ax.set_ylabel(f"Δ FUT − PD [{UNITS[key]}]", fontsize=8)
        ax.set_xticks(range(Y0, Y1 + 1, 3)); ax.tick_params(labelsize=7.5)
        ax.legend(fontsize=6.3, loc="best", frameon=False)
        ax.grid(alpha=0.25, lw=0.5)
    axes[0].figure.supxlabel("nudging (met) year — both slices share it; not a calendar year of the 2100 run", fontsize=9)
    fig.suptitle(title, fontsize=12, fontweight="bold")
    fig.savefig(OUT / fname, dpi=170, bbox_inches="tight"); plt.close(fig)
    print("Saved", OUT / fname)


where = {"global": "global mean", "regional": "modified cells (BVOC emissions) / ≥45°N (other variables)"}
for line in ("global", "regional"):
    figure(line, [(lab, c, ls) for _, _, lab, c, ls in PAIRS], f"fut_minus_pd_{line}_{Y0}_{Y1}.png",
           f"FUT − PD, paired by nudging year ({Y0}–{Y1}), {where[line]}\nlegend = mean ± 95 % CI over years; dotted = mean")
    figure(line, [("[LCC − CTRL]_FUT − [LCC − CTRL]_PD", pal.GOLD, "-")], f"forest_effect_change_{line}_{Y0}_{Y1}.png",
           f"Change of the forest-expansion effect: [LCC − CTRL]_FUT − [LCC − CTRL]_PD ({Y0}–{Y1}), {where[line]}")

# quick numbers for the reply: regional means ± CI
rows = []
for key in PANELS:
    sub = d.xs((key, "regional"), level=("panel", "line"))
    rows.append({"panel": key, "units": UNITS[key], **{c: "{:+.3g} ± {:.2g}".format(*mean_ci(sub[c])) for c in d.columns}})
print(pd.DataFrame(rows).set_index("panel").to_string())
