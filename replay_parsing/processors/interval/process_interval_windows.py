import copy
from functools import partial
from typing import Dict

import pandas as pd

from replay_parsing.modules import MatchSplitter
from . import execute_window_aggregation
from ..aggregations import WINDOWS_BASE
from ..processing_utils import add_data_type_name
from ...windows import INTERVAL_WINDOWS_AGGS

PROCESSED_DATA_NAME = 'interval'
AN = partial(add_data_type_name, text_to_add=PROCESSED_DATA_NAME)


def process_interval_windows(df: pd.DataFrame, MS: MatchSplitter) -> Dict[str, Dict]:
    data_by_player = {f'_{x}': {} for x in range(10)}

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
        for column, agg_type in INTERVAL_WINDOWS_AGGS:
            value_name = AN(f'{column}__{agg_type}')
            current_agg_window_data = copy.deepcopy(WINDOWS_BASE)

            for p_window, agg_window in zip(player_windows, agg_by_time_windows):
                if not p_window['exists']:
                    continue

                value = execute_window_aggregation(df=p_window['df'],
                                                   column=column,
                                                   agg_type=agg_type,
                                                   df_agg=agg_window['df'])

                current_agg_window_data[p_window['name']] = value

            data_by_player[player_df['name']][value_name] = current_agg_window_data

    return data_by_player
