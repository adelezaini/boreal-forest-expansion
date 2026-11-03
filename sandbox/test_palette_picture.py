"""Sandbox: palette from the user's reference picture (gold / teal / navy / plum), extended with orange and red.

Draws the charts that use the categorical colours of forcing_maps (TERM_STYLE, WATER_BUDGET_COLORS,
PERIOD_COLORS, REGION_COLORS) with the current palette (A) and the picture palette (G), same data,
so they can be compared side by side. Maps (RdBu_r) are not affected. Nothing in results/ is touched.

Run:  cd sandbox && PYTHONPATH=../src <lcc-env python> test_palette_picture.py
Out:  sandbox/test_palette_picture_outputs/{swatch,cvd,<figure>_<option>}.png/.csv
"""
import itertools
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import to_rgb

from boreal_forest_expansion.plotting import forcing_maps as fm
from boreal_forest_expansion.plotting.style import set_default_style

set_default_style()
OUT = HERE / "test_palette_picture_outputs"
OUT.mkdir(exist_ok=True)
START, END = 2001, 2014
years = dict(start_year=START, end_year=END, save=False)

# ---------------------------------------------------------------- the palette
# First four: sampled from the screenshot (blurred, so approximate; gold made a bit more saturated
# than the sampled #e2c265, which is the anti-aliased marker edge). Orange and red: added at the
# same "muted, mid-dark" character so the six read as one family, hue order gold → orange → red
# → plum → navy → teal.
PICTURE = {
    "gold":   "#E3B94F",
    "orange": "#DE7A3A",
    "red":    "#B5332E",
    "plum":   "#8C4A90",
    "navy":   "#36449A",   # sampled #23257A; lightened (user 2026-11-03 16:00: "a bit less dark")
    "teal":   "#5D9A92",
}
P = PICTURE

PALETTES = {
    "A_current": dict(dir="#d08a2e", cloud="#3b75af", rest="#c44e52", PD="#3b75af", FUT="#c44e52",
                      water=["#3b75af", "#4f9e5a", "#d08a2e", "#7fc6d6", "#8c6bb1", "#9a9a9a"]),
    # Roles: aerosol-direct = gold (sunlight), cloud = navy, rest = teal; PD = navy, FUT = red
    # (also modified cells = red, unmodified = navy). Water: P navy, ET teal, R_liq orange,
    # R_ice gold, ΔTWS plum, residual grey (WATER_BUDGET_TERMS order).
    "G_picture": dict(dir=P["gold"], cloud=P["navy"], rest=P["teal"], PD=P["navy"], FUT=P["red"],
                      water=[P["navy"], P["teal"], P["orange"], P["gold"], P["plum"], "#9a9a9a"]),
}
# User 2026-11-03 15:50: series take the palette colours IN ORDER (bar 1 = colour 1, bar 2 = colour 2, ...).
# Two possible orders: H = the picture's (gold, teal, navy, plum) continued with red, orange;
# I = hue wheel (gold, orange, red, plum, navy, teal). PD / FUT keep navy / red (two series, max contrast).
ORDERS = {"H_order_picture": ["gold", "teal", "navy", "plum", "red", "orange"],
          "I_order_hue": ["gold", "orange", "red", "plum", "navy", "teal"],
          "J_order_teal_first": ["teal", "navy", "plum", "red", "orange", "gold"]}   # user 2026-11-03 15:56
for key, order in ORDERS.items():
    c = [P[n] for n in order]
    PALETTES[key] = dict(dir=c[0], cloud=c[1], rest=c[2], PD=P["navy"], FUT=P["red"], water=c[:5] + ["#9a9a9a"])
# User 2026-11-03 16:23: total not black; albedo-proxy hatch in the F_rest colour (now in forcing_maps).
PALETTES["J2_total_grey"] = {**PALETTES["J_order_teal_first"], "toa": "#8C8C8C"}
PALETTES["J3_total_gold"] = {**PALETTES["J_order_teal_first"], "toa": P["gold"]}
# User 2026-11-03 16:31 (plan can-we-try-to-mellow-sutherland): J tuned for CVD. navy darker, plum lighter/pinker,
# gold lighter, orange/red/teal kept; light grey (#CCCCCC) for total + water residual (mid grey ~ teal under CVD).
PICTURE_TUNED = {**PICTURE, "navy": "#2C3990", "plum": "#A8559A", "gold": "#EBC45C"}
_n = [PICTURE_TUNED[k] for k in ["teal", "navy", "plum", "red", "orange", "gold"]]
_base = dict(dir=_n[0], cloud=_n[1], rest=_n[2], PD=PICTURE_TUNED["navy"], FUT=PICTURE_TUNED["red"], water=_n[:5] + ["#CCCCCC"])
PALETTES["N1_tuned_total_lightgrey"] = {**_base, "toa": "#CCCCCC"}
PALETTES["N2_tuned_total_hollow"] = {**_base, "toa": "none"}   # outline bar, see forcing_maps
# User 2026-11-03 17:01: red more pastel (closer to plum); total in gold (O1) or orange (O2).
PICTURE_O = {**PICTURE_TUNED, "red": "#C4524E"}   # sampled-family red #B5332E softened; vs orange 9.7, vs plum 8.5 (worst CVD)
_o = [PICTURE_O[k] for k in ["teal", "navy", "plum", "red", "orange", "gold"]]
_obase = dict(dir=_o[0], cloud=_o[1], rest=_o[2], PD=PICTURE_O["navy"], FUT=PICTURE_O["red"], water=_o[:5] + ["#CCCCCC"])
PALETTES["O1_pastelred_total_gold"] = {**_obase, "toa": PICTURE_O["gold"]}
PALETTES["O2_pastelred_total_orange"] = {**_obase, "toa": PICTURE_O["orange"]}
# User 2026-11-03 17:07: plum dark again (like #8C4A90) but pinker -> #9A4A84 (worst CVD: navy 10.8, red 10.0, teal 11.3).
PICTURE_P = {**PICTURE_O, "plum": "#9A4A84"}
_q = [PICTURE_P[k] for k in ["teal", "navy", "plum", "red", "orange", "gold"]]
_pbase = dict(dir=_q[0], cloud=_q[1], rest=_q[2], PD=PICTURE_P["navy"], FUT=PICTURE_P["red"], water=_q[:5] + ["#CCCCCC"])
PALETTES["P1_darkplum_total_gold"] = {**_pbase, "toa": PICTURE_P["gold"]}
PALETTES["P2_darkplum_total_orange"] = {**_pbase, "toa": PICTURE_P["orange"]}
# User 2026-11-03 17:14: red in between #B5332E and pastel #C4524E -> #BC423E.
PICTURE_Q = {**PICTURE_P, "red": "#BC423E"}
_r = [PICTURE_Q[k] for k in ["teal", "navy", "plum", "red", "orange", "gold"]]
_qbase = dict(dir=_r[0], cloud=_r[1], rest=_r[2], PD=PICTURE_Q["navy"], FUT=PICTURE_Q["red"], water=_r[:5] + ["#CCCCCC"])
PALETTES["Q1_midred_total_gold"] = {**_qbase, "toa": PICTURE_Q["gold"]}
PALETTES["Q2_midred_total_orange"] = {**_qbase, "toa": PICTURE_Q["orange"]}
# User 2026-11-03 16:13: 12-colour set = 4 hue families x 3 shades (light, mid, dark).
FAMILIES = {
    "purple-1": "#D2D1E2", "purple-2": "#C1A7C4", "purple-3": "#AD7BA4",
    "blue-1": "#93C7EC", "blue-2": "#6DA1D6", "blue-3": "#3E79BD",
    "green-1": "#B8D29E", "green-2": "#7BB47D", "green-3": "#2C925B",
    "gold": "#F4A937", "orange": "#EB7121", "red": "#D9070D",
}
F = FAMILIES
# K = by meaning: aerosol-direct warm, cloud blue, rest (mostly surface albedo of the forest) green;
#     water: P dark blue, ET green (vegetation), runoff liquid/ice = mid/light blue (one family), dTWS purple.
PALETTES["K_families_meaning"] = dict(dir=F["orange"], cloud=F["blue-3"], rest=F["green-3"], PD=F["blue-3"], FUT=F["red"],
                                      water=[F["blue-3"], F["green-3"], F["blue-2"], F["blue-1"], F["purple-3"], "#9a9a9a"])
# L = in list order, darkest shade of each family, then the warm trio: purple, blue, green, gold, orange, red.
_l = [F["purple-3"], F["blue-3"], F["green-3"], F["gold"], F["orange"], F["red"]]
PALETTES["L_families_order"] = dict(dir=_l[0], cloud=_l[1], rest=_l[2], PD=F["blue-3"], FUT=F["red"], water=_l[:5] + ["#9a9a9a"])
# User 2026-11-03 16:19: Paul Tol "muted", in Tol's order; M takes the colours in that order.
MUTED = {"indigo": "#332288", "cyan": "#88CCEE", "teal": "#44AA99", "green": "#117733", "olive": "#999933",
         "sand": "#DDCC77", "rose": "#CC6677", "wine": "#882255", "purple": "#AA4499"}
_m = list(MUTED.values())
PALETTES["M_tol_muted_order"] = dict(dir=_m[0], cloud=_m[1], rest=_m[2], PD=MUTED["indigo"], FUT=MUTED["rose"],
                                     water=_m[:5] + ["#bbbbbb"])
DEFAULTS = dict(TERM_STYLE=dict(fm.TERM_STYLE), WATER_BUDGET_COLORS=list(fm.WATER_BUDGET_COLORS),
                PERIOD_COLORS=dict(fm.PERIOD_COLORS), REGION_COLORS=dict(fm.REGION_COLORS))


def apply(p):
    ts = DEFAULTS["TERM_STYLE"]
    fm.TERM_STYLE = {**ts, "toa": (ts["toa"][0], p.get("toa", ts["toa"][1])), "dir": (ts["dir"][0], p["dir"]),
                     "cloud": (ts["cloud"][0], p["cloud"]), "rest": (ts["rest"][0], p["rest"])}
    fm.WATER_BUDGET_COLORS = p["water"]
    fm.PERIOD_COLORS = {"PD": p["PD"], "FUT": p["FUT"]}
    fm.REGION_COLORS = dict(zip(DEFAULTS["REGION_COLORS"], [p["FUT"], p["PD"]]))  # modified, unmodified


def restore():
    for k, v in DEFAULTS.items():
        setattr(fm, k, v)


# ---------------------------------------------------------------- colour-blind check (as test_palettes.ipynb)
MACHADO = {   # Machado, Oliveira & Fernandes (2009), severity 1.0, linear RGB
    "deutan": np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]]),
    "protan": np.array([[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]]),
    "tritan": np.array([[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]]),
}


def to_linear(c):
    c = np.array(to_rgb(c))
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def oklab(lin):
    lms = np.array([[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566],
                    [0.0883024619, 0.2817188376, 0.6299787005]]) @ np.clip(lin, 0, 1)
    return np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099],
                     [0.0259040371, 0.7827717662, -0.8086757660]]) @ np.cbrt(lms)


def worst_pair(colors, vision):
    lab = {c: oklab(MACHADO[vision] @ to_linear(c) if vision != "normal" else to_linear(c)) for c in colors}
    return min((100 * np.linalg.norm(lab[a] - lab[b]), f"{a}–{b}") for a, b in itertools.combinations(colors, 2))


def cvd_table():
    rows = []
    groups_of = lambda p: {"Ghan terms (+ total)": ([] if p.get("toa") == "none" else [p.get("toa", "#333333")])
                                                    + [p["dir"], p["cloud"], p["rest"]],
                           "water budget": p["water"], "PD / FUT": [p["PD"], p["FUT"]]}
    for name, p in {**PALETTES, "G_all_six": None}.items():
        groups = {"all six": list(PICTURE.values())} if p is None else groups_of(p)
        for group, colors in groups.items():
            r = dict(option=name, chart=group)
            for v in ("normal", "deutan", "protan", "tritan"):
                de, pair = worst_pair(colors, v)
                r[v], r[f"{v} pair"] = round(de, 1), pair
            rows.append(r)
    return pd.DataFrame(rows)


def swatch(colors=None, title="Picture palette (gold/teal/navy/plum) + orange, red", fname="swatch.png"):
    colors = colors or PICTURE
    """The six colours as markers + error bars (the picture's style) and as bars, normal + simulated CVD."""
    visions = ["normal", "deutan", "protan", "tritan"]
    fig, axes = plt.subplots(1, len(visions), figsize=(14, 0.45 * len(colors) + 0.6), constrained_layout=True)
    rng = np.random.default_rng(0)
    for ax, v in zip(axes, visions):
        for i, (nm, c) in enumerate(colors.items()):
            rgb = to_rgb(c) if v == "normal" else tuple(np.clip(
                (lambda l: np.where(l <= 0.0031308, 12.92 * l, 1.055 * np.clip(l, 0, None) ** (1 / 2.4) - 0.055))(
                    MACHADO[v] @ to_linear(c)), 0, 1))
            ax.barh(i, 1, left=0, color=rgb, height=0.8)
            x = np.linspace(1.2, 2.8, 8)
            ax.errorbar(x, i + 0.25 * rng.standard_normal(8), yerr=0.2, fmt="o", ms=3.5, color=rgb, capsize=0, lw=1)
            ax.text(-0.05, i, f"{nm} {c}" if v == "normal" else nm, ha="right", va="center", fontsize=8)
        ax.set_xlim(-1.2 if v == "normal" else -0.6, 3)
        ax.set_ylim(-0.6, len(colors) - 0.4)
        ax.invert_yaxis()
        ax.axis("off")
        ax.set_title(v if v == "normal" else f"simulated {v}", fontsize=10)
    fig.suptitle(title, fontsize=11, fontweight="bold")
    fig.savefig(OUT / fname, dpi=130, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    swatch()
    swatch(FAMILIES, "12-colour set: 4 families x 3 shades", "swatch_families.png")
    swatch(PICTURE_TUNED, "Palette J tuned for colour-blind readers", "swatch_tuned.png")
    swatch(PICTURE_O, "Palette O: J tuned + pastel red", "swatch_O.png")
    swatch(PICTURE_P, "Palette P: pastel red + dark pink plum", "swatch_P.png")
    swatch(PICTURE_Q, "Palette Q: mid red + dark pink plum", "swatch_Q.png")
    swatch(MUTED, "Paul Tol muted (Tol order)", "swatch_muted.png")
    cvd = cvd_table()
    cvd.to_csv(OUT / "cvd.csv", index=False)
    print(cvd[["option", "chart", "normal", "deutan", "protan", "tritan", "deutan pair"]].to_string(index=False))

    print("tables ...", flush=True)
    budget = fm.radiative_budget_table(START, END)
    water = fm.water_budget_table(START, END)
    figures = [("radiative_budget", lambda: fm.make_radiative_budget_figure(budget, **years)),
               ("water_budget", lambda: fm.make_water_budget_figure(water, "LCC-CTRL", **years)),
               ("paired_years", lambda: fm.make_paired_years_figure(budget, band="NET", **years)),
               ("emission_origin", lambda: fm.make_emission_origin_figure(**years))]
    only = sys.argv[1:]   # optional: palette names to draw, e.g. H_order_picture I_order_hue
    for name, p in PALETTES.items():
        if only and name not in only:
            continue
        apply(p)
        try:
            for tag, make in figures:
                try:
                    fig, _ = make()
                except Exception as e:   # one broken chart must not stop the others
                    print(f"  {tag} {name}: FAILED {type(e).__name__}: {e}")
                    continue
                fig.savefig(OUT / f"{tag}_{name}.png", dpi=110, bbox_inches="tight")
                plt.close(fig)
                print(f"  {tag}_{name}.png", flush=True)
        finally:
            restore()
    print("done")
