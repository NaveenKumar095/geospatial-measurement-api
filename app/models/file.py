from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.database import Base


class UploadedFile(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    status = Column(String, default="uploaded")
    created_at = Column(DateTime, default=datetime.utcnow)
    