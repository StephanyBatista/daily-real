import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.id.user.route import user_router

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


# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for validation errors that returns 400 instead of 422
    """
    logger.warning(f"Validation error on {request.url}: {exc.errors()}")

    errors = []
    for error in exc.errors():
        field_name = ".".join(
            str(loc) for loc in error["loc"][1:]
        )  # Skip 'body' prefix
        errors.append(
            {"field": field_name, "message": error["msg"], "type": error["type"]}
        )

    return JSONResponse(
        status_code=400, content={"error": "Validation failed", "details": errors}
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


@app.get("/health")
async def health_check():
    return JSONResponse(status_code=200, content={"status": "ok"})


# Initialize database only when running the app directly
if __name__ == "__main__":
    from app.infra.database import create_tables, init_database

    init_database()
    create_tables()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app, host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", "8000"))
    )
