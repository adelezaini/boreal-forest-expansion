"""PowerPoint of analysis/simulation-contrasts.ipynb (2001–2025) on the CICERO template.

Run: python build_contrasts_pptx.py OUT.pptx [TEMPLATE.pptx]  (needs python-pptx, Pillow, lxml)
One slide per figure, with the notebook's row definitions next to (or under) the grid.
Every *_2001_2025.png of the notebook must be placed, else it stops with the list.
"""
import sys
from pathlib import Path

from pptx.enum.dml import MSO_THEME_COLOR as TC
from pptx.util import Inches

sys.path.insert(0, str(Path(__file__).parent))
from cicero_pptx import Deck, M  # noqa: E402

ROOT = Path("/cluster/home/adelez/BOREAL-FOREST-EXPANSION")
FIGDIR = ROOT / "analysis/simulation-contrasts_outputs/figures"
Y = "2001_2025"
DB = "LCC_FUT_fBVOClccFUT is the design-B stand-in (LCC_FUT − CTRL_FUT + CTRL_FUT_fBVOCctrlFUT) until run 24g is processed."

# fig id -> (title, [(row label, text)], note)
FIGS = {
    "1a": ("Combined effect of land-cover change and climate change",
           [("LCC_FUT − CTRL_PD", "future vegetation in the future climate vs present vegetation in the present "
                                  "climate. The climate part dominates most variables: compare with 1b and 1c.")], None),
    "1b": ("Total effect of land-cover change, in PD and in FUT",
           [("Row 1  LCC_PD − CTRL_PD", "total LCC effect, PD climate"),
            ("Row 2  LCC_FUT − CTRL_FUT", "total LCC effect, FUT climate"),
            ("Row 3  row 2 − row 1", "does the total LCC effect change between PD and FUT? "
                                     "(LCC × climate interaction; positive = larger in FUT)")],
           "Both rows contain the BVOC part (Fig. 2) and the non-BVOC part (Fig. 3a)."),
    "1c": ("Background climate change, no land-cover change",
           [("Row 1  CTRL_FUT − CTRL_PD", "climate change with current vegetation"),
            ("Row 2  LCC_FUT − LCC_PD", "climate change with future vegetation"),
            ("Row 3  row 2 − row 1", "does the climate response depend on the vegetation?")],
           "Row 3 is algebraically the same map as row 3 of Fig. 1b."),
    "2": ("BVOC-related effects: only the prescribed emissions differ",
          [("Row 1  fBVOC [lccPD − ctrlPD], PD", "emission change from LCC, PD climate"),
           ("Row 2  fBVOC [lccFUT − ctrlFUT], FUT", "emission change from LCC, FUT climate"),
           ("Row 3  fBVOC [lccFUT − lccPD], FUT", "emission change from climate change, LCC vegetation"),
           ("Row 4  fBVOC [lccFUT − ctrlPD], FUT", "emission change from LCC and climate change together")],
          "Same land and climate in both runs, so the prescription artefact cancels. Rows 2–4: " + DB +
          " With it the artefact no longer cancels exactly (residual art(LCC land) − art(CTRL land))."),
    "2b": ("Supplementary BVOC-related contrasts",
           [("Row 1  fBVOC [ctrlFUT − ctrlPD], FUT", "emission change from climate change, current vegetation"),
            ("Row 2  fBVOC [lccPD − ctrlPD], FUT", "emission change from LCC (PD emissions) in the FUT climate; "
                                                   "not really physical")], None),
    "3a": ("Non-BVOC effects of land-cover change (same prescribed emissions)",
           [("Row 1  [LCC_PD − CTRL_PD]_fBVOCctrlPD", "PD climate"),
            ("Row 2  [LCC_FUT − CTRL_FUT]_fBVOCctrlFUT", "FUT climate"),
            ("Row 3  row 2 − row 1", "does the fixed-BVOC LCC response change between PD and FUT?")],
           "Same prescribed emissions in both runs: the emission columns are ≈ 0 and what remains is the "
           "biogeophysical effect."),
    "3b": ("Non-BVOC effects of climate change (same prescribed emissions)",
           [("Row 1  [LCC_FUT − LCC_PD]_fBVOCctrlPD", "climate change on LCC land"),
            ("Row 2  [LCC_FUT − CTRL_PD]_fBVOCctrlPD", "LCC and climate change together, fixed CTRL_PD "
                                                       "emissions (non-BVOC counterpart of Fig. 1a)"),
            ("Row 3  row 2 − row 1", "algebraically the same as row 1 of Fig. 3a")],
           "Both runs prescribe CTRL_PD emissions (relabelled to 2100 in FUT): the BVOC response to the "
           "climate is switched off."),
    "4a": ("Prescription artefacts on LCC land",
           [("Row 1  art_LCC_PD", "LCC_PD − LCC_PD_fBVOCctrlPD"),
            ("Row 2  art_LCC_FUT", "LCC_FUT − LCC_FUT_fBVOCctrlFUT")],
           "Uncorrected BVOC effects: the emission change from LCC plus the prescription artefact. "
           "Minus Fig. 4b = design-B corrected BVOC effect."),
    "4b": ("Prescription artefacts on CTRL land",
           [("Row 1  art_CTRL_PD", "CTRL_PD − CTRL_PD_fBVOCctrlPD"),
            ("Row 2  art_CTRL_FUT", "CTRL_FUT − CTRL_FUT_fBVOCctrlFUT"),
            ("Row 3  row 2 − row 1", "does the artefact change between PD and FUT? ≈ 0 means one correction "
                                     "works in both backgrounds")],
           "The design-B correction subtracts these; its assumption art(LCC land) ≈ art(CTRL land) is tested "
           "in how_big_artefact_is_PD.ipynb."),
}
STORY = [  # (section, [fig ids])
    ("Total effects", ["1a", "1b", "1c"]),
    ("BVOC-related effects", ["2", "2b"]),
    ("Non-BVOC effects", ["3a", "3b"]),
    ("Prescription artefacts", ["4a", "4b"]),
]
COLUMNS = ("Columns: isoprene and monoterpene emissions, SOA burden, aerosol number, liquid cloud fraction, "
           "droplet effective radius, droplet number, evapotranspiration.")


def rows_text(fid):
    _, rows, note = FIGS[fid]
    lines = []
    for lab, txt in rows:
        lines.append((lab, {"bold": True, "color": TC.TEXT_2}))
        lines.append(txt)
    if note:
        lines.append((note, {"italic": True, "color": "595959"}))
    return lines


def figure(d, sec, kick, fid, path):
    title = f"Fig. {fid}. {FIGS[fid][0]}"
    s = d.content_slide(sec, kick, title)
    top, H, Wb = 1.6, 5.25, d.W - 2 * M
    from PIL import Image
    w, h = Image.open(path).size
    a = w / h
    fw = min(Wb, H * a)
    side = Wb - fw
    if side >= 2.2:  # text beside the grid
        pic, _, _ = d.picture(s, path, M, top, fw, H)
        x = M + fw + 0.3
        d.text(s, x, top, d.W - M - x, H, rows_text(fid), 11, TC.TEXT_1, space_after=3, name="Rows")
    else:  # text under the grid; shrink the grid if needed to leave ≥ 1.0 in
        below = max(1.0, H - Wb / a)
        pic, _, dh = d.picture(s, path, M, top, Wb, H - below - 0.1)
        y = top + (H - below - 0.1 + dh) / 2 + 0.15
        pairs = FIGS[fid][1]
        cols = max(1, len(pairs))
        cw = (Wb - 0.3 * (cols - 1)) / cols
        for i, (lab, txt) in enumerate(pairs):
            d.text(s, M + i * (cw + 0.3), y, cw, top + H - y - (0.3 if FIGS[fid][2] else 0),
                   [(lab, {"bold": True, "color": TC.TEXT_2}), txt], 12, TC.TEXT_1, name=f"Row {i+1}")
        if FIGS[fid][2]:
            d.text(s, M, top + H - 0.25, Wb, 0.25, (FIGS[fid][2], {"italic": True, "color": "595959"}), 11)
    rel = str(path.relative_to(ROOT))
    notes = "\n".join([title, *(f"{lab}: {t}" for lab, t in FIGS[fid][1]), FIGS[fid][2] or "", COLUMNS, f"File: {rel}"])
    d.finish(s, rel, notes)


def questions_table(d, sec, kick):
    s = d.content_slide(sec, kick, "One figure per question")
    rows = [("Fig.", "Question", "Contrasts (case1 − case2)")]
    for fid, (t, r, _) in FIGS.items():
        rows.append((fid, t, " · ".join(lab.split("  ", 1)[-1] for lab, _ in r if not lab.endswith("row 1"))))
    tbl = s.shapes.add_table(len(rows), 3, Inches(M), Inches(1.6), Inches(d.W - 2 * M),
                             Inches(0.42 * len(rows))).table
    tbl.columns[0].width, tbl.columns[1].width = Inches(0.6), Inches(4.4)
    tbl.columns[2].width = Inches(d.W - 2 * M - 5.0)
    for i, row in enumerate(rows):
        for c, v in enumerate(row):
            cell = tbl.cell(i, c)
            cell.margin_top = cell.margin_bottom = Inches(0.03)
            cell.fill.solid()
            cell.fill.fore_color.theme_color = (TC.TEXT_2 if i == 0 else
                                                TC.BACKGROUND_2 if i % 2 else TC.BACKGROUND_1)
            run = cell.text_frame.paragraphs[0].add_run()
            run.text = v
            d.style(run, 11, TC.BACKGROUND_1 if i == 0 else TC.TEXT_1, i == 0 or c == 0)
    d.text(s, M, 6.55, d.W - 2 * M, 0.3, (COLUMNS + " " + DB, {"italic": True, "color": "595959"}), 10)
    d.finish(s, "analysis/simulation-contrasts.ipynb")


if __name__ == "__main__":
    OUT = Path(sys.argv[1])
    d = Deck(*sys.argv[2:3])
    used = set()
    d.title_slide("Simulation contrasts: BVOC → SOA → cloud",
                  "One figure per question, nudged runs 2001–2025",
                  ["BOREAL-FOREST-EXPANSION", "analysis/simulation-contrasts.ipynb", "9 November 2026"])
    story = [dict(num=i + 1, title=t, subs=[(f"{f} {FIGS[f][0]}", None) for f in figs])
             for i, (t, figs) in enumerate(STORY)]
    d.agenda(story)
    questions_table(d, "Overview", "Overview · The questions")
    for k, (sec, figs) in enumerate(STORY, 1):
        for fid in figs:
            p = FIGDIR / f"contrast_grid_fig{fid}_{Y}.png"
            assert p.exists(), p
            used.add(p)
            figure(d, f"{k} {sec}", f"{k}  {sec} · Fig. {fid}", fid, p)
    missing = [p for p in FIGDIR.glob(f"*_{Y}.png") if p not in used]
    assert not missing, "figures not placed:\n" + "\n".join(map(str, missing))
    d.save(OUT, "Simulation contrasts 2001–2025")
    print("slides:", len(d.prs.slides), "figures:", len(used), "->", OUT)
