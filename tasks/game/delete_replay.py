import os
from pathlib import Path

from celery import shared_task
from dotenv import load_dotenv
from celery.utils.log import get_task_logger
import shutil
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
        try:
            shutil.rmtree(folder_path)
        except:
            logger.error(f'Something went wrong when deleting match {match_id} ')
            raise

    return None


