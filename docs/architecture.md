# Project Architecture

## Overview

The project follows a modular data pipeline architecture.

```text
Scraping → Preprocessing → Aggregation → Visualization
```

Each module is isolated to improve readability, maintainability, and testing.

---

## Modules

### scraper.py

Responsible for:
- web scraping;
- parsing listing information;
- text normalization;
- exporting raw data.

---

### preprocessing.py

Responsible for:
- data cleaning;
- missing value handling;
- feature engineering;
- filtering unrealistic observations.

---

### visualization.py

Responsible for:
- statistical aggregation;
- GeoJSON processing;
- Folium visualization;
- HTML export.

---

### pipeline.py

Central orchestration module connecting all pipeline stages.

The pipeline:
1. checks dataset availability;
2. launches scraping if necessary;
3. preprocesses the data;
4. generates the interactive map.

---

## Testing Strategy

Unit tests are implemented separately for:
- preprocessing;
- scraping utilities;
- visualization functions.

The modular architecture simplifies isolated testing and debugging.

---

## Outputs

The project generates:
- cleaned datasets;
- district-level statistics;
- interactive HTML visualizations.
