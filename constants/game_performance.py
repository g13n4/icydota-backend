class GamePerformanceTypeConstant:
    MATCH_DATA: int = 101
    MATCH_DATA_COMPARISON: int = 102

    AGGREGATION: int = 203
    AGGREGATION_COMPARISON: int = 204

    # MADE USING NORMAL DATA
    CROSS_COMPARISON: int = 305
    # MADE USING COMPARISON DATA


class AbilitiesPerformanceTypeConstant:
    MATCH_DATA: int = 1001
    AGGREGATION: int = 1002
    CROSS_COMPARISON: int = 1003


class PerformanceTypeConstant:
    ability: [AbilitiesPerformanceTypeConstant] = AbilitiesPerformanceTypeConstant
    game: [GamePerformanceTypeConstant] = GamePerformanceTypeConstant
