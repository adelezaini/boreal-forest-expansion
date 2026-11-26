"""Sandbox test of analysis/radiative_forcing_tree_5rows.py layout (user 2026-11-25, 2026-11-26: section labels,
one shared vertical colourbar for rows 3-5). Draws from the 2001-2040 caches into
sandbox/test_forcing_tree_5rows_outputs/; results/ untouched. Usage: python sandbox/test_forcing_tree_5rows.py [CASE]"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "analysis")); sys.path.insert(0, str(REPO / "src"))
import radiative_forcing_tree_5rows as t4  # noqa: E402

t4.FIG = REPO / "sandbox" / "test_forcing_tree_5rows_outputs"
t4.draw(sys.argv[1] if len(sys.argv) > 1 else None)
