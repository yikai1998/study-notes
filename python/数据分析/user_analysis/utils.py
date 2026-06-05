"""
Shared plot helpers, print utilities, and statistical primitives.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ── Plot helpers ──────────────────────────────────────────────────────────────

def annotate_bars(ax, fmt=".1%", offset=0.01, fontsize=9):
    """Add value labels above each bar in a bar chart."""
    for bar in ax.patches:
        h = bar.get_height()
        if h == 0:
            continue
        label = format(h, fmt) if isinstance(fmt, str) else fmt(h)
        ax.text(bar.get_x() + bar.get_width() / 2, h + offset,
                label, ha="center", fontsize=fontsize)


def annotate_hbars(ax, values, fmt=".3f", offset=0.01, fontsize=9):
    """Add value labels to the right of each horizontal bar."""
    for bar, val in zip(ax.patches, values):
        ax.text(bar.get_width() + offset, bar.get_y() + bar.get_height() / 2,
                format(val, fmt), va="center", fontsize=fontsize)


def section_header(n: int, title: str):
    print("\n" + "═" * 60)
    print(f"{n}. {title}")
    print("═" * 60)


# ── Statistical helpers ───────────────────────────────────────────────────────

def proportion_ci(p: float, n: int, z: float = 1.96) -> tuple[float, float]:
    """
    Wilson score confidence interval for a proportion.
    More accurate than the normal approximation near 0 or 1.
    Returns (lower, upper).
    """
    if n == 0:
        return 0.0, 1.0
    denom  = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half   = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return max(0.0, center - half), min(1.0, center + half)


def add_ci_errorbars(ax, x_positions, proportions, counts, color="black", capsize=4):
    """
    Overlay 95% Wilson CI error bars on a bar chart.
    x_positions: numeric x coordinates of bars.
    """
    lo, hi = [], []
    for p, n in zip(proportions, counts):
        l, h = proportion_ci(p, n)
        lo.append(p - l)
        hi.append(h - p)
    ax.errorbar(x_positions, proportions, yerr=[lo, hi],
                fmt="none", color=color, capsize=capsize, linewidth=1.2)


def chi2_test(df: pd.DataFrame, group_col: str, binary_col: str) -> dict:
    """
    Chi-square test of independence between a grouping variable and a binary column.
    Returns chi2, p-value, degrees of freedom, and Cramér's V effect size.

    Cramér's V interpretation:
      < 0.10  → negligible effect
      0.10–0.20 → small effect
      0.20–0.40 → moderate effect
      > 0.40  → strong effect
    """
    try:
        from scipy.stats import chi2_contingency
    except ImportError:
        return {"chi2": float("nan"), "p": float("nan"), "dof": 0,
                "cramers_v": float("nan"), "significant": False,
                "_error": "scipy not installed"}
    ct = pd.crosstab(df[group_col], df[binary_col])
    chi2, p, dof, _ = chi2_contingency(ct)
    n = ct.values.sum()
    v = np.sqrt(chi2 / (n * (min(ct.shape) - 1))) if min(ct.shape) > 1 else 0.0
    return {"chi2": chi2, "p": p, "dof": dof, "cramers_v": v,
            "significant": p < 0.05}


def mann_whitney_test(a: pd.Series, b: pd.Series, label_a="A", label_b="B") -> dict:
    """
    Mann-Whitney U test: non-parametric test for whether two distributions differ.
    Does not assume normality — appropriate for rates and skewed metrics.
    """
    try:
        from scipy.stats import mannwhitneyu
    except ImportError:
        return {"U": float("nan"), "p": float("nan"),
                "median_a": a.median(), "median_b": b.median(),
                "label_a": label_a, "label_b": label_b,
                "significant": False, "_error": "scipy not installed"}
    a_clean = a.dropna()
    b_clean = b.dropna()
    stat, p = mannwhitneyu(a_clean, b_clean, alternative="two-sided")
    return {
        "U": stat, "p": p,
        "median_a": a_clean.median(), "median_b": b_clean.median(),
        "label_a": label_a, "label_b": label_b,
        "significant": p < 0.05,
    }
