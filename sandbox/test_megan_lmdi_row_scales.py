"""Style test: LMDI attribution maps with one colour scale per row (not paper output).
Reuses the loading code of analysis/megan-lmdi-attribution-maps.ipynb; writes only to
sandbox/test_megan_lmdi_row_scales_outputs/.  Usage: script.py stats | script.py draw R2_PD R2_FUT"""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats as st

REPO = Path("/cluster/home/adelez/BOREAL-FOREST-EXPANSION")
OUT = REPO / "sandbox/test_megan_lmdi_row_scales_outputs"
OUT.mkdir(exist_ok=True)
nb = json.load(open(REPO / "analysis/megan-lmdi-attribution-maps.ipynb"))
for i in (2, 3):   # setup + loading + season terms
    exec("".join(nb["cells"][i]["source"]))


def weights(E0):
    e = E0.mean("year")
    thr = MIN_EMISSION_SHARE * float(np.nanquantile(e.where(e["lat"] >= LAT_MIN).values, 0.98))
    keep = e > thr
    return keep, (e * np.cos(np.deg2rad(e["lat"]))).where(keep, 0), mm._modified_mask(e)


if sys.argv[1] == "stats":
    rows = []
    for (exp, group, season), (E0, T) in data.items():
        keep, w, mod = weights(E0)
        for k in ["dlnE", "composition", "activity", *GAMMAS]:
            if k == "gammaC" and group != "isoprene":
                continue
            x = T[k].where(keep)
            for region, mask in (("45N", x["lat"] >= LAT_MIN), ("modified", (x["lat"] >= LAT_MIN) & (mod > 0))):
                ww = w.where(mask, 0)
                y = ((x * ww).sum(("lat", "lon")) / ww.where(np.isfinite(x)).sum(("lat", "lon"))).values
                m, s = y.mean(), y.std(ddof=1)
                n = next((n for n in range(3, 201) if st.t.ppf(.975, n - 1) * s / np.sqrt(n) < abs(m)), np.nan)
                rows.append(dict(exp=exp, group=group, season=season, region=region, term=k, mean=m, sd_years=s,
                                 ci95=st.t.ppf(.975, 5) * s / np.sqrt(6), n_years_for_sig=n,
                                 p98_abs=float(np.nanquantile(abs(x.mean("year").where(mask)).values, .98))))
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "row_scale_stats.csv", index=False)
    pd.set_option("display.width", 200, "display.max_rows", 500)
    print(t[(t.season == "JJA")].round(2).to_string(index=False))
else:
    R2 = {"PD": float(sys.argv[2]), "FUT": float(sys.argv[3])}
    R1 = {"PD": (60.0, 15.0), "FUT": (100.0, 25.0)}
    for (exp, group, season), (E0, T) in data.items():
        keep, w, mod = weights(E0)
        lcc, ctrl = EXPERIMENTS[exp][1:]
        gam = [g for g in GAMMAS if group == "isoprene" or g != "gammaC"]
        rows = [["dlnE", "composition", "activity", "safeguard"], gam]
        scales = [R1[exp], (R2[exp], R2[exp] / 4)]
        ncols = max(map(len, rows))
        fig, axes = fm.map_grid(2, ncols, left=2.2, titles_every_row=True)
        for i, keys in enumerate(rows):
            v, step = scales[i]
            norm = mcolors.TwoSlopeNorm(vmin=-v, vcenter=0, vmax=v)
            for j in range(ncols):
                if j >= len(keys):
                    axes[i, j].set_visible(False)
                    continue
                x = T[keys[j]].where(keep)
                m, half = mm._interval(x, w, LAT_MIN)
                p = mm._panel(axes[i, j], x.mean("year"), norm, "RdBu_r", TITLE[keys[j]], LAT_MIN,
                              not_sig=mm._not_significant(x, LAT_MIN, FDR_ALPHA), modified=mod,
                              text=fm._format_interval(m, half))
            cb = fm._cbar_below(fig, axes[i, :len(keys)], p, "100 · Δln (≈ % change), LCC vs CTRL",
                                fm.CBAR_LABELSIZE_SHARED, shrink=0.6)
            cb.set_ticks(np.arange(-v, v + step / 2, step))
        mm._row_label(axes[0, 0], "Δln E\n= Δln(w·ε)\n+ Σ Δln γ$_i$\n+ safeguard")
        mm._row_label(axes[1, 0], "activity\n= Σ Δln γ$_i$\n(exact, no\nresidual)")
        mm._title(fig, f"Attribution of the emission change, exact split (LMDI), {mm.GROUP_TITLE[group]}: "
                       f"{exp} {lcc} vs {ctrl}, {season} (6 years: {', '.join(map(str, YEARS))})",
                  rf"$\mathit{{Under\ the\ maps}}$: CTRL-emission-weighted mean {LAT_MIN:g}–90°N ± 95 % CI of the 6 yearly means"
                  " · hatched: not significant · dashed line: modified cells · colour scale differs between rows")
        fig.savefig(OUT / f"{exp}_{group}_attribution_LMDI_{season}_6yr.png", dpi=200, bbox_inches="tight")
        plt.close(fig)
    print("drawn in", OUT)
