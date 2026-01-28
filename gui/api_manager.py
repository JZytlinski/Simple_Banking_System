import os
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
        detail = data.get("detail", data) if isinstance(data, dict) else str(data)
        raise requests.HTTPError(detail)

    return data


def get_all_managers() -> List[Dict]:
    url = f"{API_BASE_URL}/managers/managers"
    resp = requests.get(url, timeout=20)
    return _handle_response(resp)


def add_manager(id_: str, name: str, surname: str, email: str) -> Dict:
    url = f"{API_BASE_URL}/managers/add"
    params = {
        "id": id_,
        "name": name,
        "surname": surname,
        "email": email,
    }
    resp = requests.post(url, params=params, timeout=20)
    return _handle_response(resp)


def get_manager_personal_data(manager_id: str) -> Dict:
    url = f"{API_BASE_URL}/managers/{manager_id}/personal_data"
    resp = requests.get(url, timeout=20)
    return _handle_response(resp)


def reverse_transaction(transaction_id: int) -> Dict:
    url = f"{API_BASE_URL}/transactions/transactions/{transaction_id}/reverse"
    resp = requests.post(url, timeout=20)
    return _handle_response(resp)


def get_all_transactions_manager() -> List[Dict]:
    url = f"{API_BASE_URL}/transactions/transactions"
    resp = requests.get(url, timeout=20)
    return _handle_response(resp)


def manager_exists(manager_id: str) -> bool:
    try:
        _ = get_manager_personal_data(manager_id)
        return True
    except Exception:
        return False
