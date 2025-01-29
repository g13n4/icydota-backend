from typing import Generator

import numpy as np

from constants.calculation.calculation_types import WindowCalculations
from constants.performance.window import GameWindows
from models import PerformanceWindowData, PerformanceWindowTable
from modules.constants import OFFSET
from modules.empty_mask_converter import EmptyMaskConverterNew


class WindowsPerformanceProcessor:

    @staticmethod
    def _get_pwd_from_calculation(data_slice: np.ndarray, calculation_id: int) -> PerformanceWindowData:
        PWT_data = dict()
        PWD_obj = PerformanceWindowData(data_calculation_id=calculation_id)
        for windows_fields, empty_mask_name in GameWindows.EMPTY_MASK_WINDOWS_MAP:

            calculation_window_data = dict()
            for window_field in windows_fields:
                calculation_window_data[window_field.name] = data_slice[window_field.index - OFFSET]

            empty_mask = EmptyMaskConverterNew.iter_to_mask(calculation_window_data.values())
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
            yield WindowsPerformanceProcessor._get_pwd_from_calculation(calculation_slice, window.index)


    @staticmethod
    def comparison_data_to_pwds(cmd_data: np.ndarray, cms_data: np.ndarray, flat: bool) -> Generator[PerformanceWindowData]:

        if flat:
            data = np.subtract(cmd_data, cms_data)
        else:
            data = np.divide(cmd_data, cms_data)

        for PWD_obj in WindowsPerformanceProcessor.data_to_pwds(data):
            yield PWD_obj
