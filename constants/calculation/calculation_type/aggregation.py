from enum import Enum
import numpy as np


class TotalAggregationMethod(Enum):
    MIN = 1
    AVG = 2
    MAX = 3
    SUM = 4

    FUNCTION_MAP: dict


TotalAggregationMethod.FUNCTION_MAP = {
    variant: func_ for enum_var, func_ in [
        (TotalAggregationMethod.MIN, np.min),
        (TotalAggregationMethod.AVG, np.nanmean),
        (TotalAggregationMethod.MAX, np.max),
        (TotalAggregationMethod.SUM, np.sum),
    ]
    for variant in [enum_var, enum_var.value]
}
