from typing import List

from fastapi import APIRouter

from app.movement.account._account_response import AccountResponse
from app.movement.account._get_accounts import get_accounts
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

account_router.add_api_route(
    "/",
    endpoint=get_accounts,
    methods=["GET"],
    response_model=List[AccountResponse],
    tags=["Account"],
    summary="Get accounts by current user",
)
