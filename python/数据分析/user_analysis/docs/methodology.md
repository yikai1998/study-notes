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
Statistical validation (is this real or noise?)
    ↓
Multivariate control (which factors independently matter?)
    ↓
Actionable output (what should we do, and by how much?)
```

### A Note on Statistical Rigour

Descriptive metrics alone are insufficient for decision-making:
- A "5% difference" between two channels could be random noise with small samples.
- A channel might look bad because it attracts users from high-risk countries, not because the channel itself is problematic.
- A recommendation without a magnitude estimate is an opinion, not an analysis.

This pipeline addresses these gaps with three additions:
1. **Significance tests** (chi-square, Mann-Whitney U) to distinguish signal from noise.
2. **Logistic regression** to isolate each factor's independent contribution to suspension risk.
3. **Quantified impact estimates** attached to every recommendation.

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
- **Mann-Whitney U test**: Splits months into high-volume and low-volume groups, then tests whether their active rate distributions are statistically different. Unlike a t-test, Mann-Whitney makes no normality assumption — appropriate for rate data over a small number of months.

**How to read the charts:**
- The bar chart (top-left) shows whether growth is accelerating, decelerating, or seasonal
- The three line charts track quality metrics on the same x-axis — look for divergence from the volume chart
- A flat or declining quality trend alongside rising volume is a red flag
- The Mann-Whitney result tells you whether the apparent tradeoff is real (p < 0.05) or could be sampling noise

**Key insight type:** Trend analysis, non-parametric hypothesis testing

---

## Section 2 — Channel Quality Comparison

**Core question:** Which acquisition channel produces the most valuable users? Which channels are problematic?

**Why it matters:** Marketing budget should be allocated to channels that produce users with high lifetime value (LTV), not just high volume. Suspension rate is a strong negative signal — suspended accounts represent direct cost (fraud, refunds, support load).

**Technique:**
- Group by `registration_source`, compute five metrics per channel
- **Chi-square test of independence** with **Cramér's V effect size**: Tests whether channel membership and outcome (suspended/not) are truly associated, and how strongly.
  - Cramér's V < 0.10: negligible — differences are likely noise
  - Cramér's V 0.10–0.20: small but real effect
  - Cramér's V > 0.20: meaningful channel-level quality difference
- **Wilson 95% confidence interval error bars** on bar charts: the Wilson formula handles proportions near 0 or 1 better than the standard normal approximation. Overlapping CIs between channels suggest the visual difference may not be meaningful.

**How to read the charts:**
- Bars show point estimates; whiskers show the range of plausible true values
- Two bars whose whiskers overlap cannot be confidently ranked — more data is needed
- A channel with high volume but low active rate + high suspension rate is a candidate for budget reduction or traffic-quality audits

**Key insight type:** Comparative benchmarking, statistical significance testing

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
- **Breakdown table:** Suspension rate segmented by each categorical attribute individually — univariate, does not control for confounders
- **Cross-tabulation heatmap:** `kyc_status × email_verified → suspension rate` — a 2D view reveals interaction effects (e.g., `kyc_failed + email unverified` may have 3× the suspension rate of either factor alone)
- **Logistic regression (statsmodels):** The key multivariate addition. Fits all features simultaneously and estimates the independent contribution of each to suspension probability. Outputs:
  - **Odds ratio (OR)**: how much a one-unit change in a feature multiplies the odds of suspension, holding all else constant. OR > 1 = increases risk; OR < 1 = decreases risk.
  - **95% confidence interval**: if the CI includes 1.0, the effect is not statistically significant
  - **p-value**: probability of seeing this OR by chance if the true effect is zero
  - **ROC-AUC**: model's discriminating ability. 0.5 = no better than random; 0.70+ = usable risk score; 0.80+ = good model
- **Forest plot**: standard medical/clinical format for presenting multiple odds ratios. Each bar's length = OR magnitude; whiskers = CI. Reference line at OR = 1.

**Why logistic regression matters here:** Without it, we might conclude "Channel X has high suspension rate" when actually Channel X mostly acquires users from high-risk countries. The regression disentangles these effects.

**How to read the forest plot:**
- Bars to the right of OR = 1: risk-increasing features
- Bars to the left: risk-reducing features (e.g., `email_verified = True` should reduce suspension risk)
- Whiskers crossing 1.0: not statistically significant — interpret with caution

**Key insight type:** Multivariate risk modelling, logistic regression

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
- **Linear trend slope** via polynomial fit gives a single signed number — positive = improving, negative = declining
- **Cohort survival proxy** (new): plots each cohort's current active rate against its age in months. Fits an OLS trendline. If the slope is negative, older cohorts are less active — a cross-sectional proxy for retention decay.

**Limitation of the survival proxy:** This is NOT a true longitudinal retention curve, which would require tracking the same users' activity status at multiple points in time. Here we only have a single snapshot of `account_status`. The proxy is biased: newer cohorts haven't had time to churn, so they look artificially healthier. Interpret the slope as a directional indicator, not a precise retention rate.

**What a proper retention curve needs:** A table of `(user_id, activity_date)` events, from which you can compute "of users registered in month M, what fraction were still active N months later." Recommend adding activity logging if this data doesn't exist.

**How to read the survival proxy chart:**
- Each bubble = one registration cohort; bubble size = cohort size
- Negative trendline slope: older cohorts have lower active rates (consistent with churn)
- Flat slope: no evidence of long-term decay in this dataset (or dataset not old enough to show it)

**Key insight type:** Trend analysis, survival proxy, cohort comparison

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
- **Weight justification (new):** Displays each metric's Pearson correlation with `suspended_rate`. Metrics with stronger negative correlation with suspension (i.e., they identify safer channels) better justify higher weights. If the correlation order contradicts the weight order, the weights should be revisited.
- **Sensitivity analysis (new):** Varies each weight ±50% (redistributed to sum to 1) and checks whether the top/bottom channel changes. If the ranking is stable under all perturbations, the conclusion is robust. If rankings flip, stakeholders should be shown a range of scenarios rather than a single score.

**How to read the chart:**
- Higher score = healthier channel overall
- A score gap > 0.10 between channels is operationally significant
- Sensitivity analysis result tells you how much to trust the exact ordering

**Ideal improvement:** Use a metric's correlation with actual revenue or LTV (if available) to set weights empirically rather than by judgement.

**Key insight type:** Multi-criteria decision analysis (MCDA), sensitivity analysis

---

## Section 10 — Actionable Recommendations

**Core question:** Given all of the above, what should the team actually do?

**Technique:** Synthesis — each recommendation traces back to a specific numerical finding from prior sections, with a quantified expected impact estimate attached.

| Domain | Focus | Success Metric |
|--------|-------|----------------|
| Growth Quality | Channel budget reallocation | Overall quality score, 60-day active rate of new cohorts |
| KYC Optimisation | Re-engagement + process SLA | # newly verified, median review time |
| Risk Controls | Transaction limits, IP velocity | 30-day suspension rate delta |
| Compliance | Re-consent / account closure | % no-terms accounts resolved |
| Security | 2FA mandate | 2FA adoption rate at 90 days |

**Effort × Impact prioritisation:** Recommendations are explicitly ranked by implementation effort vs expected impact. This prevents high-effort, low-impact work from crowding out quick wins.

**How to use this output:**
- Each finding includes a user count — use this to prioritise by impact magnitude
- Each recommendation includes a specific measurable outcome — define a baseline before acting, then measure change
- Re-run the full pipeline after any significant product or campaign change to refresh the numbers
- The impact estimates use conservative conversion assumptions (e.g., 15% KYC re-engagement rate). Replace with your own product benchmarks for more accurate projections.

---

## Common Pitfalls

**Survivorship bias:** Some metrics (e.g., active rate by cohort) can look artificially high for very recent cohorts because those users haven't had time to churn yet. Interpret recent cohort data with caution.

**Correlation ≠ causation:** The channel scorecard tells you which channels *have* better users — it doesn't prove the channel *caused* the quality difference. Users may self-select into channels.

**Sample size sensitivity:** Geographic and hourly analyses can be noisy for small segments. The `users >= 20` filter in S5 is a minimum threshold; adjust it based on your dataset size.

**Timezone inconsistency:** `registration_date` is stored as UTC. The hourly pattern (S7) reflects UTC time, not local user time. Interpretation differs for user bases concentrated in a single timezone vs globally distributed populations.
