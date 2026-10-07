from pathlib import Path
from zipfile import ZipFile


SUPPORTED_EXTENSIONS = {".shp", ".kml"}


def validate_zip_file(file_path: str) -> bool:
    path = Path(file_path)

    if not path.exists():
        return False

    if path.suffix.lower() != ".zip":
        return False

    with ZipFile(path, "r") as zip_file:
        for name in zip_file.namelist():
            extension = Path(name).suffix.lower()

            if extension in SUPPORTED_EXTENSIONS:
                return True

    return False