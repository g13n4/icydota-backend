from typing import Dict, List

import requests
from celery.utils.log import get_task_logger
from sqlmodel import select, Session

from celery_app import celery_app
from db import get_sync_db_session
from models import Game
from models import League
from tasks import process_game
from tasks.create_league import update_league_obj_dates, create_league


logger = get_task_logger(__name__)


def _get_league(league_id: int, db_session: Session, league_obj: League = None, ) -> League:
    if league_obj is None:
        league_q = db_session.execute(select(League).where(League.league_id == league_id)).first()
        if not league_q:
            league_obj = create_league(league_id)
            db_session.add(league_obj)
            db_session.commit()
            db_session.refresh(league_obj)
        else:
            league_obj: League = league_q[0]
    return league_obj


@celery_app.task(name='process match')
def process_match(match_id: int = None, league_id: int | None = None, ):
    db_session: Session = get_sync_db_session()
    logger.info(f'Processing match {match_id}...')
    league_obj = _get_league(league_id, db_session)

    process_game.delay(match_id=match_id, league_id=league_obj.id, )


@celery_app.task(name='process league')
def process_league(league_obj: League | None = None,
                   league_id: int | None = None):
    db_session: Session = get_sync_db_session()
    logger.info(f'Processing league {league_id}...')

    league_obj = _get_league(league_id, db_session, league_obj)

    r = requests.get(f'https://api.opendota.com/api/leagues/{league_obj.league_id}/matches')
    league_match_data = r.json()

    db_league_games: Dict[int, Game] = {x.match_id: x for x in league_obj.games}
    new_games_found = 0
    for game in league_match_data:
        if game['match_id'] in db_league_games:
            continue
        else:
            process_game.delay(match_id=game['match_id'],
                               league_id=league_obj.id, )

            new_games_found += 1

    if new_games_found:
        logger.info(f'Found {new_games_found} new games in league {league_id}')

    if new_games_found:
        pass
        # process_aggregation.delay(
        #     db_session=db_session,
        #     league_id=league_obj.id, )


@celery_app.task(name='process league games (cron)')
def process_leagues_cron() -> None:
    db_session: Session = get_sync_db_session()
    logger.info(f'Processing leagues: start')

    sel_res = db_session.execute(select(League).where(League.has_started == True and
                                                      League.fully_parsed == False))
    league_objs: List[League] = sel_res.scalars().all()

    for league_obj in league_objs:
        process_league.delay(db_session=db_session,
                             league_obj=league_obj)

        update_league_obj_dates(league_obj)

        if league_obj.has_ended:
            league_obj.fully_parsed = True

        db_session.add(league_obj)

    db_session.commit()
    db_session.close()
    logger.info(f'Processing leagues: end')


@celery_app.task(name='update leagues date (cron)')
def update_leagues_dates_cron() -> None:
    db_session: Session = get_sync_db_session()
    logger.info(f'Updating leagues dates: start')

    sel_res = db_session.execute(select(League).where(League.has_dates == False))
    league_objs: List[League] = sel_res.scalars().all()

    for league_obj in league_objs:
        updated = update_league_obj_dates(league_obj)
        if updated:
            logger.info(f'Updating dates of league {league_obj.league_id}')
            db_session.add(league_obj)

    db_session.commit()
    db_session.close()
    logger.info(f'Updating leagues dates: complete')
