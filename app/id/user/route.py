from fastapi import APIRouter

from app.id.user._get_profile import UserProfile, get_user_profile
from app.id.user._post_register import UserResponse, register
from app.id.user._post_token import TokenResponse, token

user_router = APIRouter()

user_router.add_api_route(
    "/register",
    endpoint=register,
    methods=["POST"],
    response_model=UserResponse,
    tags=["User Registration"],
    summary="Register a new user",
    description="Register a new user with email, name, and password.",
)

user_router.add_api_route(
    "/token",
    endpoint=token,
    methods=["POST"],
    response_model=TokenResponse,
    tags=["Generate Access Token"],
    summary="Generate Access Token",
    description="Generate Access Token",
)

user_router.add_api_route(
    "/profile",
    endpoint=get_user_profile,
    methods=["get"],
    response_model=UserProfile,
    tags=["User Profile"],
    summary="Get User Profile",
    description="Get User Profile (protected endpoint example).",
)
