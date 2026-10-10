import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from app.config import ROUTE_WEIGHTS

class AirfareIndexEngine:
    """
    Computes route-level elementary indices using the Jevons geometric mean formula
    and aggregates them into a National Airfare Price Index using Laspeyres volume weights.
    """

    def __init__(self, cleaned_df: pd.DataFrame, target_booking_horizon: int = 7):
        """
        :param cleaned_df: Cleaned dataframe from Step 3.
        :param target_booking_horizon: Fixed purchase window (default: 7 days advance)
                                       to maintain product comparability over time.
        """
        self.df = cleaned_df.copy()
        self.target_horizon = target_booking_horizon
        
        # Standardize dates
        self.df["collection_date"] = pd.to_datetime(self.df["collection_date"]).dt.date
        
        # Filter for the chosen constant booking window to avoid mix-shift bias
        self.stratified_df = self.df[self.df["days_to_departure"] == self.target_horizon].copy()
        
        # Fallback if horizon filter has too few records: use all records
        if len(self.stratified_df) < 50:
            self.stratified_df = self.df.copy()

        self.base_prices: Dict[str, float] = {}
        self.base_start_date: Optional[object] = None
        self.base_end_date: Optional[object] = None

    def set_base_period(self, start_date: str = None, end_date: str = None, baseline_days: int = 7):
        """
        Defines the base period where Index = 100.0.
        Calculates geometric mean price (P_r,0) for each route during this baseline window.
        """
        unique_dates = sorted(self.stratified_df["collection_date"].unique())
        if not unique_dates:
            raise ValueError("No valid observations found in dataset to set base period.")

        if start_date and end_date:
            self.base_start_date = pd.to_datetime(start_date).date()
            self.base_end_date = pd.to_datetime(end_date).date()
        else:
            # Default: Use the earliest N days in the dataset as the reference period
            self.base_start_date = unique_dates[0]
            end_idx = min(baseline_days - 1, len(unique_dates) - 1)
            self.base_end_date = unique_dates[end_idx]

        mask = (self.stratified_df["collection_date"] >= self.base_start_date) & \
               (self.stratified_df["collection_date"] <= self.base_end_date)
        base_df = self.stratified_df[mask]

        print(f"[IndexEngine] Reference Base Period locked: {self.base_start_date} to {self.base_end_date}")

        for route in ROUTE_WEIGHTS.keys():
            fares = base_df[base_df["route"] == route]["total_fare"].values
            if len(fares) > 0:
                # Jevons geometric mean: exp(mean(log(P)))
                self.base_prices[route] = float(np.exp(np.mean(np.log(fares))))
            else:
                # Fallback to route average if baseline subset is empty
                all_fares = self.stratified_df[self.stratified_df["route"] == route]["total_fare"].values
                self.base_prices[route] = float(np.mean(all_fares)) if len(all_fares) > 0 else 4000.0

            print(f"  └─ Baseline Price for {route} (P_0): Rs. {self.base_prices[route]:.2f}")

    def compute_daily_index(self) -> pd.DataFrame:
        """
        Calculates daily route indices and composite national Laspeyres index.
        """
        if not self.base_prices:
            self.set_base_period()

        unique_dates = sorted(self.stratified_df["collection_date"].unique())
        series_records: List[dict] = []

        for date in unique_dates:
            day_df = self.stratified_df[self.stratified_df["collection_date"] == date]
            national_index = 0.0
            route_indices = {}

            for route, weight in ROUTE_WEIGHTS.items():
                fares = day_df[day_df["route"] == route]["total_fare"].values
                
                if len(fares) > 0 and route in self.base_prices:
                    # Current day geometric mean
                    current_geom_mean = np.exp(np.mean(np.log(fares)))
                    # Elementary Jevons Index for route r at time t
                    r_index = (current_geom_mean / self.base_prices[route]) * 100.0
                else:
                    # If no flights observed on date, default to 100.0 (or carry-forward)
                    r_index = 100.0

                route_indices[route] = round(float(r_index), 2)
                national_index += weight * r_index

            row = {
                "date": str(date),
                "national_index": round(float(national_index), 2),
            }
            # Append individual route indices
            for r, val in route_indices.items():
                row[f"idx_{r}"] = val

            series_records.append(row)

        index_df = pd.DataFrame(series_records)
        return index_df

    def get_summary_metrics(self, index_df: pd.DataFrame) -> dict:
        """
        Generates high-level statistical inflation metrics for executive dashboard reporting.
        """
        if index_df.empty:
            return {}

        latest = index_df.iloc[-1]
        earliest = index_df.iloc[0]
        
        # Cumulative inflation from base period
        inflation_from_base = round(latest["national_index"] - 100.0, 2)
        
        # 7-day velocity / momentum
        if len(index_df) >= 7:
            prev_7d = index_df.iloc[-7]["national_index"]
            velocity_7d = round(((latest["national_index"] - prev_7d) / prev_7d) * 100.0, 2)
        else:
            velocity_7d = 0.0

        # Determine which route is driving inflation the most
        route_deltas = {}
        for route in ROUTE_WEIGHTS.keys():
            col = f"idx_{route}"
            if col in latest:
                route_deltas[route] = round(latest[col] - 100.0, 2)

        top_driver = max(route_deltas.items(), key=lambda x: x[1])

        return {
            "current_index": latest["national_index"],
            "base_period": f"{self.base_start_date} to {self.base_end_date}",
            "inflation_from_base_pct": inflation_from_base,
            "weekly_velocity_pct": velocity_7d,
            "latest_date": latest["date"],
            "top_inflation_driver": {
                "route": top_driver[0],
                "change_from_base_pct": top_driver[1]
            },
            "route_breakdown": route_deltas
        }