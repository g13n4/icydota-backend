import datetime
from typing import List

from celery import shared_task
from celery.utils.log import get_task_logger
from sqlmodel import Session, select

from db import get_sync_db_session
from models import League
from tasks.league.create_league import update_league_obj_dates


logger = get_task_logger(__name__)


@shared_task(name='update_leagues_date_(cron)', ignore_result=True)
def update_leagues_dates_cron() -> None:
    db_session: Session = get_sync_db_session(expire=True)
    logger.info(f'Updating leagues dates: start')

    found_in_last_8_days = datetime.datetime.now() - datetime.timedelta(days=8)

    sel_res = db_session.exec(select(League).where(League.new_game_found_at > found_in_last_8_days))
    league_objs: List[League] = sel_res.all()

    for league_obj in league_objs:
        updated = update_league_obj_dates(league_obj)
        if updated:
            logger.info(f'Updating dates of league {league_obj.id}')
            db_session.add(league_obj)

    db_session.full_commit()
    logger.info(f'Updating leagues dates: complete')
