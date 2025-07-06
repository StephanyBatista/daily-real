from pydantic import BaseModel


class UserByToken(BaseModel):
    email: str
    name: str
