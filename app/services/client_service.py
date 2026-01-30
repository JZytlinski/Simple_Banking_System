from decimal import Decimal
from io import BytesIO
import uuid
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.models.client import Client
from app.models.person import Person, PersonRole
from app.models.transaction import Transaction
from app.reports.statement_pdf import build_statement_pdf
from app.services.person_service import _to_money


def get_client_or_404(db: Session, client_id: str) -> Client:
    client = db.get(Client, client_id)
    if not client:
        raise ValueError("Client not found")
    return client


def deposit(db: Session, client_id: str, amount: Decimal):
    if amount <= 0:
        raise ValueError("Amount must be positive")

    client = get_client_or_404(db, client_id)

    client.deposit(amount)

    db.add(
        Transaction(client_id=client_id, type="deposit", amount=Decimal(str(amount)))
    )
    db.commit()
    db.refresh(client)
    return client


def withdraw(db: Session, client_id: str, amount: Decimal):
    client = get_client_or_404(db, client_id)
    client.withdraw(amount)

    db.add(
        Transaction(client_id=client_id, type="withdrawal", amount=Decimal(str(amount)))
    )
    db.commit()
    db.refresh(client)
    return client


def transactions(db: Session, client_id: str):
    client = get_client_or_404(db, client_id)
    return client.transactions


def personal_data(db: Session, client_id: str):
    client = get_client_or_404(db, client_id)
    return client


def get_all_clients(db: Session):
    return db.query(Client).all()


def generate_client_statement_pdf(db: Session, client_id: str):
    client = get_client_or_404(db, client_id)

    transactions = client.transactions

    pdf_bytes = build_statement_pdf(client, transactions)
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="statement_{client_id}.pdf"'
        },
    )


def create_client(
    db: Session,
    id: str,
    name: str,
    surname: str,
    email: str,
    initial_balance: Decimal | float | int = 0,
):

    if db.get(Person, id):
        raise HTTPException(status_code=400, detail="User with this ID already exists")

    init = _to_money(initial_balance)
    if init < Decimal("0.00"):
        raise HTTPException(
            status_code=400, detail="Initial balance cannot be negative"
        )

    client = Client(
        id=id, name=name, surname=surname, email=email, role=PersonRole.CLIENT
    )
    db.add(client)
    db.flush()

    if init > Decimal("0.00"):
        client.deposit(init)

        tx = Transaction(
            client_id=client.id,
            type="deposit",
            amount=init,
        )
        db.add(tx)

    db.commit()
    db.refresh(client)
    return client


def create_transfer(db: Session, sender_id: str, receiver_id: str, amount: Decimal):

    sender = get_client_or_404(db, sender_id)
    receiver = get_client_or_404(db, receiver_id)

    if sender.balance < amount:
        raise HTTPException(400, "Sender does not have enough balance.")

    group_id = uuid.uuid4().int % ((1 << 63) - 1)

    tx_out = Transaction(
        client_id=sender_id,
        type="transfer_out",
        amount=amount,
        transfer_group_id=group_id,
    )

    tx_in = Transaction(
        client_id=receiver_id,
        type="transfer_in",
        amount=amount,
        transfer_group_id=group_id,
    )

    sender.withdraw(amount)
    receiver.deposit(amount)

    db.add(tx_out)
    db.add(tx_in)

    db.commit()
    db.refresh(tx_out)
    db.refresh(tx_in)
    db.refresh(sender)

    return sender
