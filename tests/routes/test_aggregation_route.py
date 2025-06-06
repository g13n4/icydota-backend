import unittest
from itertools import product

import requests
from ddt import ddt, idata, unpack

from constants.api import GameStageEnum, ComparisonEnum, LoPEnum
from helpers import HEADERS, API_PREFIX, ADDRESS, test_output, delay
from utils.helpers import get_enum_values


# TEST DATA
LoP = [(LoPEnum.league.value, 18111), (LoPEnum.patch.value, 57), (LoPEnum.patch.value, 58)]
DEFAULT_CALC_ID = 101

player_iterator = product(
    LoP,
    [0, DEFAULT_CALC_ID],
    range(1, 9),
    get_enum_values(GameStageEnum),
    get_enum_values(ComparisonEnum),
)

team_iterator = product(
    LoP,
    [0, DEFAULT_CALC_ID],
    get_enum_values(GameStageEnum),
    get_enum_values(ComparisonEnum),
)


@ddt
class AggregationRouteTest(unittest.TestCase):
    @idata(player_iterator)
    @unpack
    def test_player_agg(self, lop_tuple, calc_id, atype, stage, comp):
        lop, lop_id = lop_tuple
        url = ADDRESS + API_PREFIX + f'/data/aggregation/player/{lop}/{lop_id}/{calc_id}'
        params = { "comp": comp, "stage": stage, "atype": atype }
        delay()
        response = requests.get(url, headers=HEADERS, params=params)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(test_output(response.json()))


    @idata(team_iterator)
    @unpack
    def test_team_agg(self, lop_tuple, calc_id, stage, comp):
        lop, lop_id = lop_tuple
        url = ADDRESS + API_PREFIX + f'/data/aggregation/team/{lop}/{lop_id}/{calc_id}'
        params = { "comp": comp, "stage": stage }
        delay()
        response = requests.get(url, headers=HEADERS, params=params)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(test_output(response.json()))
