import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.api import ingest, forecast, anomalies
from app.db import Database

app = FastAPI(title="Urban Mobility Insights")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://frontend:3000",
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router, prefix="/ingest", tags=["Ingestion"])
app.include_router(forecast.router, prefix="/forecast", tags=["Forecasting"])
app.include_router(anomalies.router, prefix="/anomalies", tags=["Anomalies"])

Instrumentator().instrument(app).expose(app)

@app.on_event("startup")
async def startup():
    await Database.connect()
    # ensure anomaly trigger exists in DB will be created in anomalies module startup

@app.on_event("shutdown")
async def shutdown():
    await Database.disconnect()

@app.get("/health")
async def health():
    return {"status": "ok"}
