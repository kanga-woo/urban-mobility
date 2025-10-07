from fastapi import APIRouter, HTTPException, Body, Query
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
import json, os, math
import joblib
import pandas as pd
from sqlalchemy import create_engine, text

router = APIRouter()
DB_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:example@timescaledb:5432/mobility")
MODEL_DIR = os.environ.get("MODEL_DIR", "./ml/model_store")
engine = create_engine(DB_URL, future=True)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2.0)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2.0)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def load_prophet_model(segment):
    path = os.path.join(MODEL_DIR, f"prophet_{segment}.pkl")
    if os.path.exists(path):
        return joblib.load(path)
    return None

def baseline_forecast_from_model_or_history(segment, horizon_hours=24):
    m = load_prophet_model(segment)
    if m:
        future = m.make_future_dataframe(periods=horizon_hours, freq='H')
        forecast = m.predict(future)
        out = forecast[['ds','yhat']].tail(horizon_hours)
        return [{"ts": row.ds.isoformat(), "pred": float(row.yhat)} for _, row in out.iterrows()]

    with engine.connect() as conn:
        q = text("""
            SELECT date_trunc('hour', ts) as hour, avg(value) as avg_val
            FROM observations
            WHERE sensor_id = :s AND ts >= now() - interval '14 days'
            GROUP BY hour
            ORDER BY hour
        """)
        rows = conn.execute(q, {"s": segment}).fetchall()
        if not rows:
            raise HTTPException(status_code=404, detail="No historical data for segment")
        by_hour = {}
        for r in rows:
            h = r.hour.hour
            by_hour.setdefault(h, []).append(float(r.avg_val))
        import statistics
        hourly_pattern = {h: statistics.mean(v) for h,v in by_hour.items()}
        now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        forecast = []
        for i in range(horizon_hours):
            t = now + timedelta(hours=i+1)
            base = hourly_pattern.get(t.hour, sum(hourly_pattern.values())/len(hourly_pattern))
            forecast.append({"ts": t.isoformat(), "pred": base})
        return forecast

def compute_spatial_uplift(event: Dict[str, Any], targets: List[Dict[str, Any]]):
    start = datetime.fromisoformat(event['start_ts']).replace(tzinfo=timezone.utc)
    end = datetime.fromisoformat(event['end_ts']).replace(tzinfo=timezone.utc)
    duration_hours = max(1, int((end - start).total_seconds() // 3600) + 1)
    attendance = float(event.get('expected_attendance', 1000))
    base_mag = min(5.0, math.sqrt(attendance) / 50.0)
    radius = max(1000, min(20000, attendance * 2))
    out = {}
    for t in targets:
        seg = t['segment']
        lat = t.get('lat'); lon = t.get('lon')
        if lat is None or lon is None:
            out[seg] = [1.0] * duration_hours
            continue
        d = haversine(event['lat'], event['lon'], lat, lon)
        sigma = radius / 2.0
        spatial = math.exp(-0.5 * (d / sigma) ** 2)
        peak_mult = 1.0 + base_mag * spatial
        series = []
        for h in range(duration_hours):
            rel = abs((h - duration_hours/2.0) / (duration_hours/2.0))
            time_factor = 1.0 - rel
            uplift = 1.0 + (peak_mult - 1.0) * time_factor
            series.append(uplift)
        out[seg] = series
    return out

@router.get("/")
async def health():
    return {"status":"ok"}

@router.get("/forecast")
async def forecast_endpoint(segment: str = Query(...), horizon_hours: int = Query(24)):
    fc = baseline_forecast_from_model_or_history(segment, horizon_hours=horizon_hours)
    return {"segment": segment, "forecast": fc}

@router.post("/simulate")
async def simulate_event(event: Dict[str, Any] = Body(...), horizon_hours: int = Body(24)):
    with engine.connect() as conn:
        res = conn.execute(text("SELECT sensor_id as segment, ST_Y(location::geometry) as lat, ST_X(location::geometry) as lon FROM sensors")).fetchall()
        targets = [{"segment": r.segment, "lat": float(r.lat) if r.lat else None, "lon": float(r.lon) if r.lon else None} for r in res]
    uplift_map = compute_spatial_uplift(event, targets)
    start = datetime.fromisoformat(event['start_ts']).replace(tzinfo=timezone.utc)
    end = datetime.fromisoformat(event['end_ts']).replace(tzinfo=timezone.utc)
    duration_hours = max(1, int((end - start).total_seconds() // 3600) + 1)
    results = {}
    for t in targets:
        seg = t['segment']
        try:
            base = baseline_forecast_from_model_or_history(seg, horizon_hours=duration_hours)
            uplift_series = uplift_map.get(seg, [1.0]*duration_hours)
            simulated = []
            for i, b in enumerate(base[:duration_hours]):
                simulated.append({"ts": b['ts'], "pred": b['pred'] * uplift_series[i]})
            results[seg] = simulated
        except Exception as e:
            results[seg] = {"error": str(e)}
    return {"event": event, "simulated_forecasts": results}
