import re
from typing import List, Optional, Dict
from .translation_dictionary import PERFORMANCE_FIELD_DICT
from .sorting_rating import performance_data_sort_rating

def to_proper_name(value: str, split: str = '_') -> str:
    return ' '.join(value.split(split)).capitalize()


def get_field_name(value: str, sum_total: Optional[bool] = None):
    if value.endswith('total'):
        field_name = PERFORMANCE_FIELD_DICT[value]
        if sum_total is None:
            field_name += ' (not calculated)'
        elif sum_total:
            field_name += ' (SUM)'
        else:
            field_name += ' (AVG)'

        return field_name

    if value in PERFORMANCE_FIELD_DICT:
        return PERFORMANCE_FIELD_DICT[value]

    return to_proper_name(value)


def to_table_format(data: List[dict], data_info: List[dict],  rows: list, sum_total: Optional[bool] = None) -> dict:
    if not data:
        return {}

    item = data[0]

    values = sorted([key_name for key_name in item.keys() if key_name not in rows],
                    key=performance_data_sort_rating)

    fields = {'rows': rows,
              'columns': [],
              'values': values,
              'valueInCols': True, }

    meta = [{
        'field': x,
        'name': get_field_name(x, sum_total), } for x in item.keys()]

    return {
        "table_data": {
            'fields': fields,
            'meta': meta,
            'data': data,
        },
        "table_options": {
            "style": {
                "layoutWidthType": 'colAdaptive', },
        },
        "table_values": data_info,
        "loading": False,
    }


def to_table_format_cross_comparison(data: Dict[int, list],
                                     values_info: list,
                                     aggregation_type: str) -> dict:
    if not data:
        return {}


    fields = {'rows': [aggregation_type],  # hero/pos/player | l2/g2/etc
              'columns': [],
              'values': sorted(data.keys(),
                               key=lambda x: str(x).lower()),  # classic windows/ total_values
              'valueInCols': True, }

    return {
        "table_data": {
            'fields': fields,
            'data': [x for x in data.values()],
        },
        "table_values": values_info,
        "loading": False,
    }
