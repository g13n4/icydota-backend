from itertools import zip_longest
from typing import Any
from typing import Iterable

from utils.helpers import is_invalid_value, to_bin_list


class EmptyMaskConverter:
    NONE_VALUE = 1
    ZERO_VALUE = 0
    MAP = {
        1: None,
        0: 0,
    }

    @staticmethod
    def iter_to_mask(data: Iterable) -> int | None:
        """
        Transforms iterable to an integer whose binary number is a mask for a calculation slice
        """
        value_map = []
        for value in data:
            if is_invalid_value(value):
                value_map.append(EmptyMaskConverter.NONE_VALUE)
            elif value == 0:
                value_map.append(EmptyMaskConverter.ZERO_VALUE)
            else:
                return None

        return int(''.join(map(str, value_map)), base=2)


    @staticmethod
    def mask_to_dict(mask: int, windows: list[str]) -> dict:
        output = dict()
        for value, field in zip_longest(to_bin_list(mask, len(windows)), windows[::-1]):
            output[field] = EmptyMaskConverter.MAP.get(value, None)
        return output
