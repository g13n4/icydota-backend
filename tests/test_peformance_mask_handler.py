from replay_parsing import PerformanceMaskHandler

import unittest


MOCK_DATA_ONE = (
    [0, 0, 0, 0, 1, 1, 0],
    6
)

MOCK_DATA_TWO = (
    [1, 1, 1, 1, 1, 1, 1, 1],
    255
)


MOCK_DATA_THREE = (
    [1, 1, 1, 1, 1, 1,],
    63
)


PMH = PerformanceMaskHandler()

class PerformanceMaskHandlerTest(unittest.TestCase):
    def test_data_one(self):
        empty_fields, integer = MOCK_DATA_ONE
        mask_integer = PMH.convert_to_mask(empty_fields)
        self.assertEqual(mask_integer, integer)

        mask_list = PMH.convert_from_mask(integer, len(empty_fields))
        self.assertListEqual(mask_list, empty_fields)

    def test_data_two(self):
        empty_fields, integer = MOCK_DATA_TWO
        mask_integer = PMH.convert_to_mask(empty_fields)
        self.assertEqual(mask_integer, integer)

        mask_list = PMH.convert_from_mask(integer, len(empty_fields))
        self.assertListEqual(mask_list, empty_fields)


    def test_data_three(self):
        empty_fields, integer = MOCK_DATA_THREE
        mask_integer = PMH.convert_to_mask(empty_fields)
        self.assertEqual(mask_integer, integer)

        mask_list = PMH.convert_from_mask(integer, len(empty_fields))
        self.assertListEqual(mask_list, empty_fields)

