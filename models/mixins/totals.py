from pydantic import condecimal
from sqlmodel import Field

from constants.performance.total import GameTotals


class PerformanceTotalDataMixin:
    """Mixin that contains dynamically created fields for "PerformanceTotalData" class"""
    __mixin__ = True


for total_field in GameTotals.VALUES:
    # create it for pydantic
    setattr(PerformanceTotalDataMixin, total_field.name, Field(default=None, nullable=True, primary_key=False))
    PerformanceTotalDataMixin.__annotations__[total_field.name] = total_field.value_type
