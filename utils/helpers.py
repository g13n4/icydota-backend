import re, enum
from decimal import Decimal
from itertools import cycle
from typing import Any, Dict, List, TypeVar, Type, Set

import pandas as pd
from psycopg2.errors import IntegrityError
from sqlmodel import select, Session
from tabulate import tabulate


T = TypeVar('T')

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
    sel_result = db_session.exec(select(model))
    return sel_result.all()


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


def get_or_create_base(db_session: Session,
                       model_obj: Type[T],
                       get_key: Any,
                       object_data: Dict[str, Any]) -> T:
    obj = db_session.get(model_obj, get_key)

    if not obj:
        new_obj = model_obj(**object_data)

        db_session.add(new_obj)
        db_session.commit()
        db_session.refresh(new_obj)

        return new_obj
    else:
        return obj


def get_or_create(logger, *args, **kwargs):
    output = None
    for x in range(2):
        if not x:
            try:
                output = get_or_create_base(*args, **kwargs)
            except IntegrityError:
                logger.warning('It seems that the there is a problem with creating an object.' +
                               "Let's give it another chance to ensure that it's not just inserting error...")
        else:
            output = get_or_create_base(*args, **kwargs)

    return output


bool_pool = cycle([True, False])


def get_sqlmodel_fields(model, include_ids: bool = False, to_set: bool = False) -> List[str] | Set[str]:
    schema = model.schema()
    fields = schema['properties']
    output = []
    for field_name in fields.keys():
        if re.search(r'(^|_)id$', field_name) and not include_ids:
            continue
        output.append(field_name)
    return output if not to_set else set(output)


def to_dec(number: float | int | None, rounding: int = 2):
    return number and round(Decimal(number), rounding)


def get_positions_approximations(db_session: Session, model, league_id) -> Dict[int, int]:
    objs = db_session.exec(select(model.player_id, model.position_id).
                           where(model.league_id == league_id))

    return {pid: poid for pid, poid in objs}

class CaseInsensitiveEnum(str, enum.Enum):
    @classmethod
    def _missing_(cls, value: str):
        for member in cls:
            if member.lower() == value.lower():
                return member
        return None
