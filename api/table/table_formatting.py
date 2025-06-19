from typing import List, Optional

from api.table.helpers import extract_formatted_columns, format_formatted_columns
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

    header_columns = extract_formatted_columns(data, rows, ALL_CALCULATION_FIELDS)

    return {
        "data": data,
        "columns": header_columns,
        "valueMapping": value_mapping,
    }


def to_table_format_cross_comparison(
        data: list,
        values_info: list,
        header_name: str,
        columns: list[str],
) -> dict:

    header_columns = format_formatted_columns(header_name, columns)

    return {
        "data": data,
        "columns": header_columns,
        "valueMapping": values_info,
    }
