import random
import math
from datetime import datetime, timedelta
from typing import List
from app.collectors.base import BaseCollector
from app.core.schemas import FareObservationCreate
from app.config import AIRLINES

class MockAirfareCollector(BaseCollector):
    def __init__(self):
        super().__init__(source_name="mock_yield_engine")
        
        # Flight prefix registry for realism
        self.flight_prefixes = {
            "IndiGo": "6E",
            "Air India": "AI",
            "Akasa Air": "QP",
            "SpiceJet": "SG"
        }
        
        # Base pricing floors for major routes (in INR)
        self.route_base_fares = {
            "BOM-DEL": 4400.0,
            "DEL-BOM": 4400.0,
            "DEL-BLR": 4800.0,
            "BLR-DEL": 4800.0,
            "BOM-BLR": 3600.0,
            "BLR-BOM": 3600.0
        }

    def _calculate_fare(self, route: str, days_ahead: int, dep_time: datetime, day_offset: int) -> float:
        base_route_price = self.route_base_fares.get(route, 4200.0)

        # 1. Booking Horizon Surge (Yield curve: steep price increase close to departure)
        urgency_multiplier = 1.0 + (1.6 / (days_ahead + 1.2))

        # 2. Day-of-week demand pattern (Friday=4, Sunday=6)
        day_of_week = dep_time.weekday()
        day_multiplier = 1.15 if day_of_week in [4, 6] else (0.95 if day_of_week in [1, 2] else 1.0)

        # 3. Macro inflation drift (simulate a gradual ~6% inflation over 90 days)
        trend_drift = 1.0 + (day_offset * 0.0007)

        # 4. Natural supply volatility (+/- 6%)
        noise = random.uniform(0.94, 1.06)

        total_fare = base_route_price * urgency_multiplier * day_multiplier * trend_drift * noise

        # 5. Inject 1% realistic dirty data / outliers for the pipeline cleaning step to handle
        rand_anomaly = random.random()
        if rand_anomaly < 0.008:
            total_fare = total_fare * 4.5  # Surge outlier / peak festival emergency ticket
        elif rand_anomaly < 0.015:
            total_fare = 150.0  # Erroneous scraping / promotional tax-only bug

        return round(total_fare, 2)

    def fetch_fares(self, origin: str, destination: str, days_ahead: int, current_time: datetime = None, day_offset: int = 0) -> List[FareObservationCreate]:
        current_time = current_time or datetime.utcnow()
        route = f"{origin}-{destination}"
        dep_date = current_time + timedelta(days=days_ahead)

        observations: List[FareObservationCreate] = []

        # Simulate 3 daily flights per route across different operators
        daily_departure_hours = [6, 13, 20]  # Morning, afternoon, evening

        for hour in daily_departure_hours:
            dep_datetime = dep_date.replace(hour=hour, minute=random.choice([0, 15, 30, 45]), second=0, microsecond=0)
            airline = random.choice(AIRLINES)
            flight_no = f"{self.flight_prefixes.get(airline, 'IX')}-{random.randint(201, 899)}"
            
            fare = self._calculate_fare(route, days_ahead, dep_datetime, day_offset)
            base_fare = round(fare * 0.82, 2)
            taxes_fees = round(fare - base_fare, 2)

            obs = FareObservationCreate(
                source=self.source_name,
                origin=origin,
                destination=destination,
                route=route,
                airline=airline,
                flight_number=flight_no,
                departure_datetime=dep_datetime,
                collection_timestamp=current_time,
                days_to_departure=days_ahead,
                cabin_class="Economy",
                base_fare=base_fare,
                taxes_fees=taxes_fees,
                total_fare=fare,
                baggage_included_kg=15,
                is_refundable=False
            )
            observations.append(obs)

        return observations