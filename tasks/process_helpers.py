from typing import Dict, List, Optional

import requests
from celery import shared_task, chain
from celery.utils.log import get_task_logger
from sqlmodel import Session, select

from db import get_sync_db_session
from models import Game, League
from tasks.create_league import get_or_create_league, update_league_obj_dates
from tasks.process_game import process_game_data
from tasks.download_replay import get_match_replay
from tasks_agg.approximate_positions import approximate_positions
from utils import bool_pool


logger = get_task_logger(__name__)


def process_game_helper(match_id: int, league_id: int | None = None, get_chain: bool = False) -> Optional[chain]:
    first_parser = next(bool_pool)

    match_chain = (get_match_replay.si(match_id=match_id, first_parser=first_parser) |
                   process_game_data.si(match_id=match_id, league_id=league_id))
    if get_chain:
        return match_chain

    match_chain.apply_async()


def process_league(league_obj: League | None = None,
                   league_id: int | None = None,
                   overwrite: bool = False):
    db_session: Session = get_sync_db_session()

    league_obj = get_or_create_league(league_id, db_session, league_obj)

    r = requests.get(f'https://api.opendota.com/api/leagues/{league_obj.id}/matches')
    league_match_data = r.json()

    db_league_games: Dict[int, Game] = {x.id: x for x in league_obj.games}
    new_games_found = 0
    for idx, game in enumerate(league_match_data):
        if game['match_id'] in db_league_games and not overwrite:
            continue
        else:
            process_game_helper(match_id=game['match_id'],
                                league_id=league_obj.id, )

            new_games_found += 1

    approximate_positions.s(league_id=league_id)
    return new_games_found



@shared_task(name='process_league_games_(cron)')
def process_leagues_cron() -> None:
    db_session: Session = get_sync_db_session()
    logger.info(f'Processing leagues: start')

    sel_res = db_session.exec(select(League).where(League.has_started == True and
                                                   League.fully_parsed == False))
    league_objs: List[League] = sel_res.all()

    for league_obj in league_objs:
        process_league(league_obj=league_obj)

        update_league_obj_dates(league_obj)

        if league_obj.has_ended:
            league_obj.fully_parsed = True

        db_session.add(league_obj)

    db_session.commit()
    db_session.close()
    logger.info(f'Processing leagues: end')


@shared_task(name='update_leagues_date_(cron)')
def update_leagues_dates_cron() -> None:
    db_session: Session = get_sync_db_session()
    logger.info(f'Updating leagues dates: start')

    sel_res = db_session.exec(select(League).where(League.has_dates == False))
    league_objs: List[League] = sel_res.all()

    for league_obj in league_objs:
        updated = update_league_obj_dates(league_obj)
        if updated:
            logger.info(f'Updating dates of league {league_obj.id}')
            db_session.add(league_obj)

    db_session.commit()
    db_session.close()
    logger.info(f'Updating leagues dates: complete')

