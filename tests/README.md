# Integration Tests with Testcontainers

This directory contains comprehensive integration tests for the user endpoints using testcontainers to provide isolated database testing.

## Overview

The integration tests cover all endpoints defined in `app/id/user_context/route.py`:

- **POST /user/register** - User registration
- **POST /user/token** - Authentication/token generation  
- **GET /user/profile** - Get user profile (protected endpoint)

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and testcontainer setup
├── integration/
│   └── test_user_endpoints.py     # Main integration tests
├── fixtures/
│   └── test_data.py              # Test data factories (optional)
└── utils/
    └── helpers.py                # Test utilities (optional)
```

## Test Categories

### 1. TestUserRegistration
- ✅ Successful user registration with valid data
- ❌ Registration with duplicate email
- ❌ Registration with missing required fields
- ❌ Registration with invalid email format

### 2. TestTokenGeneration  
- ✅ Successful token generation with valid credentials
- ❌ Token generation with non-existent email
- ❌ Token generation with wrong password
- ❌ Token generation with missing credentials

### 3. TestUserProfile
- ✅ Profile retrieval with valid token
- ❌ Profile retrieval without token
- ❌ Profile retrieval with invalid token
- ❌ Profile retrieval with malformed token
- ❌ Profile retrieval with expired token

### 4. TestEndToEndUserFlow
- ✅ Complete user journey: register → login → get profile
- ✅ Multiple users registration and authentication
- ✅ User data isolation testing

### 5. TestDatabaseState
- ✅ User data persistence verification
- ✅ Email uniqueness constraint testing

## Key Features

### Testcontainers Integration
- **PostgreSQL container**: Fresh database for each test session
- **Automatic cleanup**: Containers are automatically destroyed after tests
- **Isolation**: Each test has a clean database state
- **Real database**: Tests run against actual PostgreSQL, not mocks

### Test Fixtures
- `postgres_container`: Starts PostgreSQL testcontainer
- `test_database_url`: Provides connection URL for test database
- `test_engine`: Creates SQLAlchemy engine for tests
- `test_db_session`: Provides database session for each test
- `test_client`: FastAPI test client with database override
- `clean_database`: Ensures clean database state between tests

### Database Setup
- Creates `id` schema automatically
- Imports User model to register with SQLAlchemy metadata
- Creates all tables before tests run
- Cleans up tables after tests complete

## Running Tests

### Run All Integration Tests
```bash
uv run pytest tests/integration/ -v
```

### Run Specific Test Class
```bash
uv run pytest tests/integration/test_user_endpoints.py::TestUserRegistration -v
```

### Run Single Test
```bash
uv run pytest tests/integration/test_user_endpoints.py::TestUserRegistration::test_successful_user_registration -v
```

### Run with Output
```bash
uv run pytest tests/integration/ -v -s
```

### Run Tests with Coverage
```bash
uv run pytest tests/integration/ --cov=app --cov-report=html
```

## Dependencies

The following packages are required and installed via `uv add --dev`:

- `pytest` - Testing framework
- `pytest-asyncio` - Async testing support
- `testcontainers` - Container management for tests
- `httpx` - HTTP client for FastAPI testing

## Configuration

### pytest.ini
```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers --disable-warnings
markers =
    integration: marks tests as integration tests
    slow: marks tests as slow running
```

## Test Data Management

Tests use inline test data to ensure clarity and maintainability:
- Each test defines its own data
- Helper methods for common operations (registration, login)
- Consistent naming patterns for test users

## Error Scenarios Covered

### Registration Errors
- Duplicate email registration (400)
- Missing required fields (422)
- Invalid data formats (422)

### Authentication Errors  
- Invalid credentials (401)
- Missing credentials (422)
- Non-existent users (401)

### Authorization Errors
- Missing authentication token (401)
- Invalid/malformed tokens (401)
- Expired tokens (401)

## Database Testing

### Data Persistence
- Verifies user data is correctly stored
- Confirms password hashing
- Validates database constraints

### Isolation Testing
- Ensures users can't access each other's data
- Verifies token-based authentication boundaries
- Tests concurrent user operations

## Performance Considerations

- **Container reuse**: PostgreSQL container is reused across test session
- **Fast cleanup**: Database tables are truncated, not dropped/recreated
- **Optimized fixtures**: Minimal setup/teardown overhead
- **Parallel execution**: Tests can run in parallel (with separate containers)

## Troubleshooting

### Common Issues

1. **Docker not available**: Ensure Docker is running
2. **Port conflicts**: Testcontainers automatically assigns free ports
3. **Container startup timeout**: Check Docker resources and network
4. **Import errors**: Ensure all dependencies are installed with `uv add --dev`

### Debug Tips

1. Use `-s` flag to see print statements
2. Use `-vv` for extra verbose output  
3. Check container logs if tests hang during startup
4. Verify database schema creation in test output

## Adding New Tests

When adding new endpoints to `route.py`:

1. Add corresponding test class in `test_user_endpoints.py`
2. Include positive and negative test cases
3. Test authentication/authorization if applicable
4. Add end-to-end flow tests
5. Verify database state changes

## Example Test Pattern

```python
def test_new_endpoint(self, test_client: TestClient, clean_database):
    """Test description."""
    # Setup test data
    test_data = {"field": "value"}
    
    # Execute request
    response = test_client.post("/endpoint", json=test_data)
    
    # Verify response
    assert response.status_code == 200
    assert response.json()["field"] == test_data["field"]
```

This comprehensive test suite ensures all user endpoints work correctly with real database interactions and proper isolation between tests.
