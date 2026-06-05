"""
Section 10 — Actionable Recommendations

Synthesises all findings into prioritised actions with quantified expected impact.
Each recommendation includes: what to do, how many users are affected, and
what measurable outcome to track.
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

    # ── Derived counts ────────────────────────────────────────────────────────
    best_channel   = scorecard.index[0]  if scorecard  is not None else "N/A"
    worst_channel  = scorecard.index[-1] if scorecard  is not None else "N/A"
    best_score     = scorecard["score"].iloc[0]  if scorecard is not None else float("nan")
    worst_score    = scorecard["score"].iloc[-1] if scorecard is not None else float("nan")
    kyc_median     = verified_df["kyc_days"].median() if verified_df is not None else float("nan")
    corr_str       = f"{corr_qty_quality:+.2f}" if corr_qty_quality is not None else "N/A"

    multi_ip_users = (
        df[df["ip_address"].isin(ip_counts[ip_counts > 1].index)]
        if ip_counts is not None else df.iloc[0:0]
    )
    no_terms_users = (
        no_terms if no_terms is not None
        else df[~df["consent_terms_accepted"].fillna(False)]
    )
    kyc_not_started_active = df[
        (df["kyc_status"] == "not_started") & (df["account_status"] == "active")
    ]
    risky_users = df[
        (df["email_verified"] == False)
        & (df["account_status"] == "active")
        & (df["kyc_status"].isin(["not_started", "pending"]))
    ]

    # ── Expected impact estimates ─────────────────────────────────────────────
    # These are conservative estimates. Adjust conversion assumptions to match
    # your actual product benchmarks.
    KYC_REACTIVATION_RATE = 0.15   # assume 15% of re-engaged users complete KYC
    kyc_lift = int(len(kyc_not_started_active) * KYC_REACTIVATION_RATE)

    total = len(df)
    worst_ch_users = int(scorecard.loc[worst_channel, "volume"]) if scorecard is not None else 0
    budget_realloc_note = (
        f"{worst_ch_users:,} users came from {worst_channel} (score {worst_score:.3f}) "
        f"vs {best_channel} (score {best_score:.3f}). "
        f"Shifting 20% of {worst_channel} budget to {best_channel} "
        f"could improve overall quality score by ~{(best_score - worst_score) * 0.20:.3f} pts."
    )

    print(f"""
┌──────────────────────────────────────────────────────────────────────┐
│              Key Findings & Recommended Actions                      │
├──────────────────────────────────────────────────────────────────────┤
│ [GROWTH QUALITY]                                                      │
│   Finding: Volume vs quality correlation = {corr_str:<6}                  │
│   Action:  Instrument quality gates (min KYC pass rate, max          │
│            suspension rate) before launching any volume campaigns.   │
│   Impact:  {budget_realloc_note[:65]:<65}│
│            {budget_realloc_note[65:130]:<65}│
│                                                                      │
│ [KYC OPTIMISATION]                                                   │
│   Finding: {len(kyc_not_started_active):,} active users have never attempted KYC.             │
│   Action:  Push/email re-engagement campaign targeting these users.  │
│   Impact:  At 15% conversion → +{kyc_lift:,} newly verified users.           │
│            Median review time: {kyc_median:.0f} days. If >3 days, investigate    │
│            manual-review SLA — faster review improves completion.   │
│                                                                      │
│ [RISK CONTROLS]                                                      │
│   Finding: {len(risky_users):,} active users: unverified email + incomplete KYC.   │
│   Action:  Apply transaction/withdrawal limits until they verify.    │
│   Impact:  Pre-empts fraud risk before suspension occurs. Measure    │
│            30-day suspension rate drop as success metric.            │
│                                                                      │
│   Finding: {len(multi_ip_users):,} accounts share an IP with at least one other.      │
│   Action:  Add IP-velocity check at registration (max N accounts     │
│            per IP per 24h). Integrate device fingerprinting.         │
│   Impact:  Direct reduction in bulk-registration fraud.              │
│                                                                      │
│ [COMPLIANCE]                                                         │
│   Finding: {len(no_terms_users):,} accounts have no accepted Terms of Service.        │
│   Action:  Force re-consent flow on next login; deactivate after     │
│            30-day grace period if not completed.                     │
│   Impact:  Closes direct GDPR/PDPA regulatory exposure.             │
│            Track: % of no-terms accounts resolved within 30 days.   │
│                                                                      │
│ [SECURITY]                                                           │
│   Finding: Overall 2FA adoption = {df["two_factor_enabled"].mean():.0%}.                      │
│   Action:  Mandate 2FA for accounts with transaction > $X / day or  │
│            KYC-verified status (highest-value segment).              │
│   Impact:  Reduced account takeover rate. Baseline: {df["two_factor_enabled"].mean():.0%} → target  │
│            ≥60% adoption within 90 days of rollout.                 │
└──────────────────────────────────────────────────────────────────────┘

  Prioritisation by effort × impact:
  ┌─────────────────────────────────┬──────────┬─────────┐
  │ Action                          │ Effort   │ Impact  │
  ├─────────────────────────────────┼──────────┼─────────┤
  │ KYC re-engagement campaign      │ Low      │ High    │
  │ Transaction limits (risky users)│ Low      │ High    │
  │ No-terms re-consent flow        │ Medium   │ High    │
  │ Budget reallocation (channels)  │ Low      │ Medium  │
  │ IP-velocity check               │ Medium   │ Medium  │
  │ 2FA mandate (high-value)        │ Medium   │ Medium  │
  └─────────────────────────────────┴──────────┴─────────┘
""")

    return {}
