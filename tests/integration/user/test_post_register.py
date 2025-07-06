from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.id.user._user import User


class TestUserRegistration:
    """Test cases for user registration endpoint."""

    def test_successful_user_registration(
        self, test_client: TestClient, test_db_session: Session, clean_database
    ):
        """Test successful user registration with valid data."""
        user_data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "secure_password123",
        }

        response = test_client.post("/user/register", json=user_data)

        assert response.status_code == 201
        # Check if user exists in database
        db_user = (
            test_db_session.query(User).filter(User.email == user_data["email"]).first()
        )
        assert db_user is not None
        assert db_user.email == user_data["email"]
        assert db_user.name == user_data["name"]
        assert db_user.hashed_password is not None
        assert db_user.hashed_password != user_data["password"]  # Should be hashed

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
        assert response1.status_code == 201

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

        response_data = response.json()
        assert response_data["error"] == "Validation failed"
        assert any("email" in detail["field"] for detail in response_data["details"])
