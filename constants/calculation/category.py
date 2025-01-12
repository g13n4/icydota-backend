from constants.helpers import Item, update_values, get_only_names, GetItemHelper


@update_values
class WindowCategories(GetItemHelper):
    INTERVAL: Item = Item(value=1)
    PINGS: Item = Item(value=2)
    DAMAGE: Item = Item(value=3)
    WARDS: Item = Item(value=4)
    DEWARD: Item = Item(value=5)
    XP: Item = Item(value=6, description='XP')
    GOLD: Item = Item(value=7)

    VALUES: list = [INTERVAL, PINGS, DAMAGE, WARDS, DEWARD, XP, GOLD]
    VALUES_NAMES: list = get_only_names(VALUES)
