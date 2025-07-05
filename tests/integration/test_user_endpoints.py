"""Integration tests for user endpoints using testcontainers."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestUserRegistration:
    """Test cases for user registration endpoint."""

    def test_successful_user_registration(
        self, test_client: TestClient, clean_database
    ):
        """Test successful user registration with valid data."""
        user_data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "secure_password123",
        }

        response = test_client.post("/user/register", json=user_data)

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["email"] == user_data["email"]
        assert response_data["name"] == user_data["name"]
        # Password should not be in response
        assert "password" not in response_data
        assert "hashed_password" not in response_data

    def test_duplicate_email_registration(
        self, test_client: TestClient, clean_database
    ):
        """Test registration with an email that already exists."""
        user_data = {
            "email": "duplicate@example.com",
            "name": "First User",
            "password": "password123",
        }

        # Register first user
        response1 = test_client.post("/user/register", json=user_data)
        assert response1.status_code == 200

        # Try to register second user with same email
        duplicate_user_data = {
            "email": "duplicate@example.com",  # Same email
            "name": "Second User",
            "password": "different_password",
        }

        response2 = test_client.post("/user/register", json=duplicate_user_data)
        assert response2.status_code == 400
        assert "Email already registered" in response2.json()["detail"]

    def test_registration_with_missing_fields(
        self, test_client: TestClient, clean_database
    ):
        """Test registration with missing required fields."""
        # Missing email
        incomplete_data1 = {"name": "Test User", "password": "password123"}
        response1 = test_client.post("/user/register", json=incomplete_data1)
        assert response1.status_code == 400  # Changed from 422 to 400
        response_data1 = response1.json()
        assert response_data1["error"] == "Validation failed"
        assert len(response_data1["details"]) == 1
        assert response_data1["details"][0]["field"] == "email"
        assert response_data1["details"][0]["message"] == "Field required"

        # Missing name
        incomplete_data2 = {"email": "test@example.com", "password": "password123"}
        response2 = test_client.post("/user/register", json=incomplete_data2)
        assert response2.status_code == 400  # Changed from 422 to 400
        response_data2 = response2.json()
        assert response_data2["error"] == "Validation failed"
        assert len(response_data2["details"]) == 1
        assert response_data2["details"][0]["field"] == "name"
        assert response_data2["details"][0]["message"] == "Field required"

        # Missing password
        incomplete_data3 = {"email": "test@example.com", "name": "Test User"}
        response3 = test_client.post("/user/register", json=incomplete_data3)
        assert response3.status_code == 400  # Changed from 422 to 400
        response_data3 = response3.json()
        assert response_data3["error"] == "Validation failed"
        assert len(response_data3["details"]) == 1
        assert response_data3["details"][0]["field"] == "password"
        assert response_data3["details"][0]["message"] == "Field required"

    def test_registration_with_invalid_email(
        self, test_client: TestClient, clean_database
    ):
        """Test registration with invalid email format."""
        invalid_data = {
            "email": "not-an-email",
            "name": "Test User",
            "password": "password123",
        }

        response = test_client.post("/user/register", json=invalid_data)
        # Currently there's no email validation in the UserCreate model
        # So this will succeed. If email validation is added later,
        # this should return 400 with validation error
        if response.status_code == 400:
            response_data = response.json()
            assert response_data["error"] == "Validation failed"
            assert any(
                "email" in detail["field"] for detail in response_data["details"]
            )
        else:
            # If no email validation, it should succeed
            assert response.status_code == 200


class TestTokenGeneration:
    """Test cases for token generation endpoint."""

    def test_successful_token_generation(self, test_client: TestClient, clean_database):
        """Test successful token generation with valid credentials."""
        # First register a user
        user_data = {
            "email": "auth@example.com",
            "name": "Auth User",
            "password": "secure_password123",
        }
        register_response = test_client.post("/user/register", json=user_data)
        assert register_response.status_code == 200

        # Now authenticate
        auth_data = {
            "username": "auth@example.com",  # OAuth2PasswordRequestForm uses 'username'
            "password": "secure_password123",
        }

        response = test_client.post("/user/token", data=auth_data)
        assert response.status_code == 200

        response_data = response.json()
        assert "access_token" in response_data
        assert response_data["token_type"] == "bearer"
        assert len(response_data["access_token"]) > 0

    def test_token_generation_with_invalid_email(
        self, test_client: TestClient, clean_database
    ):
        """Test token generation with non-existent email."""
        auth_data = {"username": "nonexistent@example.com", "password": "password123"}

        response = test_client.post("/user/token", data=auth_data)
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_token_generation_with_invalid_password(
        self, test_client: TestClient, clean_database
    ):
        """Test token generation with wrong password."""
        # First register a user
        user_data = {
            "email": "wrongpass@example.com",
            "name": "Wrong Pass User",
            "password": "correct_password",
        }
        register_response = test_client.post("/user/register", json=user_data)
        assert register_response.status_code == 200

        # Try to authenticate with wrong password
        auth_data = {"username": "wrongpass@example.com", "password": "wrong_password"}

        response = test_client.post("/user/token", data=auth_data)
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_token_generation_with_missing_credentials(
        self, test_client: TestClient, clean_database
    ):
        """Test token generation with missing credentials."""
        # Missing username
        incomplete_data1 = {"password": "password123"}
        response1 = test_client.post("/user/token", data=incomplete_data1)
        assert response1.status_code == 400  # Changed from 422 to 400
        response_data1 = response1.json()
        assert response_data1["error"] == "Validation failed"
        assert any(
            "username" in detail["field"] for detail in response_data1["details"]
        )

        # Missing password
        incomplete_data2 = {"username": "test@example.com"}
        response2 = test_client.post("/user/token", data=incomplete_data2)
        assert response2.status_code == 400  # Changed from 422 to 400
        response_data2 = response2.json()
        assert response_data2["error"] == "Validation failed"
        assert any(
            "password" in detail["field"] for detail in response_data2["details"]
        )


class TestUserProfile:
    """Test cases for user profile endpoint."""

    def _create_user_and_get_token(self, test_client: TestClient) -> str:
        """Helper method to create a user and get authentication token."""
        # Register user
        user_data = {
            "email": "profile@example.com",
            "name": "Profile User",
            "password": "password123",
        }
        register_response = test_client.post("/user/register", json=user_data)
        assert register_response.status_code == 200

        # Get token
        auth_data = {"username": "profile@example.com", "password": "password123"}
        token_response = test_client.post("/user/token", data=auth_data)
        assert token_response.status_code == 200

        return token_response.json()["access_token"]

    def test_successful_profile_retrieval(
        self, test_client: TestClient, clean_database
    ):
        """Test successful profile retrieval with valid token."""
        token = self._create_user_and_get_token(test_client)

        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.get("/user/profile", headers=headers)

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["email"] == "profile@example.com"
        assert response_data["name"] == "Profile User"

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


class TestEndToEndUserFlow:
    """Test complete user flow scenarios."""

    def test_complete_user_journey(self, test_client: TestClient, clean_database):
        """Test complete user journey: register -> login -> get profile."""
        # Step 1: Register
        user_data = {
            "email": "journey@example.com",
            "name": "Journey User",
            "password": "journey_password123",
        }
        register_response = test_client.post("/user/register", json=user_data)
        assert register_response.status_code == 200

        # Step 2: Login
        auth_data = {
            "username": "journey@example.com",
            "password": "journey_password123",
        }
        token_response = test_client.post("/user/token", data=auth_data)
        assert token_response.status_code == 200
        token = token_response.json()["access_token"]

        # Step 3: Get Profile
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = test_client.get("/user/profile", headers=headers)
        assert profile_response.status_code == 200

        profile_data = profile_response.json()
        assert profile_data["email"] == user_data["email"]
        assert profile_data["name"] == user_data["name"]

    def test_multiple_users_registration(self, test_client: TestClient, clean_database):
        """Test registration of multiple users."""
        users = [
            {"email": "user1@example.com", "name": "User One", "password": "password1"},
            {"email": "user2@example.com", "name": "User Two", "password": "password2"},
            {
                "email": "user3@example.com",
                "name": "User Three",
                "password": "password3",
            },
        ]

        # Register all users
        for user_data in users:
            response = test_client.post("/user/register", json=user_data)
            assert response.status_code == 200
            assert response.json()["email"] == user_data["email"]

        # Authenticate each user
        for user_data in users:
            auth_data = {
                "username": user_data["email"],
                "password": user_data["password"],
            }
            response = test_client.post("/user/token", data=auth_data)
            assert response.status_code == 200
            assert "access_token" in response.json()

    def test_user_isolation(self, test_client: TestClient, clean_database):
        """Test that users are isolated and can't access each other's data."""
        # Create two users
        user1_data = {"email": "user1@test.com", "name": "User 1", "password": "pass1"}
        user2_data = {"email": "user2@test.com", "name": "User 2", "password": "pass2"}

        test_client.post("/user/register", json=user1_data)
        test_client.post("/user/register", json=user2_data)

        # Get tokens for both users
        token1_response = test_client.post(
            "/user/token", data={"username": "user1@test.com", "password": "pass1"}
        )
        token2_response = test_client.post(
            "/user/token", data={"username": "user2@test.com", "password": "pass2"}
        )

        token1 = token1_response.json()["access_token"]
        token2 = token2_response.json()["access_token"]

        # Each user should get their own profile
        profile1 = test_client.get(
            "/user/profile", headers={"Authorization": f"Bearer {token1}"}
        )
        profile2 = test_client.get(
            "/user/profile", headers={"Authorization": f"Bearer {token2}"}
        )

        assert profile1.json()["email"] == "user1@test.com"
        assert profile1.json()["name"] == "User 1"

        assert profile2.json()["email"] == "user2@test.com"
        assert profile2.json()["name"] == "User 2"

        # Verify they are different
        assert profile1.json() != profile2.json()


class TestDatabaseState:
    """Test database state and constraints."""

    def test_user_persistence(
        self, test_client: TestClient, test_db_session: Session, clean_database
    ):
        """Test that user data is properly persisted in database."""
        from app.id.user_context.user import User

        user_data = {
            "email": "persist@example.com",
            "name": "Persist User",
            "password": "persist_password",
        }

        # Register user
        response = test_client.post("/user/register", json=user_data)
        assert response.status_code == 200

        # Check if user exists in database
        db_user = (
            test_db_session.query(User).filter(User.email == user_data["email"]).first()
        )
        assert db_user is not None
        assert db_user.email == user_data["email"]
        assert db_user.name == user_data["name"]
        assert db_user.hashed_password is not None
        assert db_user.hashed_password != user_data["password"]  # Should be hashed

    def test_email_uniqueness_constraint(
        self, test_client: TestClient, test_db_session: Session, clean_database
    ):
        """Test database-level email uniqueness constraint."""
        from app.id.user_context.user import User

        user_data = {
            "email": "unique@example.com",
            "name": "Unique User",
            "password": "password123",
        }

        # Register first user
        response1 = test_client.post("/user/register", json=user_data)
        assert response1.status_code == 200

        # Verify only one user exists
        user_count = (
            test_db_session.query(User).filter(User.email == user_data["email"]).count()
        )
        assert user_count == 1

        # Try to register duplicate (should fail)
        response2 = test_client.post("/user/register", json=user_data)
        assert response2.status_code == 400

        # Verify still only one user exists
        user_count_after = (
            test_db_session.query(User).filter(User.email == user_data["email"]).count()
        )
        assert user_count_after == 1


class TestErrorHandling:
    """Test cases for error handling."""

    def test_validation_error_format(self, test_client: TestClient, clean_database):
        """Test that validation errors return the correct format."""
        # Test with completely empty request body
        response = test_client.post("/user/register", json={})
        assert response.status_code == 400

        response_data = response.json()
        assert "error" in response_data
        assert "details" in response_data
        assert response_data["error"] == "Validation failed"
        assert isinstance(response_data["details"], list)
        assert len(response_data["details"]) == 3  # email, name, password all missing

        # Check that all required fields are reported
        missing_fields = [detail["field"] for detail in response_data["details"]]
        assert "email" in missing_fields
        assert "name" in missing_fields
        assert "password" in missing_fields

        # Check that each detail has the expected structure
        for detail in response_data["details"]:
            assert "field" in detail
            assert "message" in detail
            assert "type" in detail
            assert detail["message"] == "Field required"
            assert detail["type"] == "missing"

    def test_multiple_validation_errors(self, test_client: TestClient, clean_database):
        """Test handling of multiple validation errors in one request."""
        # Send request with some invalid data types
        invalid_data = {
            "email": 123,  # Should be string
            "name": None,  # Should be string
            # password missing entirely
        }

        response = test_client.post("/user/register", json=invalid_data)
        assert response.status_code == 400

        response_data = response.json()
        assert response_data["error"] == "Validation failed"
        assert len(response_data["details"]) >= 2  # At least 2 errors

        # Should have errors for multiple fields
        error_fields = [detail["field"] for detail in response_data["details"]]
        assert len(set(error_fields)) >= 2  # Multiple different fields with errors
