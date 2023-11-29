import subprocess
from pathlib import Path
import os
import bz2
import requests

CURRENT_DIR = Path.cwd()
BASE_PATH = os.path.join(CURRENT_DIR, Path('./replays'))


def _is_empty(path: Path) -> bool:
    return os.stat(path).st_size == 0


def continue_to_process(file_path: Path, match_id: int, process_name: str, overwrite: bool, ) -> bool:
    if file_path.exists():
        if overwrite:
            os.remove(file_path)
        else:
            if _is_empty(file_path):
                print(f'{match_id} | {process_name} | file is empty! Trying to process again...')
            else:
                print(f'{match_id} | {process_name} | already exists')
                return False
    return True


def _get_match_download_info(match_id: int) -> list:
    r = requests.get(f'https://api.opendota.com/api/replays', params={'match_id': match_id})
    if r.status_code == 200:
        print(f'{match_id} received match info successfully')
        return r.json()
    else:
        print(f'{match_id} received no match info')
        return []


def _download_archived_replay(match_id: int,
                              folder_path: Path,
                              valve_replay_info: list | None = None,
                              overwrite: bool = False) -> None:
    file_path = Path(os.path.join(folder_path, f'{match_id}.dem.bz2'))

    if not continue_to_process(file_path=file_path,
                               match_id=match_id,
                               process_name='downloading',
                               overwrite=overwrite):
        return None

    if not valve_replay_info:
        valve_replay_info = _get_match_download_info(match_id)

    for replay in valve_replay_info:
        match_id = replay['match_id']
        cluster = replay['cluster']
        replay_salt = replay['replay_salt']

        download_url = f"http://replay{cluster}.valve.net/570/{match_id}_{replay_salt}.dem.bz2"

        r = requests.get(download_url, stream=True)
        with open(file_path, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)

        print(f'{match_id} downloaded successfully')


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
    print(f'{match_id} decompressed replay successfully')





def _parse_replay_v2(match_id: int, folder_path: Path, overwrite: bool = False) -> None:
    output_path = Path(os.path.join(folder_path, f'{match_id}.jsonl'))

    if not continue_to_process(file_path=output_path,
                               match_id=match_id,
                               process_name='parsing',
                               overwrite=overwrite):
        return None

    command = 'curl localhost:5600 --data-binary ' + \
              f'"@replays/{match_id}/{match_id}.dem" > "replays/{match_id}/{match_id}.jsonl"'
    subprocess.run(command, shell=True)
    print(f'{match_id} replay is parsed successfully')


def get_match_replay(match_id: int, overwrite: bool = False):
    match_folder_path = Path(f'{BASE_PATH}/{match_id}/')
    match_folder_path.mkdir(parents=True, exist_ok=True)

    _download_archived_replay(match_id=match_id, folder_path=match_folder_path, overwrite=overwrite)
    _decompress_archived_replay(match_id=match_id, folder_path=match_folder_path)
    _parse_replay_v2(match_id=match_id, folder_path=match_folder_path)


get_match_replay(7402800418)
