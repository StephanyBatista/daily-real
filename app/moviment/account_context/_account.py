import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.infra.database import Base


class AccountType(enum.Enum):
    BANK = "Bank"
    CREDIT_CARD = "CreditCard"
    CASH = "Cash"


# SQLAlchemy models
class CreditDetails(Base):
    __tablename__ = "credit_details"
    __table_args__ = {"schema": "moviment"}

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("moviment.accounts.id"), nullable=False)
    last_four_digits = Column(String(4), nullable=False)
    billing_cycle_day = Column(Integer, nullable=False)
    due_day = Column(Integer, nullable=False)
    credit_limit = Column(Numeric(10, 2), nullable=False)
    available_credit = Column(Numeric(10, 2), nullable=False)


class BankDetail(Base):
    __tablename__ = "bank_details"
    __table_args__ = {"schema": "moviment"}

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("moviment.accounts.id"), nullable=False)
    agency = Column(String(10), nullable=False)
    account_number = Column(String(20), nullable=False)
    account_type = Column(String(20), nullable=False)  # "Checking", "Savings"
    balance = Column(Numeric(10, 2), nullable=False)


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = {"schema": "moviment"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    type = Column(Enum(AccountType), nullable=False)
    created_by = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships to detail tables
    credit_details = relationship("CreditDetails", uselist=False)
    bank_detail = relationship("BankDetail", uselist=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Validate after initialization
        self._validate_type()

    def _validate_type(self):
        """Validate that required detail records exist based on account type."""
        if not self.type:
            return  # Skip validation if type is not set yet

        if self.type == AccountType.BANK and not self.bank_detail:
            raise ValueError("Bank accounts must have bank_detail filled")
        elif self.type == AccountType.CREDIT_CARD and not self.credit_details:
            raise ValueError("Credit card accounts must have credit_details filled")
        elif self.type == AccountType.CASH and (
            self.bank_detail or self.credit_details
        ):
            raise ValueError(
                "Cash accounts should not have bank_detail or credit_details"
            )
