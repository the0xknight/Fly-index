import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
from pipeline.cleaning import DataCleaningPipeline

def test_pipeline():
    db = SessionLocal()
    try:
        cleaner = DataCleaningPipeline(db)
        clean_df = cleaner.run()
        
        print("\n--- Cleaned Data Summary ---")
        print("Routes tracked:", clean_df["route"].unique().tolist())
        print("Booking horizons (days ahead):", sorted(clean_df["days_to_departure"].unique().tolist()))
        print("Min fare observed: Rs.", clean_df["total_fare"].min())
        print("Max fare observed: Rs.", clean_df["total_fare"].max())
        print("Average fare: Rs.", round(clean_df["total_fare"].mean(), 2))
    finally:
        db.close()

if __name__ == "__main__":
    test_pipeline()