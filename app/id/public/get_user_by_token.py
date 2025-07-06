from fastapi import HTTPException, status
from fastapi.params import Depends

from app.id.public.user_by_token import UserByToken
from app.id.user._auth import oauth2_scheme, verify_token


async def get_user_by_token(token: str = Depends(oauth2_scheme)):
    """Dependency to get current authenticated user."""
    payload = verify_token(token)
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserByToken(email=email, name=payload.get("name"))
