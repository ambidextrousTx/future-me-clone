from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class Settings(BaseSettings):
    DATABASE_URL: str  # automatically pulls this environment variable


settings = Settings()

engine = create_async_engine(settings.DATABASE_URL, echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        yield session
