import os
from typing import Dict, Optional

import celery
import requests
from celery import chain, group
from dotenv import load_dotenv
from sqlmodel import Session

from db import get_sync_db_session
from models import Game, League
from tasks import set_comparison_names
from tasks.approximate_positions import approximate_positions
from tasks.game.create_bad_game import create_bad_game_on_error
from tasks.game.delete_replay import delete_replay_folder
from tasks.game.download_replay import get_match_replay
from tasks.game.process_game import process_game_data
from tasks.game.single_task_match_processing import single_task_process_game
from tasks.league.create_league import get_or_create_league
from utils.game_parsers_list import AVAILABLE_PARSERS_PORT


load_dotenv()

MATCH_ONE_TASK = os.getenv('MATCH_ONE_TASK', default='true')


def process_game_helper(
        match_id: int,
        league_id: int | None = None,
        execute: bool = False,
        reason: int | None = None,
) -> Optional[chain]:
    port = next(AVAILABLE_PARSERS_PORT)
    if MATCH_ONE_TASK == "true":
        task = single_task_process_game.si(match_id=match_id, league_id=league_id, port=port, reason=reason)
    else:
        task = (
                get_match_replay.si(match_id=match_id, parser_port=port, reason=reason) |
                process_game_data.si(match_id=match_id, league_id=league_id, reason=reason) |
                delete_replay_folder.si(match_id=match_id, reason=reason)
        )

    task = task.on_error(
        create_bad_game_on_error.si(match_id=match_id, league_id=league_id) |
        delete_replay_folder.si(match_id=match_id)
    )

    if execute:
        task.apply_async()
        return None
    else:
        return task


def get_league_games_tasks(
        league_obj: League | None = None,
        league_id: int | None = None,
        overwrite: bool = False,
        reason: int | None = None,
) -> list:
    db_session: Session = get_sync_db_session(expire=False)

    league_obj = get_or_create_league(db_session=db_session, league_id=league_id, existing_obj=league_obj)

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
                    reason=reason,
                )
            )

    db_session.full_commit()
    return new_games_found_list


def process_league_task_group(
        league_obj: League | None = None,
        league_id: int | None = None,
        overwrite: bool = False,
        execute: bool = True,
        reason: int | None = None,
) -> tuple[int, None | celery.group]:
    tasks = get_league_games_tasks(league_obj=league_obj, league_id=league_id, overwrite=overwrite, reason=reason)

    if tasks:
        task = (
                group(*tasks) |
                approximate_positions.si(league_id=league_id) |
                set_comparison_names.si()
        ).on_error(
            approximate_positions.si(league_id=league_id) | set_comparison_names.si()
        )
        if execute:
            task.apply_async()
            return len(tasks), None

        return len(tasks), task

    else:
        return 0, None
