import datetime

from celery import shared_task
from celery.utils.log import get_task_logger
from sqlmodel import Session, select

from db import get_sync_db_session
from models import League, Game
from tasks.cron.set_flags_for_league_and_patch import set_leagues_and_patch_flags_cron
from tasks.league.process_league import process_game_helper


logger = get_task_logger(__name__)


@shared_task(name='attempt_to_process_bad_games_(cron)', ignore_result=True)
def attempt_to_process_bad_games_cron() -> None:
    db_session: Session = get_sync_db_session(expire=True)
    logger.info(f'Processing leagues: start')

    found_in_last_8_days = datetime.datetime.now() - datetime.timedelta(days=8)

    league_select = db_session.exec(
        select(League.id, Game.id)
        .join(Game, onclause=League.id == Game.league_id)
        .where(League.new_game_found_at > found_in_last_8_days, )
    )

    for league_id, game_id in league_select.all():
        task = process_game_helper(
            match_id=game_id,
            league_id=league_id,
            execute=False,
        )

        chain_task = task | set_leagues_and_patch_flags_cron.si(league_id=league_id)
        chain_task.apply_async()

    db_session.close()
