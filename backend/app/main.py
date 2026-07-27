from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db

app = FastAPI()


@app.get('/health')
async def health():
    return {'message': 'OK'}


@app.get('/health/db')
async def health_db(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1"))
    result.scalar_one()
    return {'message': 'DB connection OK'}
