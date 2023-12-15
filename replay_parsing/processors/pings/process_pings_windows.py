import copy
import pandas as pd
from replay_parsing.modules import MatchSplitter
from ..aggregations import WINDOWS_BASE_NULLS
from functools import partial
from ..processing_utils import add_data_type_name

PROCESSED_DATA_NAME = 'pings'
AN = partial(add_data_type_name, text_to_add=PROCESSED_DATA_NAME)

def _aggregate_pings(df: pd.DataFrame | None) -> pd.DataFrame | None:
    if df is None:
        return None
    return df.groupby('slot')['type'].count()


def process_pings_windows(df: pd.DataFrame, MS: MatchSplitter) -> dict:
    player_data = {AN(x): copy.deepcopy(WINDOWS_BASE_NULLS) for x in ['pings', 'pings_per_minute']}
    players_windows = {f'_{x}': copy.deepcopy(player_data) for x in range(10)}

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
