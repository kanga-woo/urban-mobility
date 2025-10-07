import os
import argparse
import pandas as pd
from prophet import Prophet
import joblib
from sqlalchemy import create_engine

DB_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:example@timescaledb:5432/mobility")
MODEL_DIR = os.environ.get("MODEL_DIR", "/app/ml/model_store")
os.makedirs(MODEL_DIR, exist_ok=True)

def load_data_for_segment(segment, lookback_days=90):
    engine = create_engine(DB_URL)
    sql = f"""
    SELECT ts AT TIME ZONE 'UTC' as ts, value
    FROM observations
    WHERE sensor_id = '{segment}' AND ts >= now() - interval '{lookback_days} days'
    ORDER BY ts
    """
    df = pd.read_sql(sql, engine, parse_dates=['ts'])
    return df.rename(columns={'ts': 'ds', 'value': 'y'})

def train_and_save(segment, df=None):
    if df is None:
        df = load_data_for_segment(segment)
    if df is None or df.shape[0] < 24:
        print(f"Not enough data to train for {segment}")
        return None
    m = Prophet(yearly_seasonality=False, weekly_seasonality=True, daily_seasonality=True)
    m.fit(df)
    path = os.path.join(MODEL_DIR, f"prophet_{segment}.pkl")
    joblib.dump(m, path)
    print(f"Saved model for {segment} -> {path}")
    return path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--segment", required=True, help="sensor/segment id")
    args = parser.parse_args()
    train_and_save(args.segment)
