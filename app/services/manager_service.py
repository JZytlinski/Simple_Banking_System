from sqlalchemy.orm import Session
from streamlit import status
from app.models.manager import Manager
from app.models.person import PersonRole


def get_manager_or_404(db: Session, manager_id: str) -> Manager:
    manager = db.get(Manager, manager_id)
    if not manager:
        raise ValueError("Manager not found")
    return manager


def personal_data(db: Session, manager_id: str):
    manager = get_manager_or_404(db, manager_id)
    return manager


def get_all_managers(db: Session):
    return db.query(Manager).all()


def create_manager(db: Session, id: str, name: str, surname: str, email: str):
    manager = Manager(
        id=id, name=name, surname=surname, email=email, role=PersonRole.MANAGER
    )
    db.add(manager)
    db.commit()
    db.refresh(manager)
    return manager
