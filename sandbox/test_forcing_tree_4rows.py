"""Four-row forcing tree, alternative layout (sandbox, user 2026-11-24). Nothing is written to results/.

Row 1  total T (NET)
Row 2  non-BVOC N · BVOC B (NET), pairs as in test_forcing_tree.py
Row 3  Ghan split of both branches (NET): cloud, direct, clean-clear-sky
Row 4  each row-3 term split into SW and LW
No physical labels (albedo, chemistry, ...): plain Ghan terms only.

Stage 1: python test_forcing_tree_4rows.py compute   yearly Ghan fields of N (cache), means + q98 tables
Stage 2: python test_forcing_tree_4rows.py draw      figures in test_forcing_tree_4rows_outputs/
Needs the test_forcing_tree.py cache (T, N, B and the Ghan terms of B, per band).
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_forcing_tree as t3  # noqa: E402  (CASES, years, cache of the 3-row tree)
from test_forcing_tree import fm  # noqa: E402

OUT = t3.REPO / "sandbox" / "test_forcing_tree_4rows_outputs"
CACHE = Path("/cluster/work/users/adelez/boreal-caches/forcing-tree-4rows")
Y0, Y1 = t3.Y0, t3.Y1
TERMS = {"cloud": "CLOUD", "dir": "DIRECT", "rest": "CLEAN-CLEAR-SKY"}   # Ghan terms
BANDS = ("NET", "SW", "LW")


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
    OUT.mkdir(exist_ok=True); CACHE.mkdir(parents=True, exist_ok=True)
    means, q98 = [], []
    for tag in t3.CASES:
        ds = load(tag); check(ds, tag)
        north = ds.mean("year").where(ds["lat"] >= 45)
        for k in ds.data_vars:
            m, h = fm.regional_mean_interval(ds[k], lat_min=45)
            v = np.abs(north[k].values); v = v[np.isfinite(v)]
            means.append(dict(case=tag, panel=k, mean=m, ci95=h)); q98.append(dict(case=tag, panel=k, q98=np.quantile(v, .98)))
    pd.DataFrame(means).to_csv(OUT / "forcing_tree_4rows_means_45N_2001_2025.csv", index=False)
    q = pd.DataFrame(q98); q.to_csv(OUT / "forcing_tree_4rows_map_ranges_45N_2001_2025.csv", index=False)
    pd.set_option("display.width", 250)
    print(q.pivot(index="panel", columns="case", values="q98").round(3).to_string())


# vmax candidates: vmax/4 is a round tick step on the shared bars
NICE = (0.04, 0.08, 0.2, 0.4, 0.8, 1, 2, 4, 8, 12, 16, 20, 40, 60, 80)


def nice(q):
    return next(v for v in NICE if v >= 0.95 * q)


def draw_one(tag):
    import matplotlib.colors as mcolors
    import matplotlib.pyplot as plt
    case = t3.CASES[tag]
    ds = load(tag)
    q = pd.read_csv(OUT / "forcing_tree_4rows_map_ranges_45N_2001_2025.csv").query("case == @tag").set_index("panel")["q98"]
    terms = list(TERMS)
    scale = {"top": nice(q[["total", "nonbvoc"]].max()), "bvoc": nice(q["bvoc"])}
    for x in "nb":
        # rows 3-4 of a branch share one scale, so SW + LW = NET can be read by eye
        scale[f"{x}3"] = scale[f"{x}4"] = nice(q[[f"{x}_{t}_{b}" for t in terms for b in BANDS]].max())

    pair = lambda p: f"{p[0]} − {p[1]}"
    branch_name = {"n": "NON-BVOC", "b": "BVOC"}
    # key -> (row, x-slot centre, field, title, subtitle, scale key); row 4 slots 0..11
    spec = {"total": (0, 5.5, "total", "TOTAL (NET)", pair(case["T"]), "top"),
            "nonbvoc": (1, 2.5, "nonbvoc", "NON-BVOC (NET)", pair(case["N"]), "top"),
            "bvoc": (1, 8.5, "bvoc", "BVOC (NET)", pair(case["B"]), "bvoc")}
    for i, x in enumerate("nb"):
        for j, t in enumerate(terms):
            slot = 6 * i + 2 * j
            spec[f"{x}_{t}"] = (2, slot + 0.5, f"{x}_{t}_NET", f"{branch_name[x]} {TERMS[t]} (NET)", None, f"{x}3")
            for k, b in enumerate(("SW", "LW")):
                spec[f"{x}_{t}_{b}"] = (3, slot + k, f"{x}_{t}_{b}", f"{branch_name[x]} {TERMS[t]} {b}", None, f"{x}4")

    fig, grid = fm.map_grid(4, 12, under=fm.UNDER_CBAR + 0.4, titles_every_row=True, top_extra=0.12,
                            map_size=2.0, col_gap=0.55)
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
        elif r in (2, 3):   # long titles: smaller font
            axes[key].set_title(title, fontsize=8.5, fontweight="semibold")

    H = fig.get_figheight()
    def link(parent, children):
        p = axes[parent].get_position()
        top = 0.62 if spec[children[0]][4] else 0.42
        y0, y2 = p.y0 - (fm.UNDER_CBAR - 0.05) / H, axes[children[0]].get_position().y1 + top / H
        y1 = (y0 + y2) / 2
        xp = (p.x0 + p.x1) / 2
        xs = [(axes[c].get_position().x0 + axes[c].get_position().x1) / 2 for c in children]
        kw = dict(transform=fig.transFigure, color="0.35", lw=0.9)
        fig.add_artist(plt.Line2D([xp, xp], [y0, y1], **kw))
        fig.add_artist(plt.Line2D([min(xs + [xp]), max(xs + [xp])], [y1, y1], **kw))
        for xc in xs:
            fig.add_artist(plt.Line2D([xc, xc], [y1, y2], **kw))
    link("total", ["nonbvoc", "bvoc"])
    for x, branch in (("n", "nonbvoc"), ("b", "bvoc")):
        link(branch, [f"{x}_{t}" for t in terms])
        for t in terms:
            link(f"{x}_{t}", [f"{x}_{t}_SW", f"{x}_{t}_LW"])

    m, h = fm.regional_mean_interval(ds["delta"], lat_min=45)
    b = axes["total"].get_position()
    fig.text(b.x1 + 0.3 / fig.get_figwidth(), (b.y0 + b.y1) / 2,
             "Closure: total = non-BVOC + BVOC + δ\n"
             f"δ = {fm._format_interval(m, h)} W m$^{{-2}}$\n"
             f"δ = art({case['T'][0]}) − art({case['T'][1]})\n"
             "art = interactive − own emissions\nprescribed (δ not drawn)\n\n"
             "Rows 3–4: Ghan terms; NET = SW + LW",
             ha="left", va="center", fontsize=10, linespacing=1.45)

    def bar(keys, vmax, label):
        sm = plt.cm.ScalarMappable(norm=mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax), cmap="RdBu_r")
        cb = fm._cbar_below(fig, [axes[k] for k in keys], sm, f"{label} [W m$^{{-2}}$]", fm.CBAR_LABELSIZE_SHARED,
                            shrink=0.9 if len(keys) == 1 else 0.85)
        n = 2 if len(keys) == 1 else 4
        cb.set_ticks(list(np.linspace(-vmax, vmax, 2 * n + 1)))
    bar(["total"], scale["top"], "total")
    bar(["nonbvoc"], scale["top"], "non-BVOC")
    bar(["bvoc"], scale["bvoc"], "BVOC")
    for x in "nb":
        bar([f"{x}_{t}" for t in terms], scale[f"{x}3"], f"{branch_name[x].lower()} Ghan terms, NET")
        bar([f"{x}_{t}_{b}" for t in terms for b in ("SW", "LW")], scale[f"{x}4"], f"{branch_name[x].lower()} Ghan terms, SW and LW")

    fm.add_suptitle(fig, f"{case['title']}: radiative forcing decomposition, Ghan terms and SW/LW", 45,
                    y=fm._suptitle_y(fig), years=Y1 - Y0 + 1)
    path = OUT / f"{tag}_forcing_tree_4rows_{Y0}_{Y1}_designA.png"
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
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
