"""Sandbox: cloud-masking-aprp figures with a formula line under each panel title (user 2026-11-25).

Copies row_figure / cloud_figure of analysis/cloud-masking-aprp.ipynb (cell 9, 11) and adds FORMULAS
under the panel titles + a definitions footnote. Reads the 2001–2025 caches only; one case.
Output: sandbox/test_aprp_formula_titles_outputs/.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.colors as mcolors  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import xarray as xr  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
from boreal_forest_expansion.plotting import forcing_maps as fm  # noqa: E402
from boreal_forest_expansion.plotting.style import set_default_style  # noqa: E402

set_default_style()
OUT = REPO / "sandbox" / "test_aprp_formula_titles_outputs"
OUT.mkdir(exist_ok=True)
CACHE = REPO / "analysis" / "cloud-masking-aprp_outputs" / "cache"
Y0, Y1, LAT_MIN = 2001, 2025, 45
TAG = sys.argv[1] if len(sys.argv) > 1 else "LCCPD_fBVOCctrlPD"
CASES = {
    "LCCPD_fBVOCctrlPD": dict(title="[LCC − CTRL] _PD", T=("LCC_PD", "CTRL_PD"),
                              N=("LCC_PD_fBVOCctrlPD", "CTRL_PD_fBVOCctrlPD"), B=("LCC_PD_fBVOClccPD", "LCC_PD_fBVOCctrlPD")),
    "LCCFUT_fBVOCctrlPD": dict(title="LCC_FUT − CTRL_PD", T=("LCC_FUT", "CTRL_PD"),
                               N=("LCC_FUT_fBVOCctrlPD", "CTRL_PD_fBVOCctrlPD"), B=("LCC_FUT_fBVOClccFUT", "LCC_FUT_fBVOCctrlPD")),
}
BRANCH = {"T": "TOTAL", "N": "NON-BVOC", "B": "BVOC"}
case = CASES[TAG]
APRP = {case[b]: xr.load_dataset(CACHE / f"{case[b][0]}__{case[b][1]}_clean_{Y0}_{Y1}.nc") for b in "TNB"}
CLOUDS = {case[b]: xr.load_dataset(CACHE / f"{case[b][0]}__{case[b][1]}_cloudvars_{Y0}_{Y1}.nc") for b in "TNB"}

# --- formula under each panel title ------------------------------------------------------------
# Each panel: how it is computed from the model output (clean = aerosol-free _DRF radiation calls).
# Clean fluxes: all-sky SW_up_TOA = FSUTADRF, SW_dn_sfc = FSDS_DRF, SW_up_sfc = FSUS_DRF; clear-sky
# SW_up_TOA = SOLIN - FSNTCDRF - (FSNTOAC - FSNTC), SW_dn_sfc = FSDSCDRF, SW_up_sfc = FSDSCDRF a_clr.
FORMULAS = {
    "ghan_cloud": "Δ(FSNT_DRF − FSNTCDRF)",
    "cloud": "−SOLIN·ΔA, only CLDTOT, γ$_{cld}$, μ$_{cld}$ changed\n= cloud amount + scattering + absorption",
    "mask_sfc": "−SOLIN·[ΔA(a$_{clr}$, a$_{oc}$) − ΔA$_{clr}$(a$_{clr}$)]\nsurface albedo all-sky − clear-sky",
    "mask_atm_other": "Δ(SOLIN − FSUTADRF − FSNTCDRF − FSNTOAC + FSNTC)\n− real cloud change − surface-albedo masking",
    "sfc_all": "−SOLIN·ΔA, only a$_{clr}$, a$_{oc}$ changed\na$_{clr}$ = (FSDSC − FSNSC) / FSDSC\na$_{oc}$ = FSUS_DRF$_{oc}$ / FSDS_DRF$_{oc}$",
    "sfc_clr": "−SOLIN·ΔA$_{clr}$, only a$_{clr}$ changed\na$_{clr}$ = (FSDSC − FSNSC) / FSDSC",
    "cld_amt": "−SOLIN·ΔA, only CLDTOT changed",
    "cld_scat": "−SOLIN·ΔA, only γ$_{cld}$ changed\nγ$_{cld}$ = 1 − (1 − γ$_{oc}$) / (1 − γ$_{clr}$)\nγ = (μ − Q) / (μ − a·Q),  Q = SW↓$_{sfc}$ / SOLIN",
    "cld_abs": "−SOLIN·ΔA, only μ$_{cld}$ = μ$_{oc}$ / μ$_{clr}$ changed\nμ$_{oc}$ = (FSUTADRF + FSDS_DRF − FSUS_DRF)$_{oc}$ / SOLIN",
    "atm_all": "−SOLIN·ΔA, only μ$_{clr}$, γ$_{clr}$ changed\nμ$_{clr}$ = 1 − (FSNTCDRF + FSNTOAC − FSNTC\n − FSDSCDRF·(1 − a$_{clr}$)) / SOLIN",
    "CLDTOT": "ΔCLDTOT × 100", "CLDLOW": "ΔCLDLOW × 100", "LWP": "ΔTGCLDLWP × 1000", "IWP": "ΔTGCLDIWP × 1000",
    "CDNUMC": "ΔCDNUMC / 10$^{10}$", "REL": "Δ(ACTREL / FCTL), yearly means",
}
APRP_NOTE = ("ΔA = change of the one-layer planetary albedo A = μγ + μa(1 − γ)²/(1 − aγ) when only the listed quantity differs between the two runs "
             "(mean of swapping it in either run), SOLIN = mean of the two runs;  all-sky A = (1 − CLDTOT)·A$_{clr}$ + CLDTOT·A$_{oc}$.\n"
             "For each column:  μ = (SW↑$_{TOA}$ + SW↓$_{sfc}$ − SW↑$_{sfc}$) / SOLIN,  γ = (μ − Q)/(μ − a·Q),  Q = SW↓$_{sfc}$ / SOLIN,  a = SW↑$_{sfc}$ / SW↓$_{sfc}$;  "
             "overcast X$_{oc}$ = (X − (1 − CLDTOT)·X$_{clr}$) / CLDTOT;  γ$_{cld}$ = 1 − (1 − γ$_{oc}$)/(1 − γ$_{clr}$),  μ$_{cld}$ = μ$_{oc}$/μ$_{clr}$.\n"
             "Clean fluxes:  all-sky SW↑$_{TOA}$ = FSUTADRF,  SW↓$_{sfc}$ = FSDS_DRF,  SW↑$_{sfc}$ = FSUS_DRF;  "
             "clear-sky SW↑$_{TOA}$ = SOLIN − FSNTCDRF − (FSNTOAC − FSNTC),  SW↓$_{sfc}$ = FSDSCDRF,  SW↑$_{sfc}$ = FSDSCDRF·(FSDSC − FSNSC)/FSDSC.  "
             "Monthly, then yearly means.")
FORMULA_SPACE = 0.48   # in, extra room above each map for up to three formula lines
FORMULA_FONTSIZE = 8.0


def add_formula(ax, key):
    """Formula under the panel title: title moved up, formula between title and map."""
    text = FORMULAS.get(key)
    if not text:
        return
    t = ax.title
    ax.set_title(t.get_text(), fontsize=t.get_fontsize(), fontweight=t.get_fontweight(),
                 pad=fm.TITLE_PAD + FORMULA_SPACE * 72 - 2)
    ax.annotate(text, xy=(0.5, 1.0), xycoords="axes fraction", xytext=(0, fm.TITLE_PAD - 5),
                textcoords="offset points", ha="center", va="bottom", fontsize=FORMULA_FONTSIZE,
                color="0.25", linespacing=1.15)


def add_note(fig, text):
    box = fig.get_tightbbox(fig.canvas.get_renderer())
    W, H = fig.get_size_inches()
    fig.text(box.x0 / W, (box.y0 - 0.1) / H, text, ha="left", va="top", fontsize=fm.REGION_FOOTNOTE_FONTSIZE,
             color="0.25")


NICE = np.array([1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10])


def nice(v):
    k = 10.0 ** np.floor(np.log10(v))
    return float(NICE[np.searchsorted(NICE, v / k * 0.999)] * k)


def q98(ds_list, keys):
    vals = np.concatenate([np.abs(ds[k].mean("year").where(ds["lat"] >= LAT_MIN).values).ravel() for ds, k in zip(ds_list, keys)])
    return float(np.nanquantile(vals, 0.98))


def row_labels(fig, grid, r, b):
    W = fig.get_figwidth()
    bx = grid[r, 0].get_position()
    fig.text(bx.x0 - 0.55 / W, (bx.y0 + bx.y1) / 2, BRANCH[b], rotation=90, ha="center", va="center",
             fontsize=11, fontweight="semibold")
    fig.text(bx.x0 - 0.3 / W, (bx.y0 + bx.y1) / 2, f"{case[b][0]}\n− {case[b][1]}", rotation=90,
             ha="center", va="center", fontsize=7.5)


def finish(fig, title, fname):
    fm.add_suptitle(fig, f"{case['title']}: {title}", LAT_MIN, y=fm._suptitle_y(fig), years=Y1 - Y0 + 1)
    fm.add_region_footnote(fig)
    add_note(fig, APRP_NOTE)
    path = OUT / f"{TAG}_{fname}_{Y0}_{Y1}.png"
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    print("Saved", path.relative_to(REPO))
    plt.close(fig)


def row_figure(columns, fname, title):
    ncol = len(columns)
    title_space = fm.TITLE_SPACE
    fm.TITLE_SPACE = title_space + FORMULA_SPACE
    try:
        fig, grid = fm.map_grid(3, ncol, under=0.75 + fm.REGION_SPACE, titles_every_row=True, left=1.15, right=1.6)
    finally:
        fm.TITLE_SPACE = title_space
    for r, b in enumerate("TNB"):
        ds = APRP[case[b]]
        vmax = nice(q98([ds] * ncol, [k for k, _ in columns]))
        for j, (k, t) in enumerate(columns):
            panel = fm.MapPanel(key=k, title=t, variable_class="RADIATIVE", variable=k, case1_role="", case2_role="")
            fm._plot_panel(grid[r, j], panel, {}, Y0, Y1, LAT_MIN, LAT_MIN, True, 0.10, vmax=vmax, d=ds[k],
                           cmap="RdBu_r", add_cbar=False)
            add_formula(grid[r, j], k)
        sm = plt.cm.ScalarMappable(norm=mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax), cmap="RdBu_r")
        fm._cbar_right(fig, grid[r], sm, "W m$^{-2}$")
        row_labels(fig, grid, r, b)
    finish(fig, title, fname)


CLOUD_VARS = {"CLDTOT": ("CLOUD FRACTION (TOTAL)", "%-pts"), "CLDLOW": ("CLOUD FRACTION (LOW)", "%-pts"),
              "LWP": ("LIQUID WATER PATH", "g m$^{-2}$"), "IWP": ("ICE WATER PATH", "g m$^{-2}$"),
              "CDNUMC": ("DROPLET NUMBER (COLUMN)", "10$^{10}$ m$^{-2}$"), "REL": ("CLOUD-TOP DROPLET RADIUS", "µm")}


def cloud_figure():
    cols = [("ghan_cloud", "GHAN CLOUD SW", "W m$^{-2}$"), ("cloud", "APRP REAL CLOUD CHANGE", "W m$^{-2}$")] + \
           [(k, t, u) for k, (t, u) in CLOUD_VARS.items()]
    title_space = fm.TITLE_SPACE
    fm.TITLE_SPACE = title_space + FORMULA_SPACE
    try:
        fig, grid = fm.map_grid(3, len(cols), titles_every_row=True, left=1.15)
    finally:
        fm.TITLE_SPACE = title_space
    for r, b in enumerate("TNB"):
        a, c = APRP[case[b]], CLOUDS[case[b]]
        for j, (k, t, u) in enumerate(cols):
            d = a[k] if k in a else c[k]
            vmax = nice(max(fm.symmetric_vmax(d.mean("year").where(d["lat"] >= LAT_MIN)), 1e-6))
            panel = fm.MapPanel(key=k, title=t, variable_class="CLOUDPROP", variable=k, case1_role="", case2_role="",
                                units=u, long_label=t.lower())
            fm._plot_panel(grid[r, j], panel, {}, Y0, Y1, LAT_MIN, LAT_MIN, True, 0.10, vmax=vmax, d=d, cmap="RdBu_r")
            add_formula(grid[r, j], k)
        row_labels(fig, grid, r, b)
    finish(fig, "cloud term and the clouds themselves", "cloud_variables")


MASK_COLS = [("ghan_cloud", "GHAN CLOUD SW"), ("cloud", "= REAL CLOUD CHANGE"),
             ("mask_sfc", "+ SURFACE-ALBEDO MASKING"), ("mask_atm_other", "+ ATMOSPHERE MASKING & OTHER")]
SPLIT_COLS = [("sfc_all", "SURFACE ALBEDO (ALL-SKY)"), ("sfc_clr", "SURFACE ALBEDO (CLEAR-SKY)"),
              ("cld_amt", "CLOUD AMOUNT"), ("cld_scat", "CLOUD SCATTERING"), ("cld_abs", "CLOUD ABSORPTION"),
              ("atm_all", "NON-CLOUD ATMOSPHERE")]
row_figure(MASK_COLS, "cloud_masking_SW", "SW cloud term = real cloud change + masking (clean APRP)")
row_figure(SPLIT_COLS, "aprp_split_SW", "APRP split of the absorbed SW (clean)")
cloud_figure()
