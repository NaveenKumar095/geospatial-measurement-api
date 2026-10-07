from fastapi import FastAPI

from app.database import Base, engine
from app.models.file import UploadedFile
from app.api.routes.files import router as files_router
from app.api.routes.measurements import router as measurements_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Geospatial File Measurement API",
    version="1.0.0",
)

app.include_router(files_router)
app.include_router(measurements_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}