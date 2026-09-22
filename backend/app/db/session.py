"""Async SQLAlchemy engine + session factory."""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(
    settings.async_db_url,
    pool_size=settings.DB_POOL_SIZE if hasattr(settings, "DB_POOL_SIZE") else 5,
    max_overflow=settings.DB_MAX_OVERFLOW if hasattr(settings, "DB_MAX_OVERFLOW") else 10,
    pool_timeout=30,
    pool_pre_ping=True, # Automatically checks if connection is alive before using it
    pool_recycle=1800,  # Recycle connections after 30 minutes to prevent timeouts
    echo=settings.APP_ENV == "development",
    connect_args={
        "statement_cache_size": 0
    }
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """SQLAlchemy declarative base — all ORM models inherit from this."""
    pass


async def get_db():
    """FastAPI dependency: yields an async DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
