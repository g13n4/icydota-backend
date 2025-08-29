from constants.helpers import Item, update_description, get_only_names, GetItemHelper


@update_description
class GameTotalsCategory(GetItemHelper):
    GENERAL: Item = Item(
        value=1,
        name="General data",
        description="General performance data",
        )
    FIRST_KILL_DEATH: Item = Item(
        value=2,
        name="First kill and death",
        description="Data regarding first kill, death and time of the event",
    )
    T1_TOWERS: Item = Item(
        value=3,
        name="First T3 towers",
        description="Data regarding towers, lanes and time of the event",
    )
    T3_TOWERS_AND_LANES: Item = Item(
        value=4,
        name="Towers and lanes",
        description="Data regarding T3 towers and barracks",
    )
    STATS: Item = Item(value=5, name="Stats", description="Statistical game data")
    PICKS: Item = Item(value=6, name="Picks", description="Data regarding game picks")


    VALUES: list = [GENERAL, FIRST_KILL_DEATH, T1_TOWERS, T3_TOWERS_AND_LANES, STATS, PICKS]
    VALUES_NAMES: list = get_only_names(VALUES)
