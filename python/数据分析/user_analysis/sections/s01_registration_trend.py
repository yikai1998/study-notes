"""
Section 1 — Registration Trend: Volume vs Quality

Question: As registration volume grows, does user quality keep pace?

Statistical addition: Mann-Whitney U test to verify that high-volume months
genuinely have lower quality — not just random noise.
"""

import matplotlib.pyplot as plt
from config import PALETTE
from utils import section_header, mann_whitney_test


def run(df, out_dir) -> dict:
    section_header(1, "Registration Trend: Volume vs Quality")

    monthly = df.groupby("reg_year_month").agg(
        total         = ("user_id",            "count"),
        active_rate   = ("account_status",     lambda x: (x == "active").mean()),
        kyc_pass_rate = ("kyc_status",         lambda x: (x == "verified").mean()),
        twofa_rate    = ("two_factor_enabled",  "mean"),
    ).reset_index()
    monthly["reg_year_month_str"] = monthly["reg_year_month"].astype(str)

    # ── Chart ─────────────────────────────────────────────────────────────────
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

    # ── Descriptive stats ─────────────────────────────────────────────────────
    low_q = monthly[monthly["active_rate"] < monthly["active_rate"].quantile(0.25)]
    print(f"  Low-quality months (bottom 25% active rate): {list(low_q['reg_year_month_str'])}")
    corr = monthly["total"].corr(monthly["active_rate"])
    print(f"  Volume vs active-rate Pearson correlation: {corr:.3f}")

    # ── Statistical test: does high volume actually mean lower quality? ───────
    # Split months at the median volume into "high" and "low" groups, then test
    # whether their active_rate distributions differ significantly.
    median_vol = monthly["total"].median()
    high_vol = monthly[monthly["total"] >= median_vol]["active_rate"]
    low_vol  = monthly[monthly["total"] <  median_vol]["active_rate"]

    mw = mann_whitney_test(high_vol, low_vol, "high-volume months", "low-volume months")
    print(f"\n  Mann-Whitney U test (active rate: high-vol vs low-vol months):")
    print(f"    Median active rate — high-volume: {mw['median_a']:.3f}  |  low-volume: {mw['median_b']:.3f}")
    print(f"    U={mw['U']:.1f}, p={mw['p']:.4f}", end="  ")
    if mw["significant"]:
        direction = "lower" if mw["median_a"] < mw["median_b"] else "higher"
        print(f"→ ✅ Significant: high-volume months have {direction} user quality (p<0.05)")
    else:
        print(f"→ ⚪ Not significant: quality difference could be random noise (p≥0.05)")

    return {"corr_qty_quality": corr}
