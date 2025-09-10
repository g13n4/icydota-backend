import os
from typing import Optional

from celery import chain
from dotenv import load_dotenv

from tasks.game.create_bad_game import create_bad_game_on_error
from tasks.game.delete_replay import delete_replay_folder
from tasks.game.download_replay import get_match_replay
from tasks.game.process_game import process_game_data
from tasks.game.single_task_match_processing import single_task_process_game
from tasks.game.singleton_task import fake_match_task, is_match_locked
from utils.game_parsers_list import AVAILABLE_PARSERS_PORT


load_dotenv()

MATCH_ONE_TASK = os.getenv('MATCH_ONE_TASK', default='true')


def process_game_helper(
        match_id: int,
        league_id: int | None = None,
        execute: bool = False,
        reason: int | None = None,
) -> Optional[chain]:
    is_locked = is_match_locked(match_id=match_id)

    if is_locked:
        task = fake_match_task.si()
    else:
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
