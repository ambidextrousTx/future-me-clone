from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

from model import Email
from scheduler import promote_due_emails
from sqlalchemy import select


def _session_factory(session):
    """Adapts an already-open test session into the factory shape
    promote_due_emails expects, without closing it (the db_session
    fixture owns that session's lifecycle)."""

    @asynccontextmanager
    async def factory():
        yield session

    return factory


async def _make_email(db_session, *, status, send_date, **overrides):
    email = Email(
        recipient_email="future-me@example.com",
        subject="test",
        body_html="<p>test</p>",
        send_date=send_date,
        status=status,
        **overrides,
    )
    db_session.add(email)
    await db_session.commit()
    await db_session.refresh(email)
    return email


async def test_promotes_due_pending_email(db_session):
    due = await _make_email(
        db_session,
        status="pending",
        send_date=datetime.now(timezone.utc) - timedelta(minutes=1),
    )

    sent_ids = await promote_due_emails(_session_factory(db_session))

    assert sent_ids == [due.id]

    await db_session.refresh(due)
    assert due.status == "sent"
    assert due.sent_at is not None
    assert due.send_attempts == 1


async def test_does_not_promote_future_pending_email(db_session):
    future = await _make_email(
        db_session,
        status="pending",
        send_date=datetime.now(timezone.utc) + timedelta(days=1),
    )

    sent_ids = await promote_due_emails(_session_factory(db_session))

    assert sent_ids == []

    await db_session.refresh(future)
    assert future.status == "pending"
    assert future.sent_at is None


async def test_does_not_re_promote_already_sent_email(db_session):
    already_sent = await _make_email(
        db_session,
        status="sent",
        send_date=datetime.now(timezone.utc) - timedelta(days=1),
        sent_at=datetime.now(timezone.utc) - timedelta(hours=1),
        send_attempts=1,
    )

    sent_ids = await promote_due_emails(_session_factory(db_session))

    assert sent_ids == []

    await db_session.refresh(already_sent)
    assert already_sent.send_attempts == 1  # unchanged, not incremented again


async def test_promotes_only_due_rows_among_a_mix(db_session):
    due = await _make_email(
        db_session,
        status="pending",
        send_date=datetime.now(timezone.utc) - timedelta(minutes=5),
    )
    future = await _make_email(
        db_session,
        status="pending",
        send_date=datetime.now(timezone.utc) + timedelta(days=1),
    )
    already_sent = await _make_email(
        db_session,
        status="sent",
        send_date=datetime.now(timezone.utc) - timedelta(days=1),
    )

    sent_ids = await promote_due_emails(_session_factory(db_session))

    assert sent_ids == [due.id]

    result = await db_session.execute(
            select(Email)
            .order_by(Email.id)
            .execution_options(populate_existing=True)
            )
    emails_by_id = {e.id: e for e in result.scalars()}

    assert emails_by_id[due.id].status == "sent"
    assert emails_by_id[future.id].status == "pending"
    assert emails_by_id[already_sent.id].status == "sent"  # already was
