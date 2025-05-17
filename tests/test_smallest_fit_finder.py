import unittest

from modules.smallest_fit_finder import SmallestFitFinder


MOCK_DATA_ONE = [1, 3, 5, 7, 9, 15, 11, 13]
MOCK_FIT_ONE = [
    (2, 1),
    (4, 3),
    (5, 5),
    (13, 13),
]

MOCK_DATA_TWO = [100, 200, 300, 400, 500]
MOCK_DATA_TWO_EXTEND = [50, 150, 250, 350, 450, 550]
MOCK_FIT_TWO = [
    (51, 50),
    (200, 200),
    (210, 200),
    (600, 550),
    (10000, 550),
    (50, 50),
]

MOCK_DATA_THREE = [0, 2, 4, 6, 8]


class SmallestFitFinderTest(unittest.TestCase):
    def test_data_one(self):
        SFF = SmallestFitFinder(MOCK_DATA_ONE)
        for value, correct_fit in MOCK_FIT_ONE:
            fit = SFF.find(value)
            self.assertEqual(fit, correct_fit)


    def test_data_two(self):
        SFF = SmallestFitFinder(MOCK_DATA_TWO)
        SFF.extend(MOCK_DATA_TWO_EXTEND)
        for value, correct_fit in MOCK_FIT_TWO:
            fit = SFF.find(value)
            self.assertEqual(fit, correct_fit)


    def test_data_three(self):
        SFF = SmallestFitFinder(MOCK_DATA_THREE)
        self.assertRaises(ValueError, SFF.find, -1)
