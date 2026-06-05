"""
Main entry point — runs all analysis sections in order.

Usage (from user_analysis/ directory):
    python run_analysis.py

Output: PNG charts saved to ../analysis_output/
"""

import sys
from pathlib import Path

# Make sure imports resolve from this directory
sys.path.insert(0, str(Path(__file__).parent))

from config import OUT_DIR
from loader import load_data

from sections import s01_registration_trend  as s01
from sections import s02_channel_quality     as s02
from sections import s03_kyc_funnel          as s03
from sections import s04_suspension_profile  as s04
from sections import s05_geo_analysis        as s05
from sections import s06_cohort              as s06
from sections import s07_behavior            as s07
from sections import s08_consent             as s08
from sections import s09_scorecard           as s09
from sections import s10_recommendations     as s10


def main():
    df = load_data()

    ctx = {}
    ctx.update(s01.run(df, OUT_DIR) or {})
    ctx.update(s02.run(df, OUT_DIR) or {})
    ctx.update(s03.run(df, OUT_DIR) or {})
    ctx.update(s04.run(df, OUT_DIR) or {})
    ctx.update(s05.run(df, OUT_DIR) or {})
    ctx.update(s06.run(df, OUT_DIR) or {})
    ctx.update(s07.run(df, OUT_DIR) or {})
    ctx.update(s08.run(df, OUT_DIR) or {})
    ctx.update(s09.run(df, OUT_DIR) or {})
    s10.run(df, OUT_DIR, **ctx)

    print(f"\nAll charts saved to {OUT_DIR}/  ({len(list(OUT_DIR.glob('*.png')))} files)")


if __name__ == "__main__":
    main()
