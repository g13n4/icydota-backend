from typing import List, Optional, Dict, Any
from utils import PERFORMANCE_FIELD_DICT, performance_data_sort_rating


def to_proper_name(value: str, split: str = '_') -> str:
    return ' '.join(value.split(split)).capitalize()


def get_field_name(value: str, sum_total: Optional[bool] = None):
    if value.endswith('total'):
        field_name = PERFORMANCE_FIELD_DICT[value]
        if sum_total is None:
            field_name += ''
        elif sum_total:
            field_name += ' (SUM)'
        else:
            field_name += ' (AVG)'

        return field_name

    if value in PERFORMANCE_FIELD_DICT:
        return PERFORMANCE_FIELD_DICT[value]

    return to_proper_name(value)


def update_row_fields(data: List[dict], rows: list[str]) -> None:
    for item in data:
        for row in rows:
            item[row] = get_field_name(item[row])


def to_table_format(data: List[dict], value_mapping: list, rows: list, columns: Optional[list] = None,
                    sum_total: Optional[bool] = None, is_vertical: bool = False) -> dict:
    # TODO: FIX SUM_TOTAL RIGHT NOW CALCULATING IT'S PRETTY MUCH IMPOSSIBLE. ADD AGG_TYPE TO DB MODELS

    if not data:
        return {}


    item = data[0]
    if columns is None:
        columns = []

    values = sorted([key_name for key_name in item.keys() if key_name not in rows],
                    key=performance_data_sort_rating)

    if is_vertical:
        fields = {'rows': rows,
                  'columns': columns,
                  'values': ['value'],
                  'valueInCols': True, }

        update_row_fields(data, rows)

    else:
        fields = {'rows': rows,
                  'columns': columns,
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
        "value_mapping": value_mapping,
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
        "value_mapping": values_info,
        "loading": False,
    }
