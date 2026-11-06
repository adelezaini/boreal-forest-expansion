"""Sandbox: forcing decomposition with one contrast line over the BVOC panels (user 2026-11-03).
Redraws all 27 decomposition figures of analysis/radiative_forcing.ipynb (3 contrasts x 3 bands x
3 scale options) into sandbox/test_group_label_outputs/; results/figures untouched."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from boreal_forest_expansion.plotting.style import set_default_style
from boreal_forest_expansion.plotting import forcing_maps as fm

set_default_style()
out = ROOT / "sandbox/test_group_label_outputs"
SUMMARY = {"PD_fBVOCctrlPD": fm.BVOC_PAIRS["PD"],
           "FUT_fBVOCctrlPD": fm.BVOC_PAIRS["FUT"],
           "FUT_fBVOCctrlFUT": {**fm.BVOC_PAIRS["FUT"], "fbvoc": "LCC_FUT_fBVOCctrlFUT"}}
for scales in (None, "shared6", "split6-2"):
    for exp, pairs in SUMMARY.items():
        for band in ("NET", "SW", "LW"):
            fig, _ = fm.make_forcing_summary_figure(exp, 2001, 2014, band=band, pairs=pairs, scales=scales,
                                                    extent_lat=45, mean_lat_min=45, figdir=out, dpi=150,
                                                    transparent_background=False)
            plt.close(fig)
