from decimal import Decimal
from typing import List, Any, Optional
from models import PerformanceWindowData
from api_helpers.model_field_info import LANE_FIELDS, GAME_FIELDS
from typing import TypeVar

T = TypeVar('T', dict, PerformanceWindowData)

class PerformanceMaskHandler:
    """
    Helper class that is used to code and decode an "*_mask_empty" field in PerformanceWindow objects.
    0 represents 0 and 1 represents None. We replace zeroes with None to save space due to zero being a double
    precision value in the DB and None takes only 1 byte
    """
    def __init__(self):
        self.lane_fields = LANE_FIELDS
        self.game_fields = GAME_FIELDS

        self.lane_length = len(LANE_FIELDS)
        self.game_length = len(GAME_FIELDS)

        self.field_index = {field: idx for idx, field in enumerate(LANE_FIELDS)}
        self.field_index.update({field: idx for idx, field in enumerate(GAME_FIELDS)})

        self.EMPTY_TOKEN = ''
        self.NONE_TOKEN = ''


    @staticmethod
    def _set_value(obj: T, field_name: str, value: Any, is_model: bool):
        if is_model:
            setattr(obj, field_name, value)
        else:
            obj[field_name] = value


    @staticmethod
    def _get_value(obj: T, field_name: str, is_model: bool) -> None | Decimal:
        if is_model:
            return getattr(obj, field_name)
        else:
            return obj[field_name]


    @staticmethod
    def convert_to_mask(empty_fields: List[int]) -> int:
        """Turn a list of integers into a mask"""
        return int(''.join(map(str, empty_fields)), 2)


    @staticmethod
    def convert_from_mask(numeric_mask: int, length: int) -> list[int]:
        """Turn a small integer into a list of integers:
        first: turn it into a binary number and then into a list
        second: remove 'b' - binary and '0' - signed/unsigned bit
        third: turn it into integers and get a slice from the beginning to the number of fields (length)
        """
        coded_values = list(map(int, list(bin(numeric_mask))[2:]))[:length]
        return ([0] * (length - len(coded_values))) + coded_values


    def set_empty_status(self, data: T) -> None:
        is_model = not isinstance(data, dict)

        for fields, f_len, empty_field in [(self.lane_fields, self.lane_length, 'l_empty_mask'),
                                           (self.game_fields, self.game_length, 'g_empty_mask')]:
            empty_code = [0] * f_len
            only_nones = True
            can_be_compressed = True

            for idx, field in enumerate(fields):
                this_value = self._get_value(data, field, is_model)

                if 0.000001 > this_value > -0.000001:
                    empty_code[idx] = 1
                    only_nones = False

                elif this_value is not None:
                    can_be_compressed = False
                    break

            if not can_be_compressed or not only_nones:
                continue

            for field in fields:
                self._set_value(data, field, None, is_model)

            empty_mask = self.convert_to_mask(empty_code)
            self._set_value(data, field_name=empty_field, value=empty_mask, is_model=is_model)
        return None


    def unpack_w_empty_status(self, data: T, exclude: List[str] = None) -> dict:
        if exclude is None:
            exclude = []

        is_model = not isinstance(data, dict)
        if is_model:
            data = data.dict()


        for fields, f_len, empty_field in [(self.lane_fields, self.lane_length, 'l_empty_mask'),
                                           (self.game_fields, self.game_length, 'g_empty_mask')]:

            if not (empty_field_mask := data[empty_field]):
                break

            converted_mask = self.convert_from_mask(empty_field_mask, f_len)

            for field, masked_value in zip(fields, converted_mask):
                if masked_value == 1:
                    data[field] = 0
                else:
                    data[field] = None

        return {k: v for k, v in data.items() if k not in exclude}


    def check_if_empty(self, field_value: Optional[Decimal], field_name: str, empty_mask: Optional[int]):
        if empty_mask is None:
            return field_value


        field_number = self.field_index[field_name]
        return
