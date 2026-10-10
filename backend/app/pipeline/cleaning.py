import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from app.core.database import FareObservationRecord

class DataCleaningPipeline:
    """
    Cleans raw fare observations, standardizes flight product definitions,
    and eliminates pricing anomalies using statistical IQR thresholds per route cohort.
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def load_raw_dataframe(self) -> pd.DataFrame:
        """Loads all stored observations from SQLite into a Pandas DataFrame."""
        query = self.db.query(FareObservationRecord)
        df = pd.read_sql(query.statement, self.db.bind)
        
        # Convert date columns to proper datetime types
        df["collection_timestamp"] = pd.to_datetime(df["collection_timestamp"])
        df["departure_datetime"] = pd.to_datetime(df["departure_datetime"])
        df["collection_date"] = df["collection_timestamp"].dt.date
        return df

    def deduplicate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Removes redundant observations gathered across duplicate scraping runs
        for the same flight on the same collection date.
        """
        initial_len = len(df)
        df = df.drop_duplicates(
            subset=["route", "flight_number", "departure_datetime", "collection_date"]
        )
        dropped = initial_len - len(df)
        if dropped > 0:
            print(f"[Cleaning] Removed {dropped} duplicate flight observations.")
        return df

    def standardize_product_specs(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filters and standardizes to comparable product units:
        Economy cabin class with standard checked baggage (15kg in Indian domestic flights).
        """
        # Restrict strictly to Economy
        df = df[df["cabin_class"].str.lower() == "economy"].copy()
        
        # Ensure total_fare is strictly positive
        df = df[df["total_fare"] > 500.0].copy()
        return df

    def remove_anomalies_iqr(self, df: pd.DataFrame, factor: float = 1.5) -> pd.DataFrame:
        """
        Removes statistical price outliers per (route, days_to_departure) cohort
        using Pandas transform to prevent index mangling.
        """
        initial_len = len(df)
        
        # Calculate Q25 and Q75 per cohort directly as columns
        q25 = df.groupby(["route", "days_to_departure"])["total_fare"].transform(lambda s: s.quantile(0.25))
        q75 = df.groupby(["route", "days_to_departure"])["total_fare"].transform(lambda s: s.quantile(0.75))
        iqr = q75 - q25

        lower_bound = (q25 - (factor * iqr)).clip(lower=500.0)
        upper_bound = q75 + (factor * iqr)

        # Filter rows using clean boolean masking
        mask = (df["total_fare"] >= lower_bound) & (df["total_fare"] <= upper_bound)
        cleaned_df = df[mask].copy().reset_index(drop=True)

        outliers_removed = initial_len - len(cleaned_df)
        print(f"[Cleaning] Flagged & removed {outliers_removed} price outliers via IQR.")
        return cleaned_df

    def run(self) -> pd.DataFrame:
        """Executes the full standardization & cleaning pipeline."""
        df = self.load_raw_dataframe()
        print(f"[Cleaning] Ingested {len(df)} total raw observations from database.")
        
        df = self.deduplicate(df)
        df = self.standardize_product_specs(df)
        df = self.remove_anomalies_iqr(df)
        
        print(f"[Cleaning] Pipeline completed. Output dataset contains {len(df)} clean records.")
        return df