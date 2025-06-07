import unittest
from itertools import product

import requests
from ddt import ddt, idata, unpack

from constants.api import ComparisonEnum, LoPEnum
from helpers import HEADERS, API_PREFIX, ADDRESS, test_output, delay


# TEST DATA
LoP = [(LoPEnum.league.value, 18111), (LoPEnum.patch.value, 57), (LoPEnum.patch.value, 58)]
DEFAULT_CALC_ID = 101

player_iterator = product(
    LoP,
    [(0, "kda"), (DEFAULT_CALC_ID, "l2"), ],
    range(1, 4),
    range(1, 4),
    [ComparisonEnum.flat.value, ComparisonEnum.perc.value, ],
)

team_iterator = product(
    LoP,
    [(0, "kda"), (DEFAULT_CALC_ID, "l2"), ],
    [ComparisonEnum.flat.value, ComparisonEnum.perc.value, ],
)


@ddt
class CrossComparisonRouteTest(unittest.TestCase):
    @idata(player_iterator)
    @unpack
    def test_player_ccomparison(self, lop_tuple, field_tuple, atype, position, comp):
        lop, lop_id = lop_tuple
        data_type, field = field_tuple
        url = ADDRESS + API_PREFIX + f'/data/cross_comparison/player/{lop}/{lop_id}/{data_type}'
        params = { "comp": comp, "field": field, "atype": atype, "position": position }
        delay()
        response = requests.get(url, headers=HEADERS, params=params)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(test_output(response.json()))


    @idata(team_iterator)
    @unpack
    def test_team_ccomparison(self, lop_tuple, field_tuple, comp):
        lop, lop_id = lop_tuple
        data_type, field = field_tuple
        url = ADDRESS + API_PREFIX + f'/data/cross_comparison/team/{lop}/{lop_id}/{data_type}'
        params = { "comp": comp, "field": field }
        delay()
        response = requests.get(url, headers=HEADERS, params=params)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(test_output(response.json()))
