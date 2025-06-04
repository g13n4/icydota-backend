from collections.abc import Iterable
from typing import Any

import numpy as np
import pandas as pd
from sqlalchemy import Select

from constants.performance.total import GameTotals
from constants.performance.window import WINDOWS_BY_MASK, AllWindows, WindowEmptyMask
from modules.empty_mask_converter import EmptyMaskConverter


DATA_MODEL_IGNORE_FIELDS = ['id', 'performance_id']
PROCESSING_COMPARISON_LIST = [(False, None), (True, True), (True, False), ]


def process_mask(mask_name: str, mask: int | None) -> dict:
    if mask is None:
        return { }

    windows = WINDOWS_BY_MASK[mask_name].VALUES_NAMES
    return EmptyMaskConverter.mask_to_dict(mask, windows)


def unpack_row(row: Iterable, names: list[str]) -> dict[str, Any]:
    output_mask = { }
    output = { }

    for name, value in zip(names, row):
        if name in [WindowEmptyMask.l_empty_mask, WindowEmptyMask.g_empty_mask]:
            mask_data = process_mask(name, value)
            output_mask.update(mask_data)
        elif name in ['window_table', 'total_data'] and value is not None:
            model_dump = value.model_dump(exclude=set(DATA_MODEL_IGNORE_FIELDS))
            output.update(model_dump)
        else:
            output[name] = value

    output.update(output_mask)
    return output


def process_data(data: list[dict[str, Any]], group_by: list[str], is_window: bool) -> Iterable:
    df = pd.DataFrame(data)
    df.replace([np.inf, -np.inf, np.nan], None, inplace=True)

    columns = AllWindows.VALUES_NAMES if is_window else GameTotals.VALUES_NAMES
    aggregated_df = df.groupby(group_by)[columns].mean()

    for idx, this_values_dict in aggregated_df.reset_index().T.to_dict().items():
        yield this_values_dict


def get_query_data(db_session, query: Select, names: list[str]) -> list[dict]:
    query_output = db_session.exec(query)

    data = list()
    for row in query_output.all():
        row_data = unpack_row(row, names)
        data.append(row_data)

    return data


def none_max(*values: int | float) -> int | float | None:
    output_value = None
    for value in values:
        if value is not None:
            # first ever not none value
            if output_value is None:
                output_value = value
            elif output_value is not None:
                output_value = max(value, output_value)

    return output_value
