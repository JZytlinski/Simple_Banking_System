from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.person_service import get_all_persons

router = APIRouter(prefix="/persons", tags=["persons"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/persons")
def get_persons(db: Session = Depends(get_db)):
    return get_all_persons(db)
