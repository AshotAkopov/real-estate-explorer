"""Main pipeline for real estate data processing.

This script orchestrates the full workflow:
- scraping raw data if needed;
- preparing (cleaning and transforming) the dataset;
- generating the final visualization map.
"""

from pathlib import Path

import pandas as pd

from real_estate_explorer.config import (
    CLEAN_LISTINGS_CSV,
    RAW_LISTINGS_CSV,
)
from real_estate_explorer.scraper import ParuVenduScraper
from real_estate_explorer.preprocessing import prepare_listings
import real_estate_explorer.visualization as visualization


def is_valid_file(path: Path) -> bool:
    """Check whether a file exists and is not empty.

    Args:
        path: Path to the file.

    Returns:
        True if the file exists and is non-empty, False otherwise.
    """
    return path.exists() and path.stat().st_size > 0


def main() -> None:
    """Run the full data pipeline: scraping → preparation → visualization."""

    # Case 1: clean data already exists
    if is_valid_file(Path(CLEAN_LISTINGS_CSV)):
        print("Clean dataset already exists. Generating map...")

    else:
        # Case 2: raw data exists → skip scraping
        if is_valid_file(Path(RAW_LISTINGS_CSV)):
            print("Raw dataset found. Starting data preparation...")
            dataframe = pd.read_csv(RAW_LISTINGS_CSV)

        else:
            # Case 3: no data → run scraping
            print("Raw dataset not found. Starting scraping...")
            scraper = ParuVenduScraper(csv_path=str(RAW_LISTINGS_CSV))
            scraper.scrape()

            if not is_valid_file(Path(RAW_LISTINGS_CSV)):
                raise RuntimeError(
                    "Scraping did not generate the expected raw dataset."
                )

            dataframe = pd.read_csv(RAW_LISTINGS_CSV)

        # Data preparation
        print("Cleaning and preparing data...")
        cleaned_dataframe = prepare_listings(dataframe)

        print("Saving cleaned dataset...")
        cleaned_dataframe.to_csv(CLEAN_LISTINGS_CSV, index=False)

    # Visualization
    print("Generating map...")
    visualization.main()

    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()
