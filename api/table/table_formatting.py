from typing import List

from api.table.helpers import extract_formatted_columns, format_formatted_columns
from constants.performance.total.total import GameTotals
from constants.performance.window import AllWindows


ALL_CALCULATION_MAP = {
    **{ item.name: item for item in GameTotals.VALUES },
    **{ item.name: item for item in AllWindows.VALUES },
}


def to_table_format(
        data: List[dict],
        value_mapping: list,
        rows: list,
        is_total: bool,
) -> dict:

    header_columns = extract_formatted_columns(
        data=data,
        pinned_columns=rows,
        item_map=ALL_CALCULATION_MAP,
        is_total=is_total,
    )

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
