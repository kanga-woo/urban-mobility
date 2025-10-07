from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import asyncio, json, os, asyncpg
from datetime import datetime

router = APIRouter()
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:example@timescaledb:5432/mobility")

@router.on_event("startup")
async def startup():
    conn = await asyncpg.connect(DB_URL)
    await conn.execute("""
    CREATE OR REPLACE FUNCTION notify_anomaly()
    RETURNS trigger AS $$
    BEGIN
        PERFORM pg_notify('new_anomaly', row_to_json(NEW)::text);
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS anomalies_notify_trigger ON anomalies;
    CREATE TRIGGER anomalies_notify_trigger
    AFTER INSERT ON anomalies
    FOR EACH ROW
    EXECUTE FUNCTION notify_anomaly();
    """)
    await conn.close()

@router.get("/stream")
async def stream_anomalies(request: Request):
    async def event_generator():
        conn = await asyncpg.connect(DB_URL)
        queue = asyncio.Queue()

        async def listener(connection, pid, channel, payload):
            await queue.put(payload)

        await conn.add_listener("new_anomaly", listener)
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=15.0)
                    anomaly = json.loads(payload)
                    yield f"event: anomaly\ndata: {json.dumps(anomaly)}\n\n"
                except asyncio.TimeoutError:
                    yield f": heartbeat {datetime.utcnow().isoformat()}\n\n"
        finally:
            await conn.remove_listener("new_anomaly", listener)
            await conn.close()

    return StreamingResponse(event_generator(), media_type="text/event-stream")
