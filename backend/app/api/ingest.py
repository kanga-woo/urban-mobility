from fastapi import APIRouter
from app.models import BatchObservations
from app.db import database
import json

router = APIRouter()

INSERT_SQL = """
INSERT INTO observations (sensor_id, ts, value, tags)
VALUES (:sensor_id, :ts, :value, :tags::jsonb)
"""


@router.post('/batch')
async def ingest_batch(payload: BatchObservations):
    async with database.transaction():
        for o in payload.observations:
            values = {
                "sensor_id": o.sensor_id,
                "ts": o.ts,
                "value": o.value,
                "tags": json.dumps(o.tags or {}),
            }
            await database.execute(query=INSERT_SQL, values=values)
    return {"ingested": len(payload.observations)}
