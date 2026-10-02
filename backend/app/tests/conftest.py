import os

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from db import get_db
from main import app
from models import Base

TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """
    Created once for an entire test run. Schema creation
    is expensive and doesn't need to be done on a per-test
    basis
    """
    engine = create_async_engine(TEST_DATABASE_URL)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture()
async def db_session(test_engine):
    """
    Runs once per test
    """
    connection = await test_engine.connect()
    trans = await connection.begin()

    session = AsyncSession(
        bind=connection,
        # Bind the test's session to a connection using
        # join_transaction_mode="create_savepoint". This makes every commit()
        # the app code calls actually commit to a savepoint (a nested
        # checkpoint within the outer transaction) instead of the real
        # transaction — so app code thinks it's committing normally, but
        # the outer transaction (which we roll back at the end of the test)
        # still undoes everything.
        join_transaction_mode="create_savepoint",
        expire_on_commit=False,
    )

    yield session

    await session.close()
    await trans.rollback()
    await connection.close()


@pytest_asyncio.fixture()
async def client(db_session):
    async def override_get_db():
        yield db_session

    # Whenever a route asks for get_db, give it this test's db_session
    # instead of the real one
    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
