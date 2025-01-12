from decimal import Decimal
from typing import Any, List, Optional, TypeVar

from models import PerformanceWindowTable
from modules.empty_mask_converter import EmptyMaskConverter


T = TypeVar("T", dict, PerformanceWindowTable)


class PerformanceMaskHandler(EmptyMaskConverter):
    """
    Helper class that is used to code and decode an "*_mask_empty" field in PerformanceWindow objects.
    0 represents 0 and 1 represents None. We replace zeroes with None to save space due to zero being a double
    precision value in the DB and None takes only 1 byte
    """

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

    def set_empty_status(self, data: T) -> None:
        is_model = not isinstance(data, dict)

        for fields, f_len, empty_field in [
            (self.lane_fields, self.lane_length, "l_empty_mask"),
            (self.game_fields, self.game_length, "g_empty_mask"),
        ]:
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
            self._set_value(
                data, field_name=empty_field, value=empty_mask, is_model=is_model
            )
        return None

    def unpack_w_empty_status(self, data: T, exclude: List[str] = None) -> dict:
        if exclude is None:
            exclude = []

        is_model = not isinstance(data, dict)
        if is_model:
            data = data.model_dump()

        for fields, f_len, empty_field in [
            (self.lane_fields, self.lane_length, "l_empty_mask"),
            (self.game_fields, self.game_length, "g_empty_mask"),
        ]:
            if not (empty_field_mask := data[empty_field]):
                break

            converted_mask = self.convert_from_mask(empty_field_mask, f_len)

            for field, masked_value in zip(fields, converted_mask):
                if masked_value == 1:
                    data[field] = 0
                else:
                    data[field] = None

        return {k: v for k, v in data.items() if k not in exclude}

    def check_if_empty(
        self, field_value: Optional[Decimal], field_name: str, empty_mask: Optional[int]
    ):
        if empty_mask is None:
            return field_value

        field_number = self.field_index[field_name]
        return
