import unittest

from replay_parsing import ODOTAPositionNormaliser


MOCK_DATA_ONE = ([{'hero_id': 58, 'neutral_kills': 9, 'lane_role': 1},
                  {'hero_id': 65, 'neutral_kills': 43, 'lane_role': 2},
                  {'hero_id': 94, 'neutral_kills': 112, 'lane_role': 1},
                  {'hero_id': 90, 'neutral_kills': 9, 'lane_role': 3},
                  {'hero_id': 71, 'neutral_kills': 28, 'lane_role': 3}, ],
                 {94: 1, 65: 2, 71: 3, 90: 4, 58: 5, },)

MOCK_DATA_TWO = ([{'hero_id': 58, 'neutral_kills': 9, 'lane_role': 1},
                  {'hero_id': 65, 'neutral_kills': 43, 'lane_role': 2},
                  {'hero_id': 94, 'neutral_kills': 112, 'lane_role': 1},
                  {'hero_id': 90, 'neutral_kills': 9, 'lane_role': 2},
                  {'hero_id': 71, 'neutral_kills': 28, 'lane_role': 3}, ],
                 {94: 1, 65: 2, 71: 3, 90: 4, 58: 5, },)

MOCK_DATA_THREE = ([{'hero_id': 58, 'neutral_kills': 9, 'lane_role': 5},
                    {'hero_id': 65, 'neutral_kills': 43, 'lane_role': 2},
                    {'hero_id': 94, 'neutral_kills': 112, 'lane_role': 5},
                    {'hero_id': 90, 'neutral_kills': 9, 'lane_role': 2},
                    {'hero_id': 71, 'neutral_kills': 28, 'lane_role': 3}, ],
                   {94: 1, 65: 2, 71: 3, 90: 4, 58: 5, },)


class ODOTAPositionNormaliserTest(unittest.TestCase):

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
