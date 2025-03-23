class CrossComparisonTypeConstant:
    POSITION_PLAYER = 1
    POSITION_HERO = 2
    POSITION_HERO_FACET = 3


class CrossComparisonPositionConstant:
    SUPPORT: int = 1
    CARRY: int = 2
    MIDDLE: int = 3


class CrossComparisonConstant:
    type_: CrossComparisonTypeConstant = CrossComparisonTypeConstant
    position: CrossComparisonPositionConstant = CrossComparisonPositionConstant
