import os
import shutil
from pathlib import Path

from celery import shared_task
from celery.utils.log import get_task_logger
from dotenv import load_dotenv


load_dotenv()

CURRENT_DIR = Path(__file__).parent.parent.parent.absolute()
BASE_REPLAY_PATH = os.path.join(CURRENT_DIR, Path('./replays'))
assert Path(BASE_REPLAY_PATH).is_dir() == True

logger = get_task_logger(__name__)

DELETE_REPLAY = os.getenv('DELETE_REPLAY', default='true')


@shared_task(name='delete_replay_folder', ignore_result=True)
def delete_replay_folder(match_id: int):
    if DELETE_REPLAY == "true":
        logger.info(f'Deleting match {match_id} replay folder')

        folder_path = Path(os.path.join(BASE_REPLAY_PATH, f'{match_id}'))
        shutil.rmtree(folder_path)

    return None
