from typing import Literal

from pydantic import BaseModel, Field


class CreditDetailsCreate(BaseModel):
    last_four_digits: str = Field(..., pattern=r"^\d{4}$")
    billing_cycle_day: int = Field(..., ge=1, le=30)
    due_day: int = Field(..., ge=1, le=30)


class BankDetailCreate(BaseModel):
    agency: str = Field(..., max_length=10)
    account_number: str = Field(..., max_length=20)
    account_type: Literal["Checking", "Savings"]


class AccountCreate(BaseModel):
    name: str = Field(..., max_length=32)
    credit_details: CreditDetailsCreate | None = None
    bank_detail: BankDetailCreate | None = None
