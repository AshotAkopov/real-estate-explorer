from __future__ import annotations

import csv
import re
from time import sleep
from typing import Any

from selenium import webdriver
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from real_estate_explorer.config import RAW_LISTINGS_CSV


class ParuVenduScraper:
    """Scrape ParuVendu real estate listings for Lyon districts."""

    DEFAULT_LOCATIONS = [
        ("Lyon 1", "Lyon 1", "69001"),
        ("Lyon 2", "Lyon 2", "69002"),
        ("Lyon 3", "Lyon 3", "69003"),
        ("Lyon 4", "Lyon 4", "69004"),
        ("Lyon 5", "Lyon 5", "69005"),
        ("Lyon 6", "Lyon 6", "69006"),
        ("Lyon 7", "Lyon 7", "69007"),
        ("Lyon 8", "Lyon 8", "69008"),
        ("Lyon 9", "Lyon 9", "69009"),
    ]

    FIELDNAMES = [
        "search_city",
        "listing_id",
        "price",
        "listing_rooms",
        "listing_bedrooms",
        "area_sqm",
    ]

    def __init__(
        self,
        csv_path: str | None = None,
        locations: list[tuple[str, str, str]] | None = None,
    ) -> None:
        """Initialize the scraper."""
        self.csv_path = str(csv_path or RAW_LISTINGS_CSV)
        self.locations = locations or self.DEFAULT_LOCATIONS
        self.driver = webdriver.Chrome()

    @staticmethod
    def clean_text(text: str) -> str:
        """Normalize whitespace in a text string."""
        return re.sub(r"\s+", " ", text or "").strip()

    @staticmethod
    def normalize_url(href: str) -> str:
        """Convert a relative or protocol-relative URL into an absolute URL."""
        if not href:
            return ""

        if href.startswith("http"):
            return href

        if href.startswith("//"):
            return f"https:{href}"

        if href.startswith("/"):
            return f"https://www.paruvendu.fr{href}"

        return href

    @staticmethod
    def extract_room_count(text: str) -> str:
        """Extract the number of rooms from a listing text."""
        if not text:
            return ""

        match = re.search(r"\b(\d+)\s*pi[eè]ce[s]?\b", text, flags=re.I)
        return match.group(1) if match else ""

    @staticmethod
    def extract_bedroom_count(text: str) -> str:
        """Extract the number of bedrooms from a listing text."""
        if not text:
            return ""

        match = re.search(r"\b(\d+)\s*chambre[s]?\b", text, flags=re.I)
        return match.group(1) if match else ""

    def click(self, xpath: str, timeout: int = 12) -> Any:
        """Click an element identified by an XPath selector."""
        element = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            element,
        )
        element.click()

        return element

    def accept_cookies(self) -> None:
        """Accept the cookie banner when it is displayed."""

        # Blocks the notification popup on the JavaScript side
        try:
            self.driver.execute_script(
                """
                if (window.Notification) {
                    Notification.requestPermission = function () {
                        return Promise.resolve('denied');
                    };
                }
                """
            )
        except Exception:
            pass

        xpaths = [
            '//button[contains(@onclick,"saveConsent")]',
            '//a[contains(@onclick,"saveConsent")]',
            '//button[contains(., "Accepter")]',
        ]

        for xpath in xpaths:
            try:
                WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                ).click()
                return
            except TimeoutException:
                continue

    def find_location_input(self, timeout: int = 15) -> Any:
        """Find the search input used for entering a location."""
        selectors = [
            (By.ID, "localisation-vente"),
            (By.NAME, "localisation"),
            (By.XPATH, '//input[contains(@id, "localisation")]'),
            (By.XPATH, '//input[contains(@name, "localisation")]'),
            (By.XPATH, '//input[@type="text"]'),
        ]

        for by, selector in selectors:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, selector))
                )
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    element,
                )
                return element
            except TimeoutException:
                continue

        raise TimeoutException("Location input field was not found.")

    def select_apartment_only(self) -> bool:
        """Select the apartment property type when available."""
        selects = self.driver.find_elements(By.TAG_NAME, "select")

        for select_tag in selects:
            try:
                select_obj = Select(select_tag)
                options = [
                    self.clean_text(opt.text) for opt in select_obj.options
                ]

                if "Appartement" in options:
                    select_obj.select_by_visible_text("Appartement")
                    return True
            except Exception:
                continue

        dropdown_xpaths = [
            '//*[self::div or self::button or self::span]'
            '[contains(normalize-space(.), "Appartement et Maison")]',
            '//*[self::div or self::button or self::span]'
            '[contains(normalize-space(.), "Appartement")]',
        ]

        for xpath in dropdown_xpaths:
            try:
                self.click(xpath, timeout=5)
                break
            except Exception:
                continue

        option_xpaths = [
            '//*[self::li or self::div or self::span or self::a]'
            '[normalize-space(.)="Appartement"]',
            '//*[self::li or self::div or self::span or self::a]'
            '[contains(normalize-space(.), "Appartement")]',
        ]

        for xpath in option_xpaths:
            try:
                self.click(xpath, timeout=5)
                return True
            except Exception:
                continue

        return False

    def set_search(self, city_text: str, postal_code: str) -> None:
        """Configure and submit the real estate search form."""
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        self.accept_cookies()

        location_input = self.find_location_input()
        location_input.clear()
        location_input.send_keys(city_text)

        self.click(
            f'//ul[starts-with(@id,"ui-id-")]'
            f'//li[contains(., "{postal_code}")]//a',
            timeout=15,
        )

        if not self.select_apartment_only():
            print("Warning: could not explicitly select apartment listings.")

        submit_xpaths = [
            '//input[@type="submit"]',
            '//button[contains(normalize-space(.), "Rechercher")]',
            '//*[self::a or self::button or self::input]'
            '[contains(normalize-space(.), "Rechercher")]',
        ]

        for xpath in submit_xpaths:
            try:
                self.click(xpath, timeout=10)
                return
            except Exception:
                continue

        raise TimeoutException("Search button was not found.")

    def scrape_results(self) -> list[dict[str, str]]:
        """Scrape listing cards from the current results page."""
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//div[@data-id]'))
        )

        cards = self.driver.find_elements(By.XPATH, '//div[@data-id]')
        results = []

        for card in cards:
            try:
                listing_id = card.get_attribute("data-id") or ""

                try:
                    price = card.find_element(
                        By.XPATH,
                        './/*[contains(text(),"€")]',
                    ).text.strip()
                except Exception:
                    price = ""

                try:
                    card_text = self.clean_text(card.text)
                except Exception:
                    card_text = ""

                try:
                    href = card.find_element(
                        By.XPATH,
                        './/a[@href][1]',
                    ).get_attribute("href")
                except Exception:
                    href = ""

                results.append(
                    {
                        "listing_id": listing_id,
                        "price": price,
                        "listing_rooms": self.extract_room_count(card_text),
                        "listing_bedrooms": self.extract_bedroom_count(
                            card_text
                        ),
                        "url": self.normalize_url(href),
                    }
                )

            except StaleElementReferenceException:
                continue

        return results

    def parse_area(self) -> str:
        """Extract the listing area from the current listing page."""
        WebDriverWait(self.driver, 12).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        body_text = (
            self.driver.find_element(By.TAG_NAME, "body")
            .get_attribute("innerText")
            or ""
        )

        match = re.search(
            r"\b(\d{1,4}(?:[.,]\d+)?)\s*(m2|m²)\b",
            body_text,
            flags=re.I,
        )

        if not match:
            return ""

        return match.group(1).replace(",", ".")

    def area_in_new_tab(self, url: str) -> str:
        """Open a listing in a new tab and extract its area."""
        original_handle = self.driver.current_window_handle
        previous_handles = set(self.driver.window_handles)

        self.driver.execute_script("window.open(arguments[0], '_blank');", url)
        WebDriverWait(self.driver, 10).until(
            lambda driver: len(driver.window_handles) > len(previous_handles)
        )

        new_handle = [
            handle
            for handle in self.driver.window_handles
            if handle not in previous_handles
        ][0]

        self.driver.switch_to.window(new_handle)
        area_sqm = self.parse_area()
        self.driver.close()
        self.driver.switch_to.window(original_handle)

        return area_sqm

    def next_page(self) -> bool:
        """Go to the next results page when available."""
        next_buttons = self.driver.find_elements(
            By.XPATH,
            '//div[contains(@class,"pgsuiv")]//a',
        )

        if not next_buttons:
            return False

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            next_buttons[0],
        )

        try:
            next_buttons[0].click()
        except Exception:
            self.driver.execute_script(
                "arguments[0].click();",
                next_buttons[0],
            )

        sleep(1.2)
        return True

    def scrape_location(
        self,
        writer: csv.DictWriter,
        city_label: str,
        city_query: str,
        postal_code: str,
    ) -> None:
        """Scrape all listings for a given city or district."""
        print(f"Searching: {city_label} | Apartment")

        self.driver.get("https://www.paruvendu.fr/immobilier/")
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        self.accept_cookies()
        self.set_search(city_query, postal_code)

        page = 1
        total_listings = 0

        while True:
            listings = self.scrape_results()
            print(f"{city_label} | Page {page} → {len(listings)} listings")

            for index, listing in enumerate(listings, start=1):
                total_listings += 1
                print(f"  [{total_listings}] listing {index}/{len(listings)}")

                area_sqm = ""
                if listing["url"]:
                    try:
                        area_sqm = self.area_in_new_tab(listing["url"])
                    except Exception:
                        pass

                writer.writerow(
                    {
                        "search_city": city_label,
                        "listing_id": listing["listing_id"],
                        "price": listing["price"],
                        "listing_rooms": listing["listing_rooms"],
                        "listing_bedrooms": listing["listing_bedrooms"],
                        "area_sqm": area_sqm,
                    }
                )

            if not self.next_page():
                break

            page += 1

        print(f"{city_label} → total: {total_listings} listings")

    def scrape(self) -> None:
        """Run the full scraping pipeline and write listings to a CSV file."""
        try:
            with open(
                self.csv_path,
                "w",
                newline="",
                encoding="utf-8",
            ) as file:
                writer = csv.DictWriter(file, fieldnames=self.FIELDNAMES)
                writer.writeheader()

                for city_label, city_query, postal_code in self.locations:
                    try:
                        self.scrape_location(
                            writer,
                            city_label,
                            city_query,
                            postal_code,
                        )
                    except Exception as error:
                        print(
                            f"Error while scraping {city_label}: "
                            f"{type(error).__name__}"
                        )
                        print(error)
                        continue

        finally:
            self.driver.quit()

        print(f"CSV created: {self.csv_path}")


def main() -> None:
    """Run the ParuVendu scraper."""
    scraper = ParuVenduScraper()
    scraper.scrape()


if __name__ == "__main__":
    main()
