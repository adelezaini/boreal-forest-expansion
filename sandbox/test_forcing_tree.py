"""Three-row forcing decomposition (sandbox, user 2026-11-23). Nothing is written to results/.

Row 1  total                 T = case1 − case2 (interactive)
Row 2  non-BVOC              N = same prescribed emissions E in both runs
       BVOC                  B = LCC_P_fBVOClccP − LCC_P_fBVOC<E>
Row 3  albedo (SW clear-sky surface proxy) of N · rest of N = N − albedo · Ghan cloud, direct, rest of B
       (LW: no albedo / rest, the proxy is a SW quantity; only the BVOC branch is split)
Closure, year by year: δ = T − N − B.

Stage 1: python test_forcing_tree.py compute   yearly fields (cache), means table, q98 table
Stage 2: python test_forcing_tree.py draw      figures in test_forcing_tree_outputs/
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
from boreal_forest_expansion.plotting import forcing_maps as fm  # noqa: E402

OUT = REPO / "sandbox" / "test_forcing_tree_outputs"
CACHE = Path("/cluster/work/users/adelez/boreal-caches/forcing-tree")
Y0, Y1 = 2001, 2025
BANDS = ("NET", "SW", "LW")   # LW: no albedo / rest panels (the albedo proxy is a SW quantity)

# tag (as in results/figures/radiative-forcing-decomposition) -> total, non-BVOC, BVOC pairs, title labels
CASES = {
    "LCCPD_fBVOCctrlPD": dict(
        T=("LCC_PD", "CTRL_PD"), N=("LCC_PD_fBVOCctrlPD", "CTRL_PD_fBVOCctrlPD"),
        B=("LCC_PD_fBVOClccPD", "LCC_PD_fBVOCctrlPD"), title="[LCC − CTRL] _PD"),
    "LCCFUT_fBVOCctrlFUT": dict(
        T=("LCC_FUT", "CTRL_FUT"), N=("LCC_FUT_fBVOCctrlFUT", "CTRL_FUT_fBVOCctrlFUT"),
        B=("LCC_FUT_fBVOClccFUT", "LCC_FUT_fBVOCctrlFUT"), title="[LCC − CTRL] _FUT"),
    "LCCFUT_fBVOClccPD": dict(
        T=("LCC_FUT", "LCC_PD"), N=("LCC_FUT_fBVOClccPD", "LCC_PD_fBVOClccPD"),
        B=("LCC_FUT_fBVOClccFUT", "LCC_FUT_fBVOClccPD"), title="LCC_FUT − LCC_PD"),
    "LCCFUT_fBVOCctrlPD": dict(
        T=("LCC_FUT", "CTRL_PD"), N=("LCC_FUT_fBVOCctrlPD", "CTRL_PD_fBVOCctrlPD"),
        B=("LCC_FUT_fBVOClccFUT", "LCC_FUT_fBVOCctrlPD"), title="LCC_FUT − CTRL_PD"),
}
PANELS = ("total", "nonbvoc", "bvoc", "albedo", "rest", "cloud", "direct", "chem")


def panels(band):
    return tuple(k for k in PANELS if band != "LW" or k not in ("albedo", "rest"))


def fields(case, band):
    """Yearly maps of every panel + δ, W m-2."""
    yd = lambda pair, var: fm.yearly_difference(*pair, "RADIATIVE", var, Y0, Y1).load()
    f = {"total": yd(case["T"], f"{band}_toa"), "nonbvoc": yd(case["N"], f"{band}_toa"),
         "bvoc": yd(case["B"], f"{band}_toa"),
         "cloud": yd(case["B"], f"{band}_cloud"), "direct": yd(case["B"], f"{band}_dir"),
         "chem": yd(case["B"], f"{band}_rest")}
    if band != "LW":
        f["albedo"] = yd(case["N"], "SFC_ALBEDO_FORCING_CLEAR")
        f["rest"] = f["nonbvoc"] - f["albedo"]
    f["delta"] = f["total"] - f["nonbvoc"] - f["bvoc"]
    ghan = float(abs(f["cloud"] + f["direct"] + f["chem"] - f["bvoc"]).max())
    if ghan > 1e-3:
        raise ValueError(f"Ghan terms do not close: {ghan}")
    return xr.Dataset({k: v.drop_attrs().rename(k) for k, v in f.items()}), ghan


def compute():
    OUT.mkdir(exist_ok=True); CACHE.mkdir(parents=True, exist_ok=True)
    means, q98 = [], []
    for tag, case in CASES.items():
        for band in BANDS:
            path = CACHE / f"{tag}_{band}.nc"
            if path.exists():   # resume after a failed NIRD read
                ds = xr.load_dataset(path)
                ghan = float(abs(ds["cloud"] + ds["direct"] + ds["chem"] - ds["bvoc"]).max())
            else:
                for attempt in range(1, 6):
                    try:
                        ds, ghan = fields(case, band)
                        break
                    except RuntimeError as exc:
                        print(f"{tag} {band}: read failed, attempt {attempt}/5: {exc}", flush=True)
                        if attempt == 5:
                            raise
                        time.sleep(20 * attempt)
                ds.to_netcdf(path.with_suffix(".tmp"))
                path.with_suffix(".tmp").rename(path)
            north = ds.mean("year").where(ds["lat"] >= 45)
            for k in (*panels(band), "delta"):
                m, h = fm.regional_mean_interval(ds[k], lat_min=45)
                means.append(dict(case=tag, band=band, panel=k, mean=m, ci95=h))
                v = np.abs(north[k].values); v = v[np.isfinite(v)]
                q98.append(dict(case=tag, band=band, panel=k, q98=np.quantile(v, .98), q995=np.quantile(v, .995)))
            print(f"{tag} {band}: Ghan closure {ghan:.1e} W m-2", flush=True)
    means, q98 = pd.DataFrame(means), pd.DataFrame(q98)
    means.to_csv(OUT / "forcing_tree_means_45N_2001_2025.csv", index=False)
    q98.to_csv(OUT / "forcing_tree_map_ranges_45N_2001_2025.csv", index=False)
    order = [*PANELS, "delta"]
    pd.set_option("display.width", 250)
    print(means.assign(v=means["mean"].map("{:+.3f}".format) + "±" + means.ci95.map("{:.3f}".format))
          .pivot(index=["case", "band"], columns="panel", values="v")[order].to_string())
    print(q98.pivot(index=["case", "band"], columns="panel", values="q98")[order].round(2).to_string())


# Colour scales, from the 98th percentile of |25-yr map| >= 45°N (forcing_tree_map_ranges_45N_2001_2025.csv).
# (vmax, tick step). LCC effect, same climate: total..rest q98 3.2–8.9 -> one scale, BVOC q98 <= 0.41.
# Climate included: total/non-BVOC q98 12–22, albedo/rest 24–38 -> two scales, BVOC q98 <= 1.94.
# LW (no albedo / rest): same climate total/non-BVOC q98 0.35–0.38, BVOC 0.16; climate included 11.9–12.3, BVOC 0.38.
SAME_PERIOD = {"NET": dict(lcc=(8, 2), bvoc=(0.4, 0.1)), "SW": dict(lcc=(8, 2), bvoc=(0.4, 0.1)),
               "LW": dict(lcc=(0.4, 0.1), bvoc=(0.4, 0.1))}
WITH_CLIMATE = {"NET": dict(top=(15, 5), low=(40, 20), bvoc=(2, 0.5)),
                "SW": dict(top=(20, 10), low=(40, 20), bvoc=(2, 0.5)),
                "LW": dict(top=(12, 4), bvoc=(0.4, 0.1))}
SCALES = {"LCCPD_fBVOCctrlPD": SAME_PERIOD, "LCCFUT_fBVOCctrlFUT": SAME_PERIOD,
          "LCCFUT_fBVOClccPD": WITH_CLIMATE, "LCCFUT_fBVOCctrlPD": WITH_CLIMATE}


def draw_one(tag, band):
    import matplotlib.colors as mcolors
    import matplotlib.pyplot as plt
    case, sc = CASES[tag], SCALES[tag][band]
    ds = xr.load_dataset(CACHE / f"{tag}_{band}.nc")
    top, low = sc.get("lcc", sc.get("top")), sc.get("lcc", sc.get("low"))
    pair = lambda p: f"{p[0]} − {p[1]}"
    # key: (row, col, title, run pair, scale)
    spec = {"total": (0, None, f"TOTAL ({band})", pair(case["T"]), top),
            "nonbvoc": (1, None, f"NON-BVOC ({band})", pair(case["N"]), top),
            "bvoc": (1, 3, f"BVOC-RELATED ({band})", pair(case["B"]), sc["bvoc"]),
            "albedo": (2, 0, "ALBEDO / SW CLEAR-SKY FORCING", None, low),
            "rest": (2, 1, f"REST NON-BVOC ({band} − albedo)", None, low),
            "cloud": (2, 2, f"BVOC-SOA-CLOUD ({band})", None, sc["bvoc"]),
            "direct": (2, 3, f"BVOC-DIRECT SOA ({band})", None, sc["bvoc"]),
            "chem": (2, 4, f"BVOC CHEMISTRY / RESIDUAL ({band})", None, sc["bvoc"])}
    if band == "LW":   # albedo proxy is SW only: no split of the non-BVOC branch
        del spec["albedo"], spec["rest"]

    fig, grid = fm.map_grid(3, 5, under=fm.UNDER_CBAR + 0.4, titles_every_row=True, top_extra=0.12)
    x = [grid[2, j].get_position().x0 for j in range(5)]
    x_non, x_bvoc = (x[0] + x[1]) / 2, x[3]
    x_pos = {"total": (x_non + x_bvoc) / 2, "nonbvoc": x_non, "bvoc": x_bvoc}
    axes = {}
    for k, (r, c, *_rest) in spec.items():
        ax = grid[r, c if c is not None else 0]
        if k in x_pos:
            b = grid[r, 0].get_position()
            ax = grid[r, 2 if k == "total" else (0 if k == "nonbvoc" else 3)]
            ax.set_position([x_pos[k], b.y0, b.width, b.height])
        axes[k] = ax
    for ax in grid.ravel():
        if not any(ax is a for a in axes.values()):
            ax.remove()

    for k, (r, c, title, runs, (vmax, _)) in spec.items():
        panel = fm.MapPanel(key=k, title=title, variable_class="RADIATIVE", variable=k, case1_role="", case2_role="")
        fm._plot_panel(axes[k], panel, {}, Y0, Y1, 45, 45, True, 0.10, vmax=vmax, d=ds[k], cmap="RdBu_r", add_cbar=False)
        if runs:
            axes[k].set_title(title, fontsize=9.5, fontweight="semibold", pad=22)
            axes[k].text(0.5, 1.035, runs, transform=axes[k].transAxes, ha="center", va="bottom", fontsize=8)

    # tree connectors, figure coordinates
    H = fig.get_figheight()
    def link(parent, children):
        p = axes[parent].get_position()
        # from below the parent's colourbar label to above the children's titles
        y0, y2 = p.y0 - (fm.UNDER_CBAR - 0.05) / H, axes[children[0]].get_position().y1 + (0.62 if children[0] in x_pos else 0.42) / H
        y1 = (y0 + y2) / 2
        xp = (p.x0 + p.x1) / 2
        xs = [(axes[c].get_position().x0 + axes[c].get_position().x1) / 2 for c in children]
        kw = dict(transform=fig.transFigure, color="0.35", lw=0.9)
        fig.add_artist(plt.Line2D([xp, xp], [y0, y1], **kw))
        fig.add_artist(plt.Line2D([min(xs + [xp]), max(xs + [xp])], [y1, y1], **kw))
        for xc in xs:
            fig.add_artist(plt.Line2D([xc, xc], [y1, y2], **kw))
    link("total", ["nonbvoc", "bvoc"]); link("bvoc", ["cloud", "direct", "chem"])
    if "albedo" in spec:
        link("nonbvoc", ["albedo", "rest"])

    # δ, quantified next to the total
    m, h = fm.regional_mean_interval(ds["delta"], lat_min=45)
    b = axes["total"].get_position()
    fig.text(b.x1 + 0.3 / fig.get_figwidth(), (b.y0 + b.y1) / 2,
             "Closure: total = non-BVOC + BVOC + δ\n"
             f"δ = {fm._format_interval(m, h)} W m$^{{-2}}$\n"
             f"δ = art({case['T'][0]}) − art({case['T'][1]})\n"
             "art = interactive − own emissions\nprescribed (δ not drawn)",
             ha="left", va="center", fontsize=10, linespacing=1.45)

    def bar(keys, scale, label):
        vmax, step = scale
        sm = plt.cm.ScalarMappable(norm=mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax), cmap="RdBu_r")
        cb = fm._cbar_below(fig, [axes[k] for k in keys], sm, f"{label} [W m$^{{-2}}$]", fm.CBAR_LABELSIZE_SHARED,
                            shrink=0.9 if len(keys) == 1 else 0.85)
        if len(keys) == 1 and 2 * round(vmax / step) + 1 > (9 if step >= 1 else 7):   # one map wide: decimals need room
            step *= 2
        n = int(round(vmax / step))
        cb.set_ticks([i * step for i in range(-n, n + 1)])
    bar(["total"], top, "total")
    bar(["nonbvoc"], top, "non-BVOC")
    bar(["bvoc"], sc["bvoc"], "BVOC-related")
    if "albedo" in spec:
        bar(["albedo", "rest"], low, "albedo, rest non-BVOC")
    bar(["cloud", "direct", "chem"], sc["bvoc"], "BVOC-related terms")

    fm.add_suptitle(fig, f"{case['title']}: radiative forcing decomposition, {band}", 45,
                    y=fm._suptitle_y(fig), years=Y1 - Y0 + 1)
    path = OUT / f"{tag}_forcing_tree_{band}_{Y0}_{Y1}_designA.png"
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("Saved", path, flush=True)


def draw(only=None):
    import matplotlib
    matplotlib.use("Agg")
    from boreal_forest_expansion.plotting.style import set_default_style
    set_default_style()
    for tag in CASES:
        for band in BANDS:
            if only is None or (tag, band) == only:
                draw_one(tag, band)


if __name__ == "__main__":
    if sys.argv[1] == "compute":
        compute()
    else:
        draw(tuple(sys.argv[2:4]) if len(sys.argv) > 2 else None)
