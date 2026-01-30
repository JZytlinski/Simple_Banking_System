from decimal import Decimal, InvalidOperation
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.person import Person


def _to_money(value) -> Decimal:
    try:
        d = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise HTTPException("Invalid amount format")
    return d


def get_person_or_404(db: Session, person_id: str) -> Person:
    person = db.get(Person, person_id)
    if not person:
        raise ValueError("Person not found")
    return person


def delete_person(db: Session, id: str):
    person = get_person_or_404(db, id)
    db.delete(person)
    db.commit()

    return {"status": "deleted", "person_id": id}


def get_all_persons(db: Session):
    return db.query(Person).all()
