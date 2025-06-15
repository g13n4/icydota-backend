from collections.abc import Iterable
from typing import Any, ClassVar, Optional, Literal

from pydantic import condecimal, BaseModel

from constants.performance.total.field_option import FieldOption
from helpers import to_proper_name, UniqueIndexChecker


MINUTE = 60


FIELD_AVAILABILITY_DATA_REPRESENTATION_TYPE_LITERAL = Literal[FieldOption.__match_args__]


class GameTotal(BaseModel):
    value_type: Any

    index: int
    name: str | None = None
    description: str | None = None
    pseudo_bool: bool = False
    availability: None | FieldOption = None
    optional: bool = False
    sort_offset: int = 0
    normalization: None | FieldOption = None

def set_total_name(klass: object):
    values = []
    checker = UniqueIndexChecker()
    for name, type_ in klass.__annotations__.items():
        if type_ is GameTotal:
            item = getattr(klass, name)
            item.name = name
            if item.description is None:
                item.description = to_proper_name(name)

            values.append(item)

            checker.add(item.index)

            if item.availability is None:
                item.optional = True

    setattr(klass, '_VALUES', values)

    return klass


class GameTotalsIterator:
    def __init__(self, values: list[GameTotal]):
        self._values = values


    def __len__(self):
        return len(self._values)


    def __call__(
            self,
            available_for: Iterable | None = None,
            only_pseudo_bools: bool = False,

            only_field: Literal["index", "name"] | None = None,
    ):
        for item in self._values:
            if only_pseudo_bools and not item.pseudo_bool:
                continue

            if available_for and item.availability is not None:
                if not item.availability.is_available(*available_for):
                    continue

            if only_field is None:
                yield item
            else:
                yield getattr(item, only_field)


    def __iter__(self):
        yield from self._values


@set_total_name
class GameTotals:
    gold: GameTotal = GameTotal(value_type=condecimal(max_digits=10, decimal_places=2), index=1)
    xp: GameTotal = GameTotal(value_type=condecimal(max_digits=8, decimal_places=2), index=2)
    kills_per_min: GameTotal = GameTotal(value_type=condecimal(max_digits=5, decimal_places=2), index=3)
    kda: GameTotal = GameTotal(value_type=condecimal(max_digits=5, decimal_places=2), index=4)
    neutral_kills: GameTotal = GameTotal(value_type=condecimal(max_digits=6, decimal_places=2), index=5)
    tower_kills: GameTotal = GameTotal(value_type=condecimal(max_digits=5, decimal_places=2), index=6)
    courier_kills: GameTotal = GameTotal(value_type=condecimal(max_digits=6, decimal_places=2), index=7)
    lane_kills: GameTotal = GameTotal(value_type=condecimal(max_digits=6, decimal_places=2), index=8)
    hero_kills: GameTotal = GameTotal(value_type=condecimal(max_digits=6, decimal_places=2), index=9)
    observer_kills: GameTotal = GameTotal(value_type=condecimal(max_digits=4, decimal_places=2), index=10)
    sentry_kills: GameTotal = GameTotal(
        value_type=condecimal(max_digits=4, decimal_places=2),
        index=11,
        description="Sentries killed"
    )
    roshan_kills: GameTotal = GameTotal(value_type=condecimal(max_digits=4, decimal_places=2), index=12)
    runes_picked_up: GameTotal = GameTotal(value_type=condecimal(max_digits=4, decimal_places=2), index=13)
    ancient_kills: GameTotal = GameTotal(value_type=condecimal(max_digits=6, decimal_places=2), index=14)
    buyback_count: GameTotal = GameTotal(value_type=condecimal(max_digits=4, decimal_places=2), index=15)
    observer_uses: GameTotal = GameTotal(value_type=condecimal(max_digits=4, decimal_places=2), index=16)
    sentry_uses: GameTotal = GameTotal(value_type=condecimal(max_digits=4, decimal_places=2), index=17)
    lane_efficiency: GameTotal = GameTotal(value_type=condecimal(max_digits=4, decimal_places=3), index=18)
    lane_efficiency_pct: GameTotal = GameTotal(value_type=condecimal(max_digits=6, decimal_places=2), index=19)

    first_blood_claimed: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=20,
        description="FB",
        pseudo_bool=True
    )
    first_kill_time: GameTotal = GameTotal(value_type=Optional[int], index=24)

    died_first: GameTotal = GameTotal(value_type=condecimal(max_digits=3, decimal_places=2), index=21, pseudo_bool=True)
    died_first_time: GameTotal = GameTotal(value_type=Optional[int], index=25)

    lost_tower_first: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=22,
        pseudo_bool=True
    )
    lost_tower_time: GameTotal = GameTotal(value_type=Optional[int], index=27)
    lost_tower_lane: GameTotal = GameTotal(
        value_type=Optional[int],
        index=26,
        availability=FieldOption(aggregation=True, cross_comparison=True),
    )

    destroyed_tower_first: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=23,
        pseudo_bool=True
    )
    destroyed_tower_lane: GameTotal = GameTotal(
        value_type=Optional[int],
        index=28,
        availability=FieldOption(aggregation=True, cross_comparison=True),
    )
    destroyed_tower_time: GameTotal = GameTotal(value_type=Optional[int], index=29)

    win: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=30,
        availability=FieldOption(match=False),
        pseudo_bool=True
    )
    picked: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=31,
        availability=FieldOption(match=False),
        pseudo_bool=True
    )

    no_death: GameTotal = GameTotal(value_type=condecimal(max_digits=3, decimal_places=2), index=32, pseudo_bool=True)
    no_kills: GameTotal = GameTotal(value_type=condecimal(max_digits=3, decimal_places=2), index=33, pseudo_bool=True)

    deaths: GameTotal = GameTotal(value_type=condecimal(max_digits=6, decimal_places=2), index=34)
    assists: GameTotal = GameTotal(value_type=condecimal(max_digits=6, decimal_places=2), index=35)

    last_hits: GameTotal = GameTotal(value_type=condecimal(max_digits=7, decimal_places=2), index=36)
    denies: GameTotal = GameTotal(value_type=condecimal(max_digits=6, decimal_places=2), index=37)

    gold_per_min: GameTotal = GameTotal(value_type=condecimal(max_digits=6, decimal_places=2), index=38)
    xp_per_min: GameTotal = GameTotal(value_type=condecimal(max_digits=6, decimal_places=2), index=39)
    level: GameTotal = GameTotal(value_type=condecimal(max_digits=5, decimal_places=2), index=40)
    net_worth: GameTotal = GameTotal(value_type=condecimal(max_digits=8, decimal_places=2), index=41)

    aghanims_scepter: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=42,
        pseudo_bool=True
    )
    aghanims_shard: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=43,
        pseudo_bool=True
    )
    moonshard: GameTotal = GameTotal(value_type=condecimal(max_digits=3, decimal_places=2), index=44, pseudo_bool=True)

    hero_damage: GameTotal = GameTotal(value_type=condecimal(max_digits=8, decimal_places=2), index=45)
    tower_damage: GameTotal = GameTotal(value_type=condecimal(max_digits=8, decimal_places=2), index=46)
    hero_healing: GameTotal = GameTotal(value_type=condecimal(max_digits=8, decimal_places=2), index=47)

    no_assists: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=48,
        availability=FieldOption(match=False),
        pseudo_bool=True
    )
    # first tower
    first_tower_destroyed_mid: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=49,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )
    first_tower_destroyed_top: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=50,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )
    first_tower_destroyed_bot: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=51,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )
    first_tower_lost_mid: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=52,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )
    first_tower_lost_top: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=53,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )
    first_tower_lost_bot: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=54,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )
    # picks
    first_pick_win: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=55,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )
    first_pick_lose: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=56,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )
    last_pick_win: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=57,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )
    last_pick_lose: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=58,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )
    last_pick_hero: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=59,
        availability=FieldOption(team=False),
        pseudo_bool=True
    )
    first_pick_hero: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=60,
        availability=FieldOption(team=False),
        pseudo_bool=True
    )
    # first lane
    first_tower_lane_destroyed_mid: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=61,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )
    first_tower_lane_destroyed_top: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=62,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )
    first_tower_lane_destroyed_bot: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=63,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )
    first_tower_lane_lost_mid: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=64,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )
    first_tower_lane_lost_top: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=65,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )
    first_tower_lane_lost_bot: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=66,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )
    # first barracks
    first_barracks_set_destroyed_mid: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=67,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )
    first_barracks_set_destroyed_top: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=68,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )
    first_barracks_set_destroyed_bot: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=69,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )
    first_barracks_set_lost_mid: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=70,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )
    first_barracks_set_lost_top: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=71,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )
    first_barracks_set_lost_bot: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=72,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )
    # first pick
    first_pick_pos_1: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=73,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )
    first_pick_pos_2: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=74,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )
    first_pick_pos_3: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=75,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )
    first_pick_pos_4: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=76,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )
    first_pick_pos_5: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=77,
        availability=FieldOption(player=False),
        pseudo_bool=True
    )


    _VALUES: ClassVar[list[GameTotal]]
    VALUES: GameTotalsIterator
    VALUES_NAMES: list[str]


GameTotals.VALUES = GameTotalsIterator(GameTotals._VALUES)
GameTotals.VALUES_NAMES = list(GameTotals.VALUES(only_field="name"))
