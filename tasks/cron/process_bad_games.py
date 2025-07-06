from typing import List

from celery import shared_task, group
from celery.utils.log import get_task_logger
from sqlmodel import Session, select

from db import get_sync_db_session
from models import League
from tasks.cron.set_flags_for_league_and_patch import set_leagues_and_patch_flags_cron
from tasks.league.process_league import process_league


logger = get_task_logger(__name__)


@shared_task(name='attempt_to_process_bad_games_(cron)', ignore_result=True)
def find_leagues_to_process_cron() -> None:
    db_session: Session = get_sync_db_session(expire=True)
    logger.info(f'Processing leagues: start')

    sel_res = db_session.exec(
        select(League).where(League.since_last_new_game != None)
    )
    league_objs: List[League] = sel_res.all()

    for league_obj in league_objs:
        found_games, processing_group = process_league(
            league_obj=league_obj,
            execute=False,
        )

        for game_task in found_games:
            chain_task = game_task | set_leagues_and_patch_flags_cron.si(league_id=league_obj.id)

            chain_task.apply_async()

    db_session.close()
