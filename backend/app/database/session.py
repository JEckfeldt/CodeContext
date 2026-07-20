from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.database.base import Base
from app.models import File, Project  # noqa: F401


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
    """Verify connectivity, enable pgvector, and create schema."""
    async with engine.begin() as connection:
        await connection.execute(text("SELECT 1"))
        if settings.database_url.startswith("postgresql"):
            await connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await connection.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    await engine.dispose()
