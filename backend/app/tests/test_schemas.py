from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from schemas import EmailCreate

VALID_PAYLOAD = {
    "recipient_email": "future-me@example.com",
    "subject": "Hello from the past",
    "body_html": "<p>Hi future me.</p>",
}


def _future(**kwargs) -> datetime:
    return datetime.now(timezone.utc) + timedelta(**kwargs)


def _past(**kwargs) -> datetime:
    return datetime.now(timezone.utc) - timedelta(**kwargs)


def test_valid_payload_constructs_successfully():
    email = EmailCreate(**VALID_PAYLOAD, send_date=_future(days=1))
    assert email.recipient_email == "future-me@example.com"
    assert email.send_date > datetime.now(timezone.utc)


def test_naive_send_date_is_rejected():
    naive_date = datetime.now() + timedelta(days=1)  # no tzinfo

    with pytest.raises(ValidationError) as exc_info:
        EmailCreate(**VALID_PAYLOAD, send_date=naive_date)

    assert "timezone information" in str(exc_info.value)


def test_past_send_date_is_rejected():
    with pytest.raises(ValidationError) as exc_info:
        EmailCreate(**VALID_PAYLOAD, send_date=_past(days=1))

    assert "must be in the future" in str(exc_info.value)


def test_invalid_email_format_is_rejected():
    payload = {**VALID_PAYLOAD, "recipient_email": "not-an-email"}

    with pytest.raises(ValidationError):
        EmailCreate(**payload, send_date=_future(days=1))


def test_missing_required_field_is_rejected():
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "subject"}

    with pytest.raises(ValidationError):
        EmailCreate(**payload, send_date=_future(days=1))


def test_client_supplied_status_is_silently_ignored():
    """
    Documents current behavior: EmailCreate has no extra="forbid" config,
    so unrecognized fields like "status" are dropped rather than rejected.
    This is safe (never reaches the DB) but worth a deliberate decision -
    see conversation notes on whether this should be stricter.
    """
    email = EmailCreate(
        **VALID_PAYLOAD, send_date=_future(days=1), status="sent"
    )
    assert not hasattr(email, "status")
