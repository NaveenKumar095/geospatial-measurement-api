from typing import Any

from pydantic import BaseModel


class MeasurementResult(BaseModel):
    feature_id: int
    geometry_type: str
    properties: dict[str, Any]
    area_m2: float | None = None
    length_m: float | None = None
    warning: str | None = None