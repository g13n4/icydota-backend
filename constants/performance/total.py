from typing import Any, ClassVar, Optional

from pydantic import condecimal, BaseModel

from constants.helpers import get_only_names
from helpers import to_proper_name, UniqueIndexChecker


MINUTE = 60


class FieldAvailability(BaseModel):
    __match_args__ = ("match", "aggregation", "cross_comparison")

    match: bool = False
    aggregation: bool = False
    cross_comparison: bool = False


    def required(self, match: bool = False, aggregation: bool = False, cross_comparison: bool = False):
        """If a value is required it should present during output. If it's not it should be removed"""
        for availability, required_var in [
            (self.match, match),
            (self.aggregation, aggregation),
            (self.cross_comparison, cross_comparison)
        ]:
            if availability == required_var:
                return True
        return False


class GameTotal(BaseModel):
    value_type: Any

    index: int
    name: str | None = None
    description: str | None = None
    pseudo_bool: bool = False
    availability: None | FieldAvailability = None


def set_total_name(klass: object):
    values = []
    checker = UniqueIndexChecker()
    for name, type_ in klass.__annotations__.items():
        if type_ is GameTotal:
            value = getattr(klass, name)
            value.name = name
            if value.description is None:
                value.description = to_proper_name(name)

            values.append(value)

            checker.add(value.index)

    setattr(klass, 'VALUES', values)
    setattr(klass, 'VALUES_NAMES', get_only_names(values))

    return klass


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
        availability=FieldAvailability(match=True),
    )

    destroyed_tower_first: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=23,
        pseudo_bool=True
    )
    destroyed_tower_lane: GameTotal = GameTotal(
        value_type=Optional[int],
        index=28,
        availability=FieldAvailability(match=True),
    )
    destroyed_tower_time: GameTotal = GameTotal(value_type=Optional[int], index=29)

    win: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=30,
        availability=FieldAvailability(aggregation=True, cross_comparison=True),
        pseudo_bool=True
    )
    picked: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=31,
        availability=FieldAvailability(aggregation=True, cross_comparison=True),
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
        availability=FieldAvailability(aggregation=True, cross_comparison=True),
        pseudo_bool=True
    )

    first_destroyed_mid: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=49,
        availability=FieldAvailability(aggregation=True, cross_comparison=True),
        pseudo_bool=True
    )
    first_destroyed_top: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=50,
        availability=FieldAvailability(aggregation=True, cross_comparison=True),
        pseudo_bool=True
    )
    first_destroyed_bot: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=51,
        availability=FieldAvailability(aggregation=True, cross_comparison=True),
        pseudo_bool=True
    )

    first_lost_mid: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=52,
        availability=FieldAvailability(aggregation=True, cross_comparison=True),
        pseudo_bool=True
    )
    first_lost_top: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=53,
        availability=FieldAvailability(aggregation=True, cross_comparison=True),
        pseudo_bool=True
    )
    first_lost_bot: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=54,
        availability=FieldAvailability(aggregation=True, cross_comparison=True),
        pseudo_bool=True
    )

    VALUES: ClassVar[list[GameTotal]]
    VALUES_NAMES: ClassVar[list[str]]
