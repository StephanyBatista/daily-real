import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.infra.database import Base
from app.movement.account._account_create import AccountCreate
from app.util.exceptions import DomainException


class AccountType(enum.Enum):
    BANK = "Bank"
    CREDIT_CARD = "CreditCard"
    CASH = "Cash"


# SQLAlchemy models
class CreditDetails(Base):
    __tablename__ = "credit_details"
    __table_args__ = {"schema": "movement"}

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("movement.accounts.id"), nullable=False)
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
    __table_args__ = {"schema": "movement"}

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("movement.accounts.id"), nullable=False)
    agency = Column(String(10), nullable=False)
    account_number = Column(String(20), nullable=False)
    account_type = Column(String(20), nullable=False)  # "Checking", "Savings"

    def __init__(self, agency: str, account_number: str, account_type: str):
        if not agency:
            raise DomainException("Agency cannot be empty")
        if not account_number:
            raise DomainException("Account number cannot be empty")
        if not account_type:
            raise DomainException("Account type cannot be empty")

        self.agency = agency
        self.account_number = account_number
        self.account_type = account_type


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = {"schema": "movement"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(32), nullable=False)
    type = Column(Enum(AccountType), nullable=False)
    created_by = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships to detail tables
    credit_details = relationship("CreditDetails", uselist=False)
    bank_detail = relationship("BankDetail", uselist=False)

    def __init__(self, payload: AccountCreate, created_by: str):
        if not payload.name:
            raise DomainException("Account name cannot be empty")
        if not created_by:
            raise DomainException("Created by cannot be empty")

        self.name = payload.name
        self.created_by = created_by
        self.created_at = datetime.now()

        if payload.bank_detail:
            self.type = AccountType.BANK
            self.bank_detail = BankDetail(
                agency=payload.bank_detail.agency,
                account_number=payload.bank_detail.account_number,
                account_type=payload.bank_detail.account_type,
            )
        elif payload.credit_details:
            self.type = AccountType.CREDIT_CARD
            self.credit_details = CreditDetails(
                last_four_digits=payload.credit_details.last_four_digits,
                billing_cycle_day=payload.credit_details.billing_cycle_day,
                due_day=payload.credit_details.due_day,
            )
        else:
            raise DomainException(
                "Must provide either credit details or bank details for account configuration"
            )
