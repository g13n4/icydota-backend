from functools import partial

import pandas as pd

from replay_parsing.modules import MatchSplitter
from utils import create_player_windows
from ..aggregations import WINDOWS_BASE_NULLS
from ..processing_utils import add_data_type_name
from ...windows import PINGS_WINDOWS

PROCESSED_DATA_NAME = 'pings'
AN = partial(add_data_type_name, text_to_add=PROCESSED_DATA_NAME)


def _aggregate_pings(df: pd.DataFrame | None) -> pd.DataFrame | None:
    if df is None:
        return None
    return df.groupby('slot')['type'].count()


def process_pings_windows(df: pd.DataFrame, MS: MatchSplitter, ) -> dict:
    players_windows = create_player_windows(WINDOWS=PINGS_WINDOWS, WINDOW_BASE_DICT=WINDOWS_BASE_NULLS, AN=AN)

    pings_windows = MS.split_in_windows(df, use_index=False)

    for df_window in pings_windows:
        agged_df = _aggregate_pings(df_window['df'])
        if not df_window['exists']:
            continue

        values = agged_df.to_dict()
        for k, v in values.items():
            players_windows[f'_{k}'][AN('pings')][df_window['name']] = v
            players_windows[f'_{k}'][AN('pings_per_minute')][df_window['name']] = v / df_window['minutes']
    return players_windows
