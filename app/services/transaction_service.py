from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.services.client_service import get_client_or_404


def get_transaction_or_404(db: Session, transaction_id: int) -> Transaction:
    transaction = db.get(Transaction, transaction_id)
    if not transaction:
        raise ValueError("Transaction not found")
    return transaction


def get_all_transactions(db: Session):
    return db.query(Transaction).all()


def reverse_transaction(db: Session, transaction_id: int):
    tx = get_transaction_or_404(db, transaction_id)

    if tx.is_reversed:
        raise HTTPException("Transaction already reversed")

    if tx.type in ("transfer_in", "transfer_out"):

        tx_out, tx_in = get_related_transfer_transactions(db, tx)

        if not tx_out or not tx_in:
            raise HTTPException(400, "Transfer pair not found.")

        sender = get_client_or_404(db, tx_out.client_id)
        receiver = get_client_or_404(db, tx_in.client_id)

        amount = abs(Decimal(str(tx_out.amount)))

        sender.deposit(amount)
        receiver.withdraw(amount)

        tx_out.is_reversed = True
        tx_in.is_reversed = True

        reversal_out = Transaction(
            client_id=sender.id,
            type="transfer_in",
            amount=amount,
            reversal_of_id=tx_out.transaction_id,
        )

        reversal_in = Transaction(
            client_id=receiver.id,
            type="transfer_out",
            amount=amount,
            reversal_of_id=tx_in.transaction_id,
        )

        db.add(reversal_out)
        db.add(reversal_in)
        db.flush()

        tx_out.reversed_by_id = reversal_out.transaction_id
        tx_in.reversed_by_id = reversal_in.transaction_id

        db.commit()

        return {
            "status": "reversed_transfer",
            "transfer_group_id": tx.transfer_group_id,
            "sender": sender.id,
            "receiver": receiver.id,
            "amount": str(amount),
            "out_reversal": reversal_out.transaction_id,
            "in_reversal": reversal_in.transaction_id,
        }

    else:

        client = get_client_or_404(db, tx.client_id)

        amount = Decimal(str(tx.amount))

        if tx.type == "deposit":
            client.withdraw(amount)
            new_type = "withdrawal"
        elif tx.type == "withdrawal":
            client.deposit(amount)
            new_type = "deposit"
        else:
            raise HTTPException("Unsupported transaction type: {tx.type}")

        reversal = Transaction(
            client_id=client.id,
            type=new_type,
            amount=amount,
            reversal_of_id=tx.transaction_id,
        )
        db.add(reversal)
        db.flush()

        tx.is_reversed = True
        tx.reversed_by_id = reversal.transaction_id

        db.commit()
        db.refresh(client)
        db.refresh(reversal)

        return {
            "status": "reversed",
            "original_transaction_id": tx.transaction_id,
            "reversal_transaction_id": reversal.transaction_id,
            "client_id": client.id,
            "new_balance": str(client.balance),
        }


def get_related_transfer_transactions(db: Session, tx: Transaction):

    if tx.transfer_group_id is None:
        return None, None

    rows = (
        db.query(Transaction)
        .filter(Transaction.transfer_group_id == tx.transfer_group_id)
        .all()
    )

    return rows
