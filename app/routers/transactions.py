from fastapi import APIRouter, HTTPException, Response, status
from typing import List
from app.schemas import TransactionCreate, TransactionRead, TransactionUpdate
from app import crud

router = APIRouter()


@router.get("/prices")
def prices():
    return {"black_and_white": crud.PRICE_BW, "colored": crud.PRICE_COLOR, "photo_paper": crud.PRICE_PHOTO}


@router.get("/summary")
def summary():
    """Return total income and transaction count."""
    return crud.total_income()


@router.post("/", response_model=TransactionRead)
def create_txn(data: TransactionCreate):
    txn = crud.create_transaction(data)
    return txn


@router.get("/", response_model=List[TransactionRead])
def list_txns():
    return crud.list_transactions()


@router.get("/{txn_id}", response_model=TransactionRead)
def get_txn(txn_id: int):
    txn = crud.get_transaction(txn_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn



@router.post("/{txn_id}/cancel")
def cancel_txn(txn_id: int):
    """Client cancels their order; marks transaction as cancelled."""
    updated = crud.cancel_transaction(txn_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Transaction not found or already cancelled")
    return {"id": updated["id"], "cancelled": bool(updated["cancelled"])}


@router.put("/{txn_id}", response_model=TransactionRead)
def update_txn(txn_id: int, data: TransactionUpdate):
    """Update an existing transaction. Recomputes total if pages change."""
    allowed_status = {"pending", "completed", "cancelled"}
    if data.status is not None and data.status not in allowed_status:
        raise HTTPException(status_code=400, detail=f"status must be one of {allowed_status}")
    updated = crud.update_transaction(txn_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Transaction not found or cannot be updated")
    return updated
