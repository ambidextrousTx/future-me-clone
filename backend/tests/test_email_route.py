from datetime import datetime, timedelta, timezone


async def test_happy_path_returns_201(client):
    send_date = datetime.now(timezone.utc) + timedelta(minutes=1)
    response = await client.post('/emails', json={
        'recipient_email': 'future-me@example.com',
        'subject': 'test',
        'body_html': '<p>test</p>',
        'send_date': send_date.isoformat()
        })

    assert response.status_code == 201

    body = response.json()
    assert isinstance(body['id'], int)
    assert body['recipient_email'] == 'future-me@example.com'
    assert body['subject'] == 'test'
    assert body['status'] == 'pending'
    assert body['send_attempts'] == 0
    assert body['created_at'] is not None
    assert body['sent_at'] is None
