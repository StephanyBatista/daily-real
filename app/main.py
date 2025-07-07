import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Import models to register them with SQLAlchemy metadata
from app.id.user._user import User  # noqa: F401
from app.id.user.route import user_router
from app.infra.database import create_tables, init_database
from app.movement.account._account import (  # noqa: F401
    Account,
    BankDetail,
    CreditDetails,
)
from app.movement.account.route import account_router
from app.util.exceptions import DomainException

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


# Create FastAPI instance
app = FastAPI(
    title="Daily Real",
    description="App to trace my money",
    version="0.1.0",
)

# Initialize database schemas and create tables
init_database()
create_tables()


# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for validation errors that returns 400 instead of 422
    """
    logger.warning(f"Validation error on {request.url}: {exc.errors()}")

    def get_human_readable_message(error):
        """Convert technical error messages to human-readable ones"""

        # Map common regex patterns to human messages
        if "String should match pattern" in error:
            if "'^\d{4}$'" in error:
                return "must be exactly 4 digits"
        return error
        # Add more pattern mappings as needed

    details = ""
    for error in exc.errors():
        field_name = ".".join(
            str(loc) for loc in error["loc"][1:]
        )  # Skip 'body' prefix
        details = f"{field_name}: {get_human_readable_message(error['msg'])}"

    return JSONResponse(
        status_code=400,
        content={
            "error": "Validation failed",
            "details": details.lower(),
        },
    )


@app.exception_handler(DomainException)
async def validation_domain_exception_handler(request: Request, exc: DomainException):
    """
    Custom handler for validation errors that returns 400 instead of 422
    """
    logger.warning(f"Validation error on {request.url}: {exc.error().lower()}")

    return JSONResponse(
        status_code=400, content={"error": "Validation failed", "details": exc.error()}
    )


# Generic exception handler for any unhandled errors
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Catch-all handler for any unhandled exceptions
    """
    logger.error(f"Unhandled exception on {request.url}: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
        },
    )


app.include_router(
    user_router,
    prefix="/user",
)

app.include_router(
    account_router,
    prefix="/account",
)


@app.get("/health")
async def health_check():
    return JSONResponse(status_code=200, content={"status": "ok"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app, host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", "8000"))
    )
