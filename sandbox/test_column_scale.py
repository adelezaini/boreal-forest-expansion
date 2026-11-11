"""Sandbox: contrast grids with one colour scale per column (scale="column"), reduced only where a row looks blank."""
import sys, time
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from boreal_forest_expansion.plotting import forcing_maps as fm
from boreal_forest_expansion.plotting.style import set_default_style
set_default_style()

OUT = REPO / "sandbox" / "test_column_scale_outputs"
which = sys.argv[1:] or ["context"]
PANELS = {"context": fm.CONTEXT_PANELS, "hydro": fm.HYDRO_PANELS}
for name in which:
    for cat in fm.CATEGORIES:
        t = time.time()
        fig, _ = fm.make_contrast_grid_figure(cat, PANELS[name], name, figdir=OUT, scale="column", dpi=150)
        plt.close(fig)
        print(f"{name} {cat}: {time.time() - t:.0f} s", flush=True)
