import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import text

from db import async_session

logger = logging.getLogger(__name__)

DUE_EMAILS_QUERY = text(
    """
    UPDATE emails
    SET status = 'sent',
        sent_at = now(),
        send_attempts = send_attempts + 1
    WHERE status = 'pending'
      AND send_date <= now()
    RETURNING id
    """
)


async def promote_due_emails() -> None:
    async with async_session() as session:
        result = await session.execute(DUE_EMAILS_QUERY)
        sent_ids = [row.id for row in result]
        await session.commit()

    if sent_ids:
        logger.info("Promoted %d email(s) to sent: %s", len(sent_ids), sent_ids)


scheduler = AsyncIOScheduler()
scheduler.add_job(promote_due_emails, "interval", seconds=30, id="promote_due_emails")
