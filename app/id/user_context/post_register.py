from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.id.user_context.auth import get_password_hash
from app.id.user_context.repository import get_user_by_username
from app.id.user_context.user import User
from app.infra.database import get_db


class UserResponse(BaseModel):
    email: str
    name: str

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: str
    name: str
    password: str


def register(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = User(
        email=user.email,
        name=user.name,
        hashed_password=get_password_hash(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
