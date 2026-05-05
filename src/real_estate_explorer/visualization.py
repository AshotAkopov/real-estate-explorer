"""Create an interactive map of Lyon districts.

The map combines:
- colored district polygons from an official GeoJSON source
- clickable popups with housing-type statistics
- permanent labels showing district names and average prices per m²
- tooltips with summary statistics

The map combines:
- colored district polygons
  from an official GeoJSON source;
- clickable popups with housing-type
  statistics;
- permanent labels displaying district names
  and average prices per square meter;
- tooltips with summary statistics.

Output:
    real_estate_map.html
"""

from __future__ import annotations

import json
from pathlib import Path

import branca.colormap as cm
import folium
import pandas as pd
import requests

from real_estate_explorer.config import (
    CLEAN_LISTINGS_CSV,
    LYON_DISTRICTS_GEOJSON,
    REAL_ESTATE_MAP_HTML,
)

GEOJSON_URL = (
    "https://geo.api.gouv.fr/communes"
    "?codeDepartement=69"
    "&type=arrondissement-municipal"
    "&format=geojson"
    "&geometry=contour"
)

LYON_CODES = [f"6938{i}" for i in range(1, 10)]
CODE_TO_LABEL = {f"6938{i}": f"Lyon {i}" for i in range(1, 10)}
HOUSING_TYPE_ORDER = ["Studio/T1", "T2", "T3", "T4+"]

DISTRICT_COORDINATES = {
    1: [45.7676, 4.8343],
    2: [45.7530, 4.8280],
    3: [45.7565, 4.8630],
    4: [45.7770, 4.8270],
    5: [45.7600, 4.8050],
    6: [45.7720, 4.8530],
    7: [45.7380, 4.8400],
    8: [45.7370, 4.8720],
    9: [45.7800, 4.8050],
}


def compute_stats(
        dataframe: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute district-level and housing-type-level statistics.

    Args:
        dataframe: Cleaned listings DataFrame.

    Returns:
        A tuple containing:
        - statistics grouped by district;
        - statistics grouped by district and housing type.
    """
    district_stats = (
        dataframe.groupby("district")
        .agg(
            listing_count=("price", "count"),
            average_price=("price", "mean"),
            average_price_per_sqm=("price_per_sqm", "mean"),
            average_area_sqm=("area_sqm", "mean"),
        )
        .round(0)
        .reset_index()
    )

    housing_type_stats = (
        dataframe.groupby(["district", "housing_type"])
        .agg(
            listing_count=("price", "count"),
            average_price=("price", "mean"),
            average_price_per_sqm=("price_per_sqm", "mean"),
        )
        .round(0)
        .reset_index()
    )

    housing_type_stats["housing_type"] = pd.Categorical(
        housing_type_stats["housing_type"],
        categories=HOUSING_TYPE_ORDER,
        ordered=True,
    )

    housing_type_stats = housing_type_stats.sort_values(
        ["district", "housing_type"]
    )

    return district_stats, housing_type_stats


def load_lyon_geojson() -> dict:
    """Load Lyon district GeoJSON data from local cache or remote API.

    Returns:
        GeoJSON FeatureCollection filtered to Lyon's nine districts.

    Raises:
        RuntimeError: If the GeoJSON file cannot be downloaded.
    """
    cache_path = Path(LYON_DISTRICTS_GEOJSON)

    if cache_path.exists():
        print(f"GeoJSON loaded from cache: {LYON_DISTRICTS_GEOJSON}")
        data = json.loads(cache_path.read_text(encoding="utf-8"))
    else:
        print("Downloading GeoJSON from geo.api.gouv.fr...")

        try:
            response = requests.get(GEOJSON_URL, timeout=30)
            response.raise_for_status()
            data = response.json()
            cache_path.write_text(json.dumps(data), encoding="utf-8")
            print(f"GeoJSON cached at: {LYON_DISTRICTS_GEOJSON}")
        except Exception as error:
            raise RuntimeError(
                f"Unable to download GeoJSON data ({error}). "
                f"Open {GEOJSON_URL} in your browser and save the result as "
                f"'{LYON_DISTRICTS_GEOJSON}'."
            ) from error

    features = [
        feature
        for feature in data["features"]
        if feature["properties"].get("code") in LYON_CODES
    ]

    for feature in features:
        feature["properties"]["district"] = CODE_TO_LABEL[
            feature["properties"]["code"]
        ]

    return {"type": "FeatureCollection", "features": features}


def build_popup_html(
    district_label: str,
    district_row: dict,
    housing_type_table: pd.DataFrame,
) -> str:
    """Build the HTML content for a district popup."""
    rows = []

    for _, row in housing_type_table.iterrows():
        rows.append(
            "<tr>"
            "<td style='padding:4px 8px; border:1px solid #ddd;'>"
            f"{row['housing_type']}</td>"
            "<td style='padding:4px 8px; border:1px solid #ddd; "
            "text-align:center;'>"
            f"{int(row['listing_count'])}</td>"
            "<td style='padding:4px 8px; border:1px solid #ddd; "
            "text-align:right;'>"
            f"{row['average_price']:,.0f} €</td>"
            "<td style='padding:4px 8px; border:1px solid #ddd; "
            "text-align:right;'>"
            f"{row['average_price_per_sqm']:,.0f} €/m²</td>"
            "</tr>"
        )

    rows_html = "\n".join(rows)

    html = (
        "<div style='font-family: sans-serif; min-width: 290px;'>"
        "<h4 style='margin: 0 0 10px 0; font-size: 16px;'>"
        f"{district_label}</h4>"
        "<div style='line-height: 1.6; font-size: 13px;'>"
        f"<b>Listings:</b> {int(district_row['listing_count'])}<br>"
        f"<b>Average price:</b> {district_row['average_price']:,.0f} €<br>"
        "<b>Average price per m²:</b> "
        f"{district_row['average_price_per_sqm']:,.0f} €/m²<br>"
        "<b>Average area:</b> "
        f"{district_row['average_area_sqm']:.0f} m²"
        "</div>"
        "<div style='font-weight:600; margin-top:10px; font-size:13px;'>"
        "By housing type"
        "</div>"
        "<table style='border-collapse: collapse; font-size: 12px; "
        "margin-top: 4px; width: 100%;'>"
        "<tr style='background: #f2f2f2;'>"
        "<th style='padding:4px 8px; border:1px solid #ddd; "
        "text-align:left;'>Type</th>"
        "<th style='padding:4px 8px; border:1px solid #ddd;'>Count</th>"
        "<th style='padding:4px 8px; border:1px solid #ddd;'>"
        "Average price</th>"
        "<th style='padding:4px 8px; border:1px solid #ddd;'>€/m²</th>"
        "</tr>"
        f"{rows_html}"
        "</table>"
        "</div>"
    )

    return html.replace(",", " ")


def build_map(
    geojson: dict,
    district_stats: pd.DataFrame,
    housing_type_stats: pd.DataFrame,
) -> folium.Map:
    """Build the Folium map with colored polygons, popups, and labels."""
    map_ = folium.Map(
        location=[45.758, 4.835],
        zoom_start=12,
        tiles="CartoDB positron",
        control_scale=True,
    )

    title_html = """
    <div style="position: fixed; top: 10px; right: 10px;
                z-index: 9999;
                background: white; padding: 10px 20px;
                border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.2);
                font-family: sans-serif; font-size: 16px; font-weight: 600;">
        Real estate in Lyon — average price per m² by district
        <div style="font-size: 11px; font-weight: 400; color: #666;
                    margin-top: 4px;">
            Click on a district to see details by housing type
        </div>
    </div>
    """
    map_.get_root().html.add_child(folium.Element(title_html))

    stats_by_district = district_stats.set_index("district").to_dict(
        orient="index"
    )
    values = [
        stats["average_price_per_sqm"]
        for stats in stats_by_district.values()
    ]

    min_value = min(values)
    max_value = max(values)

    colormap = cm.LinearColormap(
        colors=["#fee6ce", "#fd8d3c", "#7f2704"],
        vmin=min_value,
        vmax=max_value,
    )
    colormap.caption = "Average price per m² (€)"

    for feature in geojson["features"]:
        district_label = feature["properties"]["district"]
        row = stats_by_district.get(district_label)

        if row is None:
            folium.GeoJson(
                feature,
                style_function=lambda _: {
                    "fillColor": "#cccccc",
                    "color": "white",
                    "weight": 2,
                    "fillOpacity": 0.4,
                },
            ).add_to(map_)
            continue

        color = colormap(row["average_price_per_sqm"])
        district_housing_types = housing_type_stats[
            housing_type_stats["district"] == district_label
        ]
        popup_html = build_popup_html(
            district_label,
            row,
            district_housing_types,
        )

        average_price = f"{int(row['average_price']):,}".replace(",", " ")
        average_price_per_sqm = (
            f"{int(row['average_price_per_sqm']):,}".replace(",", " ")
        )

        folium.GeoJson(
            feature,
            style_function=lambda _, fill_color=color: {
                "fillColor": fill_color,
                "color": "white",
                "weight": 2,
                "fillOpacity": 0.75,
            },
            highlight_function=lambda _: {
                "color": "#222",
                "weight": 3.5,
                "fillOpacity": 0.9,
            },
            tooltip=folium.Tooltip(
                f"<b>{district_label}</b><br>"
                f"Listings: {int(row['listing_count'])}<br>"
                f"Average price: {average_price} €<br>"
                f"Average price per m²: {average_price_per_sqm} €/m²"
            ),
            popup=folium.Popup(popup_html, max_width=500),
        ).add_to(map_)

    for district_number, coordinates in DISTRICT_COORDINATES.items():
        district_label = f"Lyon {district_number}"
        row = stats_by_district.get(district_label)

        if row is None:
            continue

        average_price_per_sqm = (
            f"{int(row['average_price_per_sqm']):,}".replace(",", " ")
        )

        label_html = f"""
        <div style="font-size: 10px; font-weight: 600; color: #222;
                    background: white; border: 1px solid #444;
                    border-radius: 4px; padding: 2px 1px;
                    text-align: center;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.25);
                    pointer-events: none;">
            {average_price_per_sqm} €/m²
        </div>
        """

        folium.Marker(
            location=coordinates,
            icon=folium.DivIcon(
                icon_size=(60, 30),
                icon_anchor=(42, 15),
                html=label_html,
            ),
        ).add_to(map_)

    # colormap.add_to(map_)

    return map_


def main() -> None:
    """Generate and save the Lyon real estate map."""
    dataframe = pd.read_csv(CLEAN_LISTINGS_CSV)

    district_stats, housing_type_stats = compute_stats(dataframe)
    geojson = load_lyon_geojson()

    map_ = build_map(geojson, district_stats, housing_type_stats)
    map_.save(REAL_ESTATE_MAP_HTML)

    print(f"Map saved: {REAL_ESTATE_MAP_HTML}")


if __name__ == "__main__":
    main()
