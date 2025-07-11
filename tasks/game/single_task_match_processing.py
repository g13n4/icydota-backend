from celery import shared_task
from celery.utils.log import get_task_logger

from tasks.game.delete_replay import delete_replay_folder
from tasks.game.download_replay import get_match_replay
from tasks.game.process_game import process_game_data


logger = get_task_logger(__name__)

@shared_task(name='single_task_process_game', retries=3, default_retry_delay=180, ignore_result=True)
def single_task_process_game(match_id: int, league_id: int | None, port: int, **kwargs):
    logger.info(f"Start full match {match_id} processing...")

    get_match_replay(match_id=match_id, parser_port=port, outer_logger=logger)
    process_game_data(match_id=match_id, league_id=league_id, outer_logger=logger)
    delete_replay_folder(match_id=match_id, outer_logger=logger)
