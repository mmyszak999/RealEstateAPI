import asyncio
from asyncio import AbstractEventLoop

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.event import listens_for
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from main import app
from src.database.db_connection import Base
from src.dependencies.get_db import get_db
from src.settings.alembic import *
from src.settings.db_settings import DatabaseSettings


@pytest.fixture(scope="session", autouse=True)
def meta_migration():
    settings = DatabaseSettings(ASYNC=False, TESTING=True)
    sync_engine = create_engine(settings.mysql_url, echo=False)

    Base.metadata.drop_all(sync_engine)
    Base.metadata.create_all(sync_engine)

    yield sync_engine

    Base.metadata.drop_all(sync_engine)


@pytest_asyncio.fixture(scope="session")
async def async_engine() -> AsyncEngine:
    settings = DatabaseSettings(TESTING=True)
    engine = create_async_engine(settings.mysql_url, echo=False, poolclass=NullPool)

    yield engine


@pytest_asyncio.fixture
async def async_session(async_engine: AsyncEngine) -> AsyncSession:
    async with async_engine.connect() as conn:
        await conn.begin()
        await conn.begin_nested()

        async_session = AsyncSession(conn, expire_on_commit=False)

        @listens_for(async_session.sync_session, "after_transaction_end")
        def end_savepoint(session, transaction):
            if conn.closed:
                return
            if not conn.in_nested_transaction():
                conn.sync_connection.begin_nested()

        yield async_session

        await async_session.close()
        await async_session.rollback()


@pytest.fixture()
def async_client(async_session: AsyncSession) -> AsyncClient:
    def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db
    yield AsyncClient(app=app, base_url="http://localhost:8000/api/")
    del app.dependency_overrides[get_db]
