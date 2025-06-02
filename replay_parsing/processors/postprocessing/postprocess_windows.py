from constants.calculation.game.calculation_type.interval import IntervalCalculationColumn, \
    IntervalCalculationAggregationMethod
from constants.calculation.game.calculation_types import WindowCalculations
from modules.performance_data_processor import PerformanceDataProcessor


def postprocess_windows(
        PDP: PerformanceDataProcessor,
) -> None:
    for window in WindowCalculations.VALUES(only_calculated_later=True):
        for slot in range(10):
            window_data = PDP.windows_data[slot]

            col, method = window.processing
            match (col, method):
                case (IntervalCalculationColumn.MOVEMENT_UNIQUE, IntervalCalculationAggregationMethod.COEFF):
                    movement_slice = window_data[WindowCalculations.movement__sum.index, :]
                    unique_slice = window_data[WindowCalculations.movement__unique__tiles__sum.index, :]

                    PDP.set_slice(slot, WindowCalculations.movement__unique__coeff, unique_slice / movement_slice)
