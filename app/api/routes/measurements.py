from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.file import UploadedFile
from app.services.geospatial_service import get_geospatial_data
from app.services.crs_service import prepare_for_measurement
from app.services.measurement_service import calculate_measurements
from app.schemas.measurement import MeasurementResult


router = APIRouter(prefix="/api/files", tags=["Measurements"])


@router.get(
    "/{file_id}/measurements/",
    response_model=list[MeasurementResult],
)
def get_measurements(
    file_id: int,
    db: Session = Depends(get_db),
):
    uploaded_file = (
        db.query(UploadedFile)
        .filter(UploadedFile.id == file_id)
        .first()
    )

    if uploaded_file is None:
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    try:
        gdf = get_geospatial_data(uploaded_file.file_path)
        measured_gdf = prepare_for_measurement(gdf)

        return calculate_measurements(measured_gdf)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process geospatial file: {exc}",
        )