from constants.helpers import to_nested_constant


@to_nested_constant
class PerformanceRankingConstant:
    PLAYER_MATCH_RANK: int = 1
    PLAYER_MATCH_BEST_RANK: int = 2
    PLAYER_MATCH_AVG_RANK: int = 3
    PLAYER_MATCH_COMPARISON_RANK: int = 4
    PLAYER_MATCH_COMPARISON_BEST_RANK: int = 5
    PLAYER_MATCH_COMPARISON_AVG_RANK: int = 6

    HERO_MATCH_RANK: int = 7
    HERO_MATCH_BEST_RANK: int = 8
    HERO_MATCH_AVG_RANK: int = 9
    HERO_MATCH_COMPARISON_RANK: int = 10
    HERO_MATCH_COMPARISON_BEST_RANK: int = 11

    TEAM_RANK: int = 12
    TEAM_BEST_RANK: int = 13

    LEAGUE_RANK: int = 14
    LEAGUE_BEST_RANK: int = 15

    PLAYER_AGGREGATED_RANK: int = 16
    HERO_AGGREGATED_RANK: int = 17

    PLAYER_AGGREGATED_COMPARISON_RANK: int = 18
    HERO_AGGREGATED_COMPARISON_RANK: int = 19
