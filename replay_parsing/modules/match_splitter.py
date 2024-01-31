import copy
from decimal import Decimal
from typing import Dict, Any, Callable, List

import pandas as pd


WINDOWS_BASE: Dict[str, int | None | Decimal] = {
    'l2': 0,
    'l4': 0,
    'l6': 0,
    'l8': 0,
    'l10': 0,

    # next phase
    'g15': 0,
    'g30': 0,
    'g45': 0,
    'g60': 0,
    'g60plus': 0,

    '_db_name': None,
    '_parsing_name': None,
}


def _copy_and_set(dict_to_copy: dict, non_existing_windows: List[str], **kwargs_to_set) -> Dict[str, Any]:
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
    def __init__(self, game_length: int, match_windows: List, base_window: Dict[str, Any] | None = None):
        """The variable _game_total_length doesn't need _offset.
        It breaks proper calculation in _calculate_time_in_window"""
        self._game_length = game_length
        self.match_windows = match_windows

        if not base_window:
            self._base_window = WINDOWS_BASE

        self.window_values_names = [name for name in self._base_window.keys() if not name.startswith('_')]


    @property
    def game_length(self) -> int:
        return self._game_length


    def split_into_windows(self, df: pd.DataFrame, use_index: bool = False) -> List[dict]:
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
    def split_by_player(df: pd.DataFrame) -> list:
        """Separate interval df by slot"""
        return [{'name': f'_{idx}', 'df': x} for idx, x in df.groupby('slot')]


    def create_windows(self, WINDOWS: Dict[str, Any], AN: Callable, ) -> Dict[str, Dict[str, Any]]:
        not_existing_windows = [w['name'] for w in self.match_windows if not w['exists']]

        player_data = {AN(_to_str(column_name)): _copy_and_set(dict_to_copy=self._base_window,
                                                               non_existing_windows=not_existing_windows,
                                                               _db_name=db_name,
                                                               _parsing_name=_to_str(column_name), )
                       for db_name, column_name in WINDOWS.items()}
        return {f'_{x}': copy.deepcopy(player_data) for x in range(10)}
