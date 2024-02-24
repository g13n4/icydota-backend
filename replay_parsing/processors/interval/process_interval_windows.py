from functools import partial
from typing import Dict

import numpy as np
import pandas as pd

from replay_parsing.modules import MatchSplitter
from . import execute_window_aggregation
from ..processing_utils import add_data_type_name
from ...windows import INTERVAL_WINDOWS


PROCESSED_DATA_NAME = 'interval'
AN = partial(add_data_type_name, text_to_add=PROCESSED_DATA_NAME)


def process_interval_windows(df: pd.DataFrame, MS: MatchSplitter, ) -> Dict[str, Dict]:
    output_windows = MS.create_windows(WINDOWS=INTERVAL_WINDOWS, AN=AN)

    agg_by_time_df = (df.groupby('time')
                      .agg({'gold': 'sum',
                            'xp': 'sum',
                            'kills': 'sum',
                            'deaths': 'sum',
                            'rune_pickups': 'sum', }))

    agg_player_windows = MS.split_into_windows(agg_by_time_df, use_index=True)
    dfs_by_player = MS.split_by_player(df)
    for player_df in dfs_by_player:
        player_windows = MS.split_into_windows(player_df['df'])
        for column_db_name, window_names in INTERVAL_WINDOWS.items():
            column, agg_type = window_names
            value_type = AN(f'{column}__{agg_type}')

            for player_window, agg_window in zip(player_windows, agg_player_windows):
                if not player_window['exists']:
                    continue

                with np.errstate(divide='ignore', invalid='ignore'):
                    value = execute_window_aggregation(df=player_window['df'],
                                                       column=column,
                                                       agg_type=agg_type,
                                                       df_agg=agg_window['df'])

                output_windows[player_df['name']][value_type][player_window['name']] = value

    return output_windows
