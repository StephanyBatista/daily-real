from fastapi.testclient import TestClient


class TestUserProfile:
    """Test cases for user profile endpoint."""

    def test_successful_profile_retrieval(
        self, test_client: TestClient, authenticated_user, clean_database
    ):
        """Test successful profile retrieval with valid token."""
        response = test_client.get(
            "/user/profile", headers=authenticated_user["headers"]
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["email"] == authenticated_user["email"]
        assert response_data["name"] == authenticated_user["name"]

    def test_profile_without_token(self, test_client: TestClient, clean_database):
        """Test profile retrieval without authentication token."""
        response = test_client.get("/user/profile")
        assert response.status_code == 401

    def test_profile_with_invalid_token(self, test_client: TestClient, clean_database):
        """Test profile retrieval with invalid token."""
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = test_client.get("/user/profile", headers=headers)
        assert response.status_code == 401

    def test_profile_with_malformed_token(
        self, test_client: TestClient, clean_database
    ):
        """Test profile retrieval with malformed token."""
        headers = {"Authorization": "InvalidFormatToken"}
        response = test_client.get("/user/profile", headers=headers)
        assert response.status_code == 401

    def test_profile_with_expired_token(self, test_client: TestClient, clean_database):
        """Test profile retrieval with expired token."""
        # This test would require manipulating token expiration
        # For now, we can create a token with past expiration date
        import os
        from datetime import datetime, timedelta, timezone

        from jose import jwt

        SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        ALGORITHM = "HS256"

        # Create expired token
        expired_payload = {
            "sub": "expired@example.com",
            "name": "Expired User",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),  # 1 hour ago
        }
        expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)

        headers = {"Authorization": f"Bearer {expired_token}"}
        response = test_client.get("/user/profile", headers=headers)
        assert response.status_code == 401
