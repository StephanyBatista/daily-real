from sqlalchemy import Column, Integer, String

from app.infra.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "id"}
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(24), unique=True, index=True)
    name = Column(String(128))
    hashed_password = Column(String)
