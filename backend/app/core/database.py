"""
Database connection and session management.

This module provides SQLAlchemy engine, session, and base model.
Supports both sync and async operations for maximum flexibility.
"""

from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create SQLAlchemy engine (sync)
# Handle both PostgreSQL (production) and SQLite (testing)
database_url = str(settings.DATABASE_URL)

if database_url.startswith("sqlite"):
    # SQLite doesn't support pool_size and max_overflow
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG,
    )
else:
    # PostgreSQL with connection pooling
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=settings.DEBUG,
    )

# Create session factory (sync)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Create async engine for async operations (checkpoint queries, etc.)
# Convert postgresql:// or postgres:// to postgresql+asyncpg://
async_database_url = str(settings.DATABASE_URL)
if async_database_url.startswith("postgres://"):
    # Handle both postgres:// and postgresql:// formats
    async_database_url = async_database_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif async_database_url.startswith("postgresql://"):
    async_database_url = async_database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif async_database_url.startswith("sqlite"):
    # SQLite async support (would need aiosqlite)
    async_database_url = async_database_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)

if async_database_url.startswith("sqlite"):
    # SQLite async engine
    async_engine = create_async_engine(
        async_database_url,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG,
    )
else:
    # PostgreSQL async engine with connection pooling
    async_engine = create_async_engine(
        async_database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=settings.DEBUG,
    )

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


def get_db():
    """
    Dependency function to get database session (sync).
    
    Yields:
        Session: SQLAlchemy database session
    
    Example:
        >>> from fastapi import Depends
        >>> @router.get("/users")
        >>> def get_users(db: Session = Depends(get_db)):
        >>>     return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get async database session.
    
    Yields:
        AsyncSession: SQLAlchemy async database session
    
    Example:
        >>> from fastapi import Depends
        >>> @router.get("/metrics")
        >>> async def get_metrics(db: AsyncSession = Depends(get_async_db)):
        >>>     result = await db.execute(query)
        >>>     return result
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
