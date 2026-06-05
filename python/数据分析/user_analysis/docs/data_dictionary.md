# Data Dictionary — user_registrations.csv

Each row represents one user registration event.

---

## Identity & Timing

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | string | Unique identifier for the user. Should have no duplicates. |
| `registration_date` | datetime (UTC) | Timestamp when the user completed registration. |
| `consent_timestamp` | datetime (UTC) | When consent was recorded. May differ from `registration_date` if consent was collected in a separate step. Can be null. |

---

## Account Status

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `account_status` | string | `active`, `suspended`, `inactive`, `closed` | Current state of the account. `active` = usable; `suspended` = restricted due to risk or compliance; `inactive` = no recent activity; `closed` = permanently deactivated. |

---

## KYC (Know Your Customer)

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `kyc_status` | string | `not_started`, `pending`, `verified`, `failed` | Identity verification stage. `not_started` = user has not submitted; `pending` = under review; `verified` = approved; `failed` = rejected. |
| `kyc_verified_date` | date | Date or null | Date KYC was successfully completed. Null for all non-verified users. |

**Derived field (added in `loader.py`):**

| Field | Type | Description |
|-------|------|-------------|
| `kyc_days` | float | Calendar days from `registration_date` to `kyc_verified_date`. Null for non-verified users. Useful for measuring review turnaround time. |

---

## Security

| Field | Type | Description |
|-------|------|-------------|
| `email_verified` | boolean | Whether the user has clicked the email verification link. Basic engagement signal; also a prerequisite for most platforms to enable full account features. |
| `two_factor_enabled` | boolean | Whether 2FA (TOTP, SMS, etc.) is active on the account. Associated with lower fraud risk and higher user intent. |

---

## Consent

All consent fields are boolean. `True` = user has explicitly accepted; `False` or null = not accepted.

| Field | Mandatory? | Description |
|-------|-----------|-------------|
| `consent_terms_accepted` | **Yes** | Acceptance of Terms of Service. Absence is a regulatory compliance risk — accounts without this are legally problematic. |
| `consent_privacy_policy` | **Yes** | Acceptance of the Privacy Policy. Required under GDPR, PDPA, and most data-protection frameworks. |
| `consent_marketing_emails` | No | Opt-in for marketing communications. Higher opt-in rate on a channel often correlates with higher user intent. |
| `consent_data_sharing` | No | Permission to share data with third parties or partners. Relevant for analytics and partnership integrations. |

---

## Acquisition

| Field | Type | Description |
|-------|------|-------------|
| `registration_source` | string | The acquisition channel or campaign that brought the user. Examples: `organic`, `referral`, `paid_social`, `email_campaign`. Used to evaluate channel ROI and quality. |
| `country` | string | ISO 2-letter country code derived from the user's registration IP or self-declared location. Used for geographic market analysis and compliance jurisdiction mapping. |
| `ip_address` | string | IPv4 address at registration time. Used to detect bulk/bot registrations (multiple accounts sharing an IP). Not used for user-level profiling. |

---

## Derived / Computed Fields

These are added by `loader.py` at load time and available in all analysis sections.

| Field | Type | Description |
|-------|------|-------------|
| `reg_year_month` | Period (M) | Year-month period for monthly grouping. |
| `reg_year` | int | Registration year. |
| `reg_month` | int | Registration month (1–12). |
| `reg_hour` | int | UTC hour of registration (0–23). Used for time-based risk analysis. |
| `reg_dow` | int | Day of week (0 = Monday, 6 = Sunday). |
| `kyc_days` | float | Days from registration to KYC verification. Null if not verified. |
| `is_suspended` | int (0/1) | Binary flag: 1 if `account_status == "suspended"`. Used as the target variable in risk analysis. |

---

## Data Quality Notes

- `consent_timestamp` can be null if consent was collected outside the registration flow.
- `kyc_verified_date` has no timezone — treated as naive local date in `loader.py`.
- Boolean fields may arrive as `"True"/"False"` strings, `"1"/"0"`, or actual booleans — `loader.py` normalises all three forms.
- `account_status` and `kyc_status` are treated as categorical; add any new status values to the relevant lambda functions in section files if the dataset changes.
