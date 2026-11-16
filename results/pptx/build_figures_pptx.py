"""Build a sectioned PowerPoint of results/figures (2001-2025) on the CICERO template.

Run: python build_figures_pptx.py OUT.pptx [TEMPLATE.pptx]  (needs python-pptx, Pillow, lxml)
Every PNG in results/figures/ (except megan_factors/, see build_megan_pptx.py) must be placed in build_story(),
else it stops with the list. Design A (user 2026-11-16): fBVOC FUT contrasts use the real 24g run; the
artefacts section shows the design-A split first and design B as comparison.
"""
import re
import sys
from pathlib import Path

from pptx.enum.dml import MSO_THEME_COLOR as TC
from pptx.util import Inches

sys.path.insert(0, str(Path(__file__).parent))
from cicero_pptx import Deck, M  # noqa: E402

FIG = Path("/cluster/home/adelez/BOREAL-FOREST-EXPANSION/results/figures")

# ---------------------------------------------------------------- labels
CONTRAST = {
    # interactive
    "LCC-CTRL_PD": "[LCC − CTRL]_PD", "LCC-CTRL_FUT": "[LCC − CTRL]_FUT",
    "CTRL_FUT-PD": "CTRL_[FUT − PD]", "LCC_FUT-PD": "LCC_[FUT − PD]",
    "LCC_FUT-CTRL_PD": "LCC_FUT − CTRL_PD",
    # fBVOC
    "fBVOC_PD_lccPD-ctrlPD": "LCC_PD_fBVOC [lccPD − ctrlPD]",
    "fBVOC_FUT_lccFUT-ctrlFUT": "LCC_FUT_fBVOC [lccFUT − ctrlFUT]",
    "fBVOC_FUT_lccFUT-lccPD": "LCC_FUT_fBVOC [lccFUT − lccPD]",
    "fBVOC_FUT_lccFUT-ctrlPD": "LCC_FUT_fBVOC [lccFUT − ctrlPD]",
    "fBVOC_FUT_ctrlFUT-ctrlPD": "LCC_FUT_fBVOC [ctrlFUT − ctrlPD]",
    "fBVOC_FUT_lccPD-ctrlPD": "LCC_FUT_fBVOC [lccPD − ctrlPD] (not really physical)",
    # non-BVOC
    "nonBVOC_LCC-CTRL_PD": "[LCC_PD − CTRL_PD]_fBVOCctrlPD",
    "nonBVOC_LCC-CTRL_FUT": "[LCC_FUT − CTRL_FUT]_fBVOCctrlFUT",
    "nonBVOC_LCC_FUT-PD": "[LCC_FUT − LCC_PD]_fBVOCctrlPD",
    "nonBVOC_LCC_FUT-CTRL_PD": "[LCC_FUT − CTRL_PD]_fBVOCctrlPD",
    # artefacts
    "art_LCC_PD": "art_LCC_PD", "art_LCC_FUT": "art_LCC_FUT",
    "art_CTRL_PD": "art_CTRL_PD", "art_CTRL_FUT": "art_CTRL_FUT",
}
ORDER = {
    "interactive": ["LCC-CTRL_PD", "LCC-CTRL_FUT", "CTRL_FUT-PD", "LCC_FUT-PD", "LCC_FUT-CTRL_PD"],
    "fBVOC": ["fBVOC_PD_lccPD-ctrlPD", "fBVOC_FUT_lccFUT-ctrlFUT", "fBVOC_FUT_ctrlFUT-ctrlPD",
              "fBVOC_FUT_lccFUT-lccPD", "fBVOC_FUT_lccFUT-ctrlPD", "fBVOC_FUT_lccPD-ctrlPD"],
    "non-BVOC": ["nonBVOC_LCC-CTRL_PD", "nonBVOC_LCC-CTRL_FUT", "nonBVOC_LCC_FUT-PD", "nonBVOC_LCC_FUT-CTRL_PD"],
    "artefacts": ["art_LCC_PD", "art_CTRL_PD", "art_LCC_FUT", "art_CTRL_FUT"],
}
BANDS = ["NET", "SW", "LW"]
BANDNAME = {"NET": "net", "SW": "shortwave", "LW": "longwave"}
CATNAME = {"interactive": "interactive runs", "fBVOC": "BVOC effect", "non-BVOC": "non-BVOC effect",
           "artefacts": "prescription artefacts"}
GRID = {  # contrast-grid panel set -> title
    "context": "BVOC, SOA, aerosol and cloud response",
    "cloud_types": "Cloud-type response (annual)",
    "cloud_types_JJA": "Cloud-type response (JJA)",
    "fsds_split": "Surface downwelling SW: all-sky, clear-sky, cloud and aerosol parts",
    "surface_energy": "Surface energy balance",
    "snow_albedo": "Snow and albedo",
    "hydro": "Hydrology",
    "carbon": "Land carbon fluxes",
    "et_split": "Evapotranspiration: transpiration, canopy and soil evaporation",
}

used = set()


def f(rel):
    p = FIG / rel
    assert p.exists(), p
    used.add(p)
    return p


def per_contrast(cat, prefix, band=None):
    """Ghan / time-series files of one category in story order."""
    out = []
    for key in ORDER[cat]:
        for b in ([band] if band else [None]):
            name = f"{prefix}{key}" + (f"_{b}" if b else "") + "_2001_2025.png"
            p = FIG / cat / name
            if p.exists():
                out.append(p)
    return out


def ghan_title(p, seasonal):
    m = re.match(r"ghan_(?:seasonal_)?(?:nonBVOC_)?(.+)_(NET|SW|LW)_2001_2025", p.stem)
    key, band = m.group(1), m.group(2)
    if not key.startswith(("fBVOC", "art_")) and "nonBVOC" in p.stem:
        key = "nonBVOC_" + key
    kind = "Seasonal forcing maps" if seasonal else "Forcing maps"
    return f"{kind}, {BANDNAME[band]} (Ghan): {CONTRAST[key]}"


def ts_title(p):
    key = re.match(r"timeseries_(?:nonBVOC_)?(.+)_2001_2025", p.stem).group(1)
    if "nonBVOC" in p.stem:
        key = "nonBVOC_" + key
    return f"Yearly time series: {CONTRAST[key]}"


# ---------------------------------------------------------------- story
def category_section(cat, num, title, intro, mech_first=False):
    c = cat
    sfx = f"_{cat}_2001_2025.png"
    subs = []
    budget = [(f(f"{c}/radiative_budget{sfx}"), f"Radiative budget at TOA: {CATNAME[cat]}")]
    if cat == "interactive":
        budget += [(f("interactive/cumulative_radiative_decomposition_2001_2025.png"),
                    "Cumulative decomposition of the net TOA change"),
                   (f("interactive/cumulative_radiative_decomposition_2001_2025_vegetation_increments.png"),
                    "Vegetation increments: non-BVOC, BVOC (design B) and its design-A parts BVOC_A + δ")]
    subs.append(("Radiative budget", budget))
    maps = []
    for key in ORDER[cat]:
        for b in BANDS:
            pref = "ghan_" if cat in ("interactive", "fBVOC", "artefacts") else "ghan_nonBVOC_"
            k = key.replace("nonBVOC_", "")
            p = FIG / c / f"{pref}{k}_{b}_2001_2025.png"
            if p.exists():
                maps.append((f(p.relative_to(FIG)), ghan_title(p, False)))
    subs.append(("Annual forcing maps", maps))
    smaps = []
    for key in ORDER[cat]:
        for b in BANDS:
            pref = "ghan_seasonal_" if cat != "non-BVOC" else "ghan_seasonal_nonBVOC_"
            k = key.replace("nonBVOC_", "")
            p = FIG / c / f"{pref}{k}_{b}_2001_2025.png"
            if p.exists():
                smaps.append((f(p.relative_to(FIG)), ghan_title(p, True)))
    subs.append(("Seasonal forcing maps", smaps))
    ts = []
    for key in ORDER[cat]:
        k = key.replace("nonBVOC_", "")
        pref = "timeseries_nonBVOC_" if cat == "non-BVOC" else "timeseries_"
        p = FIG / c / f"{pref}{k}_2001_2025.png"
        if p.exists():
            ts.append((f(p.relative_to(FIG)), ts_title(p)))
    for b in BANDS:
        ts.append((f(f"{c}/paired_years_{cat}_{b}_2001_2025.png"),
                   f"Paired years, {BANDNAME[b]}: year-by-year contrasts"))
    subs.append(("Time series and interannual variability", ts))
    surf = [(f(f"{c}/contrast_grid_{g}{sfx}"), GRID[g])
            for g in ["snow_albedo", "surface_energy", "fsds_split", "hydro", "et_split", "carbon"]]
    surf.append((f(f"{c}/water_budget{sfx}"), "Water budget"))
    if cat == "interactive":
        surf.append((f("interactive/seasonal_cycle_carbon_et_modified_2001_2025.png"),
                     "Seasonal cycle of carbon fluxes and ET, modified cells"))
    cloud = [(f(f"{c}/contrast_grid_context{sfx}"), GRID["context"]),
             (f(f"{c}/contrast_grid_cloud_types{sfx}"), GRID["cloud_types"]),
             (f(f"{c}/contrast_grid_cloud_types_JJA{sfx}"), GRID["cloud_types_JJA"]),
             (f(f"{c}/seasonal_cloud_types{sfx}"), "Seasonal cycle of cloud types"),
             (f(f"{c}/cloud_profile_{cat}_ANN_2001_2025.png"), "Vertical cloud profiles (annual)"),
             (f(f"{c}/cloud_profile_{cat}_JJA_2001_2025.png"), "Vertical cloud profiles (JJA)")]
    mech = [("BVOC, aerosol and clouds", cloud), ("Surface, snow and water", surf)]
    if not mech_first:
        mech = mech[::-1]
    subs += mech
    return dict(num=num, title=title, intro=intro, subs=subs)


def build_story():
    S = []
    S.append(dict(num=1, title="Experiment and runs",
                  intro="What was simulated: NorESM2.3, nudged 2001–2025, PD and FUT backgrounds, "
                        "CTRL vs LCC vegetation, interactive vs prescribed BVOC (fBVOC). "
                        "Absolute yearly values of every run.",
                  subs=[("Contrasts used", [("TABLE", "The 19 contrasts in 4 categories")]),
                        ("Absolute time series", [
                            (f("timeseries/timeseries_absolute_PD_global_2001_2025.png"), "Absolute yearly values, PD runs: global"),
                            (f("timeseries/timeseries_absolute_PD_regional_2001_2025.png"), "Absolute yearly values, PD runs: regional"),
                            (f("timeseries/timeseries_absolute_FUT_global_2001_2025.png"), "Absolute yearly values, FUT runs: global"),
                            (f("timeseries/timeseries_absolute_FUT_regional_2001_2025.png"), "Absolute yearly values, FUT runs: regional")])]))
    S.append(category_section("interactive", 2, "Total response: interactive runs",
                              "Forest expansion with interactive BVOC, in the PD and FUT backgrounds, "
                              "compared with the effect of the future background itself."))
    S.append(category_section("non-BVOC", 3, "Biogeophysical part: non-BVOC effect",
                              "Land-cover change with BVOC emissions held fixed (prescribed): "
                              "albedo, surface energy and water fluxes."))
    S.append(category_section("fBVOC", 4, "Biogeochemical part: BVOC effect",
                              "Changing only the prescribed BVOC emissions (design A: prescribed − prescribed, so the "
                              "artefact cancels): the BVOC → SOA → aerosol → cloud chain.", mech_first=True))
    S.append(dict(num=5, title="PD vs FUT attribution",
                  intro="Putting the categories side by side: how the PD and FUT signals compare and "
                        "where the emission changes come from.",
                  subs=[("Radiative budget across categories", [
                            (f("pd-fut-attribution/pd_fut_radiative_budget_2001_2025.png"), "Radiative budget: PD and FUT contrasts of the 4 categories"),
                            (f("pd-fut-attribution/pd_fut_paired_years_NET_2001_2025.png"), "PD vs FUT paired years, net"),
                            (f("pd-fut-attribution/pd_fut_paired_years_SW_2001_2025.png"), "PD vs FUT paired years, shortwave"),
                            (f("pd-fut-attribution/pd_fut_paired_years_LW_2001_2025.png"), "PD vs FUT paired years, longwave")]),
                        ("BVOC emission changes", [
                            (f("pd-fut-attribution/fbvoc_percent_change_maps_2001_2025.png"), "BVOC emission change maps (%)"),
                            (f("pd-fut-attribution/emission_origin_monthly_2001_2025.png"), "Monthly origin of the emission change")]),
                        ("Mechanism chain", [
                            (f("pd-fut-attribution/pd_mechanism_source_boxes_2001_2025.png"), "PD: precursor, SOA and aerosol changes in four source boxes"),
                            (f("pd-fut-attribution/seasonal_chain_bvoc_soa_cloud_sw_2001_2025.png"), "Seasonal chain: BVOC → SOA → cloud → SW")])]))
    art = category_section("artefacts", 6, "Robustness: BVOC prescription artefacts",
                           "art = interactive − prescribed own emissions. Design A (used): BVOC_A = "
                           "prescribed − prescribed, δ = art_LCC_own − art_CTRL; design B (matched "
                           "baseline) shown for comparison, BVOC_B = BVOC_A + δ.", mech_first=True)
    dA, dB = "artefacts/design-A-split/", "artefacts/design-B-split/"
    splitA = [(f(dA + "radiative_budget_split_designA_NET_2001_2025.png"),
               "Design-A split of the net TOA budget: total = non-BVOC + BVOC_A + δ"),
              (f(dB + "radiative_budget_split_designB_vs_A_NET_2001_2025.png"),
               "Design B vs design A, net TOA budget (BVOC_B = BVOC_A + δ)")]
    srcsA = {"PD": [("", "ctrlPD", "fBVOCctrlPDdesignA")],
             "FUT": [("", "ctrlFUT", "fBVOCctrlFUTdesignA"), ("-ctrlPD", "ctrlPD", "fBVOCctrlPDdesignA"),
                     ("-lccPD", "lccPD", "fBVOClccPDdesignA")]}
    for per in ["PD", "FUT"]:
        for sfx, src, ctx in srcsA[per]:
            lab = f"BVOC_A = LCC_{per}_fBVOC[lcc{per} − {src}]"
            splitA.append((f(dA + f"{per}_{ctx}_bvoc_context_maps_2001_2025.png"),
                           f"{per}: BVOC_A ({src} emissions), context maps"))
            for b in BANDS:
                splitA.append((f(dA + f"{per}_ghan_BVOCA{sfx}_{b}_2001_2025.png"),
                               f"{per} forcing maps, {BANDNAME[b]}: {lab}"))
            splitA.append((f(dA + f"{per}_ghan_seasonal_BVOCA{sfx}_NET_2001_2025.png"),
                           f"{per} seasonal forcing maps, net: {lab}"))
        for which, lab in [("delta", "δ = art_LCC_own − art_CTRL"),
                           ("artLCCown", f"art_LCC_own = LCC_{per} − LCC_{per}_fBVOClcc{per}")]:
            for b in BANDS:
                splitA.append((f(dA + f"{per}_ghan_{which}_{b}_2001_2025.png"),
                               f"{per} forcing maps, {BANDNAME[b]}: {lab}"))
            splitA.append((f(dA + f"{per}_ghan_seasonal_{which}_NET_2001_2025.png"),
                           f"{per} seasonal forcing maps, net: {lab}"))
        for b in BANDS:
            splitA.append((f(dB + f"{per}_ghan_nonBVOC_{b}_2001_2025.png"),
                           f"{per} forcing maps, {BANDNAME[b]}: non-BVOC part (same in A and B)"))
        splitA.append((f(dB + f"{per}_ghan_seasonal_nonBVOC_NET_2001_2025.png"),
                       f"{per} seasonal forcing maps, net: non-BVOC part (same in A and B)"))
    art["subs"].append(("Design-A split: BVOC_A, δ and non-BVOC", splitA))
    tagsA = [("PD_fBVOCctrlPDdesignA", "PD, ctrlPD emissions"), ("FUT_fBVOCctrlFUTdesignA", "FUT, ctrlFUT emissions"),
             ("FUT_fBVOCctrlPDdesignA", "FUT, ctrlPD emissions"), ("FUT_fBVOClccPDdesignA", "FUT, lccPD emissions")]
    for folder, sub, extra in [("individual-scale", "Design-A decomposition, individual scales", ""),
                               ("split6-2", "Design-A decomposition, 6 + 2 split", "_split6-2")]:
        items = []
        for tag, lab in tagsA:
            for b in BANDS:
                items.append((f(dA + f"{folder}/{tag}_forcing_decomposition_{b}{extra}_2001_2025.png"),
                              f"Forcing decomposition, {BANDNAME[b]}: {lab} (BVOC_A)"))
        art["subs"].append((sub, items))
    d = dB
    split = [(f(d + "radiative_budget_split_NET_2001_2025.png"), "Design-B split of the net TOA budget (comparison)")]
    srcs = {"PD": [("", "ctrlPD", "fBVOCctrlPDcorr")],
            "FUT": [("", "ctrlFUT", "fBVOCctrlFUTcorr"), ("-ctrlPD", "ctrlPD", "fBVOCctrlPDcorr"),
                    ("-lccPD", "lccPD", "fBVOClccPDcorr")]}
    for per in ["PD", "FUT"]:
        for sfx, src, ctx in srcs[per]:
            lab = f"corrected BVOC part, design B ({src} emissions)"
            split.append((f(d + f"{per}_{ctx}_bvoc_context_maps_2001_2025.png"),
                          f"{per}: corrected BVOC effect, design B ({src} emissions), context maps"))
            for b in BANDS:
                split.append((f(d + f"{per}_ghan_BVOCcorr{sfx}_{b}_2001_2025.png"),
                              f"{per} forcing maps, {BANDNAME[b]}: {lab}"))
            split.append((f(d + f"{per}_ghan_seasonal_BVOCcorr{sfx}_NET_2001_2025.png"),
                          f"{per} seasonal forcing maps, net: {lab}"))
    art["subs"].append(("Design-B split (comparison)", split))
    for folder, sub, extra in [("individual-scale", "Design-B decomposition, individual scales", ""),
                               ("split6-2", "Design-B decomposition, 6 + 2 split", "_split6-2")]:
        items = []
        for tag, lab in [("PD_fBVOCctrlPDcorr", "PD, ctrlPD emissions"),
                         ("FUT_fBVOCctrlPDcorr", "FUT, ctrlPD emissions"),
                         ("FUT_fBVOCctrlFUTcorr", "FUT, ctrlFUT emissions"),
                         ("FUT_fBVOClccPDcorr", "FUT, lccPD emissions")]:
            for b in BANDS:
                items.append((f(d + f"{folder}/{tag}_forcing_decomposition_{b}{extra}_2001_2025.png"),
                              f"Forcing decomposition, {BANDNAME[b]}: {lab} (design B, corrected)"))
        art["subs"].append((sub, items))
    S.append(art)
    return S


# ---------------------------------------------------------------- drawing (CICERO template)
# Usage: python build_figures_pptx.py OUT.pptx [TEMPLATE.pptx]


def contrast_table(d, sec_name, kick):
    s = d.content_slide(sec_name, kick, "The 19 contrasts in 4 categories")
    rows = [("Category", "Contrast", "What it isolates")]
    desc = {"interactive": "Full response with interactive MEGAN BVOC",
            "fBVOC": "Only the prescribed BVOC emissions change",
            "non-BVOC": "Land cover changes, BVOC emissions fixed",
            "artefacts": "Interactive − prescribed own emissions"}
    for cat in ["interactive", "non-BVOC", "fBVOC", "artefacts"]:
        for i, k in enumerate(ORDER[cat]):
            rows.append((cat if i == 0 else "", CONTRAST[k], desc[cat] if i == 0 else ""))
    tbl = s.shapes.add_table(len(rows), 3, Inches(M), Inches(1.6), Inches(d.W - 2 * M),
                             Inches(0.245 * len(rows))).table
    tbl.columns[0].width, tbl.columns[1].width = Inches(1.8), Inches(5.6)
    tbl.columns[2].width = Inches(d.W - 2 * M - 7.4)
    for r, row in enumerate(rows):
        tbl.rows[r].height = Inches(0.245)
        for c, v in enumerate(row):
            cell = tbl.cell(r, c)
            cell.margin_top = cell.margin_bottom = Inches(0.02)
            cell.fill.solid()
            cell.fill.fore_color.theme_color = (TC.TEXT_2 if r == 0 else
                                                TC.BACKGROUND_2 if r % 2 else TC.BACKGROUND_1)
            run = cell.text_frame.paragraphs[0].add_run()
            run.text = v
            d.style(run, 11, TC.BACKGROUND_1 if r == 0 else TC.TEXT_1, r == 0 or c == 0)
    d.finish(s, "Contrast definitions: src/boreal_forest_expansion/plotting/forcing_maps.py (CONTRASTS)")


if __name__ == "__main__":
    OUT = Path(sys.argv[1])
    d = Deck(*sys.argv[2:3])
    story = build_story()
    all_png = sorted(p for p in FIG.rglob("*.png") if "megan_factors" not in p.parts)  # own deck
    missing = [p for p in all_png if p not in used]
    assert not missing, "figures not placed:\n" + "\n".join(map(str, missing))
    d.title_slide("Climatic impacts of the Arctic expansion of boreal forests",
                  f"Results 2001–2025: all {len(all_png)} figures, ordered as a story",
                  ["BOREAL-FOREST-EXPANSION", "NorESM2.3 (CAM tropstratchem + CLM5), nudged runs",
                   "16 November 2026 · design A"])
    d.agenda(story)
    for sec in story:
        d.divider(sec)
        for i, (sub, items) in enumerate(sec["subs"]):
            kick = f"{sec['num']}.{i+1}  {sec['title']} · {sub}"
            sname = f"{sec['num']}.{i+1} {sub}"
            for path, title in items:
                if path == "TABLE":
                    contrast_table(d, sname, kick)
                else:
                    d.figure_slide(sname, kick, title, path, "results/figures/" + str(path.relative_to(FIG)))
            print(f"{sname}: {len(items)}", flush=True)
    d.save(OUT, "Climatic impacts of the Arctic expansion of boreal forests: figures 2001–2025")
    print("slides:", len(d.prs.slides), "figures:", len(used), "->", OUT)
