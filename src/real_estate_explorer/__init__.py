def __init__(
    self,
    csv_path: str | None = None,
    locations: list[tuple[str, str, str]] | None = None,
) -> None:
    """Initialize the scraper."""
    self.csv_path = str(csv_path or RAW_LISTINGS_CSV)
    self.locations = locations or self.DEFAULT_LOCATIONS

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_experimental_option(
        "prefs",
        {
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.notifications": 2,
        },
    )

    self.driver = webdriver.Chrome(options=options)
