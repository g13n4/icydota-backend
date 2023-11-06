from fastapi import Depends, FastAPI
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models import League

app = FastAPI()


@app.get("/ping")
async def pong():
    return {"ping": "pong!"}


@app.get("/leagues", response_model=list[League])
async def get_leagues(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(League))
    leagues = result.scalars().all()
    return [League(name=league.name) for league in leagues]


@app.get("/")
def read_root():
    return {"Hello": "World"}

