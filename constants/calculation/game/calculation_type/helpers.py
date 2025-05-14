from typing import Callable, TypeVar, Any

from pydantic import BaseModel
from sqlmodel import Field

from constants.helpers import Item
from helpers import UniqueIndexChecker


CalculationType = TypeVar('CalculationType')


class PostprocessingItem(BaseModel):
    total_format: int | None = None
    calculated_later: bool = False


class CalculationItem(BaseModel):
    name: str
    description: str
    value: int | None = None
    db_id: int | None = None

    is_active: bool = True
    index: int
    category: Item | None = None
    active: bool = True
    processing: tuple[Any, Any] | None = None
    postprocessing: PostprocessingItem = Field(default_factory=PostprocessingItem)



GLOBAL_VALUE_COUNTER = 0


def set_category_and_value(category: Item) -> Callable:
    def decorator(klass: object) -> object:
        checker = UniqueIndexChecker()
        for name, type_ in klass.__annotations__.items():
            if type_ is CalculationItem:
                item = getattr(klass, name)
                item.category = category
                item.db_id = category.value * 100 + item.index

                global GLOBAL_VALUE_COUNTER
                item.value = GLOBAL_VALUE_COUNTER
                GLOBAL_VALUE_COUNTER += 1

                checker.add(item.db_id)

        return klass


    return decorator


def add_values(klass: CalculationType) -> CalculationType:
    VALUES = []
    VALUES_NAMES = []
    for name, type_ in klass.__annotations__.items():
        if type_ is CalculationItem:
            value = getattr(klass, name)
            VALUES.append(value)
            VALUES_NAMES.append(name)

    setattr(klass, 'VALUES', VALUES)
    setattr(klass, 'VALUES_NAMES', VALUES_NAMES)
    return klass
