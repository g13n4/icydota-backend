
from constants.helpers import Item, update_values


@to_nested_constant
class GamePerformanceConstant:
    MATCH_DATA: int = 1
    MATCH_DATA_COMPARISON: int = 2
    AGGREGATION: int = 3
    AGGREGATION_COMPARISON: int = 4
    COMBINED_AGGREGATION: int = 5
    COMBINED_AGGREGATION_COMPARISON: int = 6
    CROSS_COMPARISON: int = 7


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


# POSITION
@update_values
class PositionConstant:
    CARRY: Item = Item(value=1, )
    MIDDLE: Item = Item(value=2, )
    OFFLANE: Item = Item(value=3, )
    SOFT_SUPPORT: Item = Item(value=4, )
    HARD_SUPPORT: Item = Item(value=5, )

    POSITIONS: list[Item] = [
        CARRY,
        MIDDLE,
        OFFLANE,
        SOFT_SUPPORT,
        HARD_SUPPORT,
    ]

    OPPONENTS: dict = {
        CARRY.value: [CARRY.value, OFFLANE.value],
        MIDDLE.value: [MIDDLE.value],
        OFFLANE.value: [CARRY.value, OFFLANE.value],
        SOFT_SUPPORT.value: [SOFT_SUPPORT.value, HARD_SUPPORT.value],
        HARD_SUPPORT.value: [SOFT_SUPPORT.value, HARD_SUPPORT.value],
    }

    POS_TO_NAME: dict = {pos.value: pos.name for pos in POSITIONS}


# BUILDING
@update_values
class MapLane:
    BASE: Item = Item(value=0, )
    BOTTOM: Item = Item(value=1, )
    MIDDLE: Item = Item(value=2, )
    TOP: Item = Item(value=3, )

    LANES: list = [BASE, BOTTOM, MIDDLE, TOP]
    REAL_LANES: list = [BOTTOM, MIDDLE, TOP]


@update_values
class TowerTier:
    TIER_ONE: Item = Item(value=1, description="Tier 1")
    TIER_TWO: Item = Item(value=2, description="Tier 2")
    TIER_THREE: Item = Item(value=3, description="Tier 3")
    TIER_FOUR: Item = Item(value=4, description="Tier 4")

    TIERS: list = [TIER_ONE, TIER_TWO, TIER_THREE, TIER_FOUR]


@update_values
class BuildingTypeConstant:
    IS_MELEE: Item = Item(value=True, )
    IS_NOT_MELEE: Item = Item(value=False, )

    IS_RAX: Item = Item(value=True, )
    IS_NOT_RAX: Item = Item(value=False, )


class BuildingConstant(MapLane, TowerTier, BuildingTypeConstant):
    pass
