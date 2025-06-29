from typing import List

from celery import shared_task, chord
from celery.utils.log import get_task_logger
from sqlmodel import Session, select

from db import get_sync_db_session
from models import Game, League, Patch
from tasks.league.process_league import process_league


logger = get_task_logger(__name__)


@shared_task(name='set_leagues_and_patch_flags_cron')
def set_leagues_and_patch_flags_cron(league_id: int) -> None:
    db_session: Session = get_sync_db_session()

    league_obj = db_session.get(League, league_id)

    league_obj.should_be_processed = True
    db_session.add(league_obj)

    patch_select = db_session.exec(
        select(Patch)
        .join(Game, onclause=Patch.id == Game.patch_id)
        .join(League, onclause=League.id == Game.id)
        .where(League.id == league_id)
    )
    for patch_obj in patch_select.all():
        patch_obj.should_be_processed = True
        db_session.add(patch_obj)

    db_session.commit()
    db_session.close()


@shared_task(name='find_leagues_to_process_cron')
def find_leagues_to_process_cron() -> None:
    db_session: Session = get_sync_db_session()
    logger.info(f'Processing leagues: start')

    sel_res = db_session.exec(
        select(League).where(League.since_last_new_game != None)
    )
    league_objs: List[League] = sel_res.all()

    for league_obj in league_objs:
        found_games, processing_group = process_league(league_obj=league_obj, execute=False)

        if found_games:
            league_obj.since_last_new_game = 0
            chord(
                processing_group | set_leagues_and_patch_flags_cron.si(league_id=league_obj.id),
            ).on_error(set_leagues_and_patch_flags_cron.si(league_id=league_obj.id))

        elif league_obj.since_last_new_game > 7:
            league_obj.since_last_new_game = None

        else:
            league_obj.since_last_new_game += 1

        db_session.add(league_obj)

    db_session.commit()
    db_session.close()
    logger.info(f'Processing leagues: end')
