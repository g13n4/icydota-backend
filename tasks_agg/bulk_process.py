from typing import List

import requests
from celery import shared_task, chain, group
from celery.utils.log import get_task_logger
from sqlmodel import Session, select

from db import get_sync_db_session
from models import League
from tasks.create_league import get_or_create_league
from tasks.process_game import process_game_helper
from .agg_helper import aggregate_league_helper, cross_compare_league_helper
from .approximate_positions import approximate_positions
from .process_aggregation import process_aggregation
from .process_aggregation_cross_comparison import create_cross_comparison_aggregation


logger = get_task_logger(__name__)


# PROCESS FULL CYCLE
def post_process_league_id(league_id: int,
                           approx: bool = True,
                           aggregate: bool = True,
                           cross_compare: bool = True) -> None:
    if approx:
        approximate_positions(league_id=league_id)
    if aggregate:
        aggregate_league_helper(league_id=league_id)
    if cross_compare:
        cross_compare_league_helper(league_id=league_id)


@shared_task(name="process_full_cycle_second_error", ignore_result=True)
def process_on_second_error(league_id: int) -> None:
    (process_aggregation.si(league_id=league_id) |
     create_cross_comparison_aggregation.si(league_id=league_id)
     ).apply_async()

@shared_task(name="process_full_cycle_first_error", ignore_result=True)
def process_on_first_error(league_id: int, games: list) -> None:

    (approximate_positions.si(league_id=league_id, ) |  # executing chord despite errors
     group(games) |
     (process_aggregation.si(league_id=league_id)
      .set(link_error=[process_on_second_error.si(league_id=league_id)])) |
     create_cross_comparison_aggregation.si(league_id=league_id)
     ).apply_async()


def process_full_cycle(league_obj: League | None = None, league_id: int | None = None):
    db_session: Session = get_sync_db_session()

    league_obj = get_or_create_league(league_id, db_session, league_obj)

    r = requests.get(f'https://api.opendota.com/api/leagues/{league_obj.id}/matches')
    league_match_data = r.json()

    games = []
    for idx, game in enumerate(league_match_data):
        match_chain: chain = process_game_helper(match_id=game['match_id'], league_id=league_obj.id, get_chain=True)
        games.append(match_chain)

    (group(games) |
     (approximate_positions.si(league_id=league_obj.id, )
      # executing chord despite errors
      .set(link_error=[process_on_first_error.si(league_id=league_obj.id, games=games)])) |
     group(games) |
     (process_aggregation.si(league_id=league_obj.id)
      .set(link_error=[process_on_second_error.si(league_id=league_obj.id)])) |
     create_cross_comparison_aggregation.si(league_id=league_obj.id)
     ).apply_async()

    logger.info(f"PARSING FOR LEAGUE {league_obj.id} IS DONE")

    return


# MASS PROCESS
def mass_process(process_type: str, league_ids: List[int]) -> None:
    db_session: Session = get_sync_db_session()

    if process_type == 'process_league':
        all_leagues = []
        filtered_leagues = []
        league_games_dict = dict()
        for league_id in league_ids:
            r = requests.get(f'https://api.opendota.com/api/leagues/{league_id}/matches')
            league_match_data = r.json()
            if not league_match_data:
                logger.warning(f'There is not league {league_id} in opendota database')
                continue

            games = []
            for idx, game in enumerate(league_match_data):
                match_chain: chain = process_game_helper(match_id=game[
                    'match_id'], league_id=league_id, get_chain=True)
                games.append(match_chain)

            all_leagues.extend(games)
            league_games_dict[league_id] = group(games)
            filtered_leagues.append(league_id)


        approximation_list = [(approximate_positions.si(league_id=x, ) | league_games_dict[x])
                              for x in filtered_leagues]
        (
            group(all_leagues) |
            group(approximation_list).set(link_error=approximation_list)
        ).apply_async()

    else:
        celery_task = (create_cross_comparison_aggregation if process_type == 'cross_compare_league'
                       else process_aggregation)

        sel_result = db_session.exec(select(League))
        league_objs: List[League] = sel_result.all()
        league_list = [x.id for x in league_objs]

        filtered_tasks = []
        for league_id in league_ids:
            if league_id in league_list:
                filtered_tasks.append(
                    celery_task.si(league_id=league_id))
            else:
                logger.warning('League {} doesn\'t exist in the database')

        group(celery_task).apply_async()
