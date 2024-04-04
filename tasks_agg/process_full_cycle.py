import requests
from celery import chain, group
from celery.utils.log import get_task_logger
from sqlmodel import Session

from db import get_sync_db_session
from models import League
from tasks.create_league import get_or_create_league
from tasks.process_game import process_game_helper
from .agg_helper import aggregate_league_helper, cross_compare_league_helper
from .approximate_positions import approximate_positions
from .process_aggregation import process_aggregation
from .process_aggregation_cross_comparison import create_cross_comparison_aggregation


logger = get_task_logger(__name__)


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


def process_full_cycle(league_obj: League | None = None, league_id: int | None = None):
    db_session: Session = get_sync_db_session()

    league_obj = get_or_create_league(league_id, db_session, league_obj)

    r = requests.get(f'https://api.opendota.com/api/leagues/{league_obj.id}/matches')
    league_match_data = r.json()

    games = []
    for idx, game in enumerate(league_match_data):
        match_chain: chain = process_game_helper(match_id=game['match_id'], league_id=league_obj.id, get_chain=True)
        games.append(match_chain)
        break

    (group(games) |
     approximate_positions.si(league_id=league_obj.id, ) |
     group(games) |
     process_aggregation.si(league_id=league_obj.id) |
     create_cross_comparison_aggregation.si(league_id=league_obj.id)
     ).apply_async()

    logger.INFO(f"PARSING FOR LEAGUE {league_obj.id} IS DONE")

    return
