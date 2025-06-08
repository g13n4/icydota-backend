from typing import List, Optional

from constants.calculation.game.calculation_types import WindowCalculations
from constants.performance.total.total import GameTotals
from constants.performance.window import AllWindows


ALL_CALCULATION_FIELDS = {
    **{ item.name: item.description for item in GameTotals.VALUES },
    **{ item.name: item.description for item in WindowCalculations.VALUES },
    **{ item.name: item.description for item in AllWindows.VALUES },
}


def to_table_format(
        data: List[dict],
        value_mapping: list,
        rows: list,
        columns: Optional[list] = None,
        sum_total: Optional[bool] = None,
) -> dict:

    if not data:
        return { }

    item = data[0]
    if columns is None:
        columns = []

    values = sorted(
        [key_name for key_name in item.keys() if key_name not in rows],
    )

    fields = {
        'rows': rows,
        'columns': columns,
        'values': values,
        'valueInCols': True,
    }

    meta = [
        {
            'field': x,
            'name': ALL_CALCULATION_FIELDS.get(x, x),
        } for x in item.keys()
    ]

    return {
        "table_data": {
            'fields': fields,
            'meta': meta,
            'data': data,
        },
        "table_options": {
            "style": {
                "layoutWidthType": 'colAdaptive',
            },
        },
        "value_mapping": value_mapping,
    }


def to_table_format_cross_comparison(
        data: list,
        values_info: list,
        header_name: str,
        columns: list[str],
) -> dict:
    fields = {
        'rows': [header_name],  # hero/pos/player | l2/g2/etc
        'columns': [],
        'values': columns,  # classic windows/ total_values
        'valueInCols': True,
    }

    return {
        "table_data": {
            'fields': fields,
            'windows_data': data,
        },
        "value_mapping": values_info,
    }
