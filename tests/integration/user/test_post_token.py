from fastapi.testclient import TestClient


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
        assert register_response.status_code == 201

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
        assert register_response.status_code == 201

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
