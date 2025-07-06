from sqlalchemy import Column, Integer, String

from app.infra.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "id"}
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(24), unique=True, index=True)
    name = Column(String(128))
    hashed_password = Column(String)

    def __init__(self, email: str, name: str):
        self.email = email
        self.name = name

        if not email:
            raise ValueError("Email must not be empty")
        if not name:
            raise ValueError("Name must not be empty")

        super().__init__()

    def update_password(self, new_hashed_password: str):
        if not new_hashed_password:
            raise ValueError("New hashed password must not be empty")
        self.hashed_password = new_hashed_password
