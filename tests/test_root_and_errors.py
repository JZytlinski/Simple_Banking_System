from fastapi import APIRouter
from app.main import app


def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"status": "running"}


def test_global_value_error_handler(client):

    router = APIRouter()

    @router.get("/_raise_value_error")
    def raise_value_error():
        raise ValueError("Test error")

    app.include_router(router)

    resp = client.get("/_raise_value_error")
    assert resp.status_code == 400
    assert resp.json() == {"detail": "Test error"}
