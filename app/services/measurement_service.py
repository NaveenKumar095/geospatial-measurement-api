import geopandas as gpd
import pandas as pd


def make_json_safe(value):
    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    if hasattr(value, "item"):
        return value.item()

    return value


def calculate_measurements(gdf: gpd.GeoDataFrame) -> list[dict]:
    results = []

    for index, row in gdf.iterrows():
        geometry = row.geometry
        geometry_type = geometry.geom_type

        result = {
            "feature_id": int(index),
            "geometry_type": geometry_type,
            "properties": {
                key: make_json_safe(value)
                for key, value in row.items()
                if key != "geometry"
            },
        }

        if geometry_type in {"Polygon", "MultiPolygon"}:
            result["area_m2"] = geometry.area

        elif geometry_type in {"LineString", "MultiLineString"}:
            result["length_m"] = geometry.length

        elif geometry_type == "Point":
            result["area_m2"] = None
            result["length_m"] = None

        else:
            result["area_m2"] = None
            result["length_m"] = None
            result["warning"] = (
                f"Measurement not supported for geometry type: {geometry_type}"
            )

        results.append(result)

    return results