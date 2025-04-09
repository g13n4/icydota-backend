import unittest

from constants.performance.window import GameWindow
from modules.match_windows_handler import MatchWindowsHandler, MatchWindow


class TestMask:
    first: str = 'first'
    second: str = 'second'


test_windows = [
    GameWindow(order=0, index=0, start_time=-100, end_time=0, ),
    GameWindow(order=1, index=1, start_time=0, end_time=100, ),
    GameWindow(order=2, index=2, start_time=100, end_time=200, ),
    GameWindow(order=3, index=3, start_time=200, end_time=300, ),
    GameWindow(order=4, index=4, start_time=300, end_time=400, ),

    GameWindow(order=1, index=5, start_time=-90, end_time=-60, ),
    GameWindow(order=2, index=6, start_time=-60, end_time=-30, ),
    GameWindow(order=3, index=7, start_time=-30, end_time=0, ),
    GameWindow(order=4, index=8, start_time=0, end_time=30, ),
    GameWindow(order=5, index=9, start_time=30, end_time=60, ),
    GameWindow(order=6, index=10, start_time=60, end_time=90, ),
    GameWindow(order=7, index=11, start_time=90, end_time=120, ),
    GameWindow(order=8, index=12, start_time=120, end_time=150, ),
]

test_range = range(-50, 75)


def _get_index(output: list[MatchWindow]) -> set[int]:
    """Compare MatchWindowsHandler output's index to set"""
    return set(item['index'] for item in output)


class MatchWindowsHandlerTest(unittest.TestCase):

    def test_one(self):
        MWH = MatchWindowsHandler(test_windows)

        self.assertSetEqual(_get_index(MWH[-80]), set([0, 5]))
        self.assertSetEqual(_get_index(MWH[0]), set([1, 8]))
        self.assertSetEqual(_get_index(MWH[121]), set([2, 12]))
        self.assertSetEqual(_get_index(MWH[121]), set([2, 12]))

        for x in test_range:
            MWH.update_time(x)
        MWH.set_window_status()

        for window in MWH.match_windows:
            index = window['index']
            # full windows
            if index in range(7, 10):
                self.assertEqual(window['exists'], True)
                self.assertEqual(window['incomplete'], False)
            # partial windows
            #             first              second
            elif index in [0, 1] or index in [6, 10]:
                self.assertEqual(window['exists'], True)
                self.assertEqual(window['incomplete'], True)
            else:
                self.assertEqual(window['exists'], False)
