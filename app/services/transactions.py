from __future__ import annotations

from collections.abc import Iterable
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Select, case, func, select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.schemas.transactions import TransactionCreate, TransactionUpdate


def create_transaction(session: Session, payload: TransactionCreate) -> Transaction:
    transaction = Transaction(
        reference=payload.reference,
        amount=payload.amount,
        currency=payload.currency.upper(),
        status=payload.status.lower(),
        description=payload.description,
        occurred_at=payload.occurred_at,
    )
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


def get_transaction(session: Session, transaction_id: int) -> Transaction | None:
    return session.get(Transaction, transaction_id)


def get_transaction_by_reference(
    session: Session, reference: str
) -> Transaction | None:
    statement: Select[tuple[Transaction]] = select(Transaction).where(
        Transaction.reference == reference
    )
    return session.scalar(statement)


def list_transactions(
    session: Session,
    offset: int,
    limit: int,
    status: str | None = None,
) -> tuple[list[Transaction], int]:
    statement: Select[tuple[Transaction]] = select(Transaction)
    count_statement = select(func.count(Transaction.id))
    if status:
        normalized = status.lower()
        statement = statement.where(Transaction.status == normalized)
        count_statement = count_statement.where(Transaction.status == normalized)
    statement = statement.order_by(Transaction.occurred_at.desc()).offset(offset).limit(limit)
    items = session.scalars(statement).all()
    total = session.scalar(count_statement) or 0
    return items, int(total)


def update_transaction(
    session: Session, transaction: Transaction, payload: TransactionUpdate
) -> Transaction:
    data = payload.model_dump(exclude_unset=True)
    if "currency" in data:
        data["currency"] = data["currency"].upper()
    if "status" in data:
        data["status"] = data["status"].lower()
    for key, value in data.items():
        setattr(transaction, key, value)
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


def delete_transaction(session: Session, transaction: Transaction) -> None:
    session.delete(transaction)
    session.commit()


def batch_insert_transactions(
    session: Session, rows: Iterable[TransactionCreate]
) -> tuple[int, int]:
    created = 0
    skipped = 0
    for payload in rows:
        if get_transaction_by_reference(session, payload.reference):
            skipped += 1
            continue
        create_transaction(session, payload)
        created += 1
    return created, skipped


def daily_metrics(session: Session, start_date: date | None = None) -> list[dict[str, object]]:
    statement = (
        select(
            func.date(Transaction.occurred_at).label("day"),
            func.count(Transaction.id).label("total_count"),
            func.coalesce(func.sum(Transaction.amount), 0).label("total_amount"),
            func.sum(case((Transaction.status == "success", 1), else_=0)).label(
                "success_count"
            ),
            func.sum(case((Transaction.status == "failed", 1), else_=0)).label(
                "failure_count"
            ),
        )
        .group_by(func.date(Transaction.occurred_at))
        .order_by(func.date(Transaction.occurred_at))
    )
    if start_date:
        statement = statement.where(Transaction.occurred_at >= start_date)
    results = session.execute(statement).all()
    return [
        {
            "day": datetime.combine(row.day, datetime.min.time()),
            "total_count": row.total_count,
            "total_amount": Decimal(row.total_amount),
            "success_count": row.success_count,
            "failure_count": row.failure_count,
        }
        for row in results
    ]


def summary_metrics(session: Session) -> dict[str, object]:
    totals = session.execute(
        select(
            func.count(Transaction.id),
            func.coalesce(func.sum(Transaction.amount), 0),
            func.coalesce(func.avg(Transaction.amount), 0),
            func.sum(case((Transaction.status == "success", 1), else_=0)),
            func.sum(case((Transaction.status == "failed", 1), else_=0)),
        )
    ).one()
    total_count = int(totals[0] or 0)
    total_amount = Decimal(totals[1] or 0)
    avg_amount = Decimal(totals[2] or 0)
    success_count = int(totals[3] or 0)
    failure_count = int(totals[4] or 0)
    if total_count:
        success_rate = success_count / total_count
        failure_rate = failure_count / total_count
    else:
        success_rate = 0.0
        failure_rate = 0.0
    return {
        "total_count": total_count,
        "total_amount": total_amount,
        "avg_amount": avg_amount,
        "success_rate": success_rate,
        "failure_rate": failure_rate,
    }
