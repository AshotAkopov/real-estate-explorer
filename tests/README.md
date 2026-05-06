# Tests

This directory contains unit tests for the project modules.

The objective of these tests is to validate:
- preprocessing consistency;
- scraping utility behavior;
- statistical aggregation correctness;
- visualization generation.

---

## test_preprocessing.py

Tests the preprocessing pipeline:
- duplicate removal;
- type conversion;
- derived variable creation;
- unrealistic value filtering.

---

## test_scraper.py

Tests scraping utilities:
- URL normalization;
- text cleaning;
- room and bedroom extraction;
- area parsing.

Selenium interactions are mocked to isolate parsing logic.

---

## test_visualization.py

Tests the visualization pipeline:
- aggregation computation;
- popup HTML generation;
- GeoJSON loading;
- Folium map generation;
- HTML export.

Temporary directories and mocked objects are used to isolate outputs.

---

## Run tests

```bash
pytest
```
