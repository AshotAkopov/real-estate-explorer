import unittest

import pandas as pd

from real_estate_explorer.preprocessing import prepare_listings


class TestPreprocessing(unittest.TestCase):
    """Tests for the data preprocessing module."""

    def setUp(self):
        """Create a small test DataFrame."""
        self.dataframe = pd.DataFrame(
            {
                "listing_id": [1, 1, 2],
                "listing_rooms": [None, 2, 3],
                "listing_bedrooms": [None, None, 2],
                "price": ["100 000 €", "200000€", "300000€"],
                "area_sqm": ["25", "40", "60"],
                "search_city": ["Lyon 1", "Lyon 1", "Lyon 2"],
                "url": ["a", "b", "c"],
                "attributes": ["x", "y", "z"],
                "energy_expenses_eur": [1000, 2000, 3000],
            }
        )

    def test_duplicates_and_unused_columns_are_removed(self):
        prepared = prepare_listings(self.dataframe)

        self.assertEqual(len(prepared), 2)
        self.assertIn("listing_id", prepared.columns)
        self.assertNotIn("url", prepared.columns)
        self.assertNotIn("attributes", prepared.columns)
        self.assertNotIn("energy_expenses_eur", prepared.columns)

    def test_columns_are_renamed(self):
        prepared = prepare_listings(self.dataframe)

        self.assertIn("district", prepared.columns)
        self.assertIn("rooms", prepared.columns)
        self.assertIn("bedrooms", prepared.columns)
        self.assertNotIn("search_city", prepared.columns)
        self.assertNotIn("listing_rooms", prepared.columns)
        self.assertNotIn("listing_bedrooms", prepared.columns)

    def test_price_is_converted_to_integer(self):
        prepared = prepare_listings(self.dataframe)

        self.assertTrue(pd.api.types.is_integer_dtype(prepared["price"]))
        self.assertEqual(prepared.iloc[0]["price"], 100000)

    def test_area_is_converted_to_float(self):
        prepared = prepare_listings(self.dataframe)

        self.assertTrue(pd.api.types.is_float_dtype(prepared["area_sqm"]))
        self.assertEqual(prepared.iloc[0]["area_sqm"], 25.0)

    def test_missing_bedrooms_are_computed(self):
        prepared = prepare_listings(self.dataframe)

        self.assertFalse(prepared["bedrooms"].isna().any())
        self.assertEqual(prepared.iloc[0]["bedrooms"], 1)

    def test_final_column_types(self):
        prepared = prepare_listings(self.dataframe)

        self.assertTrue(pd.api.types.is_integer_dtype(prepared["rooms"]))
        self.assertTrue(pd.api.types.is_integer_dtype(prepared["bedrooms"]))

    def test_derived_columns_are_created(self):
        prepared = prepare_listings(self.dataframe)

        self.assertIn("price_per_sqm", prepared.columns)
        self.assertIn("district_number", prepared.columns)
        self.assertIn("housing_type", prepared.columns)

        self.assertEqual(prepared.iloc[0]["price_per_sqm"], 4000.0)
        self.assertEqual(prepared.iloc[0]["district_number"], 1)
        self.assertEqual(prepared.iloc[0]["housing_type"], "Studio/T1")
        self.assertEqual(prepared.iloc[1]["housing_type"], "T3")

    def test_unrealistic_values_are_filtered(self):
        dataframe = pd.DataFrame(
            {
                "listing_id": [1, 2, 3],
                "listing_rooms": [1, 2, 3],
                "listing_bedrooms": [1, 1, 2],
                "price": ["9000€", "200000€", "300000€"],
                "area_sqm": ["20", "7", "60"],
                "search_city": ["Lyon 1", "Lyon 2", "Lyon 3"],
            }
        )

        prepared = prepare_listings(dataframe)

        self.assertEqual(len(prepared), 1)
        self.assertEqual(prepared.iloc[0]["district"], "Lyon 3")


if __name__ == "__main__":
    unittest.main()
