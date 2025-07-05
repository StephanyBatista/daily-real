import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.id.user_context.route import user_router

# Load environment variables from .env file
load_dotenv()

# Create FastAPI instance
app = FastAPI(
    title="Daily Real",
    description="App to trace my money",
    version="0.1.0",
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
