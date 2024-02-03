import bz2
import os
import re
import subprocess
from pathlib import Path

import requests
from celery.utils.log import get_task_logger


CURRENT_DIR = Path(__file__).parent.parent.absolute()
BASE_REPLAY_PATH = os.path.join(CURRENT_DIR, Path('./replays'))

assert Path(BASE_REPLAY_PATH).is_dir() == True

logger = get_task_logger(__name__)


def _is_empty(path: Path) -> bool:
    return os.stat(path).st_size == 0


def _jsonl_exists(file_path: Path) -> bool:
    if file_path.exists():
        return True
    return False


def _jsonl_is_valid(file_path: Path) -> bool:
    with open(file_path, 'r') as file:
        required_words = ['"cosmetics"', '"dotaplus"', '"epilogue"']
        matched_words = set()
        for line in file.readlines()[::-1]:
            for word in required_words:
                if re.search(word, line):
                    matched_words.add(word)

            if len(required_words) == len(matched_words):
                return True

    return False


def continue_to_process(file_path: Path, match_id: int, process_name: str, overwrite: bool, ) -> bool:
    if file_path.exists():
        if overwrite:
            os.remove(file_path)
        else:
            if _is_empty(file_path):
                logger.info(f'{match_id} | {process_name} | file is empty! Trying to process again...')
            else:
                logger.info(f'{match_id} | {process_name} | already exists')
                return False
    return True


def _download_archived_replay(match_id: int,
                              folder_path: Path,
                              url: str,
                              overwrite: bool = False, ) -> None:
    file_path = Path(os.path.join(folder_path, f'{match_id}.dem.bz2'))

    if not continue_to_process(file_path=file_path,
                               match_id=match_id,
                               process_name='downloading',
                               overwrite=overwrite):
        return None

    r = requests.get(url, stream=True)
    with open(file_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)

    logger.info(f'{match_id} downloaded successfully')


def _decompress_archived_replay(match_id: int, folder_path: Path, overwrite: bool = False) -> None:
    input_path = Path(os.path.join(folder_path, f'{match_id}.dem.bz2'))
    output_path = Path(os.path.join(folder_path, f'{match_id}.dem'))

    if not continue_to_process(file_path=output_path,
                               match_id=match_id,
                               process_name='decompressing',
                               overwrite=overwrite):
        return None

    with bz2.BZ2File(input_path, 'rb') as file_input, open(output_path, 'wb') as file_output:
        for data in iter(lambda: file_input.read(100 * 1024), b''):
            file_output.write(data)
    logger.info(f'{match_id} decompressed replay successfully')


def _parse_replay(match_id: int, folder_path: Path, overwrite: bool = False) -> None:
    output_path = Path(os.path.join(folder_path, f'{match_id}.jsonl'))

    if not continue_to_process(file_path=output_path,
                               match_id=match_id,
                               process_name='parsing',
                               overwrite=overwrite):
        return None

    curl_file_path = f'"@{str(folder_path)}/{match_id}.dem"'  # double quotes are intentional
    curl_file_output = f'"{str(folder_path)}/{match_id}.jsonl"'

    command = 'curl localhost:5600 --data-binary ' + f'{curl_file_path} > {curl_file_output}'
    curl_json = subprocess.run(command, shell=True, check=True, capture_output=True)
    logger.info(f'{match_id} replay is parsed successfully')


def get_match_replay(match_id: int,
                     url: str,
                     overwrite: bool = False,
                     folder_path: Path | None = None, ) -> None:
    folder_path.mkdir(parents=True, exist_ok=True)

    output_path = Path(os.path.join(folder_path, f'{match_id}.jsonl'))
    if not overwrite and \
            _jsonl_exists(file_path=output_path) and \
            not _jsonl_is_valid(file_path=output_path):
        overwrite = True
        logger.warning(f'It seems that parsed match {match_id} is broken. Overwriting...')

    try:
        _download_archived_replay(match_id=match_id, folder_path=folder_path, url=url, overwrite=overwrite, )
        _decompress_archived_replay(match_id=match_id, folder_path=folder_path, overwrite=overwrite, )
        _parse_replay(match_id=match_id, folder_path=folder_path, overwrite=overwrite)
    except EOFError:
        get_match_replay(match_id=match_id, url=url, overwrite=True, folder_path=folder_path)

    return None
