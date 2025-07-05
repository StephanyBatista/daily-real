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

    # Create the 'id' schema that our app expects
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS id"))
        conn.commit()

    # Import User model to register it with Base.metadata
    from app.id.user._user import User  # noqa: F401

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
    # Delete all users from the test database
    try:
        test_db_session.execute(text("DELETE FROM id.users"))
        test_db_session.commit()
    except Exception:
        # Table might not exist yet, ignore the error
        test_db_session.rollback()

    yield

    # Clean up after test
    try:
        test_db_session.execute(text("DELETE FROM id.users"))
        test_db_session.commit()
    except Exception:
        # Table might not exist, ignore the error
        test_db_session.rollback()
