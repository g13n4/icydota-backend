from typing import Callable

import numpy as np
import pandas as pd

from constants.calculation.game.calculation_type.interval import IntervalCalculationAggregationMethod as AGG_METHOD
from constants.calculation.game.calculation_type.interval import IntervalCalculationColumn as COLUMN


def normalise_output_type_wrapper(allow_none: bool = False):
    def wrapper_outer(func: Callable) -> Callable:
        def wrapper_inner(*args, **kwargs) -> int | float | None:
            output = func(*args, **kwargs)

            return process_output(output, allow_none=allow_none)
        return wrapper_inner
    return wrapper_outer


def _clean_division(x, y) -> int | float:
    if np.isnan(x) or np.isnan(y) or not (x and y):
        return 0
    return x / y


def _get_by_minute_slice(ser: pd.Series) -> pd.Series:
    return ser.iloc[::-60].iloc[::-1]


def _shift_series(series: pd.Series) -> pd.Series:
    return series.shift(1).fillna(series.iloc[0])


def _find_distance(axis_x: pd.Series, axis_y: pd.Series) -> pd.Series:
    shifted_x = _shift_series(axis_x)
    shifted_y = _shift_series(axis_y)
    return (np.square(shifted_x - axis_x) + np.square(shifted_y - axis_y))


@normalise_output_type_wrapper(allow_none=True)
def execute_window_aggregation(df: pd.DataFrame,
                               column: COLUMN,
                               agg_method: AGG_METHOD,
                               df_agg: pd.DataFrame):
    match column:
        case COLUMN.MOVEMENT:
            if not len(df['x']) or not len(df['y']):
                return 0

            ser = _find_distance(df['x'], df['y'])
        case COLUMN.STACKED:
            ser = df['camps_stacked'] + df['creeps_stacked']
        case COLUMN.KDA:
            ser = df['kills'] + (df['assists'] * 0.5)
        case _:
            ser = df[column.value]

    if not len(ser):
        return 0

    if column in df_agg:
        ser_agg = df_agg[column.value]
    else:
        ser_agg = None

    # CASES
    match (agg_method, agg_method):
        case (AGG_METHOD.MAX, _):
            return np.max(ser)

        case (AGG_METHOD.GAINED_PM_MEDIAN, _):
            ser_pm = _get_by_minute_slice(ser)
            shifted_ser_pm = _shift_series(ser_pm)
            return np.median(ser_pm.iloc[1:] - shifted_ser_pm.iloc[1:])

        case (AGG_METHOD.AVG_BY_LENGTH_PM, COLUMN.MOVEMENT):
            return np.sum(ser) / (len(ser) / 60)

        case (AGG_METHOD.AVG_BY_LENGTH_PM, _):
            return (np.max(ser) - np.min(ser)) / (len(ser) / 60)

        case (AGG_METHOD.GAINED_PW, _):
            return (np.max(ser) - np.min(ser))

        case (AGG_METHOD.MAX_GLOBAL_PERC, _):
            ser_value = ser.max()
            ser_agg_value = ser_agg.max()
            return _clean_division(ser_value, ser_agg_value)

        case (AGG_METHOD.SUM, _):
            return ser.sum()

        case (AGG_METHOD.MIN, _):
            return ser.min()

        case (AGG_METHOD.AVG, _):
            return ser.mean()

        case (_, _):
            raise NameError(f"Aggregation type {agg_method} does not exist")
