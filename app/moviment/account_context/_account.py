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


class BankDetail(Base):
    __tablename__ = "bank_details"
    __table_args__ = {"schema": "moviment"}

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("moviment.accounts.id"), nullable=False)
    agency = Column(String(10), nullable=False)
    account_number = Column(String(20), nullable=False)
    account_type = Column(String(20), nullable=False)  # "Checking", "Savings"


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

    def __init__(
        self,
        name: str,
        created_by: str,
        agency: str = None,
        account_number: str = None,
        account_type: str = None,
        balance: float = None,
        last_four_digits: str = None,
        billing_cycle_day: int = None,
        due_day: int = None,
        credit_limit: float = None,
        available_credit: float = None,
    ):
        self.name = name
        self.created_by = created_by
        self.created_at = datetime.now()

        if agency and account_number and account_type:
            self.type = AccountType.BANK
            self.bank_detail = BankDetail(
                agency=agency,
                account_number=account_number,
                account_type=account_type,
            )
        elif (
            last_four_digits
            and billing_cycle_day
            and due_day
            and credit_limit is not None
        ):
            self.type = AccountType.CREDIT_CARD
            self.credit_details = CreditDetails(
                last_four_digits=last_four_digits,
                billing_cycle_day=billing_cycle_day,
                due_day=due_day,
            )
        else:
            raise ValueError(
                "Bank or credit card details must be provided for the account type"
            )
