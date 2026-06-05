"""
Section 9 — Channel Composite Health Score

Combines five quality signals into a single weighted score per channel.

Additions vs original:
  1. Empirical weight justification: each metric's correlation with suspension
     rate is shown — metrics that predict bad outcomes more strongly should
     carry more weight.
  2. Sensitivity analysis: vary each weight ±50% and check whether the channel
     ranking is stable. If the top/bottom channels don't change, the conclusion
     is robust to the exact weight choice.

Weights (justified below):
  active_rate    0.30  — strongest proxy for genuine intent
  kyc_pass_rate  0.30  — compliance quality; unlocks full monetisation
  email_verify   0.15  — basic engagement signal
  twofa_rate     0.10  — security posture
  (1−suspended)  0.15  — inverted direct risk signal
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from config import PALETTE
from utils import section_header, annotate_hbars

BASE_WEIGHTS = {
    "active_rate":    0.30,
    "kyc_pass_rate":  0.30,
    "email_verify":   0.15,
    "twofa_rate":     0.10,
    "suspended_inv":  0.15,   # 1 − suspended_rate
}


def _compute_score(sc: pd.DataFrame, w: dict) -> pd.Series:
    return (
        sc["active_rate"]   * w["active_rate"]
        + sc["kyc_pass_rate"] * w["kyc_pass_rate"]
        + sc["email_verify"]  * w["email_verify"]
        + sc["twofa_rate"]    * w["twofa_rate"]
        + (1 - sc["suspended_rate"]) * w["suspended_inv"]
    ).round(4)


def run(df, out_dir) -> dict:
    section_header(9, "Channel Composite Health Score")

    scorecard = df.groupby("registration_source").agg(
        active_rate    = ("account_status",    lambda x: (x == "active").mean()),
        kyc_pass_rate  = ("kyc_status",         lambda x: (x == "verified").mean()),
        email_verify   = ("email_verified",     "mean"),
        twofa_rate     = ("two_factor_enabled", "mean"),
        suspended_rate = ("is_suspended",       "mean"),
        volume         = ("user_id",            "count"),
    )

    scorecard["score"] = _compute_score(scorecard, BASE_WEIGHTS)
    scorecard = scorecard.sort_values("score", ascending=False)

    print(scorecard[["volume", "active_rate", "kyc_pass_rate", "suspended_rate", "score"]]
          .round(3).to_string())

    # ── Weight justification: metric-suspension correlation ───────────────────
    # A metric that strongly predicts lower suspension deserves higher weight.
    # We expect negative correlations (lower suspension = better channel = higher metric).
    print("\n  Weight Justification — each metric's correlation with suspended_rate:")
    print("  (Negative correlation = metric identifies safer channels)")
    print(f"  {'Metric':<20}  {'Corr w/ suspended_rate':>24}  {'Current weight':>16}")
    print("  " + "-" * 64)
    for col, weight_key in [
        ("active_rate",   "active_rate"),
        ("kyc_pass_rate", "kyc_pass_rate"),
        ("email_verify",  "email_verify"),
        ("twofa_rate",    "twofa_rate"),
    ]:
        corr = scorecard[col].corr(scorecard["suspended_rate"])
        w    = BASE_WEIGHTS[weight_key]
        print(f"  {col:<20}  {corr:>+24.3f}  {w:>16.2f}")

    # ── Sensitivity analysis ──────────────────────────────────────────────────
    base_ranking = list(scorecard.index)
    print(f"\n  Sensitivity Analysis — vary each weight ±50%, check ranking stability")
    print(f"  Baseline ranking: {base_ranking}")

    instabilities = []
    for metric in BASE_WEIGHTS:
        for direction, delta in [("↑ +50%", 0.5), ("↓ −50%", -0.5)]:
            w_alt = BASE_WEIGHTS.copy()
            w_alt[metric] = w_alt[metric] * (1 + delta)
            total = sum(w_alt.values())
            w_norm = {k: v / total for k, v in w_alt.items()}

            alt_scores  = _compute_score(scorecard, w_norm)
            alt_ranking = list(scorecard.assign(_s=alt_scores).sort_values("_s", ascending=False).index)

            if alt_ranking != base_ranking:
                instabilities.append(f"    {metric} {direction}: {alt_ranking}")

    if not instabilities:
        print("  ✅ Ranking is stable across all ±50% weight perturbations.")
        print("     The choice of exact weights does not change which channels are best/worst.")
    else:
        print("  ⚠ Ranking changes under the following weight variations:")
        for msg in instabilities:
            print(msg)
        print("  → Consider presenting the range of possible rankings to stakeholders.")

    # ── Chart ─────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 4))
    scores_rev = scorecard["score"][::-1]
    ax.barh(scorecard.index[::-1], scores_rev,
            color=[PALETTE[i] for i in range(len(scorecard))])
    ax.set_title("Channel Composite Health Score (max 1.0)", fontsize=13, fontweight="bold")
    ax.set_xlim(0, 1)
    annotate_hbars(ax, list(scores_rev), fmt=".3f", offset=0.01)

    plt.tight_layout()
    plt.savefig(out_dir / "09_channel_scorecard.png")
    plt.close()

    return {"scorecard": scorecard}
