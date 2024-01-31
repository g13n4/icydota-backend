from decimal import Decimal
from typing import Any

import pandas as pd
from sqlmodel import select, Session
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


def get_all_sqlmodel_objs(db_session: Session, model, ) -> list:
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
        for k, v in kwargs.items():
            equals = (getattr(obj, k) == v)
            suitable.append(equals)

        if all(suitable):
            return obj

    return None


def none_to_zero(value: Any) -> Decimal:
    if value:
        return Decimal(value)
    return Decimal(0.0)


def refresh_objects(db_session: Session, objects, ) -> None:
    for obj in objects:
        db_session.refresh(obj)
    return None
