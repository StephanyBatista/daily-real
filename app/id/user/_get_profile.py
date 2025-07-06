from fastapi.params import Depends

from app.id.public.get_user_by_token import get_user_by_token
from app.id.public.user_by_token import UserByToken


async def get_user_profile(
    current_user: UserByToken = Depends(get_user_by_token),
) -> UserByToken:
    """Get current user profile (protected endpoint example)."""
    return UserByToken(email=current_user.email, name=current_user.name)
