"""Test data fixtures and factories."""

from typing import Any, Dict


class TestUserData:
    """Test user data factory."""

    @staticmethod
    def valid_user() -> Dict[str, Any]:
        """Create valid user registration data."""
        return {
            "email": "test@example.com",
            "name": "Test User",
            "password": "testpassword123",
        }

    @staticmethod
    def valid_user_2() -> Dict[str, Any]:
        """Create another valid user for testing multiple users."""
        return {
            "email": "user2@example.com",
            "name": "Second User",
            "password": "password456",
        }

    @staticmethod
    def invalid_user_missing_email() -> Dict[str, Any]:
        """User data with missing email."""
        return {"name": "Test User", "password": "testpassword123"}

    @staticmethod
    def invalid_user_missing_name() -> Dict[str, Any]:
        """User data with missing name."""
        return {"email": "test@example.com", "password": "testpassword123"}

    @staticmethod
    def invalid_user_missing_password() -> Dict[str, Any]:
        """User data with missing password."""
        return {"email": "test@example.com", "name": "Test User"}

    @staticmethod
    def invalid_user_bad_email() -> Dict[str, Any]:
        """User data with invalid email format."""
        return {
            "email": "not-an-email",
            "name": "Test User",
            "password": "testpassword123",
        }

    @staticmethod
    def login_credentials(
        email: str = "test@example.com", password: str = "testpassword123"
    ) -> Dict[str, str]:
        """Create login credentials for OAuth2PasswordRequestForm."""
        return {
            "username": email,  # FastAPI OAuth2 uses 'username' field
            "password": password,
        }

    @staticmethod
    def invalid_login_credentials() -> Dict[str, str]:
        """Create invalid login credentials."""
        return {"username": "nonexistent@example.com", "password": "wrongpassword"}
