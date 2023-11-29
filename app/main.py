from fastapi import Depends, FastAPI
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from celery import shared_task, Celery
from pydantic import BaseModel
import time

from db import get_session
from models import League

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
async def get_leagues(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(League))
    leagues = result.scalars().all()
    return [League(name=league.name) for league in leagues]


@app.get("/")
def read_root():
    return {"Hello": "World"}
