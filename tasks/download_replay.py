import bz2
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Callable

import requests
from celery import shared_task
from celery.utils.log import get_task_logger


CURRENT_DIR = Path(__file__).parent.parent.absolute()
BASE_REPLAY_PATH = os.path.join(CURRENT_DIR, Path('./replays'))

assert Path(BASE_REPLAY_PATH).is_dir() == True

logger = get_task_logger(__name__)


class ReplayDataError(Exception):
    pass


# FILE CHECK
def _is_empty(path: Path) -> bool:
    return os.stat(path).st_size == 0


def clean_up_file(func: Callable) -> Callable:
    def wrapper(*args, **kwargs) -> bool:
        output: bool = func(*args, **kwargs)  # add try / except
        if not output:
            file: Path = kwargs.get('file_path', None) or args[0]

            if file.is_file():
                os.remove(file)
        return output


    return wrapper


@clean_up_file
def _json_exists_and_valid(file_path: Path) -> bool:
    if file_path.exists() and not _is_empty(file_path):
        with open(file_path, "r") as file:
            game_data = json.load(file)
            if 'error' not in game_data:
                return True

    return False


@clean_up_file
def _any_file_exists(file_path: Path) -> bool:
    if file_path.exists() and not _is_empty(file_path):
        return True

    return False


@clean_up_file
def _jsonl_exists_and_valid(file_path: Path) -> bool:
    if file_path.exists() and not _is_empty(file_path):
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


def extract_url_from_json(file_path: Path) -> str:
    with open(file_path, "r") as match_json:
        game_data = json.load(match_json)

    replay_url = game_data.get('replay_url', None)
    if not game_data['replay_url']:
        replay_url = f"http://replay{game_data['cluster']}.valve.net/" + \
                     f"570/{game_data['match_id']}_{game_data['replay_salt']}.dem.bz2"

    return replay_url


# FILE DOWNLOAD
def download_json(match_id: int, file_path: Path) -> str:
    r = requests.get(f'https://api.opendota.com/api/matches/{match_id}')
    if r.status_code == 200:
        game_data = r.json()
        if 'error' not in game_data:
            replay_url = game_data.get('replay_url', None)
            if not game_data['replay_url']:
                replay_url = f"http://replay{game_data['cluster']}.valve.net/570/{match_id}_{game_data['replay_salt']}.dem.bz2"

            with open(file_path, "w") as match_json:
                json.dump(game_data, match_json)

            return replay_url

    raise ConnectionError("Can't access open dota")


def download_dem_bz2(url: str, bz2_path: Path):
    r = requests.get(url, stream=True)
    with open(bz2_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)


def unzip_dem(bz2_path: Path, dem_path: Path):
    with bz2.BZ2File(bz2_path, 'rb') as file_input, open(dem_path, 'wb') as file_output:
        for data in iter(lambda: file_input.read(100 * 1024), b''):
            file_output.write(data)


def parse_replay(dem_file: Path, replay_file: Path, port: int = 5600):
    command = f'curl localhost:{port} --data-binary ' + f'"@{str(dem_file)}" > "{str(replay_file)}"'
    curl_reponse = subprocess.run(command, shell=True, check=True, capture_output=True)
    return curl_reponse


@shared_task(name='get_match_replay', retries=3, default_retry_delay=7)
def get_match_replay(match_id: int, first_parser: bool = True) -> int:
    logger.info(f'Download replay for {match_id}')

    folder_path = Path(os.path.join(BASE_REPLAY_PATH, f'{match_id}/'))
    folder_path.mkdir(parents=True, exist_ok=True)

    json_file = Path(os.path.join(folder_path, f'./{match_id}.json'))
    is_valid = _json_exists_and_valid(file_path=json_file)
    if not is_valid:
        url = download_json(match_id=match_id, file_path=json_file)
    else:
        url = extract_url_from_json(file_path=json_file)

    dem_bz2_file = Path(os.path.join(folder_path, f'./{match_id}.dem.bz2'))
    is_valid = _any_file_exists(dem_bz2_file)
    if not is_valid:
        download_dem_bz2(url, dem_bz2_file)

    dem_file = Path(os.path.join(folder_path, f'./{match_id}.dem'))
    is_valid = _any_file_exists(dem_file)
    if not is_valid:
        unzip_dem(bz2_path=dem_bz2_file, dem_path=dem_file)

    parser_port = 5600
    if not first_parser:
        parser_port = 5700

    jsonl_file = Path(os.path.join(folder_path, f'./{match_id}.jsonl'))
    is_valid = _jsonl_exists_and_valid(jsonl_file)
    if not is_valid:
        curl_response = parse_replay(dem_file, jsonl_file, parser_port)
        is_valid = _jsonl_exists_and_valid(jsonl_file)

        if not is_valid:
            logger.error(f"Replay data for match {match_id} is not correct!")
            raise ReplayDataError(curl_response)

    return match_id
