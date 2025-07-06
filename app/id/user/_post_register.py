from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.id.user._auth import get_password_hash
from app.id.user._repository import get_user_by_username
from app.id.user._user import User
from app.id.user._user_create import UserCreate
from app.infra.database import get_db


def post_register(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = User(
        email=user.email,
        name=user.name,
    )
    db_user.update_password(get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return JSONResponse(
        status_code=201, content=None, headers={"Location": f"/users/{db_user.id}"}
    )
