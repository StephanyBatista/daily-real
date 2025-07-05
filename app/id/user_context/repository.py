from sqlalchemy.orm import Session

from app.id.user_context.user import User


def get_user_by_username(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()
