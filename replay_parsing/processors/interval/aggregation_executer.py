import pandas as pd
import numpy as np


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


def execute_window_aggregation(df: pd.DataFrame,
                               column: str,
                               agg_type: str,
                               df_agg: pd.DataFrame):
    if column == 'movement':
        ser = _find_distance(df['x'], df['y'])
    elif column == 'stacked':
        ser = df['camps_stacked'] + df['creeps_stacked']
    elif column == 'kda':
        ser = df['kills'] + (df['assists'] * 0.5)
    else:
        ser = df[column]

    if column in df_agg:
        ser_agg = df_agg[column]
    else:
        ser_agg = None

    # CASES
    if agg_type == 'max':
        return np.max(ser)

    elif agg_type == 'gained_pm_median':
        ser_pm = _get_by_minute_slice(ser)
        shifted_ser_pm = _shift_series(ser_pm)
        return np.median(ser_pm.iloc[1:] - shifted_ser_pm.iloc[1:])

    elif agg_type == 'avg_(by_length)':
        if column == 'movement':
            return np.sum(ser) / (len(ser) / 60)
        else:
            return (np.max(ser) - np.min(ser)) / (len(ser) / 60)

    elif agg_type == 'gained_pw':
        return (np.max(ser) - np.min(ser))

    elif agg_type == 'max_global_perc':
        ser_value = ser.max()
        ser_agg_value = ser_agg.max()
        return _clean_division(ser_value, ser_agg_value)

    elif agg_type == 'sum':
        return ser.sum()

    elif agg_type == 'min':
        return ser.min()

    elif agg_type == 'avg':
        return ser.mean()

    raise NameError(f"Aggregation type {agg_type} does not exist")
