"""
Section 10 — Actionable Recommendations

Synthesises findings from all previous sections into prioritised actions.
Requires context dict produced by earlier sections.
"""

from utils import section_header


def run(df, out_dir,
        corr_qty_quality=None,
        scorecard=None,
        verified_df=None,
        ip_counts=None,
        no_terms=None,
        **_) -> dict:
    section_header(10, "Actionable Recommendations")

    best_channel  = scorecard.index[0]  if scorecard  is not None else "N/A"
    worst_channel = scorecard.index[-1] if scorecard  is not None else "N/A"
    kyc_median    = verified_df["kyc_days"].median() if verified_df is not None else float("nan")
    corr_str      = f"{corr_qty_quality:+.2f}" if corr_qty_quality is not None else "N/A"

    multi_ip_users = (
        df[df["ip_address"].isin(ip_counts[ip_counts > 1].index)]
        if ip_counts is not None else df.iloc[0:0]
    )
    no_terms_users = no_terms if no_terms is not None else df[~df["consent_terms_accepted"].fillna(False)]

    kyc_not_started_active = df[
        (df["kyc_status"] == "not_started") & (df["account_status"] == "active")
    ]
    risky_users = df[
        (df["email_verified"] == False)
        & (df["account_status"] == "active")
        & (df["kyc_status"].isin(["not_started", "pending"]))
    ]

    print(f"""
┌─────────────────────────────────────────────────────────────────┐
│               Key Findings & Recommended Actions                │
├─────────────────────────────────────────────────────────────────┤
│ [GROWTH QUALITY]                                                 │
│   • Top-scored channel:    {best_channel:<12} → prioritise budget    │
│   • Bottom-scored channel: {worst_channel:<12} → audit traffic source │
│   • Volume vs active-rate correlation: {corr_str}               │
│     → Set quality gates when running promotions                 │
│                                                                 │
│ [KYC OPTIMISATION]                                              │
│   • KYC-not-started active users: {len(kyc_not_started_active):,}              │
│     → High-value re-engagement: push/email to complete KYC      │
│   • Median KYC review time: {kyc_median:.0f} days                       │
│     → If > 3 days, investigate manual-review bottlenecks        │
│                                                                 │
│ [RISK CONTROLS]                                                 │
│   • High-risk users (unverified email + incomplete KYC): {len(risky_users):,}  │
│     → Restrict withdrawals/trades until verification complete   │
│   • Shared-IP registration accounts: {len(multi_ip_users):,}               │
│     → Integrate device fingerprinting at registration           │
│                                                                 │
│ [COMPLIANCE]                                                    │
│   • Users without accepted terms: {len(no_terms_users):,}                  │
│     → Regulatory risk: force re-consent or deactivate accounts  │
│                                                                 │
│ [SECURITY]                                                      │
│   • Overall 2FA adoption: {df["two_factor_enabled"].mean():.0%}                      │
│     → Mandate 2FA for high-value / high-activity accounts       │
└─────────────────────────────────────────────────────────────────┘
""")

    return {}
