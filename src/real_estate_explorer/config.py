"""Project configuration paths."""

from pathlib import Path


# Base directories
BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

OUTPUT_DIR = BASE_DIR / "outputs"


# Input data (raw)
RAW_LISTINGS_CSV = RAW_DATA_DIR / "paruvendu_listings.csv"
LYON_DISTRICTS_GEOJSON = RAW_DATA_DIR / "lyon_districts.geojson"


# Processed data
CLEAN_LISTINGS_CSV = (
    PROCESSED_DATA_DIR / "paruvendu_listings_clean.csv"
)


# Outputs
REAL_ESTATE_MAP_HTML = (
    OUTPUT_DIR / "real_estate_map.html"
)
