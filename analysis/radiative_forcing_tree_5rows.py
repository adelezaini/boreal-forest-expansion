"""Five-row forcing tree (4 rows until 2026-11-25, renamed with row 5, user), alternative layout (from sandbox, user 2026-11-24; moved to analysis/ 2026-11-24).
Figures in results/figures/radiative-forcing-tree-5rows/, tables in results/tables/radiative-forcing-tree-5rows/.

Row 1  total T (NET)
Row 2  non-BVOC N · BVOC B (NET), pairs as in radiative_forcing_tree.py
Row 3  Ghan split of both branches (NET): cloud, direct, clean-clear-sky
Row 4  each row-3 term split into SW and LW
Row 5  CLOUD SW of both branches split by APRP (user 2026-11-25; Taylor et al. 2007, clean fluxes, as in
       analysis/cloud-masking-aprp.ipynb, whose cache it reads): real cloud change + surface-albedo masking
       + atmosphere masking & other. "Other" = Ghan − real − surface masking, so the three add up exactly to
       the CLOUD SW panel (it holds the atmosphere masking, APRP residual and the ≤ 0.01 W m-2 APRP−Ghan gap).
       If the APRP cache for Y0–Y1 is missing, row 5 is left out with a warning (run the notebook first).
No physical labels (albedo, chemistry, ...) in rows 3–4: plain Ghan terms only.

Stage 1: python analysis/radiative_forcing_tree_5rows.py compute   yearly Ghan fields of N (cache), means + q98 tables
Stage 2: python analysis/radiative_forcing_tree_5rows.py draw      figures in results/figures/radiative-forcing-tree-5rows/
Needs the radiative_forcing_tree.py cache (T, N, B and the Ghan terms of B, per band).
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import radiative_forcing_tree as t3  # noqa: E402  (CASES, years, cache of the 3-row tree)
from radiative_forcing_tree import fm  # noqa: E402

FIG = t3.REPO / "results" / "figures" / "radiative-forcing-tree-5rows"
TAB = t3.REPO / "results" / "tables" / "radiative-forcing-tree-5rows"
Y0, Y1 = t3.Y0, t3.Y1
CACHE = Path("/cluster/work/users/adelez/boreal-caches/forcing-tree-5rows") / f"{Y0}_{Y1}"
TERMS = {"cloud": "CLOUD", "dir": "DIRECT", "rest": "CLEAN-CLEAR-SKY"}   # Ghan terms
BANDS = ("NET", "SW", "LW")
APRP_CACHE = t3.REPO / "analysis" / "cloud-masking-aprp_outputs" / "cache"
MASK = {"real": "REAL CLOUD CHANGE", "msfc": "SURFACE-ALBEDO MASKING", "matm": "ATMOSPHERE MASKING & OTHER"}


def add_aprp(ds, tag):
    """Row 5: {n,b}_cloud_SW_{real,msfc,matm} from the clean APRP cache; False if the cache is missing."""
    for x, b in (("n", "N"), ("b", "B")):
        path = APRP_CACHE / "{}__{}_clean_{}_{}.nc".format(*t3.CASES[tag][b], Y0, Y1)
        if not path.exists():
            print(f"WARNING {tag}: no APRP cache {path.name} -> row 5 left out (run analysis/cloud-masking-aprp.ipynb)", flush=True)
            return False
        a = xr.load_dataset(path)
        ghan = ds[f"{x}_cloud_SW"]
        err = float(abs(a["ghan_cloud"] - ghan).max())   # same SW_cloud difference, two caches
        if err > 1e-3 or not np.array_equal(a["year"], ghan["year"]):
            raise ValueError(f"{tag} {x}: APRP ghan_cloud differs from the tree's CLOUD SW by {err}")
        ds[f"{x}_cloud_SW_real"] = a["cloud"]
        ds[f"{x}_cloud_SW_msfc"] = a["mask_sfc"]
        ds[f"{x}_cloud_SW_matm"] = ghan - a["cloud"] - a["mask_sfc"]   # closes exactly on the CLOUD SW panel
        gap = float(abs(ds[f"{x}_cloud_SW_matm"] - a["mask_atm_other"]).max())
        print(f"{tag} {x}: APRP ok, max |matm − (mask_atm + other)| = {gap:.1e} W m-2", flush=True)
    return True


def load(tag):
    """Dataset with keys total, nonbvoc, bvoc (NET) and {n,b}_{term}_{band}, W m-2, yearly."""
    path = CACHE / f"{tag}_nonbvoc_ghan.nc"
    if not path.exists():
        pair = t3.CASES[tag]["N"]
        for attempt in range(1, 6):
            try:
                ds = xr.Dataset({f"n_{t}_{b}": fm.yearly_difference(*pair, "RADIATIVE", f"{b}_{t}", Y0, Y1)
                                 .load().drop_attrs() for t in TERMS for b in BANDS})
                break
            except RuntimeError as exc:
                print(f"{tag}: read failed, attempt {attempt}/5: {exc}", flush=True)
                if attempt == 5:
                    raise
                time.sleep(20 * attempt)
        ds.to_netcdf(path.with_suffix(".tmp")); path.with_suffix(".tmp").rename(path)
    ds = xr.load_dataset(path)
    for b in BANDS:
        c = xr.load_dataset(t3.CACHE / f"{tag}_{b}.nc")
        if b == "NET":
            for k in ("total", "nonbvoc", "bvoc", "delta"):
                ds[k] = c[k]
        for t, k in (("cloud", "cloud"), ("dir", "direct"), ("rest", "chem")):
            ds[f"b_{t}_{b}"] = c[k]
    return ds


def check(ds, tag):
    """Ghan sum = branch NET, and SW + LW = NET, for every term (max abs error, W m-2)."""
    err = {}
    for x, branch in (("n", "nonbvoc"), ("b", "bvoc")):
        err[f"{x} ghan"] = float(abs(sum(ds[f"{x}_{t}_NET"] for t in TERMS) - ds[branch]).max())
        err[f"{x} sw+lw"] = max(float(abs(ds[f"{x}_{t}_SW"] + ds[f"{x}_{t}_LW"] - ds[f"{x}_{t}_NET"]).max())
                                for t in TERMS)
    print(tag, " ".join(f"{k} {v:.1e}" for k, v in err.items()), flush=True)
    if max(err.values()) > 1e-3:
        raise ValueError(f"{tag}: terms do not close {err}")


def compute():
    TAB.mkdir(parents=True, exist_ok=True); CACHE.mkdir(parents=True, exist_ok=True)
    means, q98 = [], []
    for tag in t3.CASES:
        ds = load(tag); check(ds, tag); add_aprp(ds, tag)
        north = ds.mean("year").where(ds["lat"] >= 45)
        for k in ds.data_vars:
            m, h = fm.regional_mean_interval(ds[k], lat_min=45)
            v = np.abs(north[k].values); v = v[np.isfinite(v)]
            means.append(dict(case=tag, panel=k, mean=m, ci95=h)); q98.append(dict(case=tag, panel=k, q98=np.quantile(v, .98)))
    pd.DataFrame(means).to_csv(TAB / f"forcing_tree_5rows_means_45N_{Y0}_{Y1}.csv", index=False)
    q = pd.DataFrame(q98); q.to_csv(TAB / f"forcing_tree_5rows_map_ranges_45N_{Y0}_{Y1}.csv", index=False)
    pd.set_option("display.width", 250)
    print(q.pivot(index="panel", columns="case", values="q98").round(3).to_string())


# vmax candidates: vmax/4 is a round tick step on the shared bars
NICE = (0.04, 0.08, 0.2, 0.4, 0.8, 1, 2, 4, 8, 12, 16, 20, 40, 60, 80)


def nice(q):
    return next(v for v in NICE if v >= 0.95 * q)


def draw_one(tag):
    import matplotlib.colors as mcolors
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mpl_ticker
    case = t3.CASES[tag]
    ds = load(tag)
    row5 = add_aprp(ds, tag)
    q = pd.read_csv(TAB / f"forcing_tree_5rows_map_ranges_45N_{Y0}_{Y1}.csv").query("case == @tag").set_index("panel")["q98"]
    if row5:   # q98 of the row-5 maps here, so draw does not depend on compute having seen the APRP cache
        north = ds.mean("year").where(ds["lat"] >= 45)
        for x in "nb":
            for m in MASK:
                v = np.abs(north[f"{x}_cloud_SW_{m}"].values); q[f"{x}_cloud_SW_{m}"] = np.quantile(v[np.isfinite(v)], .98)
    terms = list(TERMS)
    scale = {"top": nice(q[["total", "nonbvoc"]].max()), "bvoc": nice(q["bvoc"])}
    for x in "nb":
        # rows 3-5 of a branch share one scale, so SW + LW = NET and the APRP split can be read by eye
        keys = [f"{x}_{t}_{b}" for t in terms for b in BANDS] + ([f"{x}_cloud_SW_{m}" for m in MASK] if row5 else [])
        scale[f"{x}3"] = scale[f"{x}4"] = scale[f"{x}5"] = nice(q[keys].max())

    pair = lambda p: f"{p[0]} − {p[1]}"
    branch_name = {"n": "NON-BVOC", "b": "BVOC"}
    # key -> (row, x-slot centre, field, title, subtitle, scale key); row 4 slots 0..5 (non-BVOC), 7..12 (BVOC);
    # slot 6 = gutter for the shared vertical colourbar of rows 3-5 (user 2026-11-26)
    spec = {"total": (0, 6.0, "total", "TOTAL (NET)", pair(case["T"]), "top"),
            "nonbvoc": (1, 2.5, "nonbvoc", "NON-BVOC (NET)", pair(case["N"]), "top"),
            "bvoc": (1, 9.5, "bvoc", "BVOC (NET)", pair(case["B"]), "bvoc")}
    first = {"n": 0, "b": 7}   # first row-4 slot of each branch
    for i, x in enumerate("nb"):
        for j, t in enumerate(terms):
            slot = first[x] + 2 * j
            spec[f"{x}_{t}"] = (2, slot + 0.5, f"{x}_{t}_NET", f"{branch_name[x]} {TERMS[t]} (NET)", None, f"{x}3")
            for k, b in enumerate(("SW", "LW")):
                spec[f"{x}_{t}_{b}"] = (3, slot + k, f"{x}_{t}_{b}", f"{branch_name[x]} {TERMS[t]} {b}", None, f"{x}4")
        if row5:   # under CLOUD SW (first slot of the branch), going right
            for k, (m, name) in enumerate(MASK.items()):
                spec[f"{x}_cloud_SW_{m}"] = (4, first[x] + k, f"{x}_cloud_SW_{m}", f"{'=+'[k > 0]} {name}", None, f"{x}5")

    nrows = 5 if row5 else 4
    fig, grid = fm.map_grid(nrows, 13, under=fm.UNDER_CBAR + 0.4, titles_every_row=True, top_extra=0.12,
                            map_size=2.0, col_gap=0.55)
    # rows 3-5 have no colourbar of their own: pull them up (bbox_inches="tight" crops the freed bottom)
    H = fig.get_figheight()
    under_text = fm.CBAR_OFFSET + 0.05    # mean + two region lines under a map
    save = (fm.UNDER_CBAR + 0.4) - (under_text + 0.55)   # 0.55 in: tree link + section label above the titles
    # row 2 beside TOTAL (user 2026-11-26): its map tops 0.1 in above the bottom of the TOTAL map
    lift = grid[0, 0].get_position().y0 + 0.1 / H - grid[1, 0].get_position().y1
    for r in range(1, nrows):
        for ax in grid[r]:
            b = ax.get_position()
            ax.set_position([b.x0, b.y0 + lift + max(r - 2, 0) * save / H, b.width, b.height])
    pitch = grid[0, 1].get_position().x0 - grid[0, 0].get_position().x0
    x0 = grid[0, 0].get_position().x0
    axes, used = {}, set()
    for key, (r, s, *_r) in spec.items():
        ax = grid[r, int(s)]
        used.add(id(ax))
        b = ax.get_position()
        ax.set_position([x0 + s * pitch, b.y0, b.width, b.height])
        axes[key] = ax
    for ax in grid.ravel():
        if id(ax) not in used:
            ax.remove()

    for key, (r, s, field, title, runs, sk) in spec.items():
        panel = fm.MapPanel(key=key, title=title, variable_class="RADIATIVE", variable=field, case1_role="", case2_role="")
        fm._plot_panel(axes[key], panel, {}, Y0, Y1, 45, 45, True, 0.10, vmax=scale[sk], d=ds[field],
                       cmap="RdBu_r", add_cbar=False)
        if runs:
            axes[key].set_title(title, fontsize=9.5, fontweight="semibold", pad=22)
            axes[key].text(0.5, 1.035, runs, transform=axes[key].transAxes, ha="center", va="bottom", fontsize=8)
        elif r in (2, 3, 4):   # long titles: smaller font
            axes[key].set_title(title, fontsize=8.5, fontweight="semibold")

    def link(parent, children, label=None):
        p = axes[parent].get_position()
        top = 0.62 if spec[children[0]][4] else 0.42
        below = (fm.UNDER_CBAR - 0.05) if spec[parent][0] < 2 else under_text   # rows 1-2 carry a colourbar
        y0, y2 = p.y0 - below / H, axes[children[0]].get_position().y1 + top / H
        y1 = (y0 + y2) / 2
        xp = (p.x0 + p.x1) / 2
        xs = [(axes[c].get_position().x0 + axes[c].get_position().x1) / 2 for c in children]
        kw = dict(transform=fig.transFigure, color="0.35", lw=0.9)
        fig.add_artist(plt.Line2D([xp, xp], [y0, y1], **kw))
        fig.add_artist(plt.Line2D([min(xs + [xp]), max(xs + [xp])], [y1, y1], **kw))
        for xc in xs:
            fig.add_artist(plt.Line2D([xc, xc], [y1, y2], **kw))
        if label:   # section label above the horizontal line, between the first two children
            fig.text((xs[0] + xs[1]) / 2, y1 + 0.06 / H, label, ha="center", va="bottom", fontsize=12)
        return y1
    # total -> branches: horizontal line from the sides of the TOTAL map, then down to the row-2 titles
    p = axes["total"].get_position()
    y_split = axes["nonbvoc"].get_position().y1 + 0.95 / H
    kw = dict(transform=fig.transFigure, color="0.35", lw=0.9)
    for c, xe in (("nonbvoc", p.x0 - 0.12 / fig.get_figwidth()), ("bvoc", p.x1 + 0.12 / fig.get_figwidth())):
        q = axes[c].get_position(); xc = (q.x0 + q.x1) / 2
        fig.add_artist(plt.Line2D([xe, xc], [y_split, y_split], **kw))
        fig.add_artist(plt.Line2D([xc, xc], [y_split, q.y1 + 0.62 / H], **kw))
    for x, branch in (("n", "nonbvoc"), ("b", "bvoc")):
        link(branch, [f"{x}_{t}" for t in terms], "GHAN'S DECOMPOSITION")
        for t in terms:
            link(f"{x}_{t}", [f"{x}_{t}_SW", f"{x}_{t}_LW"])
        if row5:
            link(f"{x}_cloud_SW", [f"{x}_cloud_SW_{m}" for m in MASK], "APRP DECOMPOSITION")
            q = axes[f"{x}_cloud_SW_matm"].get_position()   # 'other' note right of the APRP triplet
            fig.text(q.x1 + 1.0 / fig.get_figwidth(), q.y1 - 0.25 / H,
                     "'other' = APRP residual\n+ APRP−Ghan gap", ha="center", va="top", fontsize=8.5, color="0.45", style="italic",
                     multialignment="center", linespacing=1.4)

    m, h = fm.regional_mean_interval(ds["delta"], lat_min=45)
    b = axes["total"].get_position()   # closure note under the TOTAL colourbar (user 2026-11-26)
    fig.text((b.x0 + b.x1) / 2, b.y0 - (fm.UNDER_CBAR + 0.15) / H,
             "Closure:\ntotal = non-BVOC + BVOC + δ\n"
             f"δ = {fm._format_interval(m, h)} W m$^{{-2}}$\n"
             f"δ = art({case['T'][0]}) − art({case['T'][1]})\n"
             "art = interactive − own\nemissions prescribed",
             ha="center", va="top", multialignment="center", fontsize=10, linespacing=1.45)

    def bar(keys, vmax, label):
        sm = plt.cm.ScalarMappable(norm=mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax), cmap="RdBu_r")
        cb = fm._cbar_below(fig, [axes[k] for k in keys], sm, f"{label} [W m$^{{-2}}$]", fm.CBAR_LABELSIZE_SHARED,
                            shrink=0.9 if len(keys) == 1 else 0.85)
        n = 2 if len(keys) == 1 else 4
        cb.set_ticks(list(np.linspace(-vmax, vmax, 2 * n + 1)))
    bar(["total"], scale["top"], "total")
    bar(["nonbvoc"], scale["top"], "non-BVOC")
    bar(["bvoc"], scale["bvoc"], "BVOC")
    # rows 3-5: one vertical colourbar in the gutter between the branches; left ticks = non-BVOC, right = BVOC
    vn, vb = scale["n3"], scale["b3"]
    top_ax, bot_ax = axes["n_cloud"].get_position(), axes[f"n_cloud_SW_{list(MASK)[-1]}" if row5 else "n_cloud_SW"].get_position()
    W, wbar = fig.get_figwidth(), 0.26
    xc = (axes["n_rest_LW"].get_position().x1 + axes["b_cloud_SW"].get_position().x0) / 2
    y_lo, y_hi = bot_ax.y0 + 0.25 / H, top_ax.y1 - 0.45 / H   # room for the extension triangles + unit label
    cax = fig.add_axes([xc - wbar / 2 / W, y_lo, wbar / W, y_hi - y_lo])
    sm = plt.cm.ScalarMappable(norm=mcolors.TwoSlopeNorm(vmin=-vn, vcenter=0, vmax=vn), cmap="RdBu_r")
    cb = fig.colorbar(sm, cax=cax, orientation="vertical", extend="both", extendfrac=0.03)
    cb.set_ticks(list(np.linspace(-vn, vn, 9)))
    cax.yaxis.set_ticks_position("left")
    sec = cax.secondary_yaxis("right", functions=(lambda y: y * vb / vn, lambda y: y * vn / vb))
    sec.set_ticks(list(np.linspace(-vb, vb, 9)))
    for a in (cax, sec):
        a.tick_params(labelsize=fm.CBAR_TICKSIZE + 1, pad=3)
        a.yaxis.set_major_formatter(mpl_ticker.FuncFormatter(lambda v, _: f"{v:g}".replace("-", "−")))
    fig.text(xc, y_hi + (0.03 * (y_hi - y_lo) * H + 0.04) / H, "W m$^{-2}$", ha="center", va="bottom", fontsize=11)

    fm.add_suptitle(fig, f"{case['title']}: radiative forcing decomposition, Ghan terms, SW/LW"
                    + (" and cloud masking" if row5 else ""), 45,
                    y=fm._suptitle_y(fig), years=Y1 - Y0 + 1)
    fig._region_footnote = True   # "*broadleaf exp.: ..." footnote, shared style (user 2026-11-26)
    fm.add_region_footnote(fig)
    FIG.mkdir(parents=True, exist_ok=True); path = FIG / f"{tag}_forcing_tree_5rows_{Y0}_{Y1}_designA.png"
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    # pixel boxes of every map (+ its title) and of the shared colourbar in the saved PNG, for
    # results/pptx/build_forcing_tree_processes_pptx.py (user 2026-11-26: process chips next to each map)
    import json
    rend = fig.canvas.get_renderer()
    tb, pad, dpi, W_in = fig.get_tightbbox(rend), 0.1, 200, fig.get_figwidth()
    x0_in, y1_in = tb.x0 - pad, tb.y1 + pad
    def px(bb):   # display bbox (fig dpi) -> [left, top, right, bottom] in PNG pixels
        f = fig.dpi
        return [round((bb.x0 / f - x0_in) * dpi), round((y1_in - bb.y1 / f) * dpi),
                round((bb.x1 / f - x0_in) * dpi), round((y1_in - bb.y0 / f) * dpi)]
    boxes = {"png_size": [round((tb.width + 2 * pad) * dpi), round((tb.height + 2 * pad) * dpi)],
             "maps": {k: {"map": px(a.get_window_extent(rend)), "title": px(a.title.get_window_extent(rend)),
                          "row": spec[k][0]} for k, a in axes.items()},
             "cbar": px(cax.get_tightbbox(rend))}
    path.with_name(path.stem + "_boxes.json").write_text(json.dumps(boxes, indent=1))
    plt.close(fig)
    print("Saved", path, scale, flush=True)


def draw(only=None):
    import matplotlib
    matplotlib.use("Agg")
    from boreal_forest_expansion.plotting.style import set_default_style
    set_default_style()
    for tag in t3.CASES:
        if only in (None, tag):
            draw_one(tag)


if __name__ == "__main__":
    if sys.argv[1] == "compute":
        compute()
    else:
        draw(sys.argv[2] if len(sys.argv) > 2 else None)
