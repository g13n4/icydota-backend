import os

from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine, Session
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()

POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_ADDRESS = os.getenv('POSTGRES_ADDRESS')
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "100"))
WEB_CONCURRENCY = int(os.getenv("WEB_CONCURRENCY", "2"))
POOL_SIZE = max(DB_POOL_SIZE // WEB_CONCURRENCY, 20)

DB_URI = f"{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_ADDRESS}/{POSTGRES_DB}"
# ASYNC SESSION
ASYNC_DATABASE_URI = "postgresql+asyncpg://" + DB_URI

async_engine = create_async_engine(ASYNC_DATABASE_URI,
                                   pool_size=POOL_SIZE,
                                   max_overflow=POOL_SIZE,
                                   pool_use_lifo=True,
                                   pool_pre_ping=True,
                                   echo=False,
                                   future=True)


async def get_async_db_session() -> AsyncSession:
    async_session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


# SYNC SESSION
SYNC_DATABASE_URI = "postgresql://" + DB_URI

sync_engine = create_engine(SYNC_DATABASE_URI, echo=False, future=True)


def get_sync_db_session() -> Session:
    sync_session = sessionmaker(
        sync_engine, class_=Session, expire_on_commit=False
    )
    with sync_session() as session:
        return session

