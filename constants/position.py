from constants.helpers import Item, update_description


@update_description
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

    POSITION_TO_NAME: dict = { pos.value: pos.name for pos in POSITIONS }


POSITION_OPPONENTS: dict = {
    PositionConstant.CARRY.value: [
        PositionConstant.CARRY.value,
        PositionConstant.OFFLANE.value
    ],
    PositionConstant.MIDDLE.value: [
        PositionConstant.MIDDLE.value,
    ],
    PositionConstant.OFFLANE.value: [
        PositionConstant.CARRY.value,
        PositionConstant.OFFLANE.value,
    ],
    PositionConstant.SOFT_SUPPORT.value: [
        PositionConstant.SOFT_SUPPORT.value,
        PositionConstant.HARD_SUPPORT.value,
    ],
    PositionConstant.HARD_SUPPORT.value: [
        PositionConstant.SOFT_SUPPORT.value,
        PositionConstant.HARD_SUPPORT.value,
    ],
}
