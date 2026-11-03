"""Draw the restyled MEGAN maps into sandbox/test_megan_style_outputs/ (style test, not paper output)."""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from boreal_forest_expansion.plotting.style import set_default_style
from boreal_forest_expansion.plotting import megan_maps as mm

set_default_style()
mm.MEGAN_FIG_DIR = Path(__file__).resolve().parent / "test_megan_style_outputs"
which = sys.argv[1:] or ["attribution", "factors", "gammas"]
t = time.time()
if "attribution" in which:
    mm.make_attribution_maps("MTERP", "PD", "ANN")
    mm.make_attribution_maps("isoprene", "PD", "JJA")
    mm.make_attribution_maps("MTERP", "FUT", "JJA")
if "factors" in which:
    mm.make_factor_maps("MTERP", "PD", "ANN")
if "gammas" in which:
    mm.make_gamma_maps("PD", "ANN")
print(f"{time.time() - t:.0f} s")
