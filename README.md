# Urban Mobility Insights & Predictive Event Impact

## Overview
Full-stack project combining:
- FastAPI backend with TimescaleDB (Timescale) for time-series storage and real-time anomalies.
- Prophet-based forecasting and an event simulation endpoint.
- React frontend (Leaflet) visualizing live anomalies via SSE.
- Monitoring with Prometheus & Grafana; Node Exporter for host metrics.
- Docker Compose to run all components locally.

## Quickstart
1. Ensure Docker & Docker Compose are installed.
2. From project root run:
   ```bash
   docker-compose up --build
   ```
3. Access:
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000 (health at /health)
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3001 (admin/admin)

## What’s included
- `backend/` — FastAPI app, REST endpoints, SSE via LISTEN/NOTIFY, model training script.
- `frontend/` — React app with map and SSE client.
- `mock_data/` — generator sending fake sensor data to backend.
- `monitoring/` — Prometheus & Grafana configs.
- `docker-compose.yml` — orchestrates all services.
