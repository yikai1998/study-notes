"""
Section 6 — Cohort Analysis

Question: Is user quality improving or deteriorating over time?
Are recent cohorts structurally better than older ones?
"""

import numpy as np
import matplotlib.pyplot as plt
from numpy.polynomial.polynomial import polyfit
from config import PALETTE
from utils import section_header


def run(df, out_dir) -> dict:
    section_header(6, "Cohort Quality Trend")

    cohort = df.groupby("reg_year_month").agg(
        users       = ("user_id",            "count"),
        active_rate = ("account_status",     lambda x: (x == "active").mean()),
        kyc_pass    = ("kyc_status",         lambda x: (x == "verified").mean()),
        twofa       = ("two_factor_enabled",  "mean"),
        suspended   = ("account_status",     lambda x: (x == "suspended").mean()),
    ).reset_index()
    cohort["reg_year_month_str"] = cohort["reg_year_month"].astype(str)

    for metric in ["active_rate", "kyc_pass", "twofa"]:
        cohort[f"{metric}_ma3"] = cohort[metric].rolling(3, min_periods=1).mean()

    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    fig.suptitle("Cohort Quality Trend (3-Month Rolling Average)", fontsize=14, fontweight="bold")

    for ax, (col, label) in zip(axes, [
        ("active_rate", "Active Rate"),
        ("kyc_pass",    "KYC Pass Rate"),
        ("twofa",       "2FA Adoption"),
    ]):
        ax.bar(cohort["reg_year_month_str"], cohort[col], alpha=0.4, color=PALETTE[0])
        ax.plot(cohort["reg_year_month_str"], cohort[f"{col}_ma3"],
                color=PALETTE[1], marker="o", linewidth=2, label="3-month rolling mean")
        ax.set_ylabel(label)
        ax.set_ylim(0, 1)
        ax.legend()
        ax.tick_params(axis="x", rotation=45)

    plt.tight_layout()
    plt.savefig(out_dir / "06_cohort_quality.png")
    plt.close()

    x = np.arange(len(cohort))
    trend_active = polyfit(x, cohort["active_rate"], 1)[1]
    trend_kyc    = polyfit(x, cohort["kyc_pass"],    1)[1]
    print(f"  Active rate long-term slope:   {trend_active:+.4f}  {'↑ improving' if trend_active > 0 else '↓ declining'}")
    print(f"  KYC pass rate long-term slope: {trend_kyc:+.4f}  {'↑ improving' if trend_kyc > 0 else '↓ declining'}")

    return {}
