"""
Section 8 — Compliance & Consent Analysis

Question: Are there users missing mandatory consent flags (regulatory risk)?
Does marketing consent correlate with engagement?
"""

import matplotlib.pyplot as plt
import seaborn as sns
from config import PALETTE
from utils import section_header


def run(df, out_dir) -> dict:
    section_header(8, "Compliance & Consent Analysis")

    consent_cols = [
        "consent_terms_accepted", "consent_privacy_policy",
        "consent_marketing_emails", "consent_data_sharing",
    ]
    consent_rates = df[consent_cols].mean().round(3)
    print(f"  Consent rates:\n{consent_rates.to_string()}")

    mkt_vs_active = (
        df.groupby("consent_marketing_emails")["account_status"]
        .value_counts(normalize=True)
        .unstack()
        .fillna(0)
    )
    print(f"\n  Marketing consent vs account status:\n{mkt_vs_active.round(3).to_string()}")

    no_terms = df[~df["consent_terms_accepted"].fillna(False)]
    print(f"\n  Users without accepted terms: {len(no_terms)} ({len(no_terms)/len(df):.1%})")
    if len(no_terms) > 0:
        print(f"  Their account statuses: {no_terms['account_status'].value_counts().to_dict()}")
        print("  ⚠ Compliance risk: mandatory consent missing — consider forced re-consent or account closure")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Compliance & Consent Analysis", fontsize=14, fontweight="bold")

    ax = axes[0]
    consent_rates.plot(kind="bar", ax=ax, color=PALETTE[:4])
    ax.set_title("Consent Acceptance Rates")
    ax.set_ylim(0, 1)
    ax.set_xticklabels([c.replace("consent_", "") for c in consent_cols], rotation=20)
    for p in ax.patches:
        ax.annotate(f"{p.get_height():.1%}",
                    (p.get_x() + p.get_width() / 2, p.get_height() + 0.01), ha="center")

    ax = axes[1]
    mkt_vs_active.plot(kind="bar", ax=ax, stacked=True,
                       color=sns.color_palette("Set2", len(mkt_vs_active.columns)))
    ax.set_title("Marketing Consent vs Account Status")
    ax.set_xlabel("consent_marketing_emails")
    ax.legend(title="Account Status", bbox_to_anchor=(1.05, 1))
    ax.tick_params(axis="x", rotation=0)

    plt.tight_layout()
    plt.savefig(out_dir / "08_consent_analysis.png")
    plt.close()

    return {"no_terms": no_terms}
