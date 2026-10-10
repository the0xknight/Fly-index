import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Top domestic corridors with passenger volume weights based on DGCA traffic distribution
ROUTE_WEIGHTS = {
    "BOM-DEL": 0.22,
    "DEL-BOM": 0.22,
    "DEL-BLR": 0.15,
    "BLR-DEL": 0.15,
    "BOM-BLR": 0.13,
    "BLR-BOM": 0.13
}

AIRLINES = ["IndiGo", "Air India", "Akasa Air", "SpiceJet"]