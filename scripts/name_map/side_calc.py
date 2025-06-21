from constants.performance.game_side import SidePerformance
from scripts.name_map.processing import check_data_map


SIDE_CALC_NAME = "side_calc"


def create_side_calc_fields_map():
    data = dict()
    for side_item in SidePerformance.VALUES:
        data[side_item.name] = side_item.description
    return data


def check_initial_calc_fields_map(func_type: str, **kwargs):
    return check_data_map(
        func_type=func_type,
        data_creation=create_side_calc_fields_map,
        file_name_const=SIDE_CALC_NAME,
        **kwargs
    )
