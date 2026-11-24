"""Style test: modified cells solid, vegetation border in denser and thinner dashes (monoterpene, FUT).

Rows = yellow cells in the broadleaf or needleleaf area. Columns = dash options.
Dash patterns are in units of the line width (matplotlib default).
Writes into sandbox/test_vegetation_outlines_outputs/ only (not paper output).
"""
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "src"), str(HERE)]

import matplotlib.pyplot as plt

import test_vegetation_border_styles as ts
import test_vegetation_outlines as tv
import test_vegetation_yellow_versions as ty
from boreal_forest_expansion.plotting import forcing_maps as fm
from boreal_forest_expansion.plotting.style import set_default_style

MODIFIED = ("-", 0.5)
DASHES = [("1  Width 0.8, short gaps", (0, (2.5, 1.0)), 0.8),
          ("2  Width 0.7, shorter dashes", (0, (2.2, 1.0)), 0.7),
          ("3  Width 0.6, densest", (0, (2.0, 1.0)), 0.6)]
ROWS = [("LCC_FUT", "CTRL_FUT")] * 2
LABELS = ["Yellow cells in\nbroadleaf area", "Yellow cells in\nneedleleaf area"]


def main():
    set_default_style()
    _, _, classes, modified, area = tv.load_classes()
    panel = next(p for p in fm.CONTEXT_PANELS if p.key == "sfmterp")
    for attempt in range(1, 9):  # NIRD reads fail intermittently with "HDF error"
        try:
            fig, axes = fm.make_contrast_grid_figure("LCC-CTRL", [panel] * len(DASHES), "Monoterpene emissions, FUT",
                                                     start_year=tv.START, end_year=tv.END, rows=ROWS, labels=LABELS,
                                                     save=False)
            break
        except (OSError, RuntimeError) as err:
            print(f"read attempt {attempt} failed: {err}", flush=True)
            plt.close("all")
            if attempt == 8:
                raise
            time.sleep(10 * attempt)
    borders = [ty.border_for(classes, area, axes[0, 0]),
               ty.border_for(classes.where(classes != 2, 3), area, axes[0, 0])]
    for i, border in enumerate(borders):
        for j, (title, dash, width) in enumerate(DASHES):
            ts.draw(axes[i, j], border, modified, (title, (dash, width), MODIFIED))
            if i == 0:
                axes[i, j].set_title(title, fontsize=10, fontweight="semibold")
    fig.savefig(tv.OUT / "border_dash_density_monoterpene.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
