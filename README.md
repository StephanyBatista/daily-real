# Daily Real

A FastAPI application for tracking personal finances and money management.

## Prerequisites

Before running this project, make sure you have the following installed:

- [Python 3.13+](https://www.python.org/downloads/)
- [UV](https://docs.astral.sh/uv/getting-started/installation/) - Python package manager
- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) - For running PostgreSQL database

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd daily-real
```

### 2. Environment Setup

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit the `.env` file with your preferred settings. The default values should work for local development.

### 3. Install Dependencies

Install all project dependencies using UV:

```bash
uv sync
```

### 4. Start the Database

Start the PostgreSQL database using Docker Compose:

```bash
docker compose up -d postgres
```

This will start a PostgreSQL container on port 5436 with the database `econ_db`.

### 5. Run the Application

Start the FastAPI development server:

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc

## Running Tests

### Run All Tests

```bash
uv run pytest tests -v
```

### Run Specific Test Categories

```bash
# Run integration tests only
uv run pytest tests/integration -v

# Run with more detailed output
uv run pytest tests -v -s

# Run with coverage (if configured)
uv run pytest tests --cov=app
```

## Project Structure

```
├── app/                    # Main application code
│   ├── main.py            # FastAPI app initialization
│   ├── id/                # Identity/user management module
│   │   └── user/  # User-related functionality
│   └── infra/             # Infrastructure code (database, etc.)
├── tests/                 # Test suite
│   ├── integration/       # Integration tests
│   ├── fixtures/          # Test data and fixtures
│   └── utils/             # Test utilities
├── docker-compose.yaml    # Docker services configuration
├── pyproject.toml         # Project dependencies and configuration
└── .env.example          # Example environment variables
```

## Development

### Code Formatting

This project uses Ruff for code formatting and linting:

```bash
# Format code
uv run ruff format

# Check for linting issues
uv run ruff check

# Fix auto-fixable linting issues
uv run ruff check --fix
```

### Database Management

The application uses SQLAlchemy with PostgreSQL. Database connection details are configured via environment variables.

## API Documentation

Once the application is running, you can explore the API using:

- **Swagger UI**: Navigate to http://localhost:8000/docs
- **ReDoc**: Navigate to http://localhost:8000/redoc

## Troubleshooting

### Common Issues

1. **Port already in use**: If port 8000 is already in use, you can specify a different port:
   ```bash
   uv run uvicorn app.main:app --reload --port 8001
   ```

2. **Database connection issues**: Make sure the PostgreSQL container is running:
   ```bash
   docker compose ps
   docker compose logs postgres
   ```

3. **Dependency issues**: If you encounter dependency conflicts, try:
   ```bash
   uv sync --reinstall
   ```

### Stopping Services

To stop the database:
```bash
docker compose down
```

To stop the application, press `Ctrl+C` in the terminal where uvicorn is running.

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Run tests to ensure everything works: `uv run pytest tests -v`
4. Format your code: `uv run ruff format`
5. Submit a pull request