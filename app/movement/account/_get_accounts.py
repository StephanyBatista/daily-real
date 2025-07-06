from typing import List

from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.id.public.get_user_by_token import get_user_by_token
from app.id.public.user_by_token import UserByToken
from app.infra.database import get_db
from app.movement.account._account import Account
from app.movement.account._account_response import AccountResponse


def get_accounts(
    db: Session = Depends(get_db),
    current_user: UserByToken = Depends(get_user_by_token),
) -> List[AccountResponse]:
    """
    Get all accounts created by the current user (based on email from token).
    """
    accounts = db.query(Account).filter(Account.created_by == current_user.email).all()

    return [AccountResponse.model_validate(account) for account in accounts]
