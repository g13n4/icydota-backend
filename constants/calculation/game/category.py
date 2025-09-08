from constants.helpers import Item, update_description, get_only_names, GetItemHelper


@update_description
class WindowCategories(GetItemHelper):
    INTERVAL: Item = Item(
        value=1,
        name="In-game windows data",
        description="Data that is collected by Dota 2 client and is shown to spectators or after the game."
        )
    PINGS: Item = Item(value=2, name="Pings", description="Data regarding players pings")
    DAMAGE: Item = Item(value=3, name="Damage", description="Data regarding hero damage. Both received and dealt")
    WARDS: Item = Item(value=4, name="Wards", description="Data regarding wards placed")
    DEWARD: Item = Item(value=5, name="Deward", description="Data regarding dewarding")
    XP: Item = Item(value=6, name="XP", description="Data regarding experience acquisition")
    GOLD: Item = Item(value=7, name="Gold", description="Data regarding gold acquisition")

    VALUES: list = [INTERVAL, PINGS, DAMAGE, WARDS, DEWARD, XP, GOLD]
    VALUES_NAMES: list = get_only_names(VALUES)
