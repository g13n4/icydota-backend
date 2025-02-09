from typing import Any

from pydantic import condecimal, BaseModel


MINUTE = 60


class GameTotal(BaseModel):
    value_type: Any

    index: int
    name: str = ''
    description: str = ''
    # is resposible for boolean values that should trasnform into chance/percent during aggregation or comparison
    pseudo_bool: bool = False


class GameTotals:
    total_gold: GameTotal = GameTotal(value_type=condecimal(max_digits=10, decimal_places=2), index=1)
    total_xp: GameTotal = GameTotal(value_type=condecimal(max_digits=10, decimal_places=2), index=2)
    kills_per_min: GameTotal = GameTotal(value_type=condecimal(max_digits=8, decimal_places=7), index=3)
    kda: GameTotal = GameTotal(value_type=condecimal(max_digits=5, decimal_places=2), index=4)
    neutral_kills: GameTotal = GameTotal(value_type=condecimal(max_digits=10, decimal_places=2), index=5)
    tower_kills: GameTotal = GameTotal(value_type=condecimal(max_digits=10, decimal_places=2), index=6)
    courier_kills: GameTotal = GameTotal(value_type=condecimal(max_digits=10, decimal_places=2), index=7)
    lane_kills: GameTotal = GameTotal(value_type=condecimal(max_digits=10, decimal_places=2), index=8)
    hero_kills: GameTotal = GameTotal(value_type=condecimal(max_digits=10, decimal_places=2), index=9)
    observer_kills: GameTotal = GameTotal(value_type=condecimal(max_digits=10, decimal_places=2), index=10)
    sentry_kills: GameTotal = GameTotal(value_type=condecimal(max_digits=10, decimal_places=2), index=11)
    roshan_kills: GameTotal = GameTotal(value_type=condecimal(max_digits=10, decimal_places=2), index=12)
    runes_picked_up: GameTotal = GameTotal(value_type=condecimal(max_digits=10, decimal_places=2), index=13)
    ancient_kills: GameTotal = GameTotal(value_type=condecimal(max_digits=10, decimal_places=2), index=14)
    buyback_count: GameTotal = GameTotal(value_type=condecimal(max_digits=10, decimal_places=2), index=15)
    observer_uses: GameTotal = GameTotal(value_type=condecimal(max_digits=10, decimal_places=2), index=16)
    sentry_uses: GameTotal = GameTotal(value_type=condecimal(max_digits=10, decimal_places=2), index=17)
    lane_efficiency: GameTotal = GameTotal(value_type=condecimal(max_digits=10, decimal_places=2), index=18)
    lane_efficiency_pct: GameTotal = GameTotal(value_type=condecimal(max_digits=10, decimal_places=2), index=19)
    first_blood_claimed: GameTotal = GameTotal(value_type=condecimal(max_digits=5, decimal_places=2), index=20)
    died_first: GameTotal = GameTotal(value_type=condecimal(max_digits=5, decimal_places=2), index=21)
    lost_tower_first: GameTotal = GameTotal(value_type=condecimal(max_digits=5, decimal_places=2), index=22)
    destroyed_tower_first: GameTotal = GameTotal(value_type=condecimal(max_digits=5, decimal_places=2), index=23)
    first_kill_time: GameTotal = GameTotal(value_type=int, index=24)
    first_death_time: GameTotal = GameTotal(value_type=int, index=25)
    lost_tower_lane: GameTotal = GameTotal(value_type=condecimal(max_digits=3, decimal_places=2), index=23, pseudo_bool=True)
    lost_tower_time: GameTotal = GameTotal(value_type=int, index=27)
    destroyed_tower_lane: GameTotal = GameTotal(value_type=condecimal(max_digits=3, decimal_places=2), index=23, pseudo_bool=True)
    destroyed_tower_time: GameTotal = GameTotal(value_type=int, index=29)
