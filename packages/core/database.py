from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from .models import Base
import os
from pathlib import Path

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/app.db")


def _ensure_db_directory_exists(db_url: str) -> None:
    """Ensure the directory for the database file exists"""
    db_path = None
    if db_url.startswith("sqlite+aiosqlite:///"):
        db_path = db_url.replace("sqlite+aiosqlite:///", "")
    elif db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
    
    if db_path and not db_path.startswith(":memory:"):
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)


# Ensure the directory for the database file exists
_ensure_db_directory_exists(DATABASE_URL)

# Convert sqlite:/// to sqlite+aiosqlite:/// for async support
if DATABASE_URL.startswith("sqlite:///"):
    DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
