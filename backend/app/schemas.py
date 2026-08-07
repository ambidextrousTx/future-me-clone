from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class EmailCreate(BaseModel):
    """
    The email creation request payload
    """
    recipient_email: EmailStr
    subject: str
    body_html: str
    send_date: datetime

    @field_validator("send_date")
    @classmethod
    def send_date_must_be_future(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("send_date must include timezone information")
        if value <= datetime.now(timezone.utc):
            raise ValueError("send_date must be in the future")
        return value


class EmailOut(BaseModel):
    """
    A representation of the rows to be inserted into the database
    """
    # Makes object usable with Sqlalchemy, instead of requiring a dict
    model_config = ConfigDict(from_attributes=True)

    id: int
    recipient_email: str
    subject: str
    body_html: str
    send_date: datetime
    status: str
    created_at: datetime
    sent_at: datetime | None
    send_attempts: int
    last_error: str | None
