from datetime import datetime, timedelta, timezone

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
    assert body['recipient_email'] == 'future-me@example.com'
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
