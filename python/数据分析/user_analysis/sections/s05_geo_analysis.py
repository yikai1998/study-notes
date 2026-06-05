"""
Section 5 — Geographic Distribution: Market Priority & Risk

Question: Which markets deserve investment? Which carry disproportionate risk?
"""

import matplotlib.pyplot as plt
from config import PALETTE
from utils import section_header


def run(df, out_dir) -> dict:
    section_header(5, "Geographic Distribution: Market Priority & Risk")

    geo = df.groupby("country").agg(
        users          = ("user_id",            "count"),
        active_rate    = ("account_status",     lambda x: (x == "active").mean()),
        kyc_pass_rate  = ("kyc_status",         lambda x: (x == "verified").mean()),
        suspended_rate = ("account_status",     lambda x: (x == "suspended").mean()),
        twofa_rate     = ("two_factor_enabled",  "mean"),
    ).sort_values("users", ascending=False)

    top10 = geo.head(10)
    print(top10.round(3).to_string())

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Geographic Distribution: Scale & Quality", fontsize=14, fontweight="bold")

    ax = axes[0]
    ax.barh(top10.index[::-1], top10["users"][::-1], color=PALETTE[0])
    ax.set_title("Top 10 Countries by Registration Volume")

    ax = axes[1]
    scatter = ax.scatter(
        top10["users"], top10["active_rate"],
        s=top10["kyc_pass_rate"] * 500,
        c=top10["suspended_rate"],
        cmap="RdYlGn_r", alpha=0.8, vmin=0, vmax=0.3,
    )
    plt.colorbar(scatter, ax=ax, label="Suspension Rate")
    for country, row in top10.iterrows():
        ax.annotate(country, (row["users"], row["active_rate"]),
                    textcoords="offset points", xytext=(5, 3), fontsize=8)
    ax.set_xlabel("Registered Users")
    ax.set_ylabel("Active Rate")
    ax.set_title("Bubble size = KYC pass rate  |  Color = suspension rate")

    plt.tight_layout()
    plt.savefig(out_dir / "05_geo_analysis.png")
    plt.close()

    high_risk = (
        geo[(geo["suspended_rate"] > geo["suspended_rate"].quantile(0.75)) & (geo["users"] >= 20)]
        .sort_values("suspended_rate", ascending=False)
    )
    print(f"\n  High-risk markets (suspension rate top 25%, sample ≥ 20):")
    print(high_risk[["users", "suspended_rate", "kyc_pass_rate"]].round(3).to_string())

    return {}
