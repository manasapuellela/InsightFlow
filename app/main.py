from fastapi import FastAPI

from app.api import health
from app.utils.logging import setup_logging

setup_logging()

app = FastAPI(title="InsightFlow API", version="0.1.0")

app.include_router(health.router, tags=["health"])
