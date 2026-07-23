from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.dbengine import AsyncEngine

AsyncSessionLocal = async_sessionmaker(
    bind = AsyncEngine,
    class_=AsyncSession,
    expire_on_commit = False,
    autocommit = False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session