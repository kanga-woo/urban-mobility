import asyncio
import json
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import ingest, forecast, anomalies
from app.db import Database


app = FastAPI(title="Urban Mobility Insights")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(ingest.router, prefix="/ingest")
app.include_router(forecast.router, prefix="/forecast")
app.include_router(anomalies.router, prefix="/anomalies")


@app.on_event("startup")
async def startup():
await Database.connect()
# start background monitor for anomalies (example)
app.state.anomaly_task = asyncio.create_task(anomalies.anomaly_poller())


@app.on_event("shutdown")
async def shutdown():
await Database.disconnect()
app.state.anomaly_task.cancel()


@app.get("/health")
async def health():
return {"status": "ok"}
