import copy
import math
from typing import List

import pandas as pd


class MatchSplitter:
    def __init__(self, game_length: int, offset: int = +90, time_windows: list = None, ):
        """The variable game_length doesn't need _offset. It breaks proper calculation in _calculate_time_in_window"""
        self._offset = offset
        self._game_length = game_length

        if not time_windows:
            early_game_windows = [(-90, 60 * 2, 'l2'),  # first 2 minutes
                                  (60 * 2, 60 * 4, 'l4'),  # 2-4
                                  (60 * 4, 60 * 6, 'l6'),  # 4-6
                                  (60 * 6, 60 * 8, 'l8'),  # 6-8
                                  (60 * 8, 60 * 10, 'l10'),  # 8-10
                                  ]
            late_game_windows = [(-90, 60 * 15, 'g15'),  # first 15 minutes
                                 (60 * 15, 60 * 30, 'g30'),  # 15 - 30
                                 (60 * 30, 60 * 45, 'g45'),  # 30 - 45
                                 (60 * 45, 60 * 60, 'g60'),  # 6-8
                                 (60 * 60, None, 'g60plus'),  # 8-10
                                 ]
            time_windows = early_game_windows + late_game_windows

        self._time_windows = self._set_time_windows(time_windows)

    @property
    def game_length(self) -> int:
        return self._game_length

    def _calculate_time_in_window(self, start_time: int, end_time: int | None) -> int:
        if self._game_length < start_time:
            # the game has ended / no such window exists
            return 0
        else:
            if end_time is not None and end_time < self._game_length:
                return end_time - start_time
            else:
                # the game ended before the end of the window
                return self._game_length - start_time

    def _set_time_windows(self, time_windows: list) -> list:
        processed_time_windows = []
        for start_time, end_time, name in time_windows:
            length = self._calculate_time_in_window(start_time, end_time)

            processed_time_windows.append(
                {
                    'name': name,
                    'start_time': start_time,
                    'end_time': end_time,
                    'start_index': start_time + self._offset,
                    'end_index': end_time + self._offset if end_time else None,
                    'length': length,
                    'minutes': math.floor(length / 60) if length else 0,
                    'exists': None,
                    'df': None,
                })
        return processed_time_windows

    def split_in_windows(self, df: pd.DataFrame, use_index: bool = True) -> List[dict]:
        """Process interval df for only one player"""
        time_windows = copy.deepcopy(self._time_windows)
        found_the_end = False

        if use_index:
            df_length = len(df.index)
            for item in time_windows:
                if found_the_end:
                    item['exists'] = False
                    continue

                item['exists'] = True
                if item['end_index'] is None or item['end_index'] > df_length:
                    item['df'] = df.iloc[item['start_index']: -1]
                    found_the_end = True
                else:
                    item['df'] = df.iloc[item['start_index']: item['end_index']]
        else:
            for item in time_windows:
                if found_the_end:
                    item['exists'] = False
                    continue

                temp_df = df[(item['start_time'] < df['time']) &
                             (df['time'] <= (item['end_time'] if item['end_time'] else 60*60*60))]  # 60+ game
                if temp_df.empty:
                    found_the_end = True
                    item['exists'] = False
                    continue

                item['exists'] = True
                item['df'] = temp_df

        return time_windows

    @staticmethod
    def split_by_player(df: pd.DataFrame) -> list:
        """Separate interval df by slot"""
        return [{'name': f'_{idx}', 'df': x} for idx, x in df.groupby('slot')]

    def get_windows_number(self) -> int:
        return len(self._time_windows)
