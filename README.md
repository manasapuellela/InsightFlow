# InsightFlow

## Problem statement
Teams need a lightweight, consistent way to ingest transaction data, standardize it, and expose reliable metrics without hard-coupling data access to API delivery. InsightFlow provides a simple transaction-centric service that organizes persistence, business rules, and HTTP delivery so future data sources and analytics can be added without reworking the core system.

## Architecture diagram (simple)

```
           +--------------------+
           |     API Clients    |
           +----------+---------+
                      |
                      v
+---------------------+---------------------+
|           FastAPI Application             |
|  app/main.py                              |
|  - Routers: health, transactions, metrics |
+---------------------+---------------------+
                      |
                      v
+---------------------+---------------------+
|         Service Layer (app/services)      |
|  - transaction CRUD                        |
|  - metrics aggregation                     |
+---------------------+---------------------+
                      |
                      v
+---------------------+---------------------+
|        Data Layer (SQLAlchemy ORM)        |
|  - models, schemas, session management    |
+---------------------+---------------------+
                      |
                      v
+---------------------+---------------------+
|              PostgreSQL Database          |
+-------------------------------------------+
```

## Tech stack
- **FastAPI** for HTTP routing and request/response handling.
- **SQLAlchemy** ORM for persistence and query composition.
- **Pydantic** models for input/output validation.
- **PostgreSQL** as the primary datastore (local via Docker).
- **Uvicorn** ASGI server for local development.

## Current features
- Health endpoint (`GET /health`) to confirm service availability.
- Transaction CRUD endpoints (`/transactions`) with pagination and status filtering.
- CSV ingestion endpoint (`POST /transactions/ingest/csv`) with validation and duplicate reference handling.
- Metrics endpoints (`/metrics/daily`, `/metrics/summary`) for aggregated transaction insights.
- Correlation ID logging middleware for request tracing.

## Planned layers (roadmap)
- **Data connectors** for external ingestion sources (files, third-party APIs).
- **Domain workflows** for enriched transaction classification and anomaly detection.
- **Delivery channels** beyond REST (CLI batch jobs, scheduled reports).
- **Observability** enhancements (structured logs, dashboards, alerts).
- **CI automation** for linting, type checks, and test execution.

## Repository structure
```
.
├── app
│   ├── api            # FastAPI routers and dependency injection
│   ├── models         # SQLAlchemy ORM models
│   ├── schemas        # Pydantic request/response models
│   ├── services       # Business logic and data access coordination
│   ├── utils          # Logging helpers and middleware
│   └── main.py        # FastAPI application entrypoint
├── docker
│   ├── Dockerfile
│   └── docker-compose.yml
├── tests              # Pytest coverage for API behaviors
├── requirements.txt
└── README.md
```

## How to run locally

### Option A: Docker Compose (recommended)
1. Build and start the API + database:
   ```bash
   docker compose -f docker/docker-compose.yml up --build
   ```
2. Open `http://localhost:8000/docs` for the interactive API docs.

### Option B: Run locally with Python
1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Ensure Postgres is running and export the connection string:
   ```bash
   export DATABASE_URL=postgresql+psycopg2://insightflow:insightflow@localhost:5432/insightflow
   ```
3. Start the API:
   ```bash
   uvicorn app.main:app --reload
   ```

## What you learned so far
- Keeping request validation in Pydantic schemas makes ingestion errors easy to surface early.
- Separating CRUD and metrics logic into service modules keeps API routes thin and predictable.
- A small middleware layer (correlation IDs) improves observability without changing route logic.
- Docker Compose offers the fastest repeatable environment for local API + database development.
