import pandas as pd

from constants.calculation.game.calculation_type.pings import PingsCalculations as Calculations
from modules import MatchSplitter
from modules.performance_data_processor import PerformanceDataProcessor


def _aggregate_pings(df: pd.DataFrame | None) -> pd.DataFrame | None:
    if df is None:
        return None
    return df.groupby('slot')['type'].count()


def process_pings_windows(df: pd.DataFrame, MS: MatchSplitter, PDP: PerformanceDataProcessor, ) -> None:

    pings_windows = MS.split_into_windows(df)

    for df_window in pings_windows:
        if df_window['exists'] and not df_window['is_empty']:
            agged_df = _aggregate_pings(df_window['df'])

            values = agged_df.to_dict()
            for slot, value in values.items():
                per_min_value = value / df_window['minutes']

                PDP.set_value(slot=slot, calculation=Calculations.pings, window_index=df_window['index'], value=value)
                PDP.set_value(
                    slot=slot,
                    calculation=Calculations.pings_per_minute,
                    window_index=df_window['index'],
                    value=per_min_value,
                )

