from collections.abc import Iterable
from functools import partial
from itertools import product
from typing import Literal, get_args


FIELD_REPRESENTATION_TYPE = Literal["lane", "percent", "level", "time", "boolean"]
FIELD_REPRESENTATION_VALUE = get_args(FIELD_REPRESENTATION_TYPE)
FIELD_REPRESENTATION_INDEX = 0

DATA_TYPE_TYPE = Literal["match", "aggregation", "cross_comparison"]
DATA_TYPE_VALUE = get_args(DATA_TYPE_TYPE)
DATA_TYPE_INDEX = 1

POT_TYPE = Literal["player", "team"]
POT_VALUE = get_args(POT_TYPE)
POT_INDEX = 2

TOW_TYPE = Literal["total", "window"]
TOW_VALUE = get_args(TOW_TYPE)
TOW_INDEX = 3

BINARY_OFFSET_MAP = {
    **{ name: idx for idx, name in enumerate(DATA_TYPE_VALUE) },
    **{ name: idx << 2 for idx, name in enumerate(POT_VALUE) },
    **{ name: idx << 3 for idx, name in enumerate(TOW_VALUE) },
    **{ name: idx << 4 for idx, name in enumerate(FIELD_REPRESENTATION_VALUE) },
}

NAME_LIST_MAP = {
    "data_type": DATA_TYPE_VALUE,
    "pot": POT_VALUE,
    "tow": TOW_VALUE,
}


class FieldRepresentation:
    __slots__ = (
        "field_repr",
        "data_type",
        "pot",
        "tow",
    )


    def __init__(
            self,
            field_repr: FIELD_REPRESENTATION_TYPE,
            data_type: DATA_TYPE_TYPE | Iterable[DATA_TYPE_TYPE] | None = None,
            pot: POT_TYPE | Iterable[POT_TYPE] | None = None,
            tow: TOW_TYPE | Iterable[TOW_TYPE] | None = None,
    ):
        self.field_repr = field_repr
        self.data_type = data_type
        self.pot = pot
        self.tow = tow


    @staticmethod
    def transform_tuple(named_tuple: tuple[str, ...], to_int: bool = False) -> tuple[int, ...] | int:
        output = [0] * len(FieldRepresentation.__slots__)
        for idx, value in enumerate(named_tuple):
            output[idx]: int = BINARY_OFFSET_MAP[value]

        if to_int:
            return sum(output)
        else:
            return tuple(output)


    def get_named_product(self) -> product:
        output = []
        for value_name in self.__slots__:
            value = getattr(self, value_name)

            if value is None:
                output.append(tuple(name for name in NAME_LIST_MAP[value_name]))
            elif isinstance(value, Iterable) and not isinstance(value, str):
                output.append(value)
            else:
                output.append((value,))  # tuple

        return product(*output)


TotalFieldRepresentation = partial(FieldRepresentation, tow="total")
WindowFieldRepresentation = partial(FieldRepresentation, tow="window")
