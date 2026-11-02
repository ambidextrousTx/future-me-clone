from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.emails import router as emails_router
from scheduler import scheduler
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db

ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000"
        ]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Everything before yield runs on startup
    scheduler.start()
    yield
    # Everything after yield runs on shutdown
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(emails_router)


@app.get('/health')
async def health():
    return {'message': 'OK'}


@app.get('/health/db')
async def health_db(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1"))
    result.scalar_one()
    return {'message': 'DB connection OK'}
