from typing import Optional

from constants.performance.game_side import SPItem, SidePerformance


class SidePerformanceDataMixin:
    """Mixin that contains dynamically created fields for "SidePerformanceData" class"""
    __mixin__ = True


for side_performance_field in SidePerformance.VALUES:
    cls_field_value = getattr(SidePerformance, side_performance_field.name)
    SidePerformanceDataMixin.__annotations__[side_performance_field.name] = Optional[cls_field_value.value_type]
