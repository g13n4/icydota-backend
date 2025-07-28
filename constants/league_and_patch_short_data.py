from pydantic import condecimal

from constants.helpers import Item, update_description


@update_description
class LeaguePatchShortDataConstant:
    first_pick_win: Item = Item(
        value=1,
        description="First pick win rate",
        type_=condecimal(max_digits=3, decimal_places=2)
        )
    last_pick_win: Item = Item(
        value=2,
        description="Last pick win rate",
        type_=condecimal(max_digits=3, decimal_places=2)
        )

    win_sent: Item = Item(value=3, description="Sentinel win rate", type_=condecimal(max_digits=3, decimal_places=2))
    win_dire: Item = Item(value=4, description="Dire win rate", type_=condecimal(max_digits=3, decimal_places=2))

    net_worth: Item = Item(value=5, description="Networth", type_=condecimal(max_digits=8, decimal_places=2))
    hero_kills: Item = Item(value=6, description="Kills", type_=condecimal(max_digits=3, decimal_places=1))

    last_hits: Item = Item(value=7, description="Last hits", type_=condecimal(max_digits=5, decimal_places=1))
    kpm: Item = Item(value=8, description="Kills per minute", type_=condecimal(max_digits=3, decimal_places=2))

    matches: Item = Item(value=9, description="Matches", type_=int)
    duration: Item = Item(value=10, description="Match length", type_=int)

    cores_networth_at_15: Item = Item(
        value=11,
        description="Cores networth at 15",
        type_=condecimal(max_digits=7, decimal_places=1)
    )
    supports_networth_at_15: Item = Item(
        value=12,
        description="Supports networth at 15",
        type_=condecimal(max_digits=7, decimal_places=1)
    )

    cores_level_at_15: Item = Item(
        value=13,
        description="Cores level at 15",
        type_=condecimal(max_digits=3, decimal_places=1)
    )
    supports_level_at_15: Item = Item(
        value=14,
        description="Supports level at 15",
        type_=condecimal(max_digits=3, decimal_places=1)
    )

    VALUES: list[Item] = [
        first_pick_win,
        last_pick_win,

        win_sent,
        win_dire,

        net_worth,
        hero_kills,

        last_hits,
        kpm,

        matches,
        duration,

        cores_networth_at_15,
        supports_networth_at_15,

        cores_level_at_15,
        supports_level_at_15,
    ]
