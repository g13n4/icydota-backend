from celery import shared_task

from tasks.game.delete_replay import delete_replay_folder
from tasks.game.download_replay import get_match_replay
from tasks.game.process_game import process_game_data


@shared_task(name='single_task_process_game', retries=2, default_retry_delay=7, ignore_result=True)
def single_task_process_game(match_id: int, league_id: int | None, port: int):
    get_match_replay(match_id=match_id, parser_port=port)
    process_game_data(match_id=match_id, league_id=league_id)
    delete_replay_folder(match_id=match_id)
