import os
from datetime import datetime, timedelta, timezone

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from main import app
from model import Base, Email
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from db import get_db

TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """
    Created once for an entire test run. Schema creation
    is expensive and doesn't need to be done on a per-test
    basis
    """
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)

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


@pytest_asyncio.fixture()
async def make_email(db_session):
    async def _make(*, status="pending", send_date=None, sent_at=None, **overrides):
        now = datetime.now(timezone.utc)

        # A sent email's send_date is in the past; a pending one is in the future.
        if send_date is None:
            send_date = now - timedelta(hours=1) if status == "sent" else now + timedelta(days=1)

        # A sent email should have a sent_at, or it would sort strangely.
        if status == "sent" and sent_at is None:
            sent_at = now

        fields = {
            "recipient_email": "future-me@example.com",
            "subject": "test",
            "body_html": "<p>test</p>",
            "send_date": send_date,
            "status": status,
            "sent_at": sent_at,
        }
        fields.update(overrides)

        email = Email(**fields)
        db_session.add(email)
        await db_session.commit()
        await db_session.refresh(email)
        return email

    return _make
