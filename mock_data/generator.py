import requests, random, time, os
from datetime import datetime, timedelta
from faker import Faker
fake = Faker()
BACKEND = os.environ.get('BACKEND_URL', 'http://backend:8000')
sensors = [f'sensor_{i}' for i in range(1, 8)]
while True:
    now = datetime.utcnow()
    batch = {"observations": []}
    for _ in range(20):
        batch["observations"].append({
            "sensor_id": random.choice(sensors),
            "ts": (now).isoformat(),
            "value": max(0, random.gauss(500, 120)),
            "tags": {"weather": random.choice(["clear","rain","fog"])}
        })
    try:
        r = requests.post(f"{BACKEND}/ingest/batch", json=batch, timeout=5)
        print("sent", len(batch["observations"]), r.status_code)
    except Exception as e:
        print("err", e)
    time.sleep(5)
