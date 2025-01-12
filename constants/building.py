from constants.helpers import Item, update_values


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
