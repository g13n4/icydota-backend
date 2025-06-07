from collections.abc import Iterable
from decimal import Decimal
from itertools import zip_longest

from utils.helpers import is_invalid_value


class EmptyMaskConverter:
    NONE_VALUE = 1
    ZERO_VALUE = 0
    MAP = {
        1: None,
        0: 0,

        "1": None,
        "0": 0,
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
            elif isinstance(value, float | int | Decimal) and not value:
                value_map.append(EmptyMaskConverter.ZERO_VALUE)
            else:
                return None

        return int(''.join(map(str, value_map)), base=2)


    @staticmethod
    def value_to_bin_list(value: int, size: int) -> str:
        full_binary_string = bin(value)
        _, binary_string = full_binary_string.split('b')  # remove 0b prefix
        pad = "0" * (size - len(binary_string))
        return pad + binary_string


    @staticmethod
    def mask_to_dict(mask: int, windows: list[str]) -> dict:
        output = dict()
        for value, field in zip_longest(EmptyMaskConverter.value_to_bin_list(mask, len(windows)), windows):
            output[field] = EmptyMaskConverter.MAP[value]
        return output

    @staticmethod
    def extract_from_mask(mask: int, index: int, from_end: bool = True) -> None | int:
        binary_string = bin(mask)

        if from_end:
            value = binary_string[-index]
        else:
            value = binary_string[index]

        return EmptyMaskConverter.MAP[value]
