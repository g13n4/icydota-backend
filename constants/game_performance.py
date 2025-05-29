class GamePerformanceTypeConstant:
    MATCH_DATA: int = 101
    MATCH_DATA_COMPARISON: int = 102

    AGGREGATION: int = 103
    AGGREGATION_COMPARISON: int = 104

    # MADE USING NORMAL DATA
    CROSS_COMPARISON: int = 105
    # MADE USING COMPARISON DATA


class TeamPerformanceConstant:
    """Data aggregated by team"""
    TEAM_MATCH_DATA: int = 201
    TEAM_MATCH_DATA_COMPARISON: int = 202

    TEAM_MATCH_AGGREGATION: int = 203
    TEAM_MATCH_AGGREGATION_COMPARISON: int = 204

    TEAM_MATCH_CROSS_COMPARISON: int = 205


class AbilitiesPerformanceTypeConstant:
    MATCH_DATA: int = 301
    AGGREGATION: int = 302
    CROSS_COMPARISON: int = 303


class PerformanceTypeConstant:
    ability: [AbilitiesPerformanceTypeConstant] = AbilitiesPerformanceTypeConstant
    game: [GamePerformanceTypeConstant] = GamePerformanceTypeConstant
    team: [TeamPerformanceConstant] = TeamPerformanceConstant
