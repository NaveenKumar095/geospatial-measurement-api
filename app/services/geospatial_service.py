from pathlib import Path
from zipfile import ZipFile
import tempfile

import geopandas as gpd


SUPPORTED_EXTENSIONS = {".shp", ".kml"}


def extract_geospatial_file(zip_path: str) -> Path:
    temp_dir = Path(tempfile.mkdtemp())

    with ZipFile(zip_path, "r") as zip_file:
        zip_file.extractall(temp_dir)

    for file_path in temp_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            return file_path

    raise ValueError("No supported geospatial file found in ZIP")


def read_geospatial_file(file_path: Path) -> gpd.GeoDataFrame:
    return gpd.read_file(file_path)


def get_geospatial_data(zip_path: str) -> gpd.GeoDataFrame:
    geospatial_file = extract_geospatial_file(zip_path)

    return read_geospatial_file(geospatial_file)