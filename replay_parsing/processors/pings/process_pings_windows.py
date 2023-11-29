import copy
import pandas as pd
from replay_parsing.modules import MatchSplitter
from ..aggregations import WINDOWS_BASE_NULLS


def _aggregate_pings(df: pd.DataFrame | None) -> pd.DataFrame | None:
    if df is None:
        return None
    return df.groupby('slot').agg({'type': 'count'})


def process_pings_windows(df: pd.DataFrame, MS: MatchSplitter) -> dict:
    players_windows = {f'_{x}': copy.deepcopy(WINDOWS_BASE_NULLS) for x in range(10)}

    pings_windows = MS.split_in_windows(df, use_index=False)
    agged_pings_windows = [(_aggregate_pings(item['df']), item['name'], item['exists']) for item in pings_windows]
    for agged_df, time_window_name, is_exists in agged_pings_windows:
        if not is_exists:
            continue

        for idx, v in agged_df.iterrows():
            players_windows[f'_{idx}'][time_window_name] = v.values[0]
    return players_windows
