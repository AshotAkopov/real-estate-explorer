import unittest
from unittest.mock import Mock, patch

from real_estate_explorer.scraper import ParuVenduScraper


class TestParuVenduScraper(unittest.TestCase):
    """Unit tests for the ParuVenduScraper class."""

    @patch("real_estate_explorer.scraper.webdriver.Chrome")
    def test_default_initialization(self, mock_chrome):
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver

        scraper = ParuVenduScraper(csv_path="data/test.csv")

        self.assertEqual(scraper.csv_path, "data/test.csv")
        self.assertEqual(len(scraper.locations), 9)
        self.assertEqual(scraper.driver, mock_driver)

    @patch("real_estate_explorer.scraper.webdriver.Chrome")
    def test_custom_locations_initialization(self, mock_chrome):
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver

        locations = [
            ("Lyon 1", "Lyon 1", "69001"),
            ("Lyon 2", "Lyon 2", "69002"),
        ]

        scraper = ParuVenduScraper(
            csv_path="data/test_custom.csv",
            locations=locations,
        )

        self.assertEqual(scraper.csv_path, "data/test_custom.csv")
        self.assertEqual(scraper.locations, locations)
        self.assertEqual(scraper.driver, mock_driver)

    @patch("real_estate_explorer.scraper.webdriver.Chrome")
    def test_parse_area(self, mock_chrome):
        mock_body = Mock()
        mock_body.get_attribute.return_value = (
            "Appartement de 48 m² avec balcon"
        )

        mock_driver = Mock()
        mock_driver.find_element.return_value = mock_body
        mock_chrome.return_value = mock_driver

        scraper = ParuVenduScraper(csv_path="data/test.csv")

        self.assertEqual(scraper.parse_area(), "48")

    @patch("real_estate_explorer.scraper.webdriver.Chrome")
    def test_parse_area_with_decimal_comma(self, mock_chrome):
        mock_body = Mock()
        mock_body.get_attribute.return_value = "Surface habitable : 42,5 m²"

        mock_driver = Mock()
        mock_driver.find_element.return_value = mock_body
        mock_chrome.return_value = mock_driver

        scraper = ParuVenduScraper(csv_path="data/test.csv")

        self.assertEqual(scraper.parse_area(), "42.5")

    def test_normalize_url_absolute(self):
        url = "https://www.paruvendu.fr/immobilier/annonce.htm"
        self.assertEqual(ParuVenduScraper.normalize_url(url), url)

    def test_normalize_url_relative(self):
        self.assertEqual(
            ParuVenduScraper.normalize_url("/immobilier/annonce.htm"),
            "https://www.paruvendu.fr/immobilier/annonce.htm",
        )

    def test_normalize_url_protocol_relative(self):
        self.assertEqual(
            ParuVenduScraper.normalize_url(
                "//www.paruvendu.fr/immobilier/annonce.htm"
            ),
            "https://www.paruvendu.fr/immobilier/annonce.htm",
        )

    def test_normalize_url_empty(self):
        self.assertEqual(ParuVenduScraper.normalize_url(""), "")

    def test_clean_text_multiple_spaces(self):
        self.assertEqual(
            ParuVenduScraper.clean_text(
                "  Bonjour   \n   tout   le   monde  "
            ),
            "Bonjour tout le monde",
        )

    def test_clean_text_empty(self):
        self.assertEqual(ParuVenduScraper.clean_text(""), "")

    def test_extract_room_count_standard(self):
        text = "48 m² | 2 pièces | 1 chambre"
        self.assertEqual(ParuVenduScraper.extract_room_count(text), "2")

    def test_extract_room_count_other_format(self):
        text = "4 pièces 3 chambres Garage Balcon"
        self.assertEqual(ParuVenduScraper.extract_room_count(text), "4")

    def test_extract_room_count_absent(self):
        text = "Appartement lumineux avec balcon"
        self.assertEqual(ParuVenduScraper.extract_room_count(text), "")

    def test_extract_bedroom_count_standard(self):
        text = "48 m² | 2 pièces | 1 chambre"
        self.assertEqual(ParuVenduScraper.extract_bedroom_count(text), "1")

    def test_extract_bedroom_count_plural(self):
        text = "4 pièces | 3 chambres | cave"
        self.assertEqual(ParuVenduScraper.extract_bedroom_count(text), "3")

    def test_extract_bedroom_count_absent(self):
        text = "Studio avec balcon"
        self.assertEqual(ParuVenduScraper.extract_bedroom_count(text), "")


if __name__ == "__main__":
    unittest.main()
