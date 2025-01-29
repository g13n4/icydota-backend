from itertools import zip_longest
from typing import Any
from typing import Iterable

from utils.helpers import is_invalid_value, to_bin_list


class EmptyMaskConverterNew:
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
                value_map.append(EmptyMaskConverterNew.NONE_VALUE)
            elif value == 0:
                value_map.append(EmptyMaskConverterNew.ZERO_VALUE)
            else:
                return None

        return int(''.join(map(str, value_map)), base=2)


    @staticmethod
    def mask_to_list(mask: int, windows: list[str]) -> dict:
        output = dict()
        for value, field in zip_longest(to_bin_list(mask), windows[::-1]):
            output[field] = EmptyMaskConverterNew.MAP.get(value, None)
        return output


class EmptyMaskConverter:
    NONE_VALUE = 1
    ZERO_VALUE = 0


    @staticmethod
    def can_be_converted(fields: list[Any]) -> bool:
        return not any(fields)


    @staticmethod
    def mask_value_converter(value: int) -> int | None:
        return None if value == EmptyMaskConverter.NONE_VALUE else value


    @staticmethod
    def convert_to_mask(empty_fields: list[int]) -> int:
        """Turn a list of integers into a mask"""
        return int("".join(map(str, empty_fields)), 2)


    @staticmethod
    def convert_from_mask(numeric_mask: int, length: int) -> list[int]:
        """Turn a small integer into a list of integers:
        first: turn it into a binary number and then into a list
        second: remove 'b' - binary and '0' - signed/unsigned bit
        third: turn it into integers and get a slice from the beginning to the number of fields (length)
        """
        coded_values = list(map(int, list(bin(numeric_mask))[2:]))[:length]
        return ([0] * (length - len(coded_values))) + coded_values


    @staticmethod
    def convert_from_mask_to_dict(numeric_mask: int, keys: list[int | str]) -> dict[int | str, int | None]:
        """Turn a small integer into a dictionary"""

        mask_values = EmptyMaskConverter.convert_from_mask(numeric_mask, len(keys))
        return {
            key: EmptyMaskConverter.mask_value_converter(value)
            for key, value in zip(keys, mask_values)
        }
