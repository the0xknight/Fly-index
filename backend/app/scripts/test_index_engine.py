import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
from pipeline.cleaning import DataCleaningPipeline
from pipeline.index_engine import AirfareIndexEngine

def test_engine():
    db = SessionLocal()
    try:
        # 1. Clean data from database
        cleaner = DataCleaningPipeline(db)
        cleaned_df = cleaner.run()

        # 2. Feed into Index Engine
        engine = AirfareIndexEngine(cleaned_df, target_booking_horizon=7)
        engine.set_base_period(baseline_days=7)

        # 3. Compute time-series
        index_df = engine.compute_daily_index()
        summary = engine.get_summary_metrics(index_df)

        print("\n=================== INDEX ENGINE RESULTS ===================")
        print(f"Total Daily Index Points Computed: {len(index_df)}")
        print(f"Current Composite National Index : {summary['current_index']}")
        print(f"Inflation relative to Base (100) : {summary['inflation_from_base_pct']}%")
        print(f"7-Day Index Velocity             : {summary['weekly_velocity_pct']}%")
        print(f"Highest Contributing Corridor    : {summary['top_inflation_driver']['route']} (+{summary['top_inflation_driver']['change_from_base_pct']}%)")
        print("\nLatest 5 Daily Index Values:")
        print(index_df[["date", "national_index", "idx_BOM-DEL", "idx_DEL-BLR"]].tail())
        print("============================================================")
    finally:
        db.close()

if __name__ == "__main__":
    test_engine()