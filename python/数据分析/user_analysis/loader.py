"""
Data loading and cleaning pipeline.

Call load_data() to get a cleaned DataFrame ready for all analysis sections.
All derived columns are added here so sections can assume they exist.
"""

import pandas as pd
from config import DATA_PATH


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)

    # ── Datetime columns ──────────────────────────────────────────────────────
    df["registration_date"] = pd.to_datetime(df["registration_date"], utc=True)
    df["consent_timestamp"]  = pd.to_datetime(df["consent_timestamp"],  utc=True, errors="coerce")
    df["kyc_verified_date"]  = pd.to_datetime(df["kyc_verified_date"],  errors="coerce")

    # ── Boolean normalisation ─────────────────────────────────────────────────
    bool_cols = [
        "email_verified", "two_factor_enabled",
        "consent_terms_accepted", "consent_privacy_policy",
        "consent_marketing_emails", "consent_data_sharing",
    ]
    for col in bool_cols:
        df[col] = (
            df[col].astype(str).str.strip().str.lower()
            .map({"true": True, "false": False, "1": True, "0": False})
        )

    # ── Derived time fields ───────────────────────────────────────────────────
    df["reg_year_month"] = df["registration_date"].dt.to_period("M")
    df["reg_year"]       = df["registration_date"].dt.year
    df["reg_month"]      = df["registration_date"].dt.month
    df["reg_hour"]       = df["registration_date"].dt.hour
    df["reg_dow"]        = df["registration_date"].dt.dayofweek   # 0 = Monday

    # ── KYC processing time (days from registration to verification) ──────────
    df["kyc_days"] = (
        df["kyc_verified_date"] - df["registration_date"].dt.tz_localize(None)
    ).dt.days

    # ── Convenience binary flag ───────────────────────────────────────────────
    df["is_suspended"] = (df["account_status"] == "suspended").astype(int)

    # ── Quality report ────────────────────────────────────────────────────────
    print("\n" + "═" * 60)
    print("0. Data Loading & Cleaning")
    print("═" * 60)
    print(f"  Rows: {len(df):,}   Columns: {df.shape[1]}")
    print(f"  Date range: {df['registration_date'].min().date()} → {df['registration_date'].max().date()}")
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if len(missing):
        print(f"  Missing values:\n{missing.to_string()}")
    dup = df["user_id"].duplicated().sum()
    if dup:
        print(f"  ⚠ Duplicate user_id: {dup}")

    return df
