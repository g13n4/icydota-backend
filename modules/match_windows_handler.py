import bisect
import math
from collections import defaultdict
from typing import TypedDict, Any

from constants.performance.window import AllWindows


class MatchWindow(TypedDict):
    name: str
    window_type: str
    index: int
    order: int

    start_time: int | None
    end_time: int | None

    window_start: int | None
    window_end: int | None
    window_length: int | None

    length: int
    minutes: int

    exists: bool
    empty: bool | None
    incomplete: bool
    df: Any | None


class MatchWindowsHandler:
    """
    A processor that creates windows using constant values of windows
    """


    def __init__(self, windows: None):
        if windows is None:
            windows = AllWindows.VALUES_REAL

        self.match_windows = [
            MatchWindow(
                name=window.name,
                window_type=window.window_type,
                index=window.index,
                order=window.order,

                start_time=None,
                end_time=None,

                window_start=window.start_time,
                window_end=window.end_time,
                window_length=window.length,

                length=0,
                minutes=0,

                exists=False,
                empty=None,
                incomplete=False,
                df=None,
            ) for window in windows
        ]

        self.grouped_windows = defaultdict(list)
        self.windows_unique_values = []

        self._group_windows()


    def __getitem__(self, value: int):
        range_key = bisect.bisect_left(self.windows_unique_values, value)
        if range_key == value:
            return self.grouped_windows[range_key]
        # if the value is not equal to the key range_key will be bigger than window that we want
        return self.grouped_windows[range_key - 1]


    def _group_windows(self):
        ranges_set = set()
        for window in self.match_windows:
            ranges_set.add(window['window_start'])
            ranges_set.add(window['window_end'])

        for value in ranges_set:
            for window in self.match_windows:
                window_start = -math.inf if window['window_start'] is None else window['window_start']
                window_end = math.inf if window['window_end'] is None else window['window_end']

                if window_start <= value < window_end:
                    self.grouped_windows[value].append(window)

        self.windows_unique_values = sorted(list(ranges_set))


    def update_windows_time(self, in_game_time: int):
        windows = self[in_game_time]
        for this_window in windows:
            if not this_window['start_time']:
                this_window['start_time']: int = in_game_time
                this_window['exists'] = True

            this_window['end_time']: int = in_game_time


    def set_window_status(self) -> None:
        for window in self.match_windows:
            if window['exists']:
                window['length'] = window['end_time'] - window['start_time'] + 1
                window['minutes'] = math.ceil(window['length'] / 60)

            if window['window_length'] is not None and window['window_length'] is not None:
                is_complete_window = (window['window_length'] + 2 > window['length'] > window['window_length'] - 2)
                if window['length'] > 0 and not is_complete_window:
                    window['incomplete'] = True
