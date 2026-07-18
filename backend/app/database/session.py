from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.app_env == "development",
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


async def init_db() -> None:
    """Verify connectivity and enable pgvector for future embedding storage."""
    async with engine.begin() as connection:
        await connection.execute(text("SELECT 1"))
        await connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))


async def close_db() -> None:
    await engine.dispose()
