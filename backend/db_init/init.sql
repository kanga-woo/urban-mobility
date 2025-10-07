CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS sensors (
  sensor_id TEXT PRIMARY KEY,
  location GEOMETRY(POINT, 4326),
  type TEXT,
  meta JSONB
);

CREATE TABLE IF NOT EXISTS observations (
    id SERIAL PRIMARY KEY,
    sensor_id TEXT NOT NULL,
    ts TIMESTAMPTZ NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    tags JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
SELECT create_hypertable('observations', 'ts', if_not_exists => TRUE);

CREATE TABLE IF NOT EXISTS anomalies (
    id SERIAL PRIMARY KEY,
    ts TIMESTAMPTZ NOT NULL,
    segment TEXT NOT NULL,
    score DOUBLE PRECISION,
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
SELECT create_hypertable('anomalies', 'ts', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_observations_sensor_ts ON observations (sensor_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_anomalies_segment_ts ON anomalies (segment, ts DESC);
