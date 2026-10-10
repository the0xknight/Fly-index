from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from typing import Dict, Any

from app.core.database import init_db, get_db, SessionLocal
from app.pipeline.cleaning import DataCleaningPipeline
from app.pipeline.index_engine import AirfareIndexEngine

# In-memory cache for ultra-fast API delivery
cache_state: Dict[str, Any] = {
    "engine": None,
    "index_df": None,
    "summary": None
}

def refresh_index_cache():
    """Reads DB, cleans data, and computes latest index series into cache."""
    db = SessionLocal()
    try:
        cleaner = DataCleaningPipeline(db)
        cleaned_df = cleaner.run()
        
        engine = AirfareIndexEngine(cleaned_df, target_booking_horizon=7)
        engine.set_base_period(baseline_days=7)
        
        index_df = engine.compute_daily_index()
        summary = engine.get_summary_metrics(index_df)
        
        cache_state["engine"] = engine
        cache_state["index_df"] = index_df
        cache_state["summary"] = summary
        print("[API Cache] Successfully cached index time-series and summary metrics.")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs on server startup
    init_db()
    refresh_index_cache()
    yield
    # Cleanup on shutdown if needed
    cache_state.clear()

app = FastAPI(
    title="National Airfare Price Index (NAPI) API",
    description="Real-time Indian Aviation Fare Index Engine for CPI Augmentation",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for React/Vite development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy", "service": "NAPI Engine"}

@app.get("/api/v1/summary")
def get_summary():
    """Returns headline metrics for top-level KPI cards."""
    if not cache_state["summary"]:
        refresh_index_cache()
    return cache_state["summary"]

@app.get("/api/v1/timeseries")
def get_timeseries():
    """Returns daily time-series data for charting national and route indices."""
    if cache_state["index_df"] is None:
        refresh_index_cache()
    # Convert DataFrame records to a clean list of dictionaries
    return cache_state["index_df"].to_dict(orient="records")

@app.post("/api/v1/recompute")
def trigger_recompute():
    """Manual trigger to re-run pipeline on demand."""
    refresh_index_cache()
    return {"message": "Index engine recomputed and cache refreshed successfully."}