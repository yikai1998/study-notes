"""
Central configuration: paths, plot defaults, shared constants.
Import this module in any section — do not hardcode paths elsewhere.
"""

import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_DIR = Path(__file__).parent          # user_analysis/
DATA_PATH   = PROJECT_DIR.parent / "user_registrations.csv"
OUT_DIR     = PROJECT_DIR.parent / "analysis_output"

OUT_DIR.mkdir(exist_ok=True)

# ── Plot defaults ─────────────────────────────────────────────────────────────
FIGURE_DPI = 130
FONT_SIZE  = 10

plt.rcParams.update({"figure.dpi": FIGURE_DPI, "font.size": FONT_SIZE})
PALETTE = sns.color_palette("tab10")
