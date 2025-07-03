from typing import Dict, Optional

import requests
from celery import chain, group
from celery.utils.log import get_task_logger
from sqlmodel import Session

from db import get_sync_db_session
from models import Game, League
from tasks import set_comparison_names
from tasks.approximate_positions import approximate_positions
from tasks.game.delete_replay import delete_replay_folder
from tasks.game.download_replay import get_match_replay
from tasks.game.process_game import process_game_data
from tasks.league.create_league import get_or_create_league
from utils.game_parsers_list import AVAILABLE_PARSERS_PORT


logger = get_task_logger(__name__)


def process_game_helper(match_id: int, league_id: int | None = None, execute: bool = False) -> Optional[chain]:
    port = next(AVAILABLE_PARSERS_PORT)
    match_chain = (
            get_match_replay.si(match_id=match_id, parser_port=port) |
            process_game_data.si(match_id=match_id, league_id=league_id) |
            delete_replay_folder.si(match_id=match_id)
    )

    if execute:
        match_chain.apply_async()
        return None
    else:
        return match_chain


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
    new_games_found_list = []

    for idx, game in enumerate(league_match_data):
        if game['match_id'] in db_league_games and not overwrite:
            continue
        else:
            new_games_found_list.append(
                process_game_helper(
                    match_id=game['match_id'],
                    league_id=league_obj.id,
                    execute=False,
                )
            )

    if new_games_found_list:
        games_found = len(new_games_found_list)
        tasks = (
                group(*new_games_found_list) | approximate_positions.si(
            league_id=league_id
        ) | set_comparison_names.si()
        ).on_error(
            approximate_positions.si(league_id=league_id) | set_comparison_names.si()
        )

        if execute:
            tasks.apply_async()
            return games_found, None
        else:
            return games_found, new_games_found_list

    else:
        return 0, None
