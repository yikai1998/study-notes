# User Registration Analysis

A modular pipeline for analysing user registration quality, KYC compliance, channel performance, and risk signals from a `user_registrations.csv` dataset.

---

## Project Structure

```
user_analysis/
├── run_analysis.py          # Entry point — run this
├── config.py                # Paths and plot settings
├── loader.py                # Data loading and cleaning (Section 0)
├── utils.py                 # Shared helpers (bar annotations, headers)
├── sections/
│   ├── s01_registration_trend.py   # Volume vs quality over time
│   ├── s02_channel_quality.py      # Acquisition channel benchmarking
│   ├── s03_kyc_funnel.py           # KYC conversion funnel
│   ├── s04_suspension_profile.py   # Suspension risk profiling
│   ├── s05_geo_analysis.py         # Geographic market analysis
│   ├── s06_cohort.py               # Cohort quality trend
│   ├── s07_behavior.py             # Time patterns & bot signals
│   ├── s08_consent.py              # Compliance & consent rates
│   ├── s09_scorecard.py            # Channel composite health score
│   └── s10_recommendations.py      # Actionable recommendations
├── docs/
│   ├── methodology.md       # Why each section exists; techniques used
│   └── data_dictionary.md   # Field-by-field data reference
└── requirements.txt
```

---

## Setup

```bash
pip install -r requirements.txt
```

Place `user_registrations.csv` in the **parent directory** of `user_analysis/` (i.e., alongside this folder, not inside it).

---

## Running

```bash
cd user_analysis
python run_analysis.py
```

Output charts are written to `../analysis_output/` (created automatically).

---

## Output Charts

| File | Section | What it shows |
|------|---------|---------------|
| `01_registration_trend.png` | S1 | Monthly volume + quality metrics (active rate, KYC, 2FA) |
| `02_channel_quality.png`    | S2 | Channel active/KYC/suspension rates side by side |
| `03_kyc_funnel.png`         | S3 | Funnel conversion, processing-time histogram, channel failure rates |
| `04_suspension_profile.png` | S4 | Suspension heatmap + KYC-failure vs suspension scatter |
| `05_geo_analysis.png`       | S5 | Top-10 country volumes + quality bubble chart |
| `06_cohort_quality.png`     | S6 | Cohort trend with 3-month rolling average |
| `07_hourly_pattern.png`     | S7 | Registration volume and quality by hour (UTC) |
| `08_consent_analysis.png`   | S8 | Consent acceptance rates + marketing consent vs account status |
| `09_channel_scorecard.png`  | S9 | Ranked composite health score per channel |

---

## Extending the Pipeline

To add a new section:
1. Create `sections/sNN_my_section.py` with a `run(df, out_dir) -> dict` function.
2. Import it in `run_analysis.py` and add `ctx.update(sNN.run(df, OUT_DIR) or {})`.
3. Return any data that later sections need in the dict.

To change data or output paths, edit `config.py` — do not hardcode paths inside section files.

---

## Documentation

- **`docs/methodology.md`** — The analytical reasoning behind each section: what question it answers, why it matters, what technique is used, and how to interpret results.
- **`docs/data_dictionary.md`** — Definitions and expected values for every field in the dataset.
