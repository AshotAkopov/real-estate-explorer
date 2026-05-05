# Architecture du projet

## Objectif

`real_estate_explorer` est un projet Python qui permet de collecter, nettoyer, analyser et visualiser des annonces immobilières.

Le projet suit un pipeline simple :

```text
Scraping → Données brutes → Prétraitement → Données nettoyées → Visualisation

## Structure générale

real_estate_explorer/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── outputs/
│
├── docs/
│
├── src/
│   └── real_estate_explorer/
│       ├── config.py
│       ├── scraper.py
│       ├── preprocessing.py
│       ├── visualization.py
│       └── pipeline.py
│
├── tests/
│
├── pyproject.toml
└── requirements.txt