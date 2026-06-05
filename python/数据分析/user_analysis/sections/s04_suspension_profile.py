"""
Section 4 — Account Health: Suspension Profile

Question: What registration-time signals predict future account suspension?

Multivariate addition: Logistic regression with statsmodels to find which
factors independently predict suspension after controlling for the others.
Outputs odds ratios with 95% CIs and ROC-AUC.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from config import PALETTE
from utils import section_header


def _build_feature_matrix(df: pd.DataFrame):
    """Encode features for logistic regression. Returns (X, y, feature_names)."""
    feat = pd.DataFrame(index=df.index)

    # Boolean features (fill NA → False)
    for col in ["email_verified", "two_factor_enabled", "consent_marketing_emails"]:
        feat[col] = df[col].fillna(False).astype(int)

    # Normalised hour
    feat["reg_hour_norm"] = (df["reg_hour"] - df["reg_hour"].mean()) / df["reg_hour"].std()

    # One-hot: registration_source (drop first as reference)
    src_dummies = pd.get_dummies(df["registration_source"], prefix="src", drop_first=True)
    feat = pd.concat([feat, src_dummies.astype(int)], axis=1)

    # One-hot: kyc_status (drop first as reference)
    kyc_dummies = pd.get_dummies(df["kyc_status"], prefix="kyc", drop_first=True)
    feat = pd.concat([feat, kyc_dummies.astype(int)], axis=1)

    # Drop any row with NaN remaining
    mask = feat.notna().all(axis=1)
    X = feat[mask].astype(float)
    y = df.loc[mask, "is_suspended"]
    return X, y


def _run_logistic_regression(X, y, out_dir):
    """Fit statsmodels Logit and plot odds ratio forest chart."""
    try:
        import statsmodels.api as sm
        from sklearn.metrics import roc_auc_score
    except ImportError:
        print("  ⚠ statsmodels / scikit-learn not installed — skipping logistic regression")
        return

    # Class imbalance warning
    suspension_rate = y.mean()
    if suspension_rate < 0.02 or suspension_rate > 0.98:
        print(f"  ⚠ Extreme class imbalance ({suspension_rate:.1%} suspended) — "
              "interpret coefficients with caution")

    Xc = sm.add_constant(X)
    try:
        model = sm.Logit(y, Xc).fit(disp=False, maxiter=200)
    except Exception as e:
        print(f"  ⚠ Model failed to converge: {e}")
        return

    # ── Summary table ─────────────────────────────────────────────────────────
    params  = model.params.drop("const")
    pvalues = model.pvalues.drop("const")
    ci      = model.conf_int().drop("const")
    odds    = np.exp(params)
    ci_odds = np.exp(ci)

    summary = pd.DataFrame({
        "OddsRatio": odds,
        "CI_lower":  ci_odds[0],
        "CI_upper":  ci_odds[1],
        "p_value":   pvalues,
    }).sort_values("OddsRatio", ascending=False)

    print("\n  Logistic Regression — Odds Ratios (predicting suspension):")
    print("  OR > 1 = increases suspension risk  |  OR < 1 = reduces risk")
    print(f"  {'Feature':<30} {'OR':>6}  {'95% CI':>16}  {'p':>8}  {'sig':>5}")
    print("  " + "-" * 70)
    for feat, row in summary.iterrows():
        sig = "***" if row.p_value < 0.001 else ("**" if row.p_value < 0.01
              else ("*" if row.p_value < 0.05 else ""))
        print(f"  {feat:<30} {row.OddsRatio:>6.3f}  "
              f"[{row.CI_lower:.3f}, {row.CI_upper:.3f}]  {row.p_value:>8.4f}  {sig:>5}")

    # ROC-AUC
    y_pred = model.predict(Xc)
    auc = roc_auc_score(y, y_pred)
    print(f"\n  ROC-AUC: {auc:.3f}  (0.5 = random; >0.70 = useful; >0.80 = good)")

    # ── Odds ratio forest plot ────────────────────────────────────────────────
    plot_df = summary.sort_values("OddsRatio")
    fig, ax = plt.subplots(figsize=(8, max(5, len(plot_df) * 0.45)))

    colors = [PALETTE[3] if or_ > 1 else PALETTE[0] for or_ in plot_df["OddsRatio"]]
    y_pos  = range(len(plot_df))

    ax.barh(y_pos, plot_df["OddsRatio"], color=colors, alpha=0.8)
    ax.errorbar(
        plot_df["OddsRatio"], y_pos,
        xerr=[plot_df["OddsRatio"] - plot_df["CI_lower"],
              plot_df["CI_upper"]  - plot_df["OddsRatio"]],
        fmt="none", color="black", capsize=4,
    )
    ax.axvline(1, color="gray", ls="--", lw=1.5, label="OR = 1 (no effect)")
    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(plot_df.index, fontsize=9)
    ax.set_xlabel("Odds Ratio (log scale)")
    ax.set_xscale("log")
    ax.set_title(
        f"Suspension Risk: Odds Ratios with 95% CI\nROC-AUC = {auc:.3f}",
        fontweight="bold",
    )
    ax.legend()

    # Significance stars
    for i, (_, row) in enumerate(plot_df.iterrows()):
        sig = "***" if row.p_value < 0.001 else ("**" if row.p_value < 0.01
              else ("*" if row.p_value < 0.05 else ""))
        if sig:
            ax.text(max(plot_df["CI_upper"]) * 1.05, i, sig,
                    va="center", fontsize=10, color="black")

    plt.tight_layout()
    plt.savefig(out_dir / "04b_risk_model.png")
    plt.close()


def run(df, out_dir) -> dict:
    section_header(4, "Account Health: Suspension Profile")

    # ── Univariate breakdown (unchanged) ─────────────────────────────────────
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

    # ── Multivariate: logistic regression ────────────────────────────────────
    print("\n  ── Multivariate Risk Model ──")
    print("  Controls for all features simultaneously to isolate independent effects.")
    X, y = _build_feature_matrix(df)
    _run_logistic_regression(X, y, out_dir)

    return {}
