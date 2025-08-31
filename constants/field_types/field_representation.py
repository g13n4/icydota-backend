from collections.abc import Iterable
from enum import StrEnum
from functools import partial
from itertools import product
from typing import Literal, get_args


class FieldRepresentationEnum(StrEnum):
    LANE = "lane"
    PERCENT = "percent"
    LEVEL = "level"
    TIME = "time"
    BOOLEAN = "boolean"


FIELD_REPRESENTATION_TYPE = Literal[
    FieldRepresentationEnum.LANE,
    FieldRepresentationEnum.PERCENT,
    FieldRepresentationEnum.LEVEL,
    FieldRepresentationEnum.TIME,
    FieldRepresentationEnum.BOOLEAN,
]
FIELD_REPRESENTATION_VALUE = get_args(FIELD_REPRESENTATION_TYPE)
FIELD_REPRESENTATION_INDEX = 0


class DataTypeRepresentationEnum(StrEnum):
    MATCH = "match"
    AGGREGATION = "aggregation"
    CROSS_COMPARISON = "cross_comparison"


DATA_TYPE_TYPE = Literal[
    DataTypeRepresentationEnum.MATCH,
    DataTypeRepresentationEnum.AGGREGATION,
    DataTypeRepresentationEnum.CROSS_COMPARISON,
]
DATA_TYPE_VALUE = get_args(DATA_TYPE_TYPE)
DATA_TYPE_INDEX = 1


class PlayerOrTeamEnum(StrEnum):
    PLAYER = "player"
    TEAM = "team"


POT_TYPE = Literal[PlayerOrTeamEnum.PLAYER, PlayerOrTeamEnum.TEAM]
POT_VALUE = get_args(POT_TYPE)
POT_INDEX = 2


class TotalOrWindowRepresentationEnum(StrEnum):
    TOTAL = "total"
    WINDOW = "window"


TOW_TYPE = Literal[
    TotalOrWindowRepresentationEnum.TOTAL,
    TotalOrWindowRepresentationEnum.WINDOW,
]
TOW_VALUE = get_args(TOW_TYPE)
TOW_INDEX = 3


class ComparisonTypeRepresentationEnum(StrEnum):
    NONE = "none"
    FLAT = "flat"


COMPARISON_TYPE = Literal[
    ComparisonTypeRepresentationEnum.NONE,
    ComparisonTypeRepresentationEnum.FLAT,
]
COMPARISON_VALUE = get_args(COMPARISON_TYPE)
COMPARISON_INDEX = 4

BINARY_OFFSET_MAP = {
    **{ name: idx for idx, name in enumerate(DATA_TYPE_VALUE) },
    **{ name: idx << 2 for idx, name in enumerate(POT_VALUE) },
    **{ name: idx << 3 for idx, name in enumerate(TOW_VALUE) },
    **{ name: idx << 4 for idx, name in enumerate(COMPARISON_VALUE) },
    # in theory there should be offset to include this part in a big integer
    # but right now it works as a key
    **{ name: idx for idx, name in enumerate(FIELD_REPRESENTATION_VALUE) },
}

NAME_LIST_MAP = {
    "data_type": DATA_TYPE_VALUE,
    "pot": POT_VALUE,
    "tow": TOW_VALUE,
    "comparison": COMPARISON_VALUE,
}


class FieldRepresentation:
    __slots__ = (
        "field_repr",
        "data_type",
        "pot",
        "tow",
        "comparison",
    )


    def __init__(
            self,
            field_repr: FIELD_REPRESENTATION_TYPE,
            data_type: DATA_TYPE_TYPE | Iterable[DATA_TYPE_TYPE] | None = None,
            pot: POT_TYPE | Iterable[POT_TYPE] | None = None,
            tow: TOW_TYPE | Iterable[TOW_TYPE] | None = None,
            comparison: COMPARISON_TYPE | Iterable[COMPARISON_TYPE] | None = None,
    ):
        self.field_repr = field_repr
        self.data_type = data_type
        self.pot = pot
        self.tow = tow
        self.comparison = comparison


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
