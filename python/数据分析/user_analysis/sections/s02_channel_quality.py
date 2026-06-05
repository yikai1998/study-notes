"""
Section 2 — Channel Quality Comparison

Question: Which acquisition channel produces the most valuable users?
Which channels have structural quality problems?
"""

import matplotlib.pyplot as plt
from config import PALETTE
from utils import section_header, annotate_bars


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

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Channel Quality Comparison", fontsize=14, fontweight="bold")

    metrics = [
        ("active_rate",    "Active Rate"),
        ("kyc_pass_rate",  "KYC Pass Rate"),
        ("suspended_rate", "Suspension Rate"),
    ]
    for ax, (col, label) in zip(axes, metrics):
        bars = ax.bar(channel.index, channel[col],
                      color=[PALETTE[i] for i in range(len(channel))])
        ax.set_title(label)
        ax.set_ylim(0, 1)
        annotate_bars(ax, fmt=".1%", offset=0.01)
        ax.tick_params(axis="x", rotation=20)

    plt.tight_layout()
    plt.savefig(out_dir / "02_channel_quality.png")
    plt.close()

    best_ch  = channel["active_rate"].idxmax()
    worst_ch = channel["suspended_rate"].idxmax()
    print(f"  Highest active-rate channel:    {best_ch} ({channel.loc[best_ch, 'active_rate']:.1%})")
    print(f"  Highest suspension-rate channel: {worst_ch} ({channel.loc[worst_ch, 'suspended_rate']:.1%})")

    return {"channel": channel}
