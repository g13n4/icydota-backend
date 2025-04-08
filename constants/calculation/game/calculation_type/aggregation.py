import numpy as np


class TotalAggregationMethod:
    MIN = 1
    AVG = 2
    MAX = 3
    SUM = 4

    FUNCTION_MAP: dict


TotalAggregationMethod.FUNCTION_MAP = {
    TotalAggregationMethod.MIN: np.min,
    TotalAggregationMethod.AVG: np.nanmean,
    TotalAggregationMethod.MAX: np.max,
    TotalAggregationMethod.SUM: np.sum,
}
