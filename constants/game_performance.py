from constants.helpers import to_nested_constant


@to_nested_constant
class GamePerformanceConstant:
    MATCH_DATA: int = 1
    MATCH_DATA_COMPARISON: int = 2

    AGGREGATION: int = 3
    AGGREGATION_COMPARISON: int = 4

    COMBINED_AGGREGATION: int = 5
    COMBINED_AGGREGATION_COMPARISON: int = 6

    CROSS_COMPARISON: int = 7
