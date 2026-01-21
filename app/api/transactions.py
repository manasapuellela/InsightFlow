from __future__ import annotations

import csv
from io import StringIO

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.schemas.transactions import (
    TransactionCreate,
    TransactionList,
    TransactionOut,
    TransactionUpdate,
)
from app.services import transactions as transaction_service

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate, session: Session = Depends(get_db_session)
) -> TransactionOut:
    existing = transaction_service.get_transaction_by_reference(session, payload.reference)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Transaction reference already exists.",
        )
    transaction = transaction_service.create_transaction(session, payload)
    return TransactionOut.model_validate(transaction)


@router.get("", response_model=TransactionList)
def list_transactions(
    session: Session = Depends(get_db_session),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: str | None = Query(None),
) -> TransactionList:
    items, total = transaction_service.list_transactions(session, offset, limit, status)
    return TransactionList(
        items=[TransactionOut.model_validate(item) for item in items], total=total
    )


@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(
    transaction_id: int, session: Session = Depends(get_db_session)
) -> TransactionOut:
    transaction = transaction_service.get_transaction(session, transaction_id)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return TransactionOut.model_validate(transaction)


@router.put("/{transaction_id}", response_model=TransactionOut)
def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    session: Session = Depends(get_db_session),
) -> TransactionOut:
    transaction = transaction_service.get_transaction(session, transaction_id)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    updated = transaction_service.update_transaction(session, transaction, payload)
    return TransactionOut.model_validate(updated)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int, session: Session = Depends(get_db_session)
) -> None:
    transaction = transaction_service.get_transaction(session, transaction_id)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    transaction_service.delete_transaction(session, transaction)


@router.post("/ingest/csv")
def ingest_csv(
    file: UploadFile = File(...), session: Session = Depends(get_db_session)
) -> dict[str, int]:
    if file.content_type not in {"text/csv", "application/vnd.ms-excel"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid CSV content type."
        )
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(StringIO(content))
    if not reader.fieldnames:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file must include headers.",
        )
    required_fields = {
        "reference",
        "amount",
        "currency",
        "status",
        "occurred_at",
    }
    missing = required_fields.difference(set(reader.fieldnames))
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required columns: {', '.join(sorted(missing))}.",
        )
    rows: list[TransactionCreate] = []
    errors: list[str] = []
    for index, row in enumerate(reader, start=2):
        try:
            payload = TransactionCreate(
                reference=row.get("reference", "").strip(),
                amount=row.get("amount", ""),
                currency=row.get("currency", "").strip(),
                status=row.get("status", "").strip(),
                description=row.get("description", "").strip() or None,
                occurred_at=row.get("occurred_at", "").strip(),
            )
            rows.append(payload)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"Row {index}: {exc}")
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=errors,
        )
    created, skipped = transaction_service.batch_insert_transactions(session, rows)
    return {"created": created, "skipped": skipped}

