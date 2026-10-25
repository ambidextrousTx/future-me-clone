from datetime import datetime, timedelta, timezone

from model import Email
from sqlalchemy import select

VALID_PAYLOAD = {
    "recipient_email": "future-me@example.com",
    "subject": "Hello from the past",
    "body_html": "<p>Hi future me.</p>",
}


async def test_happy_path_returns_201(client):
    send_date = datetime.now(timezone.utc) + timedelta(minutes=1)
    response = await client.post('/emails', json={
        **VALID_PAYLOAD,
        'send_date': send_date.isoformat()
        })

    assert response.status_code == 201

    body = response.json()
    assert isinstance(body['id'], int)
    assert body["recipient_email"] == VALID_PAYLOAD["recipient_email"]
    assert body['subject'] == VALID_PAYLOAD["subject"]
    assert body['status'] == 'pending'
    assert body['send_attempts'] == 0
    assert body['created_at'] is not None
    assert body['sent_at'] is None


async def test_past_send_date_returns_422(client):
    send_date = datetime.now(timezone.utc) - timedelta(minutes=1)

    response = await client.post('/emails', json={
        **VALID_PAYLOAD,
        'send_date': send_date.isoformat()
        })

    assert response.status_code == 422
    detail = response.json()["detail"][0]
    assert detail["loc"] == ["body", "send_date"]
    assert "must be in the future" in detail["msg"]


async def test_naive_send_date_returns_422(client):
    send_date = datetime.now() + timedelta(days=1)

    response = await client.post('/emails', json={
        **VALID_PAYLOAD,
        'send_date': send_date.isoformat()
        })

    assert response.status_code == 422
    detail = response.json()["detail"][0]
    assert detail["loc"] == ["body", "send_date"]
    assert "timezone" in detail["msg"]


async def test_invalid_email_returns_422(client):
    send_date = datetime.now(timezone.utc) - timedelta(minutes=1)

    response = await client.post('/emails', json={
        **VALID_PAYLOAD,
        'recipient_email': 'not-an-email',
        'send_date': send_date.isoformat()
        })

    assert response.status_code == 422
    detail = response.json()["detail"][0]
    assert detail["loc"] == ["body", "recipient_email"]


async def test_created_email_is_persisted(client, db_session):
    send_date = datetime.now(timezone.utc) + timedelta(days=1)

    response = await client.post("/emails", json={
        **VALID_PAYLOAD,
        "send_date": send_date.isoformat(),
    })
    assert response.status_code == 201
    email_id = response.json()["id"]

    result = await db_session.execute(
        select(Email)
        .where(Email.id == email_id)
        .execution_options(populate_existing=True)
    )
    row = result.scalar_one()

    assert row.recipient_email == VALID_PAYLOAD["recipient_email"]
    assert row.subject == VALID_PAYLOAD["subject"]
    assert row.body_html == VALID_PAYLOAD["body_html"]
    assert row.send_date == send_date
    assert row.status == "pending"
    assert row.send_attempts == 0
    assert row.sent_at is None


async def test_client_supplied_status_still_creates_pending(client, db_session):
    send_date = datetime.now(timezone.utc) + timedelta(days=1)

    response = await client.post("/emails", json={
        **VALID_PAYLOAD,
        "send_date": send_date.isoformat(),
        "status": "sent"
    })
    assert response.status_code == 201
    assert response.json()["status"] == "pending"

    email_id = response.json()["id"]
    result = await db_session.execute(
        select(Email)
        .where(Email.id == email_id)
        .execution_options(populate_existing=True)
    )
    row = result.scalar_one()

    assert row.status == "pending"
    assert row.sent_at is None
    assert row.send_attempts == 0


async def test_empty_list_is_returned_for_no_emails(db_session):
    pass


async def test_only_sent_emails_are_returned(db_session):
    pass


async def test_sent_emails_are_ordered_descending(db_session):
    pass


async def test_ui_required_fields_are_returned(db_session):
    pass
