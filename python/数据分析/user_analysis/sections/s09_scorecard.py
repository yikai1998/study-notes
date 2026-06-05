"""
Section 9 — Channel Composite Health Score

Combines five quality signals into a single weighted score per channel,
enabling direct channel-to-channel comparison for budget allocation decisions.

Weights:
  active_rate    0.30  — proxy for genuine intent / long-term retention
  kyc_pass_rate  0.30  — compliance quality, directly monetisable
  email_verify   0.15  — basic engagement signal
  twofa_rate     0.10  — security posture indicator
  (1−suspended)  0.15  — inverse risk signal
"""

import matplotlib.pyplot as plt
from config import PALETTE
from utils import section_header, annotate_hbars


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

    scorecard["score"] = (
        scorecard["active_rate"]   * 0.30
        + scorecard["kyc_pass_rate"] * 0.30
        + scorecard["email_verify"]  * 0.15
        + scorecard["twofa_rate"]    * 0.10
        + (1 - scorecard["suspended_rate"]) * 0.15
    ).round(3)

    scorecard = scorecard.sort_values("score", ascending=False)
    print(scorecard[["volume", "active_rate", "kyc_pass_rate", "suspended_rate", "score"]]
          .round(3).to_string())

    fig, ax = plt.subplots(figsize=(8, 4))
    scores_rev = scorecard["score"][::-1]
    bars = ax.barh(scorecard.index[::-1], scores_rev,
                   color=[PALETTE[i] for i in range(len(scorecard))])
    ax.set_title("Channel Composite Health Score (max 1.0)", fontsize=13, fontweight="bold")
    ax.set_xlim(0, 1)
    annotate_hbars(ax, list(scores_rev), fmt=".3f", offset=0.01)

    plt.tight_layout()
    plt.savefig(out_dir / "09_channel_scorecard.png")
    plt.close()

    return {"scorecard": scorecard}
