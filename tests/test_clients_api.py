from decimal import Decimal
import pytest
from app.models.client import Client
from app.models.transaction import Transaction


def test_add_client_with_zero_balance(client, db_session):
    resp = client.post(
        "/clients/add",
        params={
            "id": "c1",
            "name": "Alice",
            "surname": "A",
            "email": "alice@example.com",
            "balance": "0.00",
        },
    )
    assert resp.status_code == 200

    c = db_session.get(Client, "c1")
    assert c is not None
    assert c.name == "Alice"
    assert c.balance == Decimal("0.00")

    txs = db_session.query(Transaction).filter(Transaction.client_id == "c1").all()
    assert len(txs) == 0


def test_add_client_with_initial_deposit_creates_tx(client, db_session):
    resp = client.post(
        "/clients/add",
        params={
            "id": "c2",
            "name": "Bob",
            "surname": "B",
            "email": "bob@example.com",
            "balance": "150.50",
        },
    )
    assert resp.status_code == 200

    c = db_session.get(Client, "c2")
    assert c.balance == Decimal("150.50")

    txs = db_session.query(Transaction).filter(Transaction.client_id == "c2").all()
    assert len(txs) == 1
    assert txs[0].type == "deposit"
    assert Decimal(txs[0].amount) == Decimal("150.50")


def test_add_client_negative_balance_is_400(client):
    resp = client.post(
        "/clients/add",
        params={
            "id": "c3",
            "name": "Chris",
            "surname": "C",
            "email": "chris@example.com",
            "balance": "-1",
        },
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Initial balance cannot be negative"


def test_deposit_success_and_invalid_amounts(client, db_session):

    client.post(
        "/clients/add",
        params={
            "id": "c4",
            "name": "Dana",
            "surname": "D",
            "email": "dana@example.com",
            "balance": "10.00",
        },
    )

    r_ok = client.post("/clients/c4/deposit", params={"amount": "25.50"})
    assert r_ok.status_code == 200
    c = db_session.get(Client, "c4")
    assert c.balance == Decimal("35.50")

    r_bad = client.post("/clients/c4/deposit", params={"amount": "0"})
    assert r_bad.status_code == 400
    assert r_bad.json()["detail"] == "Amount must be positive"


def test_withdraw_success_and_insufficient_funds(client, db_session):
    client.post(
        "/clients/add",
        params={
            "id": "c5",
            "name": "Eve",
            "surname": "E",
            "email": "eve@example.com",
            "balance": "40.00",
        },
    )

    r_ok = client.post("/clients/c5/withdrawal", params={"amount": "15"})
    assert r_ok.status_code == 200
    c = db_session.get(Client, "c5")
    assert c.balance == Decimal("25.00")

    r_bad = client.post("/clients/c5/withdrawal", params={"amount": "30"})
    assert r_bad.status_code == 400
    assert r_bad.json()["detail"] == "Insufficient funds"


def test_transfer_success(client, db_session):
    client.post(
        "/clients/add",
        params={
            "id": "s1",
            "name": "Sender",
            "surname": "S",
            "email": "sender@example.com",
            "balance": "100.00",
        },
    )

    client.post(
        "/clients/add",
        params={
            "id": "r1",
            "name": "Receiver",
            "surname": "R",
            "email": "receiver@example.com",
            "balance": "0.00",
        },
    )

    r = client.post("/clients/s1/r1/transfer", params={"amount": "60.00"})
    assert r.status_code == 200

    s = db_session.get(Client, "s1")
    rcv = db_session.get(Client, "r1")
    assert s.balance == Decimal("40.00")
    assert rcv.balance == Decimal("60.00")

    tx_sender = (
        db_session.query(Transaction)
        .filter(Transaction.client_id == "s1", Transaction.type == "transfer_out")
        .one()
    )
    tx_receiver = (
        db_session.query(Transaction)
        .filter(Transaction.client_id == "r1", Transaction.type == "transfer_in")
        .one()
    )
    assert tx_sender.transfer_group_id is not None
    assert tx_sender.transfer_group_id == tx_receiver.transfer_group_id


def test_transfer_insufficient_funds(client):
    client.post(
        "/clients/add",
        params={
            "id": "s2",
            "name": "Sender2",
            "surname": "S",
            "email": "sender2@example.com",
            "balance": "10.00",
        },
    )
    client.post(
        "/clients/add",
        params={
            "id": "r2",
            "name": "Receiver2",
            "surname": "R",
            "email": "receiver2@example.com",
            "balance": "0.00",
        },
    )

    r = client.post("/clients/s2/r2/transfer", params={"amount": "11.00"})
    assert r.status_code == 400
    assert "enough balance" in r.json()["detail"]


def test_get_transactions_endpoint(client, db_session):
    client.post(
        "/clients/add",
        params={
            "id": "t1",
            "name": "Tx",
            "surname": "One",
            "email": "tx1@example.com",
            "balance": "0.00",
        },
    )
    client.post("/clients/t1/deposit", params={"amount": "5.00"})
    client.post("/clients/t1/deposit", params={"amount": "7.00"})
    client.post("/clients/t1/withdrawal", params={"amount": "3.00"})

    r = client.get("/clients/t1/transactions")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)

    count = db_session.query(Transaction).filter(Transaction.client_id == "t1").count()
    assert len(data) == count
