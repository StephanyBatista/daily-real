from fastapi.params import Depends
from pydantic import BaseModel

from app.id.user._auth import get_user_by_token
from app.id.user._user import User


class UserProfile(BaseModel):
    email: str
    name: str

    class Config:
        from_attributes = True


async def get_user_profile(
    current_user: User = Depends(get_user_by_token),
) -> UserProfile:
    """Get current user profile (protected endpoint example)."""
    return UserProfile(email=current_user.email, name=current_user.name)
