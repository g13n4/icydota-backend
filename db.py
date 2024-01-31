import os

import httpx
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine, Session
from sqlmodel.ext.asyncio.session import AsyncSession, AsyncEngine


load_dotenv()

POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_ADDRESS = os.getenv('POSTGRES_ADDRESS')

DB_URI = f"{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_ADDRESS}/{POSTGRES_DB}"
# ASYNC SESSION
ASYNC_DATABASE_URI = "postgresql+asyncpg://" + DB_URI

async_engine = AsyncEngine(create_engine(ASYNC_DATABASE_URI,
                                         echo=True,
                                         future=True))


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


async def get_web_client():
    async with httpx.AsyncClient() as client:
        yield client
