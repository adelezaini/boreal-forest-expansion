import matplotlib.pyplot as plt
from cycler import cycler

from .palette import PALETTE_ORDER

def set_default_style():
    # Cantarell for text and math, so the bold mean (mathtext \mathbf) matches the text; chosen 2026-10-28,
    # comparison in sandbox/test_fonts.ipynb. System font (/usr/share/fonts/cantarell, .otf).
    # Cantarell has no italic: math italic (\mathit, e.g. 'Under the maps') uses DejaVu Sans Oblique.
    plt.rcParams['font.family'] = 'Cantarell'
    plt.rcParams['mathtext.fontset'] = 'custom'
    plt.rcParams['mathtext.rm'] = 'Cantarell'
    plt.rcParams['mathtext.bf'] = 'Cantarell:bold'
    plt.rcParams['mathtext.it'] = 'DejaVu Sans:italic'
    plt.rcParams['figure.titlesize'] = '22'
    plt.rcParams['axes.titlesize'] = '18'
    plt.rcParams['font.size'] = '15'
    # Project palette as the default colour cycle (user 2026-11-03), so series without an explicit colour use it in order.
    plt.rcParams['axes.prop_cycle'] = cycler(color=PALETTE_ORDER)
