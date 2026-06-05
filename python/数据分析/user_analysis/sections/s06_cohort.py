"""
Section 6 — Cohort Analysis

Question: Is user quality improving over time?
Do older cohorts show signs of long-term decay?

Addition: Cohort survival proxy — plots active rate vs cohort age in months.
This is a cross-sectional approximation of a retention curve: if the slope is
negative, older cohorts are less active, suggesting ongoing churn.

Caveat: This is NOT a true longitudinal retention curve — we only have a single
point-in-time snapshot of account_status, not a historical activity log. Newer
cohorts will appear healthier partly because they haven't had time to churn.
Interpret the slope as an upper-bound estimate of retention decay.
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

    # ── Chart 1: quality trend with rolling average ───────────────────────────
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

    # ── Linear trend direction ────────────────────────────────────────────────
    x = np.arange(len(cohort))
    trend_active = polyfit(x, cohort["active_rate"], 1)[1]
    trend_kyc    = polyfit(x, cohort["kyc_pass"],    1)[1]
    print(f"  Active rate long-term slope:   {trend_active:+.4f}  {'↑ improving' if trend_active > 0 else '↓ declining'}")
    print(f"  KYC pass rate long-term slope: {trend_kyc:+.4f}  {'↑ improving' if trend_kyc > 0 else '↓ declining'}")

    # ── Chart 2: cohort survival proxy ────────────────────────────────────────
    # Compute each cohort's age in months relative to the last registration date
    ref_date = df["registration_date"].max().tz_localize(None)
    cohort["cohort_start"]      = cohort["reg_year_month"].dt.to_timestamp()
    cohort["cohort_age_months"] = ((ref_date - cohort["cohort_start"]).dt.days / 30).round(1)

    fig, ax = plt.subplots(figsize=(10, 5))

    scatter = ax.scatter(
        cohort["cohort_age_months"], cohort["active_rate"],
        s=cohort["users"] * 0.3 + 30,
        color=PALETTE[0], alpha=0.75, edgecolors="white", linewidth=0.5,
        label="Cohort (size ∝ user count)",
    )

    # OLS trendline
    z    = np.polyfit(cohort["cohort_age_months"], cohort["active_rate"], 1)
    p_fn = np.poly1d(z)
    x_ln = np.linspace(cohort["cohort_age_months"].min(), cohort["cohort_age_months"].max(), 200)
    ax.plot(x_ln, p_fn(x_ln), color=PALETTE[3], ls="--", lw=2,
            label=f"OLS trend  (slope = {z[0]:+.4f} / month)")

    ax.set_xlabel("Cohort Age (months since first registration in that cohort)")
    ax.set_ylabel("Current Active Rate")
    ax.set_ylim(0, 1)
    ax.set_title(
        "Cohort Survival Proxy: Active Rate vs Cohort Age\n"
        "⚠ Cross-sectional snapshot — newer cohorts haven't had time to churn yet",
        fontsize=11,
    )
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_dir / "06b_cohort_survival.png")
    plt.close()

    # Interpretation
    if z[0] < -0.002:
        print(f"\n  Survival proxy slope: {z[0]:+.4f} / month")
        print("  → Negative slope: older cohorts have lower active rates, "
              "suggesting ongoing churn. True retention curve recommended "
              "once longitudinal activity data is available.")
    elif z[0] > 0.002:
        print(f"\n  Survival proxy slope: {z[0]:+.4f} / month")
        print("  → Positive slope: older cohorts appear more active — "
              "may reflect early period low-quality batches being cleaned up.")
    else:
        print(f"\n  Survival proxy slope: {z[0]:+.4f} / month (near-flat)")
        print("  → No strong cohort age effect detected.")

    return {}
