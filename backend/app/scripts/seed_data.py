import sys
import os
from datetime import datetime, timedelta

# Ensure parent path is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import init_db, SessionLocal, FareObservationRecord
from collectors.mock_collector import MockAirfareCollector
from config import ROUTE_WEIGHTS

DAYS_OF_HISTORY = 60
OBSERVATION_HORIZONS = [3, 7, 14, 30]  # Days ahead of departure

def run_seed():
    print("Initializing database tables...")
    init_db()

    db = SessionLocal()
    collector = MockAirfareCollector()

    # Clear existing data to ensure idempotent seeding runs
    deleted_count = db.query(FareObservationRecord).delete()
    db.commit()
    print(f"Cleared {deleted_count} previous records.")

    print(f"Generating {DAYS_OF_HISTORY} days of simulated airfare observations across 6 major routes...")

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=DAYS_OF_HISTORY)
    
    total_records = 0
    batch_records = []

    for day_offset in range(DAYS_OF_HISTORY + 1):
        simulated_collection_time = start_date + timedelta(days=day_offset)

        for route_str in ROUTE_WEIGHTS.keys():
            origin, dest = route_str.split("-")

            for days_ahead in OBSERVATION_HORIZONS:
                fares = collector.fetch_fares(
                    origin=origin,
                    destination=dest,
                    days_ahead=days_ahead,
                    current_time=simulated_collection_time,
                    day_offset=day_offset
                )

                for fare in fares:
                    record = FareObservationRecord(
                        source=fare.source,
                        origin=fare.origin,
                        destination=fare.destination,
                        route=fare.route,
                        airline=fare.airline,
                        flight_number=fare.flight_number,
                        departure_datetime=fare.departure_datetime,
                        collection_timestamp=fare.collection_timestamp,
                        days_to_departure=fare.days_to_departure,
                        cabin_class=fare.cabin_class,
                        base_fare=fare.base_fare,
                        taxes_fees=fare.taxes_fees,
                        total_fare=fare.total_fare,
                        baggage_included_kg=fare.baggage_included_kg,
                        is_refundable=fare.is_refundable
                    )
                    batch_records.append(record)

        # Batch insert every 10 days of observations to optimize SQLite performance
        if len(batch_records) >= 500:
            db.bulk_save_objects(batch_records)
            db.commit()
            total_records += len(batch_records)
            batch_records = []

    if batch_records:
        db.bulk_save_objects(batch_records)
        db.commit()
        total_records += len(batch_records)

    db.close()
    print(f"Seeding completed successfully! Ingested {total_records} structured flight observations into `airfare.db`.")

if __name__ == "__main__":
    run_seed()