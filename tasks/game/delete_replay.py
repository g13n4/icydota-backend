import os
import shutil
from pathlib import Path

from celery import shared_task
from celery.utils.log import get_task_logger
from dotenv import load_dotenv

from dev_constants import BASE_REPLAY_PATH


load_dotenv()

logger = get_task_logger(__name__)

DELETE_REPLAY = os.getenv('DELETE_REPLAY', default='true')


@shared_task(name='delete_replay_folder', ignore_result=True)
def delete_replay_folder(match_id: int, outer_logger=None, **kwargs):
    this_logger = outer_logger or logger

    if DELETE_REPLAY == "true":
        this_logger.info(f'Deleting match {match_id} replay folder')

        folder_path = Path(os.path.join(BASE_REPLAY_PATH, f'{match_id}'))
        if os.path.isdir(folder_path):
            shutil.rmtree(folder_path)
            this_logger.info(f"Deleted folder for game {match_id} successfully")
        else:
            this_logger.warning(f"No folder for game {match_id} was found")


    return None
