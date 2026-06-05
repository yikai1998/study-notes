"""
Section 1 — Registration Trend: Volume vs Quality

Question: As registration volume grows, does user quality keep pace?
"""

import matplotlib.pyplot as plt
from config import PALETTE
from utils import section_header


def run(df, out_dir) -> dict:
    section_header(1, "Registration Trend: Volume vs Quality")

    monthly = df.groupby("reg_year_month").agg(
        total         = ("user_id",            "count"),
        active_rate   = ("account_status",     lambda x: (x == "active").mean()),
        kyc_pass_rate = ("kyc_status",         lambda x: (x == "verified").mean()),
        twofa_rate    = ("two_factor_enabled",  "mean"),
    ).reset_index()
    monthly["reg_year_month_str"] = monthly["reg_year_month"].astype(str)

    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    fig.suptitle("Registration Trend: Volume vs Quality", fontsize=14, fontweight="bold")

    ax = axes[0, 0]
    ax.bar(monthly["reg_year_month_str"], monthly["total"], color=PALETTE[0])
    ax.set_title("Monthly Registrations")
    ax.tick_params(axis="x", rotation=45)

    ax = axes[0, 1]
    ax.plot(monthly["reg_year_month_str"], monthly["active_rate"], marker="o", color=PALETTE[1])
    ax.set_title("Active Account Rate (Monthly)")
    ax.set_ylim(0, 1)
    ax.axhline(monthly["active_rate"].mean(), ls="--", color="gray", lw=1,
               label=f"Mean {monthly['active_rate'].mean():.1%}")
    ax.legend()
    ax.tick_params(axis="x", rotation=45)

    ax = axes[1, 0]
    ax.plot(monthly["reg_year_month_str"], monthly["kyc_pass_rate"], marker="s", color=PALETTE[2])
    ax.set_title("KYC Pass Rate (Monthly)")
    ax.set_ylim(0, 1)
    ax.axhline(monthly["kyc_pass_rate"].mean(), ls="--", color="gray", lw=1)
    ax.tick_params(axis="x", rotation=45)

    ax = axes[1, 1]
    ax.plot(monthly["reg_year_month_str"], monthly["twofa_rate"], marker="^", color=PALETTE[3])
    ax.set_title("2FA Adoption Rate (Monthly)")
    ax.set_ylim(0, 1)
    ax.tick_params(axis="x", rotation=45)

    plt.tight_layout()
    plt.savefig(out_dir / "01_registration_trend.png")
    plt.close()

    low_q = monthly[monthly["active_rate"] < monthly["active_rate"].quantile(0.25)]
    print(f"  Low-quality months (bottom 25% active rate): {list(low_q['reg_year_month_str'])}")
    corr = monthly["total"].corr(monthly["active_rate"])
    print(f"  Volume vs active-rate correlation: {corr:.3f}")
    if corr < -0.2:
        print("  ⚠ Negative correlation: high-volume months tend to have lower user quality")

    return {"corr_qty_quality": corr}
