from constants.helpers import Item, update_description, get_only_names, GetItemHelper


@update_description
class WindowCategories(GetItemHelper):
    GENERAL: Item = Item(
        value=1,
        name="General data",
        description="General performance data.",
        )
    FIRST_KILL_DEATH: Item = Item(
        value=2,
        name="First kill and death",
        description="Data regarding first kill, death and time of the event",
    )
    TOWERS_LANES: Item = Item(
        value=3,
        name="Towers and lanes",
        description="Data regarding towers, lanes and time of the event",
    )
    STATS: Item = Item(value=4, name="Stats", description="Statistical game data")
    PICKS: Item = Item(value=5, name="Picks", description="Data regarding game picks")


    VALUES: list = [GENERAL, FIRST_KILL_DEATH, TOWERS_LANES, STATS, PICKS]
    VALUES_NAMES: list = get_only_names(VALUES)
