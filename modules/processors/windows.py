from typing import Generator

import numpy as np

from constants.calculation.game.calculation_types import WindowCalculations
from constants.performance.window import AllWindows
from models.performance import PerformanceWindowData, PerformanceWindowTable
from modules.constants import OFFSET
from modules.empty_mask_converter import EmptyMaskConverter
from utils import to_dec


class WindowsPerformanceProcessor:

    @staticmethod
    def get_pwd_from_iterable(
            data_iterable: np.ndarray | dict,
            calculation_id: int,
            to_decimal: bool = False,
    ) -> PerformanceWindowData:
        PWT_data = dict()
        PWD_obj = PerformanceWindowData(data_calculation_id=calculation_id)
        for windows_fields, empty_mask_name in AllWindows.EMPTY_MASK_WINDOWS_MAP:

            calculation_window_data = dict()
            for window_field in windows_fields:
                if isinstance(data_iterable, dict):
                    value =  data_iterable[window_field.name]
                else:
                    value = data_iterable[window_field.index - OFFSET]

                if to_decimal:
                    value = to_dec(value)

                calculation_window_data[window_field.name] = value

            empty_mask = EmptyMaskConverter.iter_to_mask(calculation_window_data.values())
            setattr(PWD_obj, empty_mask_name, empty_mask)
            if empty_mask is None:
                PWT_data.update(calculation_window_data)

        if PWT_data:
            PWT_obj = PerformanceWindowTable(**PWT_data)
            PWD_obj.performance_table = PWT_obj

        return PWD_obj


    @staticmethod
    def data_to_pwds(player_data_matrix: np.array) -> Generator[PerformanceWindowData]:
        """
        Transforms saved windows_data into windows one line at a time
        """
        for window in WindowCalculations.VALUES:
            window_idx = window.index - OFFSET
            calculation_slice = player_data_matrix[window_idx, :]
            yield WindowsPerformanceProcessor.get_pwd_from_iterable(calculation_slice, window.index)


    @staticmethod
    def comparison_data_to_pwds(cmd_data: np.ndarray, cms_data: np.ndarray, flat: bool) -> Generator[PerformanceWindowData]:

        if flat:
            data = np.subtract(cmd_data, cms_data)
        else:
            data = np.divide(cmd_data, cms_data)

        for PWD_obj in WindowsPerformanceProcessor.data_to_pwds(data):
            yield PWD_obj
