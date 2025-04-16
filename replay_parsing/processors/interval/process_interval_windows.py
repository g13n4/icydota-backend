import numpy as np
import pandas as pd

from constants.calculation.game.calculation_type.interval import IntervalCalculations
from modules.match_splitter import MatchSplitter
from modules.performance_data_processor import PerformanceDataProcessor
from replay_parsing.processors.interval.aggregation_executer import execute_window_aggregation


def process_interval_windows(df: pd.DataFrame, MS: MatchSplitter, PDP: PerformanceDataProcessor, ) -> None:
    agg_by_time_df = (df.groupby('time')
                      .agg({'gold': 'sum',
                            'xp': 'sum',
                            'kills': 'sum',
                            'deaths': 'sum',
                            'rune_pickups': 'sum', }))

    agg_player_windows = MS.split_into_windows(agg_by_time_df, use_index=True)
    dfs_by_player = MS.split_by_player(df)
    for slot, player_df in dfs_by_player:
        player_windows = MS.split_into_windows(player_df)
        for calc_item in IntervalCalculations.VALUES:
            for player_window, agg_window in zip(player_windows, agg_player_windows):
                if not player_window['exists']:
                    continue

                with np.errstate(divide='ignore', invalid='ignore'):
                    value = execute_window_aggregation(
                        df=player_window['df'],
                        column=calc_item.processing[0],
                        agg_method=calc_item.processing[1],
                        df_agg=agg_window['df']
                    )

                PDP.set_value(slot=slot, calculation=calc_item.value, window_index=player_window['index'], value=value)
