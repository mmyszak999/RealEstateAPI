from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_connection import async_session


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session