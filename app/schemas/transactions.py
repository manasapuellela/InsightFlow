from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TransactionBase(BaseModel):
    reference: str = Field(..., min_length=6, max_length=64)
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(..., min_length=3, max_length=3)
    status: str = Field(..., min_length=3, max_length=16)
    description: str | None = Field(default=None, max_length=255)
    occurred_at: datetime


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    status: str | None = Field(default=None, min_length=3, max_length=16)
    description: str | None = Field(default=None, max_length=255)
    occurred_at: datetime | None = None


class TransactionOut(TransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class TransactionList(BaseModel):
    items: list[TransactionOut]
    total: int


class TransactionMetricsSummary(BaseModel):
    total_count: int
    total_amount: Decimal
    avg_amount: Decimal
    success_rate: float
    failure_rate: float


class TransactionDailyMetric(BaseModel):
    day: datetime
    total_count: int
    total_amount: Decimal
    success_count: int
    failure_count: int
