# Methodology

## Data Collection

Real estate listings were collected from ParuVendu using Selenium-based web scraping.

The scraper extracts:
- district information;
- listing prices;
- property area;
- number of rooms;
- number of bedrooms.

The collected data are stored as raw CSV files before preprocessing.

---

## Data Cleaning

Several preprocessing steps were applied to improve data quality and consistency.

### Duplicate Removal

Duplicate listings are removed using listing identifiers.

---

### Type Conversion

Text-based numerical variables are converted into numeric formats:
- prices → integers;
- areas → floats.

Examples:
- `"200 000 €"` → `200000`
- `"42,5 m²"` → `42.5`

---

### Missing Values

Missing bedroom counts are estimated using room information when possible.

---

### Unrealistic Value Filtering

Listings with unrealistic values are removed to improve robustness.

Examples:
- extremely low prices;
- very small areas.

---

## Feature Engineering

Several derived variables are created during preprocessing.

### Price per Square Meter

```text
price_per_sqm = price / area_sqm
```

This metric allows district-level comparison independently of apartment size.

---

### Housing Type Categorization

Properties are categorized according to the number of rooms:

| Rooms | Category |
|---|---|
| 1 | Studio/T1 |
| 2 | T2 |
| 3 | T3 |
| 4+ | T4+ |

---

### District Number

District names are converted into numerical arrondissement identifiers.

Example:

```text
Lyon 1 → 1
```

---

## Statistical Aggregation

District-level statistics are computed:
- average price;
- average area;
- average price per square meter;
- listing counts.

Additional aggregations are computed by housing type.

---

## Visualization

An interactive Folium map is generated using Lyon district GeoJSON boundaries.

The visualization includes:
- district polygons;
- choropleth-style coloring;
- interactive popups;
- housing-type summaries.

---

## Limitations

The project has several limitations:

- scraped listings may contain inconsistencies;
- online listings may not represent the entire housing market;
- district-level averages may hide local heterogeneity;
- scraping results may evolve over time as listings change.
