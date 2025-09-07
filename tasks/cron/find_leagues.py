import datetime

from celery import shared_task
from celery.utils.log import get_task_logger
from sqlmodel import Session, select

from constants.task_reason import TaskReason
from db import get_sync_db_session
from models import League
from tasks.cron.set_flags_for_league_and_patch import set_leagues_and_patch_flags_cron
from tasks.league.process_league import process_league_task_group


logger = get_task_logger(__name__)


@shared_task(name='find_leagues_to_process_(cron)', ignore_result=True)
def find_leagues_to_process_cron() -> None:
    db_session: Session = get_sync_db_session(expire=False)
    logger.info(f'Processing leagues: start')

    found_in_last_8_days = datetime.datetime.now() - datetime.timedelta(days=8)

    sel_res = db_session.exec(select(League).where(League.new_game_found_at > found_in_last_8_days))

    for league_obj in sel_res.all():
        found_games, processing_group = process_league_task_group(
            league_obj=league_obj,
            league_id=league_obj.id,
            overwrite=False,
            execute=False,
            reason=TaskReason.PROCESS_LEAGUE_CRON,
        )
        league_text = f"League {league_obj.name} - ({league_obj.id}):"
        if found_games:
            logger.info(f'{league_text} {found_games} games found')
            league_obj.new_game_found_at = datetime.datetime.now()
            task = (
                    processing_group | set_leagues_and_patch_flags_cron.si(league_id=league_obj.id)
            ).on_error(set_leagues_and_patch_flags_cron.si(league_id=league_obj.id))

            task.apply_async()

        else:
            logger.info(f'{league_text} no games found. Last time game was found was {league_obj.new_game_found_at}')

        db_session.add(league_obj)

    db_session.commit()
    db_session.close()
    logger.info(f'Processing leagues: end')
