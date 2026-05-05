import json
import os
import tempfile
import unittest
from unittest.mock import Mock, patch

import pandas as pd

import real_estate_explorer.visualization as visualization


class TestVisualization(unittest.TestCase):
    """Tests for the visualization module."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.csv_path = os.path.join(
            self.temp_dir.name,
            "paruvendu_listings_clean.csv",
        )
        self.output_path = os.path.join(
            self.temp_dir.name,
            "real_estate_map.html",
        )

        self.dataframe = pd.DataFrame(
            [
                {
                    "listing_id": 1,
                    "district": "Lyon 1",
                    "rooms": 1,
                    "bedrooms": 1,
                    "area_sqm": 20.0,
                    "price": 200000,
                    "price_per_sqm": 10000.0,
                    "district_number": 1,
                    "housing_type": "Studio/T1",
                },
                {
                    "listing_id": 2,
                    "district": "Lyon 1",
                    "rooms": 2,
                    "bedrooms": 1,
                    "area_sqm": 40.0,
                    "price": 300000,
                    "price_per_sqm": 7500.0,
                    "district_number": 1,
                    "housing_type": "T2",
                },
                {
                    "listing_id": 3,
                    "district": "Lyon 2",
                    "rooms": 3,
                    "bedrooms": 2,
                    "area_sqm": 60.0,
                    "price": 360000,
                    "price_per_sqm": 6000.0,
                    "district_number": 2,
                    "housing_type": "T3",
                },
            ]
        )
        self.dataframe.to_csv(self.csv_path, index=False)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_compute_stats_returns_expected_aggregations(self):
        district_stats, housing_type_stats = visualization.compute_stats(
            self.dataframe
        )

        self.assertIn("Lyon 1", district_stats["district"].values)
        self.assertIn("Lyon 2", district_stats["district"].values)

        lyon_1 = district_stats[district_stats["district"] == "Lyon 1"].iloc[0]
        self.assertEqual(lyon_1["listing_count"], 2)
        self.assertEqual(lyon_1["average_price"], 250000)
        self.assertEqual(lyon_1["average_area_sqm"], 30)
        self.assertEqual(lyon_1["average_price_per_sqm"], 8750)

        lyon_1_types = housing_type_stats[
            housing_type_stats["district"] == "Lyon 1"
        ]
        types = list(lyon_1_types["housing_type"].astype(str))
        self.assertEqual(types, ["Studio/T1", "T2"])

    def test_build_popup_html_contains_expected_information(self):
        district_row = {
            "listing_count": 2,
            "average_price": 250000,
            "average_price_per_sqm": 8750,
            "average_area_sqm": 30,
        }

        housing_type_table = pd.DataFrame(
            [
                {
                    "housing_type": "Studio/T1",
                    "listing_count": 1,
                    "average_price": 200000,
                    "average_price_per_sqm": 10000,
                },
                {
                    "housing_type": "T2",
                    "listing_count": 1,
                    "average_price": 300000,
                    "average_price_per_sqm": 7500,
                },
            ]
        )

        html = visualization.build_popup_html(
            "Lyon 1",
            district_row,
            housing_type_table,
        )

        self.assertIn("Lyon 1", html)
        self.assertIn("Listings", html)
        self.assertIn("By housing type", html)
        self.assertIn("Studio/T1", html)
        self.assertIn("T2", html)
        self.assertIn("250 000 €", html)

    def test_load_lyon_geojson_from_cache(self):
        cache_path = os.path.join(self.temp_dir.name, "test_geo.json")
        fake_geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"code": "69381"},
                    "geometry": {"type": "Polygon", "coordinates": []},
                },
                {
                    "type": "Feature",
                    "properties": {"code": "99999"},
                    "geometry": {"type": "Polygon", "coordinates": []},
                },
            ],
        }

        with open(cache_path, "w", encoding="utf-8") as file:
            json.dump(fake_geojson, file)

        with patch.object(visualization, "LYON_DISTRICTS_GEOJSON", cache_path):
            result = visualization.load_lyon_geojson()

        self.assertEqual(result["type"], "FeatureCollection")
        self.assertEqual(len(result["features"]), 1)
        self.assertEqual(result["features"][0]["properties"]["district"],
                         "Lyon 1")

    @patch("real_estate_explorer.visualization.requests.get")
    def test_load_lyon_geojson_downloads_when_cache_is_missing(self, mock_get):
        cache_path = os.path.join(self.temp_dir.name, "missing_geo.json")
        fake_geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"code": "69382"},
                    "geometry": {"type": "Polygon", "coordinates": []},
                }
            ],
        }

        fake_response = Mock()
        fake_response.json.return_value = fake_geojson
        fake_response.raise_for_status.return_value = None
        mock_get.return_value = fake_response

        with patch.object(visualization, "LYON_DISTRICTS_GEOJSON", cache_path):
            result = visualization.load_lyon_geojson()

        self.assertTrue(os.path.exists(cache_path))
        self.assertEqual(len(result["features"]), 1)
        self.assertEqual(result["features"][0]["properties"]["district"],
                         "Lyon 2")

    def test_build_map_returns_folium_map(self):
        district_stats, housing_type_stats = visualization.compute_stats(
            self.dataframe
        )

        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"district": "Lyon 1"},
                    "geometry": {"type": "Polygon", "coordinates": []},
                },
                {
                    "type": "Feature",
                    "properties": {"district": "Lyon 2"},
                    "geometry": {"type": "Polygon", "coordinates": []},
                },
            ],
        }

        map_ = visualization.build_map(
            geojson,
            district_stats,
            housing_type_stats,
        )

        self.assertIsInstance(map_, visualization.folium.Map)

    def test_main_generates_html_map(self):
        fake_geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"district": "Lyon 1"},
                    "geometry": {"type": "Polygon", "coordinates": []},
                },
                {
                    "type": "Feature",
                    "properties": {"district": "Lyon 2"},
                    "geometry": {"type": "Polygon", "coordinates": []},
                },
            ],
        }

        with patch.object(
            visualization,
            "CLEAN_LISTINGS_CSV",
            self.csv_path,
        ), patch.object(
            visualization,
            "REAL_ESTATE_MAP_HTML",
            self.output_path,
        ), patch.object(
            visualization,
            "load_lyon_geojson",
            return_value=fake_geojson,
        ):
            visualization.main()

        self.assertTrue(os.path.exists(self.output_path))
        self.assertGreater(os.path.getsize(self.output_path), 0)


if __name__ == "__main__":
    unittest.main()
