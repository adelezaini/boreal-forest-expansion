"""Layout test (user 2026-11-25): LMDI attribution maps with LAI moved to row 1 (not paper output).
Row 1 (one scale, panels add up): EMISSION = COMPOSITION + LAI + ACTIVITY w/o LAI (+ CLM SAFEGUARD)
Row 2 (own scale): split of ACTIVITY w/o LAI = temperature + light + leaf age (+ CO2, isoprene only)
Variant "with-safeguard": safeguard panel in row 1; "no-safeguard": safeguard only in the footnote.
Reuses cells 2-3 of analysis/megan-lmdi-attribution-maps.ipynb; writes only to sandbox/test_megan_lmdi_lai_row1_outputs/.
Usage: python sandbox/test_megan_lmdi_lai_row1.py"""
import json
from pathlib import Path

REPO = Path("/cluster/home/adelez/BOREAL-FOREST-EXPANSION")
OUT = REPO / "sandbox/test_megan_lmdi_lai_row1_outputs"
OUT.mkdir(exist_ok=True)
nb = json.load(open(REPO / "analysis/megan-lmdi-attribution-maps.ipynb"))
for i in (2, 3):   # setup + loading + season terms (defines data, TITLE, GAMMAS, mm, fm, ...)
    exec("".join(nb["cells"][i]["source"]))

R1 = {"PD": (60.0, 15.0), "FUT": (100.0, 25.0)}   # = mm.ATTRIBUTION_VMAX (row 1 addable by eye)
R2 = {"PD": (10.0, 2.5), "FUT": (10.0, 2.5)}
TITLE["other"] = "ACTIVITY w/o LAI\nΔln γ$_T$+γ$_P$+γ$_A$+γ$_C$"
rows_tab = []

for (exp, group, season), (E0, T) in data.items():
    T = dict(T)
    other = [g for g in GAMMAS if g != "gammaL" and (group == "isoprene" or g != "gammaC")]
    T["other"] = sum(T[g] for g in other)
    lcc, ctrl = EXPERIMENTS[exp][1:]
    e_ctrl = E0.mean("year")
    thr = MIN_EMISSION_SHARE * float(np.nanquantile(e_ctrl.where(e_ctrl["lat"] >= LAT_MIN).values, 0.98))
    keep = e_ctrl > thr
    w_em = (e_ctrl * np.cos(np.deg2rad(e_ctrl["lat"]))).where(keep, 0)
    mod = mm._modified_mask(e_ctrl)
    clos = float(abs(T["composition"] + T["gammaL"] + T["other"] + T["safeguard"] - T["dlnE"]).max())
    assert clos < 1e-8, clos
    for variant in ("with-safeguard", "no-safeguard"):
        row1 = ["dlnE", "composition", "gammaL", "other"] + (["safeguard"] if variant == "with-safeguard" else [])
        rows, scales = [row1, other], [R1[exp], R2[exp]]
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
                m, half = mm._interval(x, w_em, LAT_MIN)
                if variant == "with-safeguard":
                    rows_tab.append(dict(experiment=exp, group=group, season=season, term=keys[j], mean=m, ci95=half))
                p = mm._panel(axes[i, j], x.mean("year"), norm, "RdBu_r", TITLE[keys[j]], LAT_MIN,
                              not_sig=mm._not_significant(x, LAT_MIN, FDR_ALPHA), modified=mod,
                              text=fm._format_interval(m, half),
                              region_text=mm._region_texts(x, lambda r, y=x: mm._interval(y.where(r), w_em, LAT_MIN)))
            cb = fm._cbar_below(fig, axes[i, :len(keys)], p, "100 · Δln (≈ % change), LCC vs CTRL",
                                fm.CBAR_LABELSIZE_SHARED, shrink=0.6)
            cb.set_ticks(np.arange(-v, v + step / 2, step))
        if variant == "with-safeguard":
            mm._row_label(axes[0, 0], "Δln E\n= Δln(w·ε)\n+ Δln γ$_L$\n+ other γ\n+ safeguard")
        else:
            sg_m, sg_h = mm._interval(T["safeguard"].where(keep), w_em, LAT_MIN)
            mm._row_label(axes[0, 0], "Δln E\n= Δln(w·ε)\n+ Δln γ$_L$\n+ other γ\n(+ safeguard$^†$)")
            fig.text(0.5, -0.045, f"$^†$CLM safeguard (MEG set to 0 when total γ is out of range): "
                     f"{fm._format_interval(sg_m, sg_h)} (45–90°N), included in EMISSION, not shown",
                     ha="center", fontsize=9)
        mm._row_label(axes[1, 0], "other γ\n= Σ Δln γ$_i$,\ni ≠ L")
        mm._title(fig, f"Attribution of the emission change, exact split (LMDI), {mm.GROUP_TITLE[group]}: "
                       f"{exp} {lcc} vs {ctrl}, {season} (6 years: {', '.join(map(str, YEARS))})",
                  rf"$\mathit{{Under\ the\ maps}}$: CTRL-emission-weighted mean ± 95 % CI of the 6 yearly means"
                  f" {mm._regions_subtitle(LAT_MIN)} · hatched: not significant{mm._outline_note()}"
                  " · colour scale differs between rows")
        fm.add_region_footnote(fig)
        path = OUT / variant / f"{exp}_{group}_attribution_LMDI_{season}_6yr.png"
        path.parent.mkdir(exist_ok=True)
        fig.savefig(path, dpi=200, bbox_inches="tight"); print("Saved", path, flush=True)
        plt.close(fig)

pd.DataFrame(rows_tab).to_csv(OUT / "lai_row1_means_45N.csv", index=False)
print("done")
