from sqlalchemy import Column, String, ForeignKey
from app.models.person import Person, PersonRole


class Manager(Person):
    __tablename__ = "managers"

    id = Column(String, ForeignKey("persons.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": PersonRole.MANAGER,
    }
