class GamePerformanceTypeConstant:
    MATCH_DATA: int = 101
    MATCH_DATA_COMPARISON: int = 102

    AGGREGATION: int = 103
    AGGREGATION_COMPARISON: int = 104

    # MADE USING NORMAL DATA
    CROSS_COMPARISON: int = 105
    # MADE USING COMPARISON DATA
    CROSS_COMPARISON_COMPARISON: int = 106


class AbilitiesPerformanceTypeConstant:
    MATCH_DATA: int = 201
    AGGREGATION: int = 202
    CROSS_COMPARISON: int = 203


class PerformanceTypeConstant:
    ability: [AbilitiesPerformanceTypeConstant] = AbilitiesPerformanceTypeConstant
    game: [GamePerformanceTypeConstant] = GamePerformanceTypeConstant
