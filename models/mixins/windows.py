from pydantic import condecimal
from sqlmodel import Field

from constants.performance.window import AllWindows, GameWindow


class PerformanceWindowTableMixin:
    """Mixin that contains dynamically created fields for "PerformanceWindowTable" class"""
    __mixin__ = True


for window in AllWindows.VALUES:
    setattr(PerformanceWindowTableMixin, window.name, Field(default=None, nullable=True, primary_key=False))
    PerformanceWindowTableMixin.__annotations__[window.name] = condecimal(max_digits=10, decimal_places=2)
