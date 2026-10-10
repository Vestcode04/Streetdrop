import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL не найден")

engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(
    engine,
    expire_on_commit=False
)


async def get_db():
    async with async_session() as session:
        yield session


class Base(DeclarativeBase):
    pass