"""Data preparation utilities for real estate listings."""

import pandas as pd


DISTRICT_LABEL_TO_NUMBER = {f"Lyon {i}": i for i in range(1, 10)}


def categorize_housing_type(room_count: int) -> str:
    """Return the housing type category based on the number of rooms."""
    if room_count == 1:
        return "Studio/T1"

    if room_count == 2:
        return "T2"

    if room_count == 3:
        return "T3"

    return "T4+"


def prepare_listings(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Clean and prepare the real estate listings DataFrame.

    The preparation pipeline:
    - removes duplicate listings;
    - fills missing room counts;
    - removes listings without area;
    - converts area and price columns;
    - filters unrealistic values;
    - completes missing bedroom counts;
    - drops unused columns;
    - creates business-oriented derived columns.

    Args:
        dataframe: Raw listings DataFrame.

    Returns:
        Cleaned and enriched listings DataFrame.
    """
    dataframe = dataframe.copy()

    dataframe = dataframe.drop_duplicates(subset="listing_id", keep="first")

    dataframe.loc[dataframe["listing_rooms"].isna(), "listing_rooms"] = 1

    dataframe = dataframe.dropna(subset=["area_sqm"])

    dataframe["area_sqm"] = (
        dataframe["area_sqm"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    dataframe["price"] = (
        dataframe["price"]
        .astype(str)
        .str.replace(r"[^\d]", "", regex=True)
        .astype(int)
    )

    dataframe = dataframe[
        (dataframe["area_sqm"] > 8)
        & (dataframe["price"] > 10_000)
    ]

    if "listing_bedrooms" in dataframe.columns:
        missing_bedrooms = dataframe["listing_bedrooms"].isna()

        dataframe.loc[
            missing_bedrooms & (dataframe["listing_rooms"] == 1),
            "listing_bedrooms",
        ] = 1

        dataframe.loc[
            missing_bedrooms & (dataframe["listing_rooms"] > 1),
            "listing_bedrooms",
        ] = (
            dataframe.loc[
                missing_bedrooms & (dataframe["listing_rooms"] > 1),
                "listing_rooms",
            ]
            - 1
        )

    dataframe["listing_rooms"] = dataframe["listing_rooms"].astype(int)

    if "listing_bedrooms" in dataframe.columns:
        dataframe["listing_bedrooms"] = dataframe[
            "listing_bedrooms"
        ].astype(int)

    columns_to_drop = [
        "url",
        "attributes",
        "energy_expenses_eur",
    ]
    existing_columns_to_drop = [
        column for column in columns_to_drop if column in dataframe.columns
    ]

    if existing_columns_to_drop:
        dataframe = dataframe.drop(columns=existing_columns_to_drop)

    dataframe = dataframe.rename(
        columns={
            "search_city": "district",
            "listing_rooms": "rooms",
            "listing_bedrooms": "bedrooms",
        }
    )

    dataframe["price_per_sqm"] = dataframe["price"] / dataframe["area_sqm"]
    dataframe["district_number"] = dataframe["district"].map(
        DISTRICT_LABEL_TO_NUMBER
    )
    dataframe["housing_type"] = dataframe["rooms"].apply(
        categorize_housing_type
    )

    return dataframe
