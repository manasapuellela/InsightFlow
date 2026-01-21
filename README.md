# InsightFlow

InsightFlow is a cloud-native data and API platform that ingests data from multiple sources, validates and processes it, stores it efficiently, and exposes it via APIs for analytics and insights.

## Architecture (Day 1)

```
insightflow/
├── app/
│   ├── api/
│   ├── services/
│   ├── models/
│   ├── schemas/
│   ├── utils/
│   └── main.py
├── tests/
├── docker/
├── README.md
```

## Local Development

### Requirements

- Python 3.11+
- PostgreSQL 14+

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run the API

```bash
uvicorn app.main:app --reload
```

### Health Check

```bash
curl http://localhost:8000/health
```

## Docker

```bash
docker compose -f docker/docker-compose.yml up --build
```
