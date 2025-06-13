import unittest
from itertools import product

import requests
from ddt import ddt, idata, unpack

from constants.api import GameStageEnum, ComparisonEnum, ComparisonTypeEnum, PoTEnum
from constants.calculation.game.calculation_types import WindowCalculations
from helpers import HEADERS, API_PREFIX, ADDRESS, test_output, delay
from utils.helpers import get_enum_values


# TEST DATA
MATCH_IDS = [8299323927, 8302819453, 8314368342]

both_iterator_total = product(
    get_enum_values(PoTEnum),
    MATCH_IDS,
    get_enum_values(ComparisonEnum),
)

player_iterator_window = product(
    MATCH_IDS,
    get_enum_values(GameStageEnum),
    get_enum_values(ComparisonEnum),
    get_enum_values(ComparisonTypeEnum),
    WindowCalculations.VALUES(only_field="db_id"),
)

team_iterator_window = product(
    MATCH_IDS,
    get_enum_values(GameStageEnum),
    get_enum_values(ComparisonEnum),
    WindowCalculations.VALUES(only_field="db_id"),
)


@ddt
class MatchRouteTest(unittest.TestCase):
    @idata(both_iterator_total)
    @unpack
    def test_both_totals(self, pot, match_id, comp):
        url = ADDRESS + API_PREFIX + f'/data/match/{pot}/{match_id}/0'
        params = { "comp": comp, "stage": "both" }
        delay()
        response = requests.get(url, headers=HEADERS, params=params)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(test_output(response.json()))


    @idata(player_iterator_window)
    @unpack
    def test_player_calculation(self, match_id, stage, comp, comp_type, calc_id):
        url = ADDRESS + API_PREFIX + f'/data/match/player/{match_id}/{calc_id}'
        params = {
            "comp": comp,
            "stage": stage,
            "ctype": comp_type,
        }
        delay()
        response = requests.get(url, headers=HEADERS, params=params)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(test_output(response.json()))


    @idata(team_iterator_window)
    @unpack
    def test_team_calculation(self, match_id, stage, comp, calc_id):
        url = ADDRESS + API_PREFIX + f'/data/match/team/{match_id}/{calc_id}'
        params = {
            "comp": comp,
            "stage": stage,
        }
        delay()
        response = requests.get(url, headers=HEADERS, params=params)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(test_output(response.json()))
