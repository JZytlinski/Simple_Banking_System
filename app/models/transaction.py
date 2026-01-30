from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(String, ForeignKey("clients.id"))
    type = Column(String(16), nullable=False)
    amount = Column(Numeric(12, 2))
    timestamp = Column(DateTime, default=datetime.now)

    transfer_group_id = Column(Integer, nullable=True, index=True)

    is_reversed = Column(Boolean, nullable=False, default=False)
    reversal_of_id = Column(
        Integer, ForeignKey("transactions.transaction_id"), nullable=True
    )
    reversed_by_id = Column(
        Integer, ForeignKey("transactions.transaction_id"), nullable=True
    )

    reversal_of = relationship(
        "Transaction",
        remote_side=[transaction_id],
        foreign_keys=[reversal_of_id],
        post_update=True,
    )
    reversed_by = relationship(
        "Transaction",
        remote_side=[transaction_id],
        foreign_keys=[reversed_by_id],
        post_update=True,
    )

    client = relationship("Client", back_populates="transactions")

    def __str__(self):
        mark = " [REVERSED]" if self.is_reversed else ""
        return f"Transaction(Type: {self.type}, Amount: {self.amount}, Time: {self.timestamp}{mark}"

    def __repr__(self):
        return (
            f"Transaction(id={self.transaction_id}, client_id={self.client_id}, "
            f"type='{self.type}', amount={self.amount}, timestamp={self.timestamp}, is_reversed={self.is_reversed},"
            f"reversal_of_id={self.reversal_of_id}, reversed_by_id={self.reversed_by_id})"
        )
