from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.person_service import delete_person
from app.services.client_service import (
    create_transfer,
    deposit,
    generate_client_statement_pdf,
    withdraw,
    transactions,
    personal_data,
    get_all_clients,
    create_client,
)
from app.services.transaction_service import reverse_transaction

router = APIRouter(prefix="/clients", tags=["clients"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/add")
def add_client(
    id: str,
    name: str,
    surname: str,
    email: str,
    balance: Decimal = Decimal("0.00"),
    db: Session = Depends(get_db),
):
    return create_client(
        db, id=id, name=name, surname=surname, email=email, initial_balance=balance
    )


@router.post("/{client_id}/deposit")
def deposite_money(client_id: str, amount: Decimal, db: Session = Depends(get_db)):
    return deposit(db, client_id, amount)


@router.post("/{client_id}/withdrawal")
def withdraw_money(client_id: str, amount: Decimal, db: Session = Depends(get_db)):
    return withdraw(db, client_id, amount)


@router.post("/{client_id}/{receiver_id}/transfer")
def transfer_money(
    client_id: str, receiver_id: str, amount: Decimal, db: Session = Depends(get_db)
):
    return create_transfer(db, client_id, receiver_id, amount)


@router.post("/transactions/{transaction_id}/reverse")
def reverse_tx(transaction_id: int, db: Session = Depends(get_db)):
    return reverse_transaction(db, transaction_id)


@router.get("/{client_id}/transactions")
def get_transactions(client_id: str, db: Session = Depends(get_db)):
    return transactions(db, client_id)


@router.delete("/delete/{person_id}")
def remove_person(person_id: str, db: Session = Depends(get_db)):
    return delete_person(db, person_id)


@router.get("/{client_id}/personal_data")
def get_data(client_id: str, db: Session = Depends(get_db)):
    return personal_data(db, client_id)


@router.get("/clients")
def get_clients(db: Session = Depends(get_db)):
    return get_all_clients(db)


@router.get("/{client_id}/statement")
def get_client_statement_pdf(client_id: str, db: Session = Depends(get_db)):
    return generate_client_statement_pdf(db, client_id)
