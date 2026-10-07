from fastapi import APIRouter, Depends
from model import Email
from schemas import EmailCreate, EmailOut
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
