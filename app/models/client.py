from decimal import Decimal, InvalidOperation
from sqlalchemy import Column, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from app.models.person import Person, PersonRole


class Client(Person):
    __tablename__ = "clients"

    id = Column(String, ForeignKey("persons.id"), primary_key=True)
    _balance = Column(
        "balance", Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )

    transactions = relationship(
        "Transaction", back_populates="client", cascade="all, delete-orphan"
    )

    __mapper_args__ = {
        "polymorphic_identity": PersonRole.CLIENT,
    }

    @property
    def balance(self) -> Decimal:
        return self._balance

    @balance.setter
    def balance(self, value):

        if value is None:
            raise ValueError("Balance cannot be None")

        try:
            dec = Decimal(str(value))
        except (InvalidOperation, ValueError):
            raise ValueError("Balance must be a decimal-compatible value")

        if dec < Decimal("0.00"):
            raise ValueError("Balance cannot be negative")

        self._balance = dec

    def deposit(self, amount):
        amt = Decimal(str(amount))
        if amt <= Decimal("0.00"):
            raise ValueError("Amount must be positive")
        self.balance = self.balance + amt

    def withdraw(self, amount):
        amt = Decimal(str(amount))
        if amt <= Decimal("0.00"):
            raise ValueError("Amount must be positive")
        if self.balance - amt < Decimal("0.00"):
            raise ValueError("Insufficient funds")
        self.balance = self.balance - amt

    def __str__(self):
        return f"Client(ID: {self.id}, Name and surname: {self.name} {self.surname}, balance: {self.balance})"

    def __repr__(self):
        return (
            f"Client(id={self.id}, name='{self.name}', email='{self.email}', "
            f"role='{self.role.value}', created_at={self.created_at}, balance={self.balance})"
        )
