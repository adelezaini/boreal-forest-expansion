"""Sandbox: split6-2 forcing summaries of analysis/artefact-corrected-split.ipynb (cell 12) with the
simulations-interpretation.pptx aliases (user 2026-11-16):
  title + left group  = [LCC − CTRL] _P
  right group, design A = LCC_P_fBVOC [lccP − E]   (bracket bold)
  right group, design B = LCC_P − LCC_P_fBVOC<E>*  + footnote "* = artefact corrected"
Writes sandbox/test_split_aliases_outputs/{design-A,design-B}/; results/figures untouched.
Run: HDF5_USE_FILE_LOCKING=FALSE $PY sandbox/test_split_aliases.py [NET|SW|LW ...]"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from boreal_forest_expansion.plotting.style import set_default_style
from boreal_forest_expansion.plotting import forcing_maps as fm

set_default_style()
OUT = ROOT / "sandbox/test_split_aliases_outputs"
BANDS = sys.argv[1:] or ["NET"]
EXTRA_SOURCES = {"PD": (), "FUT": ("lccPD", "ctrlPD")}
common = dict(start_year=2001, end_year=2025, extent_lat=45, mean_lat_min=45, save=True, scales="split6-2",
              transparent_background=False, dpi=150)


def ref_A(P, source=None):   # as in the notebook
    source = source or f"ctrl{P}"
    return fm.VirtualRun(f"LCC_{P}_fBVOC{source}_A",
                         {f"LCC_{P}": 1.0, f"LCC_{P}_fBVOClcc{P}": -1.0, f"LCC_{P}_fBVOC{source}": 1.0})


def labels(P, source, design, total=None):
    """pptx aliases: title, left (LCC − CTRL) and right (BVOC) group labels, footnote."""
    E = source or f"ctrl{P}"
    total = total or f"[LCC − CTRL] _{P}"
    if design == "A":
        bvoc = [(f"LCC_{P}_fBVOC ", "normal"), (f"[lcc{P} − {E}]", "bold")]
        foot = None
    else:
        bvoc, foot = f"LCC_{P} − LCC_{P}_fBVOC{E}*", "* = artefact corrected"
    return dict(title=total, group_labels={"ctrl": total, "fbvoc": bvoc}, footnote=foot)


CASES = [(P, s) for P in ("PD", "FUT") for s in (None, *EXTRA_SOURCES[P])]
ONLY_FUTPD = "--futpd" in sys.argv   # only the LCC_FUT − CTRL_PD case
BANDS = [b for b in BANDS if not b.startswith("--")] or ["NET"]

# LCC_FUT − CTRL_PD (user 2026-11-16): LCC and climate change together; BVOC maps = the FUT ctrlPD case
for design in ("A", "B"):
    pairs = {"lcc": "LCC_FUT", "ctrl": "CTRL_PD",
             "fbvoc": ref_A("FUT", "ctrlPD") if design == "A" else fm.corrected_fbvoc("FUT", "ctrlPD")}
    tag = f"LCCFUT-CTRLPD_fBVOCctrlPD{'designA' if design == 'A' else 'corr'}"
    for band in BANDS:
        fig, _ = fm.make_forcing_summary_figure(tag, band=band, pairs=pairs, figdir=OUT / f"design-{design}",
                                                **labels("FUT", "ctrlPD", design, total="LCC_FUT − CTRL_PD"), **common)
        plt.close(fig)

for P in ("PD", "FUT") if not ONLY_FUTPD else ():
    for s in (None, *EXTRA_SOURCES[P]):
        E = s or f"ctrl{P}"
        for design in ("A", "B"):
            pairs = ({**fm.BVOC_PAIRS[P], "fbvoc": ref_A(P, s)} if design == "A"
                     else {**fm.CORRECTED_PAIRS[P], "fbvoc": fm.corrected_fbvoc(P, s)})
            tag = f"{P}_fBVOC{E}{'designA' if design == 'A' else 'corr'}"
            for band in BANDS:
                fig, _ = fm.make_forcing_summary_figure(tag, band=band, pairs=pairs, figdir=OUT / f"design-{design}",
                                                        **labels(P, s, design), **common)
                plt.close(fig)
