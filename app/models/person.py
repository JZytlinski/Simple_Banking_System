from sqlalchemy import Column, String, DateTime, Enum
from datetime import datetime
import enum

from app.core.database import Base


class PersonRole(str, enum.Enum):
    CLIENT = "client"
    MANAGER = "manager"


class Person(Base):
    __tablename__ = "persons"

    id = Column(String, primary_key=True, index=True)
    name = Column(String(80), nullable=False)
    surname = Column(String(80), nullable=False)
    email = Column(String(120), unique=True)
    role = Column(Enum(PersonRole), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    __mapper_args__ = {
        "polymorphic_on": role,
        "polymorphic_identity": "person",
    }

    def __str__(self):
        return f"{self.role.value.capitalize()}(ID: {self.id}, Name and surname: {self.name} {self.surname})"

    def __repr__(self):
        return (
            f"Person(id={self.id}, name='{self.name}', email='{self.email}', "
            f"role='{self.role.value}', created_at={self.created_at})"
        )
