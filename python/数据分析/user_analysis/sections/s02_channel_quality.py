"""
Section 2 — Channel Quality Comparison

Question: Which acquisition channel produces the most valuable users?

Statistical additions:
  - Chi-square test: are channel differences statistically significant?
  - Wilson 95% CI error bars: distinguish real signal from small-sample noise.
"""

import numpy as np
import matplotlib.pyplot as plt
from config import PALETTE
from utils import section_header, chi2_test, add_ci_errorbars


def run(df, out_dir) -> dict:
    section_header(2, "Channel Quality Comparison")

    channel = df.groupby("registration_source").agg(
        count          = ("user_id",            "count"),
        active_rate    = ("account_status",     lambda x: (x == "active").mean()),
        kyc_pass_rate  = ("kyc_status",         lambda x: (x == "verified").mean()),
        kyc_fail_rate  = ("kyc_status",         lambda x: (x == "failed").mean()),
        twofa_rate     = ("two_factor_enabled",  "mean"),
        email_verify   = ("email_verified",      "mean"),
        suspended_rate = ("account_status",     lambda x: (x == "suspended").mean()),
    ).sort_values("count", ascending=False)

    print(channel.round(3).to_string())

    # ── Statistical significance ──────────────────────────────────────────────
    print("\n  Chi-square tests (are channel differences statistically significant?)")
    for col, target_val, label in [
        ("account_status", "suspended", "suspension rate"),
        ("kyc_status",     "verified",  "KYC pass rate"),
        ("account_status", "active",    "active rate"),
    ]:
        tmp = df.copy()
        tmp["_target"] = (tmp[col] == target_val).astype(int)
        res = chi2_test(tmp, "registration_source", "_target")
        sig = "✅ significant" if res["significant"] else "⚠ not significant"
        print(f"  {label:<22}  χ²={res['chi2']:.1f}  p={res['p']:.4f}  "
              f"Cramér's V={res['cramers_v']:.3f}  → {sig}")

    # ── Chart with CI error bars ──────────────────────────────────────────────
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Channel Quality Comparison (bars = point estimate, whiskers = 95% CI)",
                 fontsize=13, fontweight="bold")

    metrics = [
        ("active_rate",    "Active Rate"),
        ("kyc_pass_rate",  "KYC Pass Rate"),
        ("suspended_rate", "Suspension Rate"),
    ]
    for ax, (col, label) in zip(axes, metrics):
        x = np.arange(len(channel))
        bars = ax.bar(x, channel[col], color=[PALETTE[i] for i in range(len(channel))])
        ax.set_title(label)
        ax.set_ylim(0, min(1.0, channel[col].max() * 1.35))
        ax.set_xticks(x)
        ax.set_xticklabels(channel.index, rotation=20, ha="right")

        # Value labels
        for bar, val in zip(bars, channel[col]):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                    f"{val:.1%}", ha="center", fontsize=9)

        # 95% Wilson CI error bars
        add_ci_errorbars(ax, x, channel[col].values, channel["count"].values)

    plt.tight_layout()
    plt.savefig(out_dir / "02_channel_quality.png")
    plt.close()

    best_ch  = channel["active_rate"].idxmax()
    worst_ch = channel["suspended_rate"].idxmax()
    print(f"\n  Highest active-rate channel:    {best_ch} ({channel.loc[best_ch, 'active_rate']:.1%})")
    print(f"  Highest suspension-rate channel: {worst_ch} ({channel.loc[worst_ch, 'suspended_rate']:.1%})")

    return {"channel": channel}
