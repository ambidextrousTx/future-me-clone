from fastapi import APIRouter, Depends
from model import Email
from schemas import EmailCreate, EmailOut
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db

router = APIRouter()


@router.post("/emails", response_model=EmailOut, status_code=201)
async def create_email(email_in: EmailCreate, db: AsyncSession = Depends(get_db)):
    email = Email(**email_in.model_dump())
    db.add(email)
    await db.commit()
    await db.refresh(email)
    return email


@router.get("/emails", response_model=list[EmailOut])
async def get_emails(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Email)
        .where(Email.status == "sent")
        .order_by(Email.sent_at.desc(), Email.id.desc())
    )
    return result.scalars().all()
