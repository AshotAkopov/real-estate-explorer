# Real Estate Explorer

Interactive real estate analysis and visualization project for Lyon districts.

---

## Project Overview

Real Estate Explorer is a Python project designed to scrape, preprocess, analyze, and visualize real estate listings in Lyon.

The project combines:
- web scraping with Selenium;
- data preprocessing and feature engineering;
- statistical aggregation;
- interactive geographic visualization using Folium.

The final output is an interactive HTML map displaying district-level housing statistics such as average prices and price per square meter.

---

## Features

- Automated scraping of apartment listings from ParuVendu
- Data cleaning and preprocessing pipeline
- Housing type categorization
- District-level statistical aggregation
- Interactive Folium visualization
- Modular project architecture
- Unit testing for core modules

---

## Project Structure

```text
real_estate_explorer/
├── data/
│   ├── raw/
│   └── processed/
│
├── docs/
│   ├── index.html
│   └── project_documentation.md
│
├── outputs/
│   └── real_estate_map.html
│
├── src/
│   └── real_estate_explorer/
│       ├── config.py
│       ├── pipeline.py
│       ├── preprocessing.py
│       ├── scraper.py
│       ├── visualization.py
│       └── __init__.py
│
├── tests/
│   ├── README.md
│   ├── test_preprocessing.py
│   ├── test_scraper.py
│   └── test_visualization.py
│
├── pyproject.toml
├── requirements.txt
└── .gitignore
```

---

## Workflow

The pipeline follows three main steps:

```text
Scraping → Preprocessing → Visualization
```

### 1. Scraping

Apartment listings are collected from ParuVendu using Selenium.

Collected information includes:
- district;
- price;
- area;
- number of rooms;
- number of bedrooms.

---

### 2. Preprocessing

The dataset is cleaned and transformed through:
- duplicate removal;
- missing value handling;
- type conversion;
- unrealistic value filtering;
- derived variable creation.

Derived features include:
- `price_per_sqm`
- `district_number`
- `housing_type`

---

### 3. Visualization

The processed dataset is aggregated by district and visualized through an interactive Folium map.

The final visualization includes:
- district polygons;
- average prices;
- average price per square meter;
- listing counts;
- housing-type statistics;
- interactive popups and tooltips.

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd real_estate_explorer
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

Run the full pipeline:

```bash
python -m real_estate_explorer.pipeline
```

The pipeline automatically:
- checks whether datasets already exist;
- launches scraping if necessary;
- preprocesses the data;
- generates the final interactive map.

---

## Interactive Map

The interactive visualization is available through GitHub Pages:

```text
https://ashotakopov.github.io/real_estate_explorer/
```

---

## Tests

Unit tests are implemented for:
- preprocessing;
- scraping utilities;
- visualization functions.

Run tests with:

```bash
pytest
```

---

## Technologies

- Python
- pandas
- Selenium
- Folium
- matplotlib
- GeoJSON
- unittest

---

## Authors

Ashot Akopov, Fadwa Drissi, Alicia Petrov, Farah Naji
