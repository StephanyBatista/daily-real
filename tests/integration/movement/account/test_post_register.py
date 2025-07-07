from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.movement.account._account import Account


class TestAccountRegistration:
    """Test cases for account registration endpoint."""

    def test_successful_credit_card_account_registration(
        self, test_client: TestClient, test_db_session: Session, authenticated_user
    ):
        """Test successful credit card account registration with valid data."""

        # Create credit card account
        account_data = {
            "name": "My Credit Card",
            "credit_details": {
                "last_four_digits": "1234",
                "billing_cycle_day": 15,
                "due_day": 5,
            },
        }

        response = test_client.post(
            "/account/", json=account_data, headers=authenticated_user["headers"]
        )

        assert response.status_code == 201
        assert "Location" in response.headers
        assert "/accounts/" in response.headers["Location"]

        # Verify account was created in database
        db_account = (
            test_db_session.query(Account)
            .filter(Account.name == account_data["name"])
            .first()
        )
        assert db_account is not None
        assert db_account.name == account_data["name"]
        assert db_account.created_by == authenticated_user["email"]
        assert db_account.type.value == "CreditCard"

        # Verify credit details
        assert db_account.credit_details is not None
        assert db_account.credit_details.last_four_digits == "1234"
        assert db_account.credit_details.billing_cycle_day == 15
        assert db_account.credit_details.due_day == 5
        assert db_account.bank_detail is None

    def test_successful_bank_account_registration(
        self,
        test_client: TestClient,
        test_db_session: Session,
        authenticated_user_factory,
    ):
        """Test successful bank account registration with valid data."""
        # Create an authenticated user
        user = authenticated_user_factory("bank@example.com", "Bank User")

        # Create bank account
        account_data = {
            "name": "My Checking Account",
            "bank_detail": {
                "agency": "1234",
                "account_number": "567890123",
                "account_type": "Checking",
            },
        }

        response = test_client.post(
            "/account/", json=account_data, headers=user["headers"]
        )

        assert response.status_code == 201
        assert "Location" in response.headers
        assert "/accounts/" in response.headers["Location"]

        # Verify account was created in database
        db_account = (
            test_db_session.query(Account)
            .filter(Account.name == account_data["name"])
            .first()
        )
        assert db_account is not None
        assert db_account.name == account_data["name"]
        assert db_account.created_by == "bank@example.com"
        assert db_account.type.value == "Bank"

        # Verify bank details
        assert db_account.bank_detail is not None
        assert db_account.bank_detail.agency == "1234"
        assert db_account.bank_detail.account_number == "567890123"
        assert db_account.bank_detail.account_type == "Checking"
        assert db_account.credit_details is None

    def test_unauthorized_account_creation(
        self, test_client: TestClient, clean_database
    ):
        """Test account creation without authentication token."""
        account_data = {
            "name": "Unauthorized Account",
            "credit_details": {
                "last_four_digits": "1234",
                "billing_cycle_day": 15,
                "due_day": 5,
            },
        }

        response = test_client.post("/account/", json=account_data)
        assert response.status_code == 401

    def test_invalid_token_account_creation(
        self, test_client: TestClient, clean_database
    ):
        """Test account creation with invalid authentication token."""
        account_data = {
            "name": "Invalid Token Account",
            "credit_details": {
                "last_four_digits": "1234",
                "billing_cycle_day": 15,
                "due_day": 5,
            },
        }

        response = test_client.post(
            "/account/",
            json=account_data,
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == 401

    def test_account_creation_with_missing_fields(
        self, test_client: TestClient, authenticated_user
    ):
        """Test account creation with missing required fields."""

        # Missing name
        incomplete_data = {
            "credit_details": {
                "last_four_digits": "1234",
                "billing_cycle_day": 15,
                "due_day": 5,
            }
        }

        response = test_client.post(
            "/account/", json=incomplete_data, headers=authenticated_user["headers"]
        )
        assert response.status_code == 400
        response_data = response.json()
        assert response_data["error"] == "Validation failed"
        assert "name: field required" in response_data["details"]

    def test_account_creation_without_details(
        self, test_client: TestClient, authenticated_user_factory
    ):
        """Test account creation without credit_details or bank_detail."""
        # Create an authenticated user
        user = authenticated_user_factory("nodetails@example.com", "No Details User")

        # Account without any details
        account_data = {"name": "Account Without Details"}

        response = test_client.post(
            "/account/", json=account_data, headers=user["headers"]
        )
        # This should fail as the endpoint tries to access .bank_detail.agency when both are None
        assert response.status_code == 400
        assert "Validation failed" in response.json()["error"]
        assert (
            "Must provide either credit details or bank details for account configuration"
            in response.json()["details"]
        )

    def test_invalid_credit_card_details(
        self, test_client: TestClient, authenticated_user_factory
    ):
        """Test account creation with invalid credit card details."""
        # Create an authenticated user
        user = authenticated_user_factory("invalid@example.com", "Invalid User")

        # Invalid last_four_digits (not 4 digits)
        invalid_data = {
            "name": "Invalid Credit Card",
            "credit_details": {
                "last_four_digits": "123",  # Only 3 digits
                "billing_cycle_day": 15,
                "due_day": 5,
            },
        }

        response = test_client.post(
            "/account/", json=invalid_data, headers=user["headers"]
        )
        assert response.status_code == 400
        response_data = response.json()
        assert response_data["error"] == "Validation failed"
        assert (
            response_data["details"]
            == "credit_details.last_four_digits: must be exactly 4 digits"
        )

    def test_invalid_billing_cycle_day(
        self, test_client: TestClient, authenticated_user_factory
    ):
        """Test account creation with invalid billing cycle day."""
        # Create an authenticated user
        user = authenticated_user_factory("billing@example.com", "Billing User")

        # Invalid billing_cycle_day (out of range)
        invalid_data = {
            "name": "Invalid Billing Day",
            "credit_details": {
                "last_four_digits": "1234",
                "billing_cycle_day": 32,  # Invalid day
                "due_day": 5,
            },
        }

        response = test_client.post(
            "/account/", json=invalid_data, headers=user["headers"]
        )
        assert response.status_code == 400
        response_data = response.json()
        assert (
            response_data["details"]
            == "credit_details.billing_cycle_day: input should be less than or equal to 30"
        )

    def test_invalid_account_type(
        self, test_client: TestClient, authenticated_user_factory
    ):
        """Test account creation with invalid bank account type."""
        # Create an authenticated user
        user = authenticated_user_factory(
            "invalidtype@example.com", "Invalid Type User"
        )

        # Invalid account_type
        invalid_data = {
            "name": "Invalid Account Type",
            "bank_detail": {
                "agency": "1234",
                "account_number": "567890123",
                "account_type": "InvalidType",  # Not "Checking" or "Savings"
            },
        }

        response = test_client.post(
            "/account/", json=invalid_data, headers=user["headers"]
        )
        assert response.status_code == 400
        response_data = response.json()
        assert (
            response_data["details"]
            == "bank_detail.account_type: input should be 'checking' or 'savings'"
        )

    def test_long_account_name(
        self, test_client: TestClient, authenticated_user_factory
    ):
        """Test account creation with name exceeding maximum length."""
        # Create an authenticated user
        user = authenticated_user_factory("longname@example.com", "Long Name User")

        # Name longer than 32 characters
        long_name_data = {
            "name": "A" * 33,  # 33 characters, exceeds 32 char limit
            "credit_details": {
                "last_four_digits": "1234",
                "billing_cycle_day": 15,
                "due_day": 5,
            },
        }

        response = test_client.post(
            "/account/", json=long_name_data, headers=user["headers"]
        )
        assert response.status_code == 400
        response_data = response.json()
        assert (
            response_data["details"] == "name: string should have at most 32 characters"
        )
