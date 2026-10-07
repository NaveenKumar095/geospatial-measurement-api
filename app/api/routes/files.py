from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.file import FileResponse, FileDetailResponse
from app.database import get_db
from app.models.file import UploadedFile
from app.services.file_service import save_uploaded_file
from app.utils.file_validation import validate_zip_file


router = APIRouter(prefix="/api/files", tags=["Files"])


@router.post("/", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    extension = Path(file.filename).suffix.lower()

    if extension != ".zip":
        raise HTTPException(
            status_code=400,
            detail="Only .zip files are supported",
        )

    file_path = save_uploaded_file(file)

    if not validate_zip_file(file_path):
        Path(file_path).unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail="ZIP must contain a .shp or .kml file",
        )

    uploaded_file = UploadedFile(
        filename=file.filename,
        file_path=file_path,
        status="uploaded",
    )

    db.add(uploaded_file)
    db.commit()
    db.refresh(uploaded_file)

    return {
        "id": uploaded_file.id,
        "filename": uploaded_file.filename,
        "file_path": uploaded_file.file_path,
        "status": uploaded_file.status,
    }

@router.get("/{file_id}", response_model=FileDetailResponse)
def get_file(
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

    return {
        "id": uploaded_file.id,
        "filename": uploaded_file.filename,
        "status": uploaded_file.status,
        "created_at": uploaded_file.created_at,
    }