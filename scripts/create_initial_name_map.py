import os
from pathlib import Path

import click

from scripts.name_map.facets import FACETS_NAME, check_initial_facets_map
from scripts.name_map.heroes import HEROES_NAME, check_initial_heroes_map
from scripts.name_map.side_calc import SIDE_CALC_NAME, check_initial_calc_fields_map


FUNCTION_MAP = {
    SIDE_CALC_NAME: check_initial_facets_map,
    FACETS_NAME: check_initial_calc_fields_map,
    HEROES_NAME: check_initial_heroes_map,
}


def create_initial_redis_name_map(on_startup: bool = False):
    for name, function in FUNCTION_MAP.items():
        function(func_type="redis")
        if not on_startup:
            print(f"Setting map data for {name}")

    if on_startup:
        print(f"Set up redis data for {", ".join(FUNCTION_MAP.keys())}")


def create_initial_json_name_map():
    app_folder = Path(os.getcwd()).parent
    data_folder_path = Path(app_folder) / "data"
    print(f"Data folder is set to {data_folder_path}")

    existing_map = {
        SIDE_CALC_NAME: False,
        FACETS_NAME: False,
        HEROES_NAME: False,

    }
    print(f"Set maps: {', '.join(existing_map.keys())}")
    with os.scandir(data_folder_path) as it:
        for entry in it:
            full_name = entry.name
            full_path = data_folder_path / full_name
            if entry.name.endswith(".json") and entry.is_file():
                file_name, _ = full_name.split(".")
                name, hash_ = file_name.split("-")

                cleanup = None
                if name in existing_map:
                    print(f"Found existing {name} file!")
                    check_func = FUNCTION_MAP[name]
                    existing_map[name] = True

                    cleanup = check_func(func_type="json", path=data_folder_path, hash_=hash_)

                if cleanup:
                    print(f"Cleaned-up old {name} file!")
                    os.remove(full_path)
                elif cleanup is None:
                    print(f"Hash for {name} is the same. No actions are needed")
                else:
                    print(f"No existing file for {name} was found! Creating one...")

    for name, is_processed in existing_map.items():
        if not is_processed:
            print(f"No existing file for {name} was found! Creating one...")
            check_func = FUNCTION_MAP[name]
            check_func(func_type="json", path=data_folder_path, hash_=None)


@click.command()
@click.option('--redis', default=None, help='Set files to redis')
@click.option('--json', default=None, help='Save in json format in data folder')
def create_initial_name_map(redis: bool | None, json: bool | None):
    if redis:
        print(f"Creation mode is set to redis")
    elif json:
        create_initial_json_name_map()
    else:
        raise KeyError("No parameter provided! Please choose from: redis, json")


if __name__ == "__main__":
    create_initial_name_map()
