import os
import tempfile
import time
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.core.database import Base
from app.api import clients as clients_router
from app.api import managers as managers_router


@pytest.fixture
def test_db():

    fd, path = tempfile.mkstemp(prefix="test_db_", suffix=".sqlite3")
    os.close(fd)
    url = f"sqlite:///{path}"

    engine = create_engine(
        url,
        connect_args={"check_same_thread": False},
        poolclass=NullPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    Base.metadata.create_all(bind=engine)

    try:
        yield {"engine": engine, "SessionLocal": TestingSessionLocal, "path": path}
    finally:

        try:
            Base.metadata.drop_all(bind=engine)
        except Exception:
            pass

        try:
            engine.dispose()
        except Exception:
            pass

        for attempt in range(5):
            try:
                os.remove(path)
                break
            except PermissionError:
                if attempt == 4:
                    raise
                time.sleep(0.1)


@pytest.fixture
def client(test_db):

    TestingSessionLocal = test_db["SessionLocal"]

    def _override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[clients_router.get_db] = _override_get_db
    app.dependency_overrides[managers_router.get_db] = _override_get_db

    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.pop(clients_router.get_db, None)
        app.dependency_overrides.pop(managers_router.get_db, None)


@pytest.fixture
def db_session(test_db):
    SessionLocal = test_db["SessionLocal"]
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
