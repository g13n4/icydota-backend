import unittest

from constants.performance.window import GameWindow
from modules.match_windows_handler import MatchWindowsHandler


class TestMask:
    first: str = 'first'
    second: str = 'second'


test_windows = [
GameWindow(order=1, start_time=-100, end_time=100, )
]




class MatchWindowsHandlerTest(unittest.TestCase):

    def test_data_one(self):
        player_data, proper_positions = MOCK_DATA_ONE
        OPN = ODOTAPositionNormaliser(player_data)
        opn_output = OPN.get_hero_to_positions()
        self.assertDictEqual(proper_positions, opn_output)


    def test_data_two(self):
        player_data, proper_positions = MOCK_DATA_TWO
        OPN = ODOTAPositionNormaliser(player_data)
        opn_output = OPN.get_hero_to_positions()
        self.assertDictEqual(proper_positions, opn_output)


    def test_data_three(self):
        player_data, proper_positions = MOCK_DATA_THREE
        OPN = ODOTAPositionNormaliser(player_data)
        opn_output = OPN.get_hero_to_positions()
        self.assertDictEqual(proper_positions, opn_output)
