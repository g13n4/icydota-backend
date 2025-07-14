from constants.position import PositionConstant
from modules.interval_chart_data_collector import LINE_VALUES_TO_PROCESS, generate_chart_name


class GamePerformanceGraphMixin:
    """Mixin that contains dynamically created fields for "GamePerformanceGraph" class"""
    __mixin__ = True


for value_type in LINE_VALUES_TO_PROCESS:
    for pos_item in PositionConstant.POSITIONS:
        GamePerformanceGraphMixin.__annotations__[generate_chart_name(pos=pos_item.value, value_type=value_type)] = str

    GamePerformanceGraphMixin.__annotations__[generate_chart_name(pos=None, value_type=value_type)] = str
