import json
from pathlib import Path
from typing import Callable

from redis_app import get_redis_single
from scripts.name_map.helpers import get_dict_hash, write_dict_to_json


def check_data_map(**kwargs):
    func_type = kwargs.get("func_type", None)
    if func_type == "redis":
        check_data_map_redis(**kwargs)
    elif func_type == "json":
        check_data_map_json(**kwargs)
    else:
        raise ValueError(f"No function found for {func_type}")


def check_data_map_redis(data_creation: Callable, file_name_const: str, **kwargs):
    r = get_redis_single()

    data = data_creation()

    if not data:
        raise ValueError("No data was generated!")

    r.set(file_name_const, json.dumps(data))


def check_data_map_json(data_creation: Callable, file_name_const: str, path: Path, hash_: str | None, **kwargs):
    data = data_creation()
    current_hash = get_dict_hash(data)

    if not data:
        raise ValueError("No data was generated!")

    if not current_hash:
        raise ValueError("No key was generated!")

    if current_hash == hash_:
        return None

    file_name = path / f"{file_name_const}-{current_hash}.json"

    write_dict_to_json(data=data, file_name=file_name)
    return bool(hash_)
