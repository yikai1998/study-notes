# Analytical Methodology

This document explains the reasoning behind each analysis section: what question it answers, why that question matters, what technique is used, and how to interpret the output.

---

## The Analytical Framework

The pipeline follows a **layered investigation** pattern:

```
Surface metrics (what happened?)
    ↓
Segmentation (who / where / when?)
    ↓
Causal signals (why did it happen?)
    ↓
Actionable output (what should we do?)
```

Each section peels back one layer. The final recommendations synthesise all layers into prioritised actions.

---

## Section 0 — Data Loading & Cleaning

**Why this matters:** Analytical conclusions are only as good as the data quality. Running checks upfront prevents silent errors from propagating through all downstream sections.

**What is checked:**
- Row count and column count (sanity check against expected schema)
- Date range (confirms the data covers the intended period)
- Null values per column (identifies fields that need imputation or exclusion)
- Duplicate `user_id` values (should be zero; duplicates indicate ETL issues)

**Technique:** Pandas `.isnull().sum()`, `.duplicated()`, `pd.to_datetime()` with `utc=True` to normalise timezones.

**Key outputs added to DataFrame:**
- `kyc_days`: measures review turnaround time
- `is_suspended`: binary target for risk analysis
- Time decomposition fields (`reg_hour`, `reg_dow`) for temporal analysis

---

## Section 1 — Registration Trend: Volume vs Quality

**Core question:** Does registration growth come with quality growth, or are we acquiring more low-quality users?

**Why it matters:** Raw registration volume is a vanity metric. A campaign that doubles registrations but halves the KYC pass rate likely destroys value. Detecting this early allows budget reallocation.

**Technique:**
- Monthly aggregation using `.groupby("reg_year_month")`
- Four quality proxies tracked in parallel: active rate, KYC pass rate, 2FA adoption
- **Pearson correlation** between monthly volume and active rate — a negative coefficient flags a quality-quantity tradeoff

**How to read the charts:**
- The bar chart (top-left) shows whether growth is accelerating, decelerating, or seasonal
- The three line charts track quality metrics on the same x-axis — look for divergence from the volume chart
- A flat or declining quality trend alongside rising volume is a red flag

**Key insight type:** Trend analysis, correlation

---

## Section 2 — Channel Quality Comparison

**Core question:** Which acquisition channel produces the most valuable users? Which channels are problematic?

**Why it matters:** Marketing budget should be allocated to channels that produce users with high lifetime value (LTV), not just high volume. Suspension rate is a strong negative signal — suspended accounts represent direct cost (fraud, refunds, support load).

**Technique:**
- Group by `registration_source`, compute five metrics per channel
- Side-by-side bar charts for direct visual comparison
- The scatter plot in S4 correlates KYC failure rate with suspension rate per channel, revealing whether a channel's KYC failures predict its fraud rate

**How to read the charts:**
- Active rate + KYC pass rate = positive quality indicators (higher is better)
- Suspension rate = negative risk indicator (lower is better)
- A channel with high volume but low active rate + high suspension rate is a candidate for budget reduction or traffic-quality audits

**Key insight type:** Comparative benchmarking

---

## Section 3 — KYC Funnel Analysis

**Core question:** Where do users abandon the identity verification process? Is slow review causing drop-off or failure?

**Why it matters:** KYC-verified users are fully monetisable and carry lower compliance risk. Every user stuck in `not_started` or `pending` is partially unrealised value. Review turnaround time is an operational lever — faster reviews can improve conversion.

**Technique:**
- **Funnel analysis:** Three stages expressed as absolute counts and conversion rates
  - Stage 1: Total registered
  - Stage 2: KYC started (status ≠ `not_started`)
  - Stage 3: KYC verified
- **Histogram:** Distribution of `kyc_days` for verified users — the shape reveals whether processing time is consistent or has a long tail
- **Channel failure rate:** Which channels send users who fail KYC most often — points to either low-quality traffic or channel-specific onboarding friction

**How to read the charts:**
- A large drop between Stage 1 and Stage 2 means users never attempt KYC — a UX or motivation problem
- A large drop between Stage 2 and Stage 3 means users attempt but fail — a document quality or process problem
- A right-skewed `kyc_days` histogram with a long tail suggests a manual review backlog

**Key insight type:** Funnel / conversion analysis

---

## Section 4 — Suspension Profile (Account Health)

**Core question:** At the time of registration, what signals predict future account suspension?

**Why it matters:** If suspended accounts cluster on specific attributes (channel, KYC status, email verification), those attributes become early-warning risk signals. They can be used to gate high-risk users into enhanced verification before they accumulate fraud.

**Technique:**
- **Breakdown table:** Suspension rate segmented by each categorical attribute individually
- **Cross-tabulation heatmap:** `kyc_status × email_verified → suspension rate` — a 2D view reveals interaction effects (e.g., `kyc_failed + email unverified` may have 3× the suspension rate of either factor alone)
- **Scatter plot:** Plots each channel's KYC failure rate against its suspension rate — a linear trend would confirm that KYC failure is a leading indicator of fraud

**How to read the charts:**
- Dark red cells in the heatmap = high-risk combinations
- Channels in the upper-right of the scatter plot have both high KYC failures and high suspensions — strongest candidates for scrutiny
- Channels with high KYC failures but low suspensions may have stricter self-screening (users who fail simply leave rather than commit fraud)

**Key insight type:** Risk factor analysis, feature importance (manual)

---

## Section 5 — Geographic Analysis

**Core question:** Which markets are large enough to justify investment? Which are high-risk despite their size?

**Why it matters:** Regulatory, fraud, and support costs vary significantly by country. A large market with high suspension rates may not be profitable. Small markets with excellent quality metrics may be underserved growth opportunities.

**Technique:**
- Aggregate four metrics per country: users, active rate, KYC pass rate, suspension rate
- **Horizontal bar chart:** Purely volumetric — shows where the user base physically is
- **Bubble chart:** Three dimensions in one view — x-axis = volume, y-axis = active rate, bubble size = KYC pass rate, colour = suspension rate. Encodes four variables simultaneously

**How to read the bubble chart:**
- Ideal market: far right (large), high on y-axis (active), large bubble (high KYC pass), green colour (low suspension)
- High-risk market: small red bubble in the lower-left
- The `quantile(0.75)` filter on suspension rate surfaces the worst-performing markets with meaningful sample sizes (≥ 20 users)

**Key insight type:** Market prioritisation matrix

---

## Section 6 — Cohort Analysis

**Core question:** Is the quality of users improving, declining, or stable across registration cohorts (months)?

**Why it matters:** Cohort analysis separates time from maturity. A drop in active rate in month 12 could mean: (a) users from that month were always lower quality, or (b) all cohorts churn at 12 months. By looking at the cohort's quality *at the time of registration*, this analysis isolates (a).

**Technique:**
- Group by registration month, compute quality metrics per cohort
- **3-month rolling average** (`rolling(3, min_periods=1)`) smooths month-to-month noise and reveals underlying trends
- **Linear trend slope** via polynomial fit (`polyfit(x, y, 1)`) gives a single signed number — positive = improving, negative = declining

**How to read the charts:**
- Bars = raw monthly values (noisy); line = smoothed trend (signal)
- A consistently declining line across all three metrics (active, KYC, 2FA) suggests a structural degradation in acquisition quality
- Sudden spikes in one month often correlate with a specific campaign or channel change

**Key insight type:** Trend analysis, cohort comparison

---

## Section 7 — Registration Timing & Suspicious Behaviour

**Core question:** Do the hours of registration or shared IP addresses signal automated or fraudulent activity?

**Why it matters:** Bots tend to register outside business hours (when human oversight is lower) and often share IP addresses across multiple accounts. These are inexpensive signals to compute and can be layered into real-time risk scoring.

**Technique:**
- **Hourly aggregation:** Suspension rate and KYC pass rate plotted by UTC hour
- **IP frequency analysis:** `ip_address.value_counts()` — any IP with >1 account is flagged. The suspension rate of shared-IP users vs the general population quantifies the risk uplift
- The `quantile(0.75)` threshold on hourly suspension rate highlights structurally higher-risk time windows

**How to read the charts:**
- If the suspension rate peaks sharply at off-hours (e.g., 2–5 AM UTC) while volume is low, that's a bot signal
- A uniform suspension rate across all hours suggests the risk driver is not time-based
- A high `shared-IP suspension rate / overall suspension rate` ratio (e.g., 3×) justifies IP-velocity checks in the registration flow

**Key insight type:** Anomaly detection (heuristic), behavioural risk signals

---

## Section 8 — Compliance & Consent Analysis

**Core question:** Are there users with missing mandatory consent (regulatory exposure)? Does marketing consent correlate with engagement?

**Why it matters:** Missing `consent_terms_accepted` is a direct compliance risk under GDPR, PDPA, and similar regulations. Marketing consent opt-in rate is also a leading indicator of user intent — users who actively opt in are more likely to engage.

**Technique:**
- **Consent rate bar chart:** `.mean()` on boolean columns gives the acceptance rate directly
- **Cross-tab:** `marketing consent × account status` stacked bar — shows whether opted-in users have a different status distribution than opted-out users
- `no_terms` filter: identifies accounts where `consent_terms_accepted` is False or null — these are the compliance-critical population

**How to read the charts:**
- Consent rates near 100% for mandatory fields are expected; anything below ~95% warrants investigation
- If marketing-opted-in users have a notably higher active rate, it confirms that consent is a quality signal, not just a legal checkbox
- Large `no_terms` count = legal team needs to be involved

**Key insight type:** Compliance audit, intent signal

---

## Section 9 — Channel Composite Health Score

**Core question:** How do channels rank when all quality dimensions are considered simultaneously?

**Why it matters:** Individual metrics can be misleading — a channel might rank first on KYC pass rate but last on suspension rate. A composite score resolves these conflicts into a single number suitable for budget decisions.

**Technique:**
- **Weighted linear combination** of five normalised metrics:

  | Metric | Weight | Rationale |
  |--------|--------|-----------|
  | Active rate | 30% | Strongest long-term retention proxy |
  | KYC pass rate | 30% | Compliance quality; unlocks full monetisation |
  | Email verification | 15% | Basic engagement signal |
  | 2FA adoption | 10% | Security posture |
  | 1 − Suspension rate | 15% | Inverted risk signal |

- All five metrics are already in [0, 1], so no normalisation step is needed
- The score is [0, 1] by construction

**How to read the chart:**
- Higher score = healthier channel overall
- A score gap > 0.10 between channels is operationally significant
- This score is a **relative** ranking tool, not an absolute standard — a score of 0.75 is only good relative to other channels in this dataset

**Key insight type:** Multi-criteria decision analysis (MCDA), composite index

---

## Section 10 — Actionable Recommendations

**Core question:** Given all of the above, what should the team actually do?

**Technique:** Synthesis — each recommendation traces back to a specific numerical finding from prior sections. The output is structured into four domains:

| Domain | Focus |
|--------|-------|
| Growth Quality | Channel budget reallocation |
| KYC Optimisation | Re-engagement and process improvement |
| Risk Controls | Fraud prevention guardrails |
| Compliance | Regulatory exposure remediation |

**How to use this output:**
- Each bullet includes a user count — use this to prioritise by impact magnitude
- Recommendations are independent; they can be actioned in parallel by different teams
- Re-run the full pipeline after any significant product or campaign change to refresh the numbers

---

## Common Pitfalls

**Survivorship bias:** Some metrics (e.g., active rate by cohort) can look artificially high for very recent cohorts because those users haven't had time to churn yet. Interpret recent cohort data with caution.

**Correlation ≠ causation:** The channel scorecard tells you which channels *have* better users — it doesn't prove the channel *caused* the quality difference. Users may self-select into channels.

**Sample size sensitivity:** Geographic and hourly analyses can be noisy for small segments. The `users >= 20` filter in S5 is a minimum threshold; adjust it based on your dataset size.

**Timezone inconsistency:** `registration_date` is stored as UTC. The hourly pattern (S7) reflects UTC time, not local user time. Interpretation differs for user bases concentrated in a single timezone vs globally distributed populations.
