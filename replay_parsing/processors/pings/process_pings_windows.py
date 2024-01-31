from functools import partial

import pandas as pd

from replay_parsing.modules import MatchSplitter
from ..processing_utils import add_data_type_name
from ...windows import PINGS_WINDOWS


PROCESSED_DATA_NAME = 'pings'
AN = partial(add_data_type_name, text_to_add=PROCESSED_DATA_NAME)


def _aggregate_pings(df: pd.DataFrame | None) -> pd.DataFrame | None:
    if df is None:
        return None
    return df.groupby('slot')['type'].count()


def process_pings_windows(df: pd.DataFrame, MS: MatchSplitter, ) -> dict:
    players_windows = MS.create_windows(WINDOWS=PINGS_WINDOWS, AN=AN)

    pings_windows = MS.split_into_windows(df)

    for df_window in pings_windows:
        if df_window['exists'] and not df_window['is_empty']:
            agged_df = _aggregate_pings(df_window['df'])

            values = agged_df.to_dict()
            for k, v in values.items():
                players_windows[f'_{k}'][AN('pings')][df_window['name']] = v
                players_windows[f'_{k}'][AN('pings_per_minute')][df_window['name']] = v / df_window['minutes']

    return players_windows
