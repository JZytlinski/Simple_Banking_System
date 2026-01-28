from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import SessionLocal

from app.services.manager_service import personal_data, get_all_managers, create_manager

router = APIRouter(prefix="/managers", tags=["managers"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/add")
def add_manager(
    id: str, name: str, surname: str, email: str, db: Session = Depends(get_db)
):
    return create_manager(db, id=id, name=name, surname=surname, email=email)


@router.get("/{manager_id}/personal_data")
def get_data(manager_id: str, db: Session = Depends(get_db)):
    return personal_data(db, manager_id)


@router.get("/managers")
def get_managers(db: Session = Depends(get_db)):
    return get_all_managers(db)
