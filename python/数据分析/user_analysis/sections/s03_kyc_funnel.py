"""
Section 3 — KYC Funnel Deep Dive

Question: Where do users drop off in the KYC process?
Does review turnaround time affect outcomes?
"""

import matplotlib.pyplot as plt
from config import PALETTE
from utils import section_header, annotate_bars


def run(df, out_dir) -> dict:
    section_header(3, "KYC Funnel Analysis")

    kyc_dist = df["kyc_status"].value_counts()
    print(f"  KYC status distribution:\n{kyc_dist.to_string()}")

    verified_df = df[df["kyc_status"] == "verified"].copy()
    print(f"\n  KYC processing time (days) — verified users only:")
    print(verified_df["kyc_days"].describe().round(1).to_string())

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("KYC Funnel Analysis", fontsize=14, fontweight="bold")

    # Funnel (horizontal bars)
    ax = axes[0]
    funnel_labels = ["Registered", "KYC Started\n(non not_started)", "KYC Verified"]
    funnel_vals = [
        len(df),
        len(df[df["kyc_status"] != "not_started"]),
        len(df[df["kyc_status"] == "verified"]),
    ]
    ax.barh(funnel_labels[::-1], funnel_vals[::-1],
            color=[PALETTE[0], PALETTE[1], PALETTE[2]])
    for i, (val, label) in enumerate(zip(funnel_vals[::-1], funnel_labels[::-1])):
        ax.text(val + 10, i, f"{val:,} ({val/funnel_vals[0]:.1%})", va="center")
    ax.set_title("KYC Conversion Funnel")
    ax.set_xlim(0, funnel_vals[0] * 1.3)

    # Processing-time histogram
    ax = axes[1]
    ax.hist(verified_df["kyc_days"].dropna(), bins=20, color=PALETTE[2], edgecolor="white")
    ax.set_title("KYC Processing Time Distribution (days)")
    ax.set_xlabel("Days")
    median_days = verified_df["kyc_days"].median()
    ax.axvline(median_days, color="red", ls="--",
               label=f"Median {median_days:.0f}d")
    ax.legend()

    # KYC failure rate by channel
    ax = axes[2]
    ch_fail = (
        df.groupby("registration_source")["kyc_status"]
        .apply(lambda x: (x == "failed").mean())
        .sort_values(ascending=False)
    )
    bars = ax.bar(ch_fail.index, ch_fail.values,
                  color=[PALETTE[i] for i in range(len(ch_fail))])
    for bar, val in zip(bars, ch_fail.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.002,
                f"{val:.1%}", ha="center", fontsize=9)
    ax.set_title("KYC Failure Rate by Channel")
    ax.tick_params(axis="x", rotation=20)

    plt.tight_layout()
    plt.savefig(out_dir / "03_kyc_funnel.png")
    plt.close()

    ns = df[df["kyc_status"] == "not_started"]["account_status"].value_counts(normalize=True)
    print(f"\n  Account status for KYC-not-started users:\n{ns.round(3).to_string()}")
    print("  → KYC-not-started + active accounts = high-value re-engagement targets")

    return {"verified_df": verified_df}
