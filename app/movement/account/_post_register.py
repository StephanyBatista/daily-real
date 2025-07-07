from fastapi.params import Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.id.public.get_user_by_token import get_user_by_token
from app.id.public.user_by_token import UserByToken
from app.infra.database import get_db
from app.movement.account._account import Account
from app.movement.account._account_create import AccountCreate


def post_register(
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: UserByToken = Depends(get_user_by_token),
):
    account_db = Account(payload=account, created_by=current_user.email)

    db.add(account_db)
    db.commit()
    db.refresh(account_db)
    return JSONResponse(
        status_code=201,
        content=None,
        headers={"Location": f"/accounts/{account_db.id}"},
    )
