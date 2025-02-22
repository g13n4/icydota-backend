import pandas as pd

from constants.calculation.game.calculation_type.wards import WardsCalculations
from modules import MatchSplitter
from modules.performance_data_processor import PerformanceDataProcessor


WARD_TYPE_MAP = {
    'sen': WardsCalculations.placed_wards_sen,
    'obs': WardsCalculations.placed_wards_obs,
}


def process_wards_windows(df: pd.DataFrame, MS: MatchSplitter, PDP: PerformanceDataProcessor, ) -> None:
    wards_windows = MS.split_into_windows(df, use_index=False)

    for window_df in wards_windows:
        if window_df['exists']:
            grouped_wdf = window_df['df'].groupby(['slot', 'type'])['time'].count()
            for k, v in grouped_wdf.to_dict().items():
                slot, ward_type = k
                calc_type = WARD_TYPE_MAP[ward_type]

                PDP.set_value(slot=slot, calculation=calc_type, window_index=window_df['index'], value=v)
