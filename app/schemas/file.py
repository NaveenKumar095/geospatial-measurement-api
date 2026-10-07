from datetime import datetime

from pydantic import BaseModel


class FileResponse(BaseModel):
    id: int
    filename: str
    file_path: str
    status: str


class FileDetailResponse(BaseModel):
    id: int
    filename: str
    status: str
    created_at: datetime