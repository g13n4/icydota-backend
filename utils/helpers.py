import copy
from typing import Dict, Any, Callable

import pandas as pd
from sqlmodel import select
from tabulate import tabulate


def print_unique_values(df: pd.DataFrame, column: str):
    for x in sorted([x for x in df[column].unique().tolist() if isinstance(x, str)]):
        print(x)


def print_table(df: pd.DataFrame) -> None:
    print(tabulate(df, headers='keys', tablefmt='psql'))
    return None


def is_numeric_type(value, none_is_true: bool = True) -> bool:
    if none_is_true and value is None:
        return True

    if not (isinstance(value, float) or isinstance(value, int)):
        return False

    return True


def get_all_sqlmodel_objs(db_session, model, ) -> list:
    sel_result = db_session.execute(select(model))
    return sel_result.scalars().all()


def get_both_slot_values(key: str | int) -> (str, int):
    if type(key) is str:
        num = int(key[-1])
        return key, num
    else:
        return f'_{key}', key


def iterate_df(df: pd.DataFrame, use_offset: bool = True, index_offset: int = 1) -> (int, dict):
    for index, values in df.T.to_dict().items():
        if use_offset:
            index += index_offset
        yield (index, values)


def combine_slot_dicts(*args) -> dict:
    data = {f'_{x}': {} for x in range(10)}
    for x in range(10):
        for item in args:
            key = f'_{x}'
            data[key].update(item[key])
    return data


def get_obj_from_list(objs_list: list, **kwargs):
    for obj in objs_list:
        suitable = []
        for k, v in kwargs:
            equals = (getattr(obj, k) == v)
            suitable.append(equals)

        if all(suitable):
            return obj

    return None


def copy_and_set(dict_to_copy: dict, **kwargs_to_set):
    new_dict = copy.deepcopy(dict_to_copy)
    for k, v in kwargs_to_set:
        new_dict[k] = v
    return new_dict


def create_player_windows(WINDOWS: Dict[str, Any],
                          WINDOW_BASE_DICT: Dict[str, Any],
                          AN: Callable) -> Dict[str, Dict[str, Any]]:
    player_data = {AN(column_name): copy_and_set(WINDOW_BASE_DICT, _db_name=db_name, _parsing_name=column_name)
                   for db_name, column_name in WINDOWS}
    return {f'_{x}': copy.deepcopy(player_data) for x in range(10)}
