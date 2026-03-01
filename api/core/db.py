from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from core.config import settings

# Async Engine used by the API endpoints
engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Sync Engine used by Alembic and possibly background threads if needed
sync_engine = create_engine(settings.SYNC_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

Base = declarative_base()


# Dependency for API Routes
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
