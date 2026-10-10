import os
import requests
from datetime import datetime, timedelta
from typing import List
from app.collectors.base import BaseCollector
from app.core.schemas import FareObservationCreate

class LiveAPICollector(BaseCollector):
    """
    Adapter for querying live external flight aggregators.
    Falls back gracefully if external credentials or networks fail.
    """
    def __init__(self, api_key: str = None):
        super().__init__(source_name="live_flight_api")
        self.api_key = api_key or os.getenv("FLIGHT_API_KEY", "")

    def fetch_fares(self, origin: str, destination: str, days_ahead: int) -> List[FareObservationCreate]:
        if not self.api_key:
            # Fallback warning if no API key is provided
            print(f"[Warning] No live API key configured. Bypassing live lookup for {origin}-{destination}.")
            return []

        search_date = (datetime.utcnow() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        route = f"{origin}-{destination}"

        # Standard aggregator endpoint example (e.g., RapidAPI or Amadeus format)
        url = "https://api.example.com/v1/flights/search"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"origin": origin, "destination": destination, "date": search_date}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("flights", []):
                total = float(item["price"])
                results.append(
                    FareObservationCreate(
                        source=self.source_name,
                        origin=origin,
                        destination=destination,
                        route=route,
                        airline=item.get("airline", "IndiGo"),
                        flight_number=item.get("flight_number", "6E-101"),
                        departure_datetime=datetime.fromisoformat(item["departure_time"]),
                        collection_timestamp=datetime.utcnow(),
                        days_to_departure=days_ahead,
                        cabin_class="Economy",
                        base_fare=round(total * 0.82, 2),
                        taxes_fees=round(total * 0.18, 2),
                        total_fare=total,
                        baggage_included_kg=15,
                        is_refundable=False
                    )
                )
            return results
        except Exception as e:
            print(f"[Collector Error] Live collection failed for {route}: {e}")
            return []