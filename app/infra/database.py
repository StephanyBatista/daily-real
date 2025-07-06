import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

# Create Base first, before it's used
Base = declarative_base()

# PostgreSQL connection string
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5436/econ_db"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Initialize database schemas"""
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS id"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS movement"))
        conn.commit()


def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)
