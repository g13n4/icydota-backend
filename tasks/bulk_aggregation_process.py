from collections.abc import Iterable
from typing import List

import requests
from celery import chain, group
from celery.utils.log import get_task_logger
from sqlmodel import Session, select

from db import get_sync_db_session
from models import League
from tasks.aggregation.delete import delete_aggregation_match, delete_aggregation_team
from tasks.aggregation.player import aggregate_league_player_task
from tasks.aggregation.team import aggregate_league_team_task
from tasks.aggregation_tasks_helper import aggregate_league_task_helper, cross_compare_league_task_helper
from tasks.approximate_positions import approximate_positions
from tasks.cross_comparison.delete import delete_cross_comparison_match, delete_cross_comparison_team
from tasks.cross_comparison.match import  cross_compare_player_task
from tasks.cross_comparison.team import cross_compare_team_task
from tasks.league.create_league import get_or_create_league
from tasks.league.process_league import process_game_helper


logger = get_task_logger(__name__)


# PROCESS FULL CYCLE
def post_process_league_id(
        league_id: int,
        approx: bool = True,
        aggregate: bool = True,
        cross_compare: bool = True
) -> None:
    if approx:
        approximate_positions(league_id=league_id)
    if aggregate:
        aggregate_league_task_helper(league_id=league_id)
    if cross_compare:
        cross_compare_league_task_helper(league_id=league_id)


def process_full_cycle(league_obj: League | None = None, league_id: int | None = None):
    db_session: Session = get_sync_db_session()

    league_obj = get_or_create_league(league_id, db_session, league_obj)

    r = requests.get(f'https://api.opendota.com/api/leagues/{league_obj.id}/matches')
    league_match_data = r.json()

    games = []
    for idx, game in enumerate(league_match_data):
        match_chain: chain = process_game_helper(match_id=game['match_id'], league_id=league_obj.id, execute=False)
        games.append(match_chain)

    (
        # process games
            group(games) |
            approximate_positions.si(league_id=league_obj.id) |
            # aggregate
            delete_aggregation_team.si(league_id=league_id, cross_comparison=False) |
            aggregate_league_team_task.si(league_id=league_id) |
            delete_aggregation_match.si(league_id=league_id, cross_comparison=False) |
            aggregate_league_player_task.si(league_id=league_id) |
            # cross compare
            delete_cross_comparison_team.si(league_id=league_id, cross_comparison=True) |
            cross_compare_team_task.si(league_id=league_id) |
            delete_cross_comparison_match.si(league_id=league_id, cross_comparison=True) |
            cross_compare_player_task.si(league_id=league_id)
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
                match_chain: chain = process_game_helper(
                    match_id=game['match_id'],
                    league_id=league_id,
                    execute=False
                )
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
        celery_helper = (
            cross_compare_league_task_helper
            if process_type == 'cross_compare_league' else
            aggregate_league_task_helper
        )

        sel_result = db_session.exec(select(League))
        league_objs: Iterable[League] = sel_result.all()
        league_list = [x.id for x in league_objs]

        for league_id in league_ids:
            if league_id in league_list:
                celery_helper(league_id=league_id)
            else:
                logger.warning('League {} doesn\'t exist in the database')
