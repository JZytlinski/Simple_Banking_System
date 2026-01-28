import os
from decimal import Decimal
from typing import Any, List, Dict

import requests

API_BASE_URL = os.getenv("ST_API_BASE_URL", "http://127.0.0.1:8000")


def _handle_response(resp: requests.Response) -> Any:
    ctype = resp.headers.get("content-type", "")

    if ctype.startswith("application/pdf"):
        if not resp.ok:
            resp.raise_for_status()
        return resp

    try:
        data = resp.json()
    except Exception:
        resp.raise_for_status()
        return {}
    if not resp.ok:
        detail = data.get("detail", data)
        raise requests.HTTPError(detail)
    return data


def get_all_clients() -> List[Dict]:
    url = f"{API_BASE_URL}/clients/clients"
    resp = requests.get(url, timeout=20)
    return _handle_response(resp)


def add_client(id_: str, name: str, surname: str, email: str, balance: Decimal) -> Dict:
    url = f"{API_BASE_URL}/clients/add"
    params = {
        "id": id_,
        "name": name,
        "surname": surname,
        "email": email,
        "balance": str(balance),
    }
    resp = requests.post(url, params=params, timeout=20)
    return _handle_response(resp)


def deposit_money(client_id: str, amount: Decimal) -> Dict:
    url = f"{API_BASE_URL}/clients/{client_id}/deposit"
    params = {"amount": str(amount)}
    resp = requests.post(url, params=params, timeout=20)
    return _handle_response(resp)


def withdraw_money(client_id: str, amount: Decimal) -> Dict:
    url = f"{API_BASE_URL}/clients/{client_id}/withdrawal"
    params = {"amount": str(amount)}
    resp = requests.post(url, params=params, timeout=20)
    return _handle_response(resp)


def transfer_money(client_id: str, receiver_id: str, amount: Decimal) -> Dict:
    url = f"{API_BASE_URL}/clients/{client_id}/{receiver_id}/transfer"
    params = {"amount": str(amount), "receiver_id": receiver_id}
    resp = requests.post(url, params=params, timeout=20)
    return _handle_response(resp)


def get_transactions(client_id: str) -> List[Dict]:
    url = f"{API_BASE_URL}/clients/{client_id}/transactions"
    resp = requests.get(url, timeout=20)
    return _handle_response(resp)


def get_personal_data(client_id: str) -> Dict:
    url = f"{API_BASE_URL}/clients/{client_id}/personal_data"
    resp = requests.get(url, timeout=20)
    return _handle_response(resp)


def delete_person(person_id: str) -> Dict:
    url = f"{API_BASE_URL}/clients/delete/{person_id}"
    resp = requests.delete(url, timeout=20)
    return _handle_response(resp)


def get_statement_pdf_response(client_id: str) -> requests.Response:

    url = f"{API_BASE_URL}/clients/{client_id}/statement"
    resp = requests.get(url, timeout=20)
    return _handle_response(resp)


def client_exists(client_id: str) -> bool:
    try:
        _ = get_personal_data(client_id)
        return True
    except Exception:
        return False
