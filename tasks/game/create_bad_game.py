import json
from pathlib import Path

from celery import shared_task
from celery.utils.log import get_task_logger

from db import get_sync_db_session
from file_path import BASE_REPLAY_PATH
from models import Game
from tasks.league.create_league import get_or_create_league


logger = get_task_logger(__name__)


@shared_task(name="create_bad_game_on_err", ignore_result=True)
def create_bad_game_on_error(match_id: int, league_id: None | int = None):
    logger.info(f'Filling bad replay for {match_id}')

    db_session = get_sync_db_session(expire=False)

    json_path = Path(f'{BASE_REPLAY_PATH}/{match_id}/{match_id}.json')
    try:
        with open(json_path, "r") as match_json:
            game_data = json.load(match_json)

    except (FileNotFoundError, json.JSONDecodeError):
        raise FileNotFoundError(f"No appropriate json found for {match_id} game!")

    if league_id is None:
        league_id = game_data['league']['leagueid']
        league_obj = get_or_create_league(db_session=db_session, league_id=league_id)
        league_id = league_obj.id

    game_obj = Game(
        id=match_id,
        league_id=league_id,
        patch_id=game_data["patch"],
        replay_url=game_data['replay_url'],
        is_broken=True,
        processed_counter=1,
    )

    db_session.add(game_obj)
    db_session.full_commit()
