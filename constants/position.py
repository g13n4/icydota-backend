from constants.helpers import Item, update_values


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
