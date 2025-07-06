from fastapi import APIRouter

from app.movement.account._post_register import post_register

account_router = APIRouter()

account_router.add_api_route(
    "/",
    endpoint=post_register,
    methods=["POST"],
    response_model=None,
    tags=["Account Registration"],
    summary="Register a new Account",
)
