from pathlib import Path

import geopandas as gpd
from shapely.geometry import Polygon, LineString, Point

from app.services.crs_service import prepare_for_measurement
from app.services.measurement_service import calculate_measurements


def test_polygon_area():
    gdf = gpd.GeoDataFrame(
        {
            "name": ["Polygon"],
            "geometry": [
                Polygon([
                    (77.5946, 12.9716),
                    (77.6046, 12.9716),
                    (77.6046, 12.9816),
                    (77.5946, 12.9816),
                    (77.5946, 12.9716),
                ])
            ],
        },
        crs="EPSG:4326",
    )

    measured = prepare_for_measurement(gdf)
    result = calculate_measurements(measured)

    assert result[0]["geometry_type"] == "Polygon"
    assert result[0]["area_m2"] > 0
    assert "length_m" not in result[0]


def test_linestring_length():
    gdf = gpd.GeoDataFrame(
        {
            "name": ["Line"],
            "geometry": [
                LineString([
                    (77.5946, 12.9716),
                    (77.6046, 12.9816),
                ])
            ],
        },
        crs="EPSG:4326",
    )

    measured = prepare_for_measurement(gdf)
    result = calculate_measurements(measured)

    assert result[0]["geometry_type"] == "LineString"
    assert result[0]["length_m"] > 0
    assert "area_m2" not in result[0]


def test_point_has_no_measurement():
    gdf = gpd.GeoDataFrame(
        {
            "name": ["Point"],
            "geometry": [
                Point(77.5996, 12.9766)
            ],
        },
        crs="EPSG:4326",
    )

    measured = prepare_for_measurement(gdf)
    result = calculate_measurements(measured)

    assert result[0]["geometry_type"] == "Point"
    assert result[0]["area_m2"] is None
    assert result[0]["length_m"] is None


def test_geographic_crs_is_projected():
    gdf = gpd.GeoDataFrame(
        {
            "geometry": [
                Point(77.5996, 12.9766)
            ]
        },
        crs="EPSG:4326",
    )

    measured = prepare_for_measurement(gdf)

    assert measured.crs.is_projected