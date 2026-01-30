from app.models.manager import Manager


def test_add_manager_success(client, db_session):
    r = client.post(
        "/managers/add",
        params={
            "id": "m1",
            "name": "Mat",
            "surname": "M",
            "email": "mat.m@example.com",
        },
    )
    assert r.status_code == 200

    m = db_session.get(Manager, "m1")
    assert m is not None
    assert m.name == "Mat"
    assert m.surname == "M"
    assert m.email == "mat.m@example.com"

    assert m.role.value == "manager"


def test_get_manager_personal_data(client):

    client.post(
        "/managers/add",
        params={
            "id": "m2",
            "name": "Mat",
            "surname": "M",
            "email": "mat.m@example.com",
        },
    )

    r = client.get("/managers/m2/personal_data")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == "m2"
    assert (
        data["role"] in ("manager", "PersonRole.MANAGER")
        or data["role"].get("value") == "manager"
    )


def test_list_managers(client):
    client.post(
        "/managers/add",
        params={
            "id": "m3",
            "name": "Alice",
            "surname": "S",
            "email": "alice.s@example.com",
        },
    )
    client.post(
        "/managers/add",
        params={
            "id": "m4",
            "name": "Bob",
            "surname": "B",
            "email": "bob.b@example.com",
        },
    )

    r = client.get("/managers/managers")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    ids = {item["id"] for item in data}
    assert {"m3", "m4"}.issubset(ids)


def test_get_manager_not_found_returns_400(client):
    r = client.get("/managers/unknown/personal_data")
    assert r.status_code == 400
    assert r.json()["detail"] == "Manager not found"
