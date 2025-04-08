import copy
from typing import Any

import pandas as pd


def _copy_and_set(dict_to_copy: dict, non_existing_windows: list[str], **kwargs_to_set) -> dict[str, Any]:
    new_dict = copy.deepcopy(dict_to_copy)
    for k, v in kwargs_to_set.items():
        new_dict[k] = v

    for window_name in non_existing_windows:
        new_dict[window_name] = None

    return new_dict


def _to_str(cname: Any) -> str:
    if isinstance(cname, str):
        return cname
    return '__'.join(list(cname))


class MatchSplitter:
    def __init__(self, game_length: int, match_windows: list):
        """The variable _game_total_length doesn't need _offset.
        It breaks proper processing in _calculate_time_in_window"""
        self.game_length = game_length
        self.match_windows = match_windows


    def split_into_windows(self, df: pd.DataFrame, use_index: bool = False) -> list[dict]:
        """Process interval df for only one player"""
        windows_for_this_df = copy.deepcopy(self.match_windows)

        for window in windows_for_this_df:
            if window['exists']:
                if use_index:
                    time = df.index
                else:
                    time = df['time']

                temp_df = df[(window['start_time'] < time) & (time <= window['end_time'])]

                window['df']: pd.DataFrame = temp_df
                window['is_empty'] = temp_df.empty

        return windows_for_this_df


    @staticmethod
    def split_by_player(df: pd.DataFrame) -> list[tuple]:
        """Separate interval df by slot"""
        return [(slot, slot_df) for slot, slot_df in df.groupby('slot')]
