from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Observation(BaseModel):
    sensor_id: str
    ts: datetime
    value: float
    tags: Optional[dict] = None

class BatchObservations(BaseModel):
    observations: List[Observation]

class ForecastRequest(BaseModel):
    segment: str
    horizon_hours: int = 24
    simulate_event: Optional[dict] = None
