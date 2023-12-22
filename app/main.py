import time

from celery import Celery
from fastapi import Depends, FastAPI
from httpx import AsyncClient
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from db import get_db_session, get_web_client
from models import League
from .base_data import create_heroes

app = FastAPI()

celery = Celery(
    'dota2lane',
    broker='redis://127.0.0.1:6379/0',
    backend='redis://127.0.0.1:6379/0',
    broker_connection_retry_on_startup=True,
)


class TaskOut(BaseModel):
    id: str
    name: str
    status: str


@app.on_event("startup")
async def on_startup(db_session: AsyncSession = Depends(get_db_session),
                     web_client: AsyncClient = Depends(get_web_client)):
    await create_heroes(db_session, web_client)


@app.on_event("shutdown")
async def shutdown(db_session: AsyncSession = Depends(get_db_session),
                   web_client: AsyncClient = Depends(get_web_client)):
    await db_session.close_all()
    await web_client.aclose()


@celery.task
def send_push_notification(device_token: str):
    time.sleep(10)  # simulates slow network call to firebase/sns
    with open("notification.log", mode="a") as notification_log:
        response = f"Successfully sent push notification to: {device_token}\n"
        notification_log.write(response)


@app.get('/test_celery')
async def test_push(device_token: str) -> TaskOut:
    r = send_push_notification.delay(device_token=device_token)
    return TaskOut(id=r.task_id, name='test_push', status=r.status)


@app.get("/push/{device_token}")
async def notify(device_token: str):
    send_push_notification.delay(device_token)
    return {"message": "Notification sent"}


@app.get("/ping")
async def pong():
    return {"ping": "pong!"}


@app.get("/leagues", response_model=list[League])
async def get_leagues(session: AsyncSession = Depends(get_db_session)):
    result = await session.execute(select(League))
    leagues = result.scalars().all()
    return [League(name=league.name) for league in leagues]


@app.get("/")
def read_root():
    return {"Hello": "World"}
