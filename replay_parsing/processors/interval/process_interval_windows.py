import copy
import pandas as pd
from replay_parsing.modules import MatchSplitter
from ..aggregations import INTERVAL_WINDOWS, WINDOWS_BASE
from . import execute_window_aggregation


def process_interval_windows(df: pd.DataFrame, MS: MatchSplitter) -> dict:
    data_by_player = {}

    agg_by_time_df = (df.groupby('time')
                      .agg({'gold': 'sum',
                            'xp': 'sum',
                            'kills': 'sum',
                            'deaths': 'sum',
                            'rune_pickups': 'sum', }))
    agg_by_time_windows = MS.split_in_windows(agg_by_time_df)
    df_by_player = MS.split_by_player(df)
    for player_df in df_by_player:
        player_windows = MS.split_in_windows(player_df['df'])
        player_data_list = []
        for column, agg_type in INTERVAL_WINDOWS:
            current_agg_window_data = copy.deepcopy(WINDOWS_BASE)
            current_agg_window_data['name'] = f'{column}__{agg_type}'
            for p_window, agg_window in zip(player_windows, agg_by_time_windows):
                if not p_window['exists']:
                    current_agg_window_data[p_window['name']] = None
                    continue

                value = execute_window_aggregation(df=p_window['df'],
                                                   column=column,
                                                   agg_type=agg_type,
                                                   df_agg=agg_window['df'])
                current_agg_window_data[p_window['name']] = value
            player_data_list.append(current_agg_window_data)
        data_by_player[player_df['name']] = player_data_list
    return data_by_player

