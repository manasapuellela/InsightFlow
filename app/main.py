import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import health, metrics, transactions
from app.models import transaction as transaction_model
from app.models.base import Base
from app.services.database import engine
from app.utils.logging import CorrelationIdMiddleware, setup_logging

setup_logging()

app = FastAPI(title="InsightFlow API", version="0.1.0")

app.include_router(health.router, tags=["health"])
app.include_router(transactions.router)
app.include_router(metrics.router)
app.add_middleware(CorrelationIdMiddleware)


@app.on_event("startup")
def on_startup() -> None:
    _ = transaction_model.Transaction
    Base.metadata.create_all(bind=engine)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logging.getLogger(__name__).exception(
        "Unhandled exception", extra={"correlation_id": request.state.correlation_id}
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error."},
    )
