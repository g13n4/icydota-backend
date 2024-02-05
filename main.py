from celery.result import AsyncResult
from celery.schedules import crontab
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from celery_app import celery_app
from tasks import process_leagues_cron, update_leagues_dates_cron, process_league, process_game_helper


load_dotenv()

app = FastAPI()


@celery_app.on_after_configure.connect
def process_new_games_in_leagues(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute='0', hour='*/6'),
        process_leagues_cron.s(),
    )


@celery_app.on_after_configure.connect
def update_leagues_dates(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute='0', hour='12', day_of_week='1,4'),
        update_leagues_dates_cron.s(),
    )


class TaskOut(BaseModel):
    id: str
    name: str
    result: str | None = None
    status: str


def _to_task_out(r: AsyncResult, name: str) -> TaskOut:
    return TaskOut(id=r.task_id,
                   status=r.status,
                   name=name,
                   result=r.traceback if r.failed() else r.result, )


# @celery_app.task
# def send_push_notification(device_token: str):
#     time.sleep(10)  # simulates slow network call to firebase/sns
#     with open("notification.log", mode="a") as notification_log:
#         response = f"Successfully sent push notification to: {device_token}\n"
#         notification_log.write(response)
#
#
# @app.get('/test_celery')
# async def test_push(device_token: str) -> TaskOut:
#     r = send_push_notification.delay(device_token=device_token)
#     return TaskOut(id=r.task_id, name='test_push', status=r.status)
#
#
# @app.get("/push/{device_token}")
# async def notify(device_token: str):
#     send_push_notification.delay(device_token)
#     return {"message": "Notification sent"}
#
#
@app.get("/ping")
async def pong():
    return {"ping": "pong!"}


#
#
# @app.get("/leagues", response_model=list[League])
# async def get_leagues(session: AsyncSession = Depends(get_db_session)):
#     result = await session.execute(select(League))
#     leagues = result.scalars().all()
#     return [League(name=league.name) for league in leagues]


@app.get('/process/league/{league_id}', status_code=202)
async def process_league_api(league_id: int):
    process_league(league_id=league_id, )
    return {'status': 'processing'}


@app.get('/process/match/{match_id}', status_code=202)
async def process_match_api(match_id: int):
    process_game_helper(match_id=match_id, )
    return {'status': 'processing'}
