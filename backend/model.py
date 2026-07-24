from datetime import datetime

from sqlalchemy import CheckConstraint, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Email(Base):
    __tablename__ = "emails"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'sent', 'failed')", name="status_check"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    recipient_email: Mapped[str] = mapped_column(Text, nullable=False)
    subject: Mapped[str] = mapped_column(Text, nullable=False)
    body_html: Mapped[str] = mapped_column(Text, nullable=False)
    send_date: Mapped[datetime] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False,
                                        default="pending")
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )  # Matches database behavior by filling in now at insert time
    sent_at: Mapped[datetime | None] = mapped_column(default=None)
    send_attempts: Mapped[int] = mapped_column(nullable=False, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, default=None)
