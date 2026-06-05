"""
Section 4 — Account Health: Suspension Profile

Question: What registration-time signals predict future account suspension?
"""

import matplotlib.pyplot as plt
import seaborn as sns
from config import PALETTE
from utils import section_header


def run(df, out_dir) -> dict:
    section_header(4, "Account Health: Suspension Profile")

    print("\n  Suspension rate by dimension:")
    for col in ["registration_source", "kyc_status", "email_verified",
                "two_factor_enabled", "consent_marketing_emails"]:
        rates = df.groupby(col)["is_suspended"].mean().round(3)
        print(f"\n  [{col}]\n{rates.to_string()}")

    combo = df.groupby(["kyc_status", "email_verified"])["is_suspended"].mean().unstack()
    print(f"\n  KYC status × email verified → suspension rate:\n{combo.round(3).to_string()}")

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Suspended Account Profile", fontsize=14, fontweight="bold")

    ax = axes[0]
    sns.heatmap(combo, annot=True, fmt=".1%", cmap="Reds", ax=ax,
                linewidths=0.5, cbar_kws={"label": "Suspension Rate"})
    ax.set_title("KYC × Email Verified → Suspension Rate")

    ax = axes[1]
    susp_ch = df.groupby("registration_source").agg(
        suspended_pct = ("is_suspended",  "mean"),
        kyc_fail_pct  = ("kyc_status",    lambda x: (x == "failed").mean()),
    ).reset_index()
    colors = [PALETTE[i] for i in range(len(susp_ch))]
    ax.scatter(susp_ch["kyc_fail_pct"], susp_ch["suspended_pct"], s=150, color=colors)
    for _, row in susp_ch.iterrows():
        ax.annotate(row["registration_source"],
                    (row["kyc_fail_pct"], row["suspended_pct"]),
                    textcoords="offset points", xytext=(6, 4), fontsize=9)
    ax.set_xlabel("KYC Failure Rate")
    ax.set_ylabel("Suspension Rate")
    ax.set_title("Channel: KYC Failure Rate vs Suspension Rate")

    plt.tight_layout()
    plt.savefig(out_dir / "04_suspension_profile.png")
    plt.close()

    return {}
