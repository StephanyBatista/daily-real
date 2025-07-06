import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
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

    def __init__(self, last_four_digits: str, billing_cycle_day: int, due_day: int):
        if not last_four_digits or len(last_four_digits) != 4:
            raise ValueError("Last four digits must be a 4-digit string")
        if billing_cycle_day < 1 or billing_cycle_day > 31:
            raise ValueError("Billing cycle day must be between 1 and 31")
        if due_day < 1 or due_day > 31:
            raise ValueError("Due day must be between 1 and 31")

        self.last_four_digits = last_four_digits
        self.billing_cycle_day = billing_cycle_day
        self.due_day = due_day


class BankDetail(Base):
    __tablename__ = "bank_details"
    __table_args__ = {"schema": "moviment"}

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("moviment.accounts.id"), nullable=False)
    agency = Column(String(10), nullable=False)
    account_number = Column(String(20), nullable=False)
    account_type = Column(String(20), nullable=False)  # "Checking", "Savings"

    def __init__(self, agency: str, account_number: str, account_type: str):
        if not agency:
            raise ValueError("Agency cannot be empty")
        if not account_number:
            raise ValueError("Account number cannot be empty")
        if not account_type:
            raise ValueError("Account type cannot be empty")

        self.agency = agency
        self.account_number = account_number
        self.account_type = account_type


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = {"schema": "moviment"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(32), nullable=False)
    type = Column(Enum(AccountType), nullable=False)
    created_by = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships to detail tables
    credit_details = relationship("CreditDetails", uselist=False)
    bank_detail = relationship("BankDetail", uselist=False)

    def __init__(
        self,
        name: str,
        created_by: str,
    ):
        if not name:
            raise ValueError("Account name cannot be empty")
        if not created_by:
            raise ValueError("Created by cannot be empty")

        self.name = name
        self.created_by = created_by
        self.created_at = datetime.now()

    def configure_credit_details(
        self, last_four_digits: str, billing_cycle_day: int, due_day: int
    ):
        self.type = AccountType.CREDIT_CARD
        self.credit_details = CreditDetails(
            last_four_digits=last_four_digits,
            billing_cycle_day=billing_cycle_day,
            due_day=due_day,
        )

    def configure_bank_details(
        self, agency: str, account_number: str, account_type: str
    ):
        self.type = AccountType.BANK
        self.bank_detail = BankDetail(
            agency=agency,
            account_number=account_number,
            account_type=account_type,
        )
