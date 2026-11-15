"""PowerPoint of analysis/land-carbon-water.ipynb (2001–2025) on the CICERO template.

Run: python build_land_carbon_water_pptx.py OUT.pptx [TEMPLATE.pptx]  (needs python-pptx, Pillow, lxml)
Slides: the 4 carbon grids, the 4 ET-split grids (one per contrast category), the seasonal cycle over the
modified cells, and the regional table (modified cells) as two table slides. Every figure of the notebook
must be placed, else it stops with the list. Rows marked "(design B)" in the table = stand-in for
LCC_FUT_fBVOClccFUT; they disappear once the notebook is rerun with the real run (design A).
"""
import csv
import sys
from pathlib import Path

from pptx.enum.dml import MSO_THEME_COLOR as TC
from pptx.util import Inches

sys.path.insert(0, str(Path(__file__).parent))
from cicero_pptx import Deck, M  # noqa: E402

ROOT = Path("/cluster/home/adelez/BOREAL-FOREST-EXPANSION")
FIG = ROOT / "results/figures"
TAB = ROOT / "results/tables/land_carbon_water_regional_2001_2025.csv"
Y = "2001_2025"
CATS = ["interactive", "fBVOC", "non-BVOC", "artefacts"]
CAT_TEXT = {
    "interactive": "Fully interactive runs: total effects of land-cover change (LCC − CTRL) and of the "
                   "background climate (FUT − PD).",
    "fBVOC": "Only the prescribed BVOC emissions differ (same land, same climate): BVOC-mediated effects. "
             "The prescription artefact cancels.",
    "non-BVOC": "Same prescribed emissions in both runs: the biogeophysical (non-BVOC) effect of the land "
                "or of the climate.",
    "artefacts": "Interactive − prescribed run on the same land: the uncorrected BVOC effect on LCC land, "
                 "the prescription artefact on CTRL land.",
}
CARBON = ("Columns: GPP, NPP = GPP − AR, plant respiration (AR), soil respiration (HR), net CO₂ flux to the "
          "atmosphere (NEE, + = source), vegetation carbon, ecosystem carbon. Fluxes in gC m⁻² yr⁻¹, "
          "stocks in kgC m⁻².")
ET = ("Columns: total ET = transpiration (QVEGT) + canopy evaporation (QVEGE) + ground evaporation (QSOIL), "
      "and LAI. Water in mm day⁻¹.")
READ = ("Number under each map: land mean 45–90°N ± 95 % CI over the 25 yearly differences. Hatching = NOT "
        "significant (paired yearly t-test, FDR α = 0.10). 'scale ÷N' = panel on a narrower colour scale than "
        "its column.")
CAVEAT = ("CO₂ is prescribed in the atmosphere (NF compsets): these land CO₂ fluxes do not feed back on "
          "atmospheric CO₂ or radiation in the runs.")


def side_text(d, s, x, y, w, h, blocks):
    lines = []
    for head, txt in blocks:
        if head:
            lines.append((head, {"bold": True, "color": TC.TEXT_2}))
        lines.append(txt if not isinstance(txt, tuple) else txt)
    d.text(s, x, y, w, h, lines, 11, TC.TEXT_1, space_after=4, name="Notes")


def grid_slide(d, sec, kick, title, path, blocks):
    s = d.content_slide(sec, kick, title)
    top, H = 1.6, 5.25
    from PIL import Image
    w, h = Image.open(path).size
    fw = min(d.W - 2 * M - 3.4, H * w / h)
    d.picture(s, path, M, top, fw, H)
    x = M + fw + 0.3
    side_text(d, s, x, top, d.W - M - x, H, blocks)
    rel = str(path.relative_to(ROOT))
    d.finish(s, rel, "\n".join([title, *(f"{a}: {b}" if a else str(b) for a, b in blocks), f"File: {rel}"]))


def fmt(v, ci):
    v, ci = float(v), float(ci)
    nd = 0 if abs(v) >= 100 else 1 if abs(v) >= 10 else 2
    sig = abs(v) > ci
    return f"{v:+.{nd}f} ± {ci:.{nd}f}", sig


def table_slide(d, sec, kick, title, rows_in, terms, note):
    s = d.content_slide(sec, kick, title)
    head = ["Contrast"] + [f"{t}\n[{u}]" for t, u in terms]
    n = len(rows_in) + 1
    W = d.W - 2 * M
    tbl = s.shapes.add_table(n, len(head), Inches(M), Inches(1.55), Inches(W), Inches(0.235 * n)).table
    for r in tbl.rows:
        r.height = Inches(0.235)
    tbl.columns[0].width = Inches(3.6)
    for c in range(1, len(head)):
        tbl.columns[c].width = Inches((W - 3.6) / (len(head) - 1))
    for i in range(n):
        for c in range(len(head)):
            cell = tbl.cell(i, c)
            cell.margin_top = cell.margin_bottom = Inches(0.02)
            cell.fill.solid()
            cell.fill.fore_color.theme_color = (TC.TEXT_2 if i == 0 else
                                                TC.BACKGROUND_2 if i % 2 else TC.BACKGROUND_1)
            p = cell.text_frame.paragraphs[0]
            if i == 0:
                run = p.add_run(); run.text = head[c]
                d.style(run, 9, TC.BACKGROUND_1, True)
                continue
            cat, con, vals = rows_in[i - 1]
            run = p.add_run()
            if c == 0:
                run.text = con
                d.style(run, 9, TC.TEXT_1, False)
            else:
                txt, sig = vals.get(terms[c - 1][0], ("–", False))
                run.text = txt
                d.style(run, 9, TC.TEXT_1, sig)
    d.text(s, M, 6.45, W, 0.4, (note, {"italic": True, "color": "595959"}), 10)
    d.finish(s, str(TAB.relative_to(ROOT)), title + "\n" + note)


def regional_rows(region):
    rows = {}
    with open(TAB) as f:
        for r in csv.DictReader(f):
            if r["region"] != region:
                continue
            key = (r["category"], r["contrast"])
            rows.setdefault(key, {})[r["term"]] = fmt(r["diff"], r["ci95"])
    order = {c: i for i, c in enumerate(CATS)}
    return [(c, con, v) for (c, con), v in sorted(rows.items(), key=lambda kv: order[kv[0][0]])]


if __name__ == "__main__":
    OUT = Path(sys.argv[1])
    d = Deck(*sys.argv[2:3])
    used = set()
    d.title_slide("Land carbon and water fluxes",
                  "Forest expansion and climate: GPP, respiration, net CO₂ flux, carbon stocks, ET split",
                  ["BOREAL-FOREST-EXPANSION", "analysis/land-carbon-water.ipynb, nudged runs 2001–2025",
                   "11 November 2026"])
    story = [dict(num=1, title="Carbon fluxes and stocks", subs=[(c, None) for c in CATS]),
             dict(num=2, title="Evapotranspiration split", subs=[(c, None) for c in CATS]),
             dict(num=3, title="Seasonal cycle and regional totals",
                  subs=[("seasonal cycle, modified cells", None), ("regional totals", None)])]
    d.agenda(story)
    for k, (stem, label, cols) in enumerate([("carbon", "Carbon fluxes and stocks", CARBON),
                                             ("et_split", "Evapotranspiration split", ET)], 1):
        for cat in CATS:
            p = FIG / cat / f"contrast_grid_{stem}_{cat}_{Y}.png"
            assert p.exists(), p
            used.add(p)
            blocks = [(f"Category: {cat}", CAT_TEXT[cat]), ("Columns", cols.split(": ", 1)[1]),
                      ("How to read", READ)]
            if stem == "carbon":
                blocks.append(("Caveat", CAVEAT))
            grid_slide(d, f"{k} {label}", f"{k}  {label} · {cat}", f"{label}: {cat} contrasts", p, blocks)
    p = FIG / "interactive" / f"seasonal_cycle_carbon_et_modified_{Y}.png"
    assert p.exists(), p
    used.add(p)
    grid_slide(d, "3 Seasonal cycle and regional totals", "3  Seasonal cycle · modified cells",
               "When in the year does the forest expansion change uptake, CO₂ flux and ET?", p,
               [("Top row", "monthly climatology 2001–2025 of the four interactive runs over the LCC-modified "
                            "cells (PD navy, FUT red; CTRL dashed, LCC solid)."),
                ("Bottom row", "LCC − CTRL per period."),
                ("Weights", "cell area × land fraction.")])
    rows = regional_rows("modified cells")
    note = ("LCC-modified cells; carbon = regional totals (TgC yr⁻¹, stocks PgC), water = area-mean mm yr⁻¹. "
            "Mean of the 25 yearly paired differences ± 95 % t-interval; bold = interval excludes 0. "
            "(design B) = stand-in for LCC_FUT_fBVOClccFUT.")
    table_slide(d, "3 Seasonal cycle and regional totals", "3  Regional totals · carbon",
                "Regional totals over the modified cells: carbon", rows,
                [("GPP", "TgC/yr"), ("NPP", "TgC/yr"), ("NEE", "TgC/yr"), ("NBP", "TgC/yr"),
                 ("TOTVEGC", "PgC"), ("TOTECOSYSC", "PgC")], note)
    table_slide(d, "3 Seasonal cycle and regional totals", "3  Regional totals · water",
                "Regional totals over the modified cells: evapotranspiration", rows,
                [("ET", "mm/yr"), ("QVEGT", "mm/yr"), ("QVEGE", "mm/yr"), ("QSOIL", "mm/yr")], note)
    nb_figs = {FIG / c / f"contrast_grid_{s}_{c}_{Y}.png" for c in CATS for s in ("carbon", "et_split")}
    nb_figs.add(FIG / "interactive" / f"seasonal_cycle_carbon_et_modified_{Y}.png")
    missing = [p for p in nb_figs if p not in used]
    assert not missing, "figures not placed:\n" + "\n".join(map(str, missing))
    d.save(OUT, "Land carbon and water 2001–2025")
    print("slides:", len(d.prs.slides), "figures:", len(used), "->", OUT)
