from typing import Callable, TypeVar, Any

from pydantic import BaseModel

from constants.helpers import Item
from modules.unique_index_checker import UniqueIndexChecker


CalculationType = TypeVar('CalculationType')


class PostprocessingItem(BaseModel):
    calculated_later: bool = False


class CalculationItem(BaseModel):
    name: str
    description: str
    value: int | None = None  # global
    db_id: int | None = None
    index: int  # local

    is_active: bool = True
    category: Item | None = None
    processing: tuple[Any, Any] | None = None
    postprocessing: PostprocessingItem | None = None

    def __eq__(self, other):
        if isinstance(type(self), type(other)):
            return self.db_id == other.db_id
        return self.db_id == other


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
