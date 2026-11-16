"""PowerPoint of the MEGAN factor figures (analysis/megan_factor_maps.ipynb) on the CICERO template.

Run: python build_megan_pptx.py OUT.pptx [TEMPLATE.pptx]  (needs python-pptx, Pillow, lxml)
Figures: results/figures-2001-2014/megan_factors/ (the notebook has not been run on 2001–2025 yet)
and the lake-fix check diagnostics/3_megan-exact-split-test/lake_fix_effect_outputs/figures/.
Every PNG in those folders must be placed, else it stops with the list.
"""
import sys
from pathlib import Path

from pptx.enum.dml import MSO_THEME_COLOR as TC

sys.path.insert(0, str(Path(__file__).parent))
from cicero_pptx import Deck, M  # noqa: E402

ROOT = Path("/cluster/home/adelez/BOREAL-FOREST-EXPANSION")
MF = ROOT / "results/figures-2001-2014/megan_factors"
LAKE = ROOT / "diagnostics/3_megan-exact-split-test/lake_fix_effect_outputs/figures"
LMDI = ROOT / "results/figures/megan_factors"   # exact LMDI split, PD, 6 years (2001-02, 2005-06, 2010-11)
Y = "2001_2014"
GROUP = {"isoprene": "isoprene", "MTERP": "monoterpenes"}
SEASON = {"ANN": "annual mean", "JJA": "JJA"}
used = set()


def f(path):
    assert path.exists(), path
    used.add(path)
    return path


def change_items(per, sfx=""):
    """Factor maps then attribution, isoprene before monoterpenes, ANN before JJA."""
    run = {"PD": "LCC_PD vs CTRL_PD", "FUT": "LCC_FUT vs CTRL_FUT"}[per]
    subs = []
    for g in ["isoprene", "MTERP"]:
        items = []
        for kind, lab in [("factors", "MEGAN factors and % change"),
                          ("attribution", "Attribution of the emission change")]:
            for s in ["ANN", "JJA"]:
                p = (MF / "before_lake_fix" / f"{per}_{g}_{kind}_{s}_{Y}_before_lake_fix.png" if sfx
                     else MF / f"{per}_{g}_{kind}_{s}_{Y}.png")
                items.append((f(p), f"{lab}, {GROUP[g]}, {SEASON[s]}: {run}"))
        subs.append((GROUP[g].capitalize(), items))
    return subs


def build_story():
    S = [dict(num=1, title="How to read the MEGAN factors",
              intro="How CLM's MEGAN builds an emission from an emission factor and activity factors, "
                    "and how the LCC − CTRL emission change is split into these factors.",
              subs=[("Emission = factors", [("INTRO", "MEGAN emission and how its change is split")])]),
         dict(num=2, title="MEGAN fields in each run",
              intro="Plain maps of the CLM history fields EPS_* and GAMMA* (annual mean 2001–2014) for "
                    "isoprene and 7 monoterpenes, in the four interactive runs.",
              subs=[(per, [(f(MF / f"{veg}_{per}_gammas_ANN_{Y}.png"), f"CLM MEGAN fields, annual mean: {veg}_{per}")
                           for veg in ["CTRL", "LCC"]]) for per in ["PD", "FUT"]]),
         dict(num=3, title="PD: forest expansion today",
              intro="LCC_PD vs CTRL_PD. Which factors change the isoprene and monoterpene emission "
                    "when the forest expands under present-day climate?",
              subs=change_items("PD")),
         dict(num=4, title="FUT: forest expansion in 2100",
              intro="LCC_FUT vs CTRL_FUT. The same split in the SSP5-8.5 2100 background.",
              subs=change_items("FUT")),
         dict(num=5, title="PD: exact LMDI split",
              intro="Exact LMDI split of the PD emission change from the MEGAN swap runs (6 years: 2001–02, "
                    "2005–06, 2010–11), and how it compares with the approximate split of sections 3–4.",
              subs=[(GROUP[g].capitalize(),
                     [(f(LMDI / f"PD_{g}_attribution_LMDI_{s}_6yr.png"),
                       f"Exact LMDI attribution, {GROUP[g]}, {SEASON[s]}: LCC_PD vs CTRL_PD") for s in ["ANN", "JJA"]]
                     + [(f(LMDI / "lmdi-vs-approx" / f"PD_{g}_lmdi_vs_approx_{s}.png"),
                         f"LMDI vs approximate split, {GROUP[g]}, {SEASON[s]}") for s in ["ANN", "JJA"]])
                    for g in ["isoprene", "MTERP"]]),
         dict(num=6, title="Appendix: the lake fix",
              intro="Bug fixed 3 Nov: lake was counted in f, the fraction where CLM defines EPS/GAMMA. "
                    "Verdict: the attribution changes very little (composition term +0.05 to +0.07, 100·Δln, ≥ 45°N).",
              subs=[("Lake-fix effect", [(f(LAKE / "lake_ratio_and_shift.png"),
                                          "Where the fix matters: lake share, f ratio and shift δ"),
                                         (f(LAKE / "composition_change_by_case.png"),
                                          "Change of the composition term, per case (after − before)")]),
                    *[(f"Before the fix: {per}", [it for _, items in change_items(per, "_before") for it in items])
                      for per in ["PD", "FUT"]]])]
    return S


def intro_slide(d, sec_name, kick):
    s = d.content_slide(sec_name, kick, "MEGAN emission and how its change is split")
    B, B2 = TC.TEXT_1, TC.TEXT_2
    h = {"bold": True, "color": B2, "size": 16}
    left = [("How MEGAN computes an emission", h),
            ("E = k · f · ε · γ", {"bold": True, "size": 20}),
            "f: land fraction where CLM defines EPS/GAMMA (natural vegetation without bare soil, plus crop)",
            "ε (EPS): emission factor of the vegetation; changes with the plant-type mix",
            "γ = γL · γT · γP · γA · γC: activity factors for LAI, temperature, light, leaf age and CO₂ "
            "(γC for isoprene only)",
            "",
            ("Caveats", h),
            "CLM's GAMMA* are area means over vegetated patches, including patches that do not emit, "
            "so they are not emission-weighted. The deck therefore also uses an effective γ_eff = E / (k f ε).",
            "EPS/GAMMA output exists for 7 of the 21 monoterpenes (≈ 89 % of MEG_MTERP ≥ 45°N).",
            "fBVOC runs have no MEGAN output: only LCC vs CTRL in the same period."]
    right = [("How the LCC − CTRL change is split", h),
             ("Δln E = Δln(f·ε) + Δln γ_eff", {"bold": True, "size": 18}),
             "composition: how much emitting vegetation, and its emission factor",
             "activity: how strongly that vegetation emits",
             "",
             ("Δln γ_eff = Σ Δln γi + residual", {"bold": True, "size": 18}),
             "the partial factors LAI, temperature, light, leaf age, CO₂",
             ("residual = weighting + co-variation", {"bold": True, "size": 16}),
             "weighting: emission-weighted γ_eff vs CLM's area-mean γ; co-variation: the product of the "
             "means vs the mean of the product",
             "",
             "Maps show 100 · Δln (≈ % change); the terms add up. Numbers under the maps: "
             "CTRL-emission-weighted mean ≥ 45°N ± 95 % CI of the yearly means. Hatched: not significant. "
             "Dashed line: modified cells.",
             ("Period 2001–2014 (not yet redone for 2001–2025).", {"italic": True, "color": "7F7F7F"})]
    d.text(s, M, 1.55, 5.95, 5.3, left, 13, B, space_after=4, name="How MEGAN works")
    d.text(s, M + 6.35, 1.55, 5.95, 5.3, right, 13, B, space_after=4, name="How the change is split")
    d.finish(s, "analysis/megan_factor_maps.ipynb · docs/MEGAN_ATTRIBUTION.md",
             "Sources: analysis/megan_factor_maps.ipynb (intro and attribution cells), "
             "diagnostics/3_megan-exact-split-test/lake_fix_effect.ipynb (definition of f).")


def gammas_slide(d, sec_name, kick, title, path, rel):
    """Tall 8 × 7 map grid on the left, reading guide on the right."""
    s = d.content_slide(sec_name, kick, title)
    top, h = 1.55, 5.35
    pic, _, _ = d.picture(s, path, M, top, 5.0, h)
    pic.left = int(M * 914400)  # flush left instead of centred in the 5" box
    x = (pic.left + pic.width) / 914400 + 0.5
    guide = [("Reading guide", {"bold": True, "color": TC.TEXT_2, "size": 16}),
             "Rows: isoprene, then the 7 monoterpenes with EPS/GAMMA output (α-pinene, carene, β-pinene, "
             "myrcene, limonene, ocimene, sabinene).",
             "Columns: EPS (ε), GAMMA (total γ), GAMMAL (LAI), GAMMAT (temperature), GAMMAP (light), "
             "GAMMAA (leaf age), GAMMAC (CO₂, isoprene only).",
             "Grid-cell values are area means over vegetated patches.",
             "Colour scale per column, shared by CTRL and LCC of the same period; EPS has its own scale "
             "per compound.",
             "Dashed line: modified cells."]
    d.text(s, x, top, d.W - M - x, h, guide, 13, TC.TEXT_1, space_after=6, name="Reading guide")
    d.finish(s, rel, f"{title}\nFile: {rel}")


if __name__ == "__main__":
    OUT = Path(sys.argv[1])
    d = Deck(*sys.argv[2:3])
    story = build_story()
    all_png = sorted(MF.rglob("*.png")) + sorted(LAKE.glob("*.png")) + sorted(LMDI.rglob("*.png"))
    missing = [p for p in all_png if p not in used]
    assert not missing, "figures not placed:\n" + "\n".join(map(str, missing))
    d.title_slide("What drives the BVOC emission change? MEGAN factors",
                  "Boreal forest expansion, LCC vs CTRL, PD and FUT, 2001–2014; exact PD LMDI split (6 yr)",
                  ["BOREAL-FOREST-EXPANSION", "NorESM2.3 / CLM5 MEGAN", "16 November 2026"])
    d.agenda(story)
    for sec in story:
        d.divider(sec)
        for i, (sub, items) in enumerate(sec["subs"]):
            kick = f"{sec['num']}.{i+1}  {sec['title']} · {sub}"
            sname = f"{sec['num']}.{i+1} {sub}"
            for path, title in items:
                if path == "INTRO":
                    intro_slide(d, sname, kick)
                    continue
                rel = str(path.relative_to(ROOT))
                if "_gammas_" in path.name:
                    gammas_slide(d, sname, kick, title, path, rel)
                else:
                    if "before_lake_fix" in path.name:
                        title = title + " (before fix)"
                    d.figure_slide(sname, kick, title, path, rel)
            print(f"{sname}: {len(items)}", flush=True)
    d.save(OUT, "MEGAN factors: what drives the BVOC emission change (2001–2014)")
    print("slides:", len(d.prs.slides), "figures:", len(used), "->", OUT)
