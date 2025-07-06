from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.movement.account._account import AccountType


class CreditDetailsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    last_four_digits: str
    billing_cycle_day: int
    due_day: int


class BankDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    agency: str
    account_number: str
    account_type: str


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: AccountType
    created_by: str
    created_at: datetime
    credit_details: Optional[CreditDetailsResponse] = None
    bank_detail: Optional[BankDetailResponse] = None
