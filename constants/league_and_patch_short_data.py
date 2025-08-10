from typing import Any
from pydantic import condecimal, BaseModel, ConfigDict
from constants.helpers import update_description


class LOPShortDataValueFormat:
    RAW = 1
    PERCENT = 2
    LEVEL = 3


class LOPShortDataItem(BaseModel):
    model_config = ConfigDict(slots=True)

    value: int
    name: str = ''
    description: str = ''
    type_: Any = None
    is_comparable: bool = True
    value_format: int = LOPShortDataValueFormat.RAW


@update_description(default_class=LOPShortDataItem)
class LeaguePatchShortDataConstant:
    first_pick_win: LOPShortDataItem = LOPShortDataItem(
        value=1,
        description="First pick win rate",
        type_=condecimal(max_digits=3, decimal_places=2),
        value_format=LOPShortDataValueFormat.PERCENT,
    )
    last_pick_win: LOPShortDataItem = LOPShortDataItem(
        value=2,
        description="Last pick win rate",
        type_=condecimal(max_digits=3, decimal_places=2),
        value_format=LOPShortDataValueFormat.PERCENT,
    )

    win_sent: LOPShortDataItem = LOPShortDataItem(
        value=3,
        description="Sentinel win rate",
        type_=condecimal(max_digits=3, decimal_places=2),
        value_format=LOPShortDataValueFormat.PERCENT
    )
    win_dire: LOPShortDataItem = LOPShortDataItem(
        value=4,
        description="Dire win rate",
        type_=condecimal(max_digits=3, decimal_places=2),
        value_format=LOPShortDataValueFormat.PERCENT
    )

    net_worth: LOPShortDataItem = LOPShortDataItem(
        value=5,
        description="Networth",
        type_=condecimal(max_digits=8, decimal_places=2)
    )
    hero_kills: LOPShortDataItem = LOPShortDataItem(
        value=6,
        description="Kills",
        type_=condecimal(max_digits=3, decimal_places=1)
    )

    last_hits: LOPShortDataItem = LOPShortDataItem(
        value=7,
        description="Last hits",
        type_=condecimal(max_digits=5, decimal_places=1)
    )
    kpm: LOPShortDataItem = LOPShortDataItem(
        value=8,
        description="Kills per minute",
        type_=condecimal(max_digits=3, decimal_places=2)
    )

    matches: LOPShortDataItem = LOPShortDataItem(value=9, description="Matches", type_=int, is_comparable=False)
    duration: LOPShortDataItem = LOPShortDataItem(value=10, description="Match length", type_=int)

    cores_networth_at_15: LOPShortDataItem = LOPShortDataItem(
        value=11,
        description="Cores networth at 15",
        type_=condecimal(max_digits=7, decimal_places=1)
    )
    supports_networth_at_15: LOPShortDataItem = LOPShortDataItem(
        value=12,
        description="Supports networth at 15",
        type_=condecimal(max_digits=7, decimal_places=1)
    )

    cores_level_at_15: LOPShortDataItem = LOPShortDataItem(
        value=13,
        description="Cores level at 15",
        type_=condecimal(max_digits=3, decimal_places=1),
        value_format=LOPShortDataValueFormat.LEVEL,
    )
    supports_level_at_15: LOPShortDataItem = LOPShortDataItem(
        value=14,
        description="Supports level at 15",
        type_=condecimal(max_digits=3, decimal_places=1),
        value_format=LOPShortDataValueFormat.LEVEL,
    )

    VALUES: list[LOPShortDataItem] = [
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

