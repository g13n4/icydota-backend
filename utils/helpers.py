import math
import re
from collections.abc import Iterable
from datetime import datetime
from decimal import Decimal
from enum import EnumType
from typing import Any, TypeVar, Type, Set, Tuple, Optional

import numpy as np
from psycopg2.errors import IntegrityError
from sqlmodel import select, Session

from models import PositionApproximation


T = TypeVar('T')

T_numeric = TypeVar('T_numeric', int, float)


def is_numeric_type(value, none_is_true: bool = True) -> bool:
    if none_is_true and value is None:
        return True

    if not (isinstance(value, float) or isinstance(value, int)):
        return False

    return True


def get_all_sqlmodel_objs(db_session: Session, model, ) -> Iterable:
    sel_result = db_session.exec(select(model))
    return sel_result.all()


def get_both_slot_values(key: str | int) -> Tuple[str, int]:
    if isinstance(key, str):
        num = int(key[-1])
        return key, num
    else:
        return f'_{key}', key


def combine_slot_dicts(*args) -> dict:
    data = { f'_{x}': { } for x in range(10) }
    for x in range(10):
        for item in args:
            key = f'_{x}'
            data[key].update(item[key])
    return data


def is_invalid_value(value: Any) -> bool:
    if isinstance(value, Decimal):
        return value.is_nan()
    elif isinstance(value, float):
        return math.isnan(value)

    return value in [-np.inf, np.inf, np.nan, None]


def get_obj_from_list(objs_list: list, **kwargs):
    for obj in objs_list:
        suitable = []
        for k, v in kwargs.items():
            equals = (getattr(obj, k) == v)
            suitable.append(equals)

        if all(suitable):
            return obj

    return None


def none_to_zero(value: Any, nullify: bool = True) -> Optional[Decimal]:
    if value:
        return Decimal(value)

    return Decimal(0.0) if nullify else None


def refresh_objects(db_session: Session, objects, ) -> None:
    for obj in objects:
        db_session.refresh(obj)
    return None


def get_or_create_base(
        db_session: Session,
        model_obj: Type[T],
        get_key: Any,
        object_data: dict[str, Any]
) -> T:
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
                logger.warning(
                    'It seems that the there is a problem with creating an object.' +
                    "Let's give it another chance to ensure that it's not just an inserting error..."
                )
        else:
            output = get_or_create_base(*args, **kwargs)

    return output


def get_sqlmodel_fields(model, include_ids: bool = False, to_set: bool = False) -> list[str] | Set[str]:
    schema = model.schema()
    fields = schema['properties']
    output = []
    for field_name in fields.keys():
        if re.search(r'(^|_)id$', field_name) and not include_ids:
            continue
        output.append(field_name)
    return output if not to_set else set(output)


def to_dec(number: float | int | None, rounding: int = 2):
    if is_invalid_value(number):
        return None

    return round(Decimal(float(number)), rounding)


def get_positions_approximations(
        db_session: Session,
        team_sentinel_id: int,
        team_dire_id: int,
        league_id: int,
) -> dict[int, int]:
    objs = db_session.exec(
        select(PositionApproximation.player_id, PositionApproximation.position_id).
        where(
            PositionApproximation.league_id == league_id,
            (PositionApproximation.team_id).in_([team_sentinel_id, team_dire_id]),
        )
    )

    return { pid: poid for pid, poid in objs }


def is_na_decimal(value: Any) -> bool:
    if (isinstance(value, Decimal)) and value.is_nan():
        return True
    return False


def to_str_time(unix_timestamp: int) -> str:
    return datetime.utcfromtimestamp(unix_timestamp).strftime('%Y/%m/%d')


def unique_list(*args: Iterable[list]) -> list:
    output = set(value for sub_list in args for value in sub_list)
    return list(output)


def is_equals_to_zero(value: Optional[T_numeric], pseudo: bool = False) -> Optional[T_numeric]:
    if value is not None:
        output = (value == 0)
        if not pseudo:
            return output
        else:
            return int(output)

    return None


def get_enum_values(enum_: EnumType):
    return [x.value for x in enum_]
