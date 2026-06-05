"""
Shared plot helpers and print utilities used across multiple sections.
"""

import matplotlib.pyplot as plt


def annotate_bars(ax, fmt=".1%", offset=0.01, fontsize=9):
    """Add value labels above each bar in a bar chart."""
    for bar in ax.patches:
        h = bar.get_height()
        if h == 0:
            continue
        label = format(h, fmt) if isinstance(fmt, str) else fmt(h)
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            h + offset,
            label,
            ha="center",
            fontsize=fontsize,
        )


def annotate_hbars(ax, values, fmt=".3f", offset=0.01, fontsize=9):
    """Add value labels to the right of each horizontal bar."""
    for bar, val in zip(ax.patches, values):
        ax.text(
            bar.get_width() + offset,
            bar.get_y() + bar.get_height() / 2,
            format(val, fmt),
            va="center",
            fontsize=fontsize,
        )


def section_header(n: int, title: str):
    print("\n" + "═" * 60)
    print(f"{n}. {title}")
    print("═" * 60)
