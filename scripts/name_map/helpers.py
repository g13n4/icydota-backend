import hashlib
import io
import json
from pathlib import Path
from typing import Callable, Literal

from redis_app import get_redis_single


def write_dict_to_json(data: dict, file_name: str | Path) -> None:
    print(file_name)
    with open(file_name, "w") as file:
        json.dump(data, file)
    return None


def check_if_exists(file_name: str | Path) -> bool:
    try:
        with open(file_name, "rb") as file:
            json.load(file)
        return True
    except json.decoder.JSONDecodeError as err:
        return False


def check_file_hash(file_path: Path, expected_hash: str | None) -> bool | None:
    """
    Checks an initial data dictionary
    :param file_path:
    :param expected_hash: hash of existing data
    :return: None if the file doesn't exist and bool indicates data correctness
    """
    if not expected_hash:
        return None

    try:
        with open(file_path, "rb") as file:
            data = json.load(file)
            if data.get("_hash", None) == expected_hash:
                return True
            return False

    except FileNotFoundError:
        return None


def get_dict_hash(data: dict) -> str:
    """MD5 hash of a dictionary."""
    dhash = hashlib.md5()
    encoded = json.dumps(data, sort_keys=True).encode()
    dhash.update(encoded)
    return dhash.hexdigest()


def get_file_hash(file: io.TextIOWrapper) -> str:
    """MD5 hash of a file."""
    dhash = hashlib.md5()
    encoded = file.read().encode()
    dhash.update(encoded)
    return dhash.hexdigest()
