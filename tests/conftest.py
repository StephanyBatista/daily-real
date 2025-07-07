"""Shared test fixtures and configuration."""

from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.postgres import PostgresContainer

from app.infra.database import Base, get_db


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """Start a PostgreSQL test container for the entire test session."""
    with PostgresContainer("postgres:15-alpine") as postgres:
        # Wait for the container to be ready
        postgres.get_connection_url()
        yield postgres


@pytest.fixture(scope="session")
def test_database_url(postgres_container: PostgresContainer) -> str:
    """Get the database URL for the test container."""
    return postgres_container.get_connection_url()


@pytest.fixture(scope="session")
def test_engine(test_database_url: str):
    """Create a test database engine."""
    engine = create_engine(test_database_url)

    # Create the schemas that our app expects
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS id"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS movement"))
        conn.commit()

    # Import models to register them with Base.metadata
    from app.id.user._user import User  # noqa: F401
    from app.movement.account._account import (  # noqa: F401
        Account,
        BankDetail,
        CreditDetails,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Cleanup
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db_session(test_engine) -> Generator[Session, None, None]:
    """Create a test database session for each test."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def test_client(test_db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database dependency override."""

    def override_get_db():
        """Override the get_db dependency to use test database."""
        try:
            yield test_db_session
        finally:
            pass  # Session cleanup handled by test_db_session fixture

    # Import app here to avoid database initialization during import
    from app.main import app

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    # Clean up dependency override
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def clean_database(test_db_session: Session):
    """Clean the database before each test."""
    # Delete all data from test database tables
    try:
        # Delete in order due to foreign key constraints
        test_db_session.execute(text("DELETE FROM movement.credit_details"))
        test_db_session.execute(text("DELETE FROM movement.bank_details"))
        test_db_session.execute(text("DELETE FROM movement.accounts"))
        test_db_session.execute(text("DELETE FROM id.users"))
        test_db_session.commit()
    except Exception:
        # Tables might not exist yet, ignore the error
        test_db_session.rollback()

    yield

    # Clean up after test
    try:
        # Delete in order due to foreign key constraints
        test_db_session.execute(text("DELETE FROM movement.credit_details"))
        test_db_session.execute(text("DELETE FROM movement.bank_details"))
        test_db_session.execute(text("DELETE FROM movement.accounts"))
        test_db_session.execute(text("DELETE FROM id.users"))
        test_db_session.commit()
    except Exception:
        # Tables might not exist, ignore the error
        test_db_session.rollback()


@pytest.fixture(scope="function")
def authenticated_user(test_client: TestClient, clean_database):
    """Create an authenticated user and return the token."""
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "password": "secure_password123",
    }
    test_client.post("/user/register", json=user_data)

    # Authenticate to get token
    auth_data = {"username": "test@example.com", "password": "secure_password123"}
    auth_response = test_client.post("/user/token", data=auth_data)
    token = auth_response.json()["access_token"]

    return {
        "token": token,
        "email": "test@example.com",
        "name": "Test User",
        "headers": {"Authorization": f"Bearer {token}"},
    }


@pytest.fixture(scope="function")
def authenticated_user_factory(test_client: TestClient, clean_database):
    """Factory fixture to create multiple authenticated users with different emails."""
    created_users = []

    def _create_user(
        email: str, name: str = "Test User", password: str = "secure_password123"
    ):
        user_data = {
            "email": email,
            "name": name,
            "password": password,
        }
        test_client.post("/user/register", json=user_data)

        # Authenticate to get token
        auth_data = {"username": email, "password": password}
        auth_response = test_client.post("/user/token", data=auth_data)
        token = auth_response.json()["access_token"]

        user_info = {
            "token": token,
            "email": email,
            "name": name,
            "headers": {"Authorization": f"Bearer {token}"},
        }
        created_users.append(user_info)
        return user_info

    yield _create_user

    # Cleanup is handled by clean_database fixture
