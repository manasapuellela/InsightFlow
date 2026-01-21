from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.schemas.transactions import TransactionDailyMetric, TransactionMetricsSummary
from app.services import transactions as transaction_service

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/daily", response_model=list[TransactionDailyMetric])
def get_daily_metrics(
    session: Session = Depends(get_db_session),
) -> list[TransactionDailyMetric]:
    items = transaction_service.daily_metrics(session)
    return [TransactionDailyMetric(**item) for item in items]


@router.get("/summary", response_model=TransactionMetricsSummary)
def get_summary_metrics(
    session: Session = Depends(get_db_session),
) -> TransactionMetricsSummary:
    data = transaction_service.summary_metrics(session)
    return TransactionMetricsSummary(**data)
