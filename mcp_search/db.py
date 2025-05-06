"""Database setup and helper utilities."""

from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector

from .settings import settings

__all__ = [
    "engine",
    "async_session",
    "init_db",
]


engine = create_async_engine(str(settings.DATABASE_URL), echo=False, future=True)
async_session: sessionmaker[AsyncSession] = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db() -> None:
    """Initialise the database schema and ensure *pgvector* extension is loaded."""
    async with engine.begin() as conn:
        # Enable the pgvector extension if it is not already enabled.
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        # Create tables declared with SQLModel models.
        await conn.run_sync(SQLModel.metadata.create_all) 