"""Test utility functions."""

from typing import Any, Dict

from fastapi.testclient import TestClient


class TestHelpers:
    """Helper functions for testing."""

    @staticmethod
    def register_user(client: TestClient, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to register a user and return the response."""
        response = client.post("/user/register", json=user_data)
        return {
            "response": response,
            "status_code": response.status_code,
            "json": response.json() if response.status_code != 422 else None,
        }

    @staticmethod
    def login_user(client: TestClient, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Helper to login a user and return the response with token."""
        response = client.post("/user/token", data=credentials)
        result = {
            "response": response,
            "status_code": response.status_code,
            "json": response.json() if response.status_code == 200 else None,
        }

        if response.status_code == 200:
            result["token"] = response.json().get("access_token")

        return result

    @staticmethod
    def get_user_profile(client: TestClient, token: str) -> Dict[str, Any]:
        """Helper to get user profile with authentication."""
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/user/profile", headers=headers)
        return {
            "response": response,
            "status_code": response.status_code,
            "json": response.json() if response.status_code == 200 else None,
        }

    @staticmethod
    def register_and_login_user(
        client: TestClient, user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Helper to register a user and then login, returning the token."""
        # Register user
        register_result = TestHelpers.register_user(client, user_data)
        if register_result["status_code"] != 200:
            return {"error": "Registration failed", "register_result": register_result}

        # Login user
        credentials = {
            "username": user_data["email"],
            "password": user_data["password"],
        }
        login_result = TestHelpers.login_user(client, credentials)

        return {
            "register_result": register_result,
            "login_result": login_result,
            "token": login_result.get("token"),
        }
