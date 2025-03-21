from collections.abc import Iterable
from typing import Any

import numpy as np
import pandas as pd

from constants.performance.total import GameTotals
from constants.performance.window import WINDOWS_BY_MASK, AllWindows
from modules.empty_mask_converter import EmptyMaskConverter


DATA_MODEL_IGNORE_FIELDS = ['id', 'game_performance_id']
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
        if name in ['l_empty_mask', 'g_empty_mask']:
            mask_data = process_mask(name, value)
            output_mask.update(mask_data)
        elif name in ['window_table', 'total_data']:
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


def get_query_data(db_session, query, names: list[str]) -> list[dict]:
    query_output = db_session.exec(query)

    data = list()
    for row in query_output.all():
        row_data = unpack_row(row, names)
        data.append(row_data)

    return data
