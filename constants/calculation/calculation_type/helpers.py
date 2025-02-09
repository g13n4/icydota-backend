from typing import Callable, TypeVar, Any

from pydantic import BaseModel
from sqlmodel import Field

from constants.helpers import Item


CalculationType = TypeVar('CalculationType')


class PostprocessingItem(BaseModel):
    carry_comparison: bool = False
    support_comparison: bool = False

    percentage: bool = False

    total_format: int | None = None


class CalculationItem(BaseModel):
    name: str
    description: str
    value: int | None = None

    is_active: bool = True
    index: int
    category: Item | None = None
    active: bool = True
    processing: tuple[Any, Any] | None = None
    postprocessing: PostprocessingItem = Field(default_factory=PostprocessingItem)


def set_category_and_value(category: Item) -> Callable:
    def decorator(klass: object) -> object:
        for name, type_ in klass.__annotations__.items():
            if isinstance(type_, CalculationItem):
                item = getattr(klass, name)
                item.category = category
                item.value = category.value * 100 + item.index

        return klass


    return decorator


def add_values(klass: CalculationType) -> CalculationType:
    VALUES = []
    for name, type_ in klass.__annotations__.items():
        if isinstance(type_, CalculationItem):
            value = getattr(klass, name)
            VALUES.append(value)

    setattr(klass, 'VALUES', VALUES)
    return klass
