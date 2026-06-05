"""
Section 7 — Registration Timing & Suspicious Behaviour

Question: Do off-hours registrations signal lower-quality or automated traffic?
Are there signs of bulk / bot registration via shared IPs?
"""

import matplotlib.pyplot as plt
from config import PALETTE
from utils import section_header


def run(df, out_dir) -> dict:
    section_header(7, "Registration Timing & Suspicious Behaviour")

    hour_stats = df.groupby("reg_hour").agg(
        count          = ("user_id",     "count"),
        suspended_rate = ("is_suspended", "mean"),
        kyc_pass_rate  = ("kyc_status",  lambda x: (x == "verified").mean()),
    ).reset_index()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Registration Timing Analysis", fontsize=14, fontweight="bold")

    ax = axes[0]
    ax.bar(hour_stats["reg_hour"], hour_stats["count"], color=PALETTE[0], alpha=0.7)
    ax.set_title("Registration Volume by Hour (UTC)")
    ax.set_xlabel("Hour (UTC)")

    ax = axes[1]
    ax.plot(hour_stats["reg_hour"], hour_stats["suspended_rate"],
            marker="o", color=PALETTE[3], label="Suspension Rate")
    ax.plot(hour_stats["reg_hour"], hour_stats["kyc_pass_rate"],
            marker="s", color=PALETTE[2], label="KYC Pass Rate")
    ax.set_title("User Quality by Registration Hour")
    ax.set_xlabel("Hour (UTC)")
    ax.set_ylim(0, 1)
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_dir / "07_hourly_pattern.png")
    plt.close()

    high_risk_hours = hour_stats[
        hour_stats["suspended_rate"] > hour_stats["suspended_rate"].quantile(0.75)
    ]
    print(f"  High-suspension hours (UTC): {list(high_risk_hours['reg_hour'])}")

    # Shared-IP detection (simple bulk-registration signal)
    ip_counts = df["ip_address"].value_counts()
    multi_ip  = ip_counts[ip_counts > 1]
    print(f"\n  IPs used by more than one account: {len(multi_ip)}")
    if len(multi_ip) > 0:
        print(f"  Max registrations from a single IP: {multi_ip.max()} (IP: {multi_ip.idxmax()})")
        suspect_users = df[df["ip_address"].isin(multi_ip.index)]
        print(f"  Suspension rate — shared-IP users: {suspect_users['is_suspended'].mean():.1%}"
              f"  vs all users: {df['is_suspended'].mean():.1%}")

    return {"ip_counts": ip_counts}
