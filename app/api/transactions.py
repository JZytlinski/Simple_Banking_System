from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.transaction_service import get_all_transactions, reverse_transaction

router = APIRouter(prefix="/transactions", tags=["transactions"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/transactions")
def get_transactions(db: Session = Depends(get_db)):
    return get_all_transactions(db)


@router.post("/transactions/{transaction_id}/reverse")
def reverse_tx(transaction_id: int, db: Session = Depends(get_db)):
    return reverse_transaction(db, transaction_id)
