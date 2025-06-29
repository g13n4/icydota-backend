from typing import Dict, Optional

import requests
from celery import chord, chain, group
from celery.utils.log import get_task_logger
from sqlmodel import Session

from db import get_sync_db_session
from models import Game, League
from tasks.approximate_positions import approximate_positions
from tasks.game.download_replay import get_match_replay
from tasks.game.process_game import process_game_data
from tasks.league.create_league import get_or_create_league
from utils.game_parsers_list import AVAILABLE_PARSERS_PORT


logger = get_task_logger(__name__)


def process_game_helper(match_id: int, league_id: int | None = None, get_chain: bool = False) -> Optional[chain]:
    port = next(AVAILABLE_PARSERS_PORT)
    match_chain = (get_match_replay.si(match_id=match_id, parser_port=port) |
                   process_game_data.si(match_id=match_id, league_id=league_id))
    if get_chain:
        return match_chain

    match_chain.apply_async()
    return None


def process_league(
        league_obj: League | None = None,
        league_id: int | None = None,
        overwrite: bool = False,
        execute: bool = True
):
    db_session: Session = get_sync_db_session()

    league_obj = get_or_create_league(league_id, db_session, league_obj)

    r = requests.get(f'https://api.opendota.com/api/leagues/{league_obj.id}/matches')
    league_match_data = r.json()

    db_league_games: Dict[int, Game] = { x.id: x for x in league_obj.games }
    new_games_found = 0
    new_games_found_list = []
    tasks = None

    for idx, game in enumerate(league_match_data):
        if game['match_id'] in db_league_games and not overwrite:
            continue
        else:
            new_games_found_list.append(
                process_game_helper(
                    match_id=game['match_id'],
                    league_id=league_obj.id,
                    get_chain=True,
                )
            )

            new_games_found += 1
    if new_games_found_list:
        tasks = chord(
            group(new_games_found_list) | approximate_positions.s(league_id=league_id)
        ).on_error(approximate_positions.s(league_id=league_id))

    if execute:
        if tasks:
            tasks.apply_async()

        return new_games_found, None

    return new_games_found, new_games_found_list
