class CrossComparisonTypeConstant:
    POSITION_PLAYER = 1
    POSITION_HERO = 2
    POSITION_HERO_FACET = 3

    VALUES: list[int] = [
        POSITION_PLAYER,
        POSITION_HERO,
        POSITION_HERO_FACET,
    ]


class CrossComparisonPositionConstant:
    SUPPORT: int = 1
    CARRY: int = 2
    MIDDLE: int = 3

    VALUES: list[int] = [
        SUPPORT,
        CARRY,
        MIDDLE,
    ]


class CrossComparisonConstant:
    type_: CrossComparisonTypeConstant = CrossComparisonTypeConstant
    position: CrossComparisonPositionConstant = CrossComparisonPositionConstant
