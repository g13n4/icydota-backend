from typing import Optional

from sqlmodel import Field, SQLModel


class PerformanceWindowField(SQLModel, table=True):
    __tablename__ = "performance_window_fields"

    l2 = 1
    l4 = 2
    l6 = 3
    l8 = 4
    l10 = 5
    ltotal = 6

    g15 = 7
    g30 = 8
    g45 = 9
    g60 = 10
    g60plus = 11
    gtotal = 12

    LANE = [l2, l4, l6, l8, l10, ltotal]
    GAME = [g15, g30, g45, g60, g60plus, gtotal]
    ALL = LANE + GAME

    TYPES = [
        (l2, "L2"),
        (l4, "L4"),
        (l6, "L6"),
        (l8, "L8"),
        (l10, "L10"),
        (ltotal, "LTOTAL"),
        (g15, "G15"),
        (g30, "G30"),
        (g45, "G45"),
        (g60, "G60"),
        (g60plus, "G60PLUS"),
        (gtotal, "GTOTAL"),
    ]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    is_active: bool = Field(default=True)


# PERFORMANCE TOTAL
class PerformanceTotalField(SQLModel, table=True):
    __tablename__ = "performance_total_fields"

    id: Optional[int] = Field(default=None, primary_key=True)

    total_gold = 1
    total_xp = 2
    kills_per_min = 3
    kda = 4

    neutral_kills = 5
    tower_kills = 6
    courier_kills = 7

    lane_kills = 8
    hero_kills = 9
    observer_kills = 10
    sentry_kills = 11
    roshan_kills = 12
    runes_picked_up = 13

    ancient_kills = 14
    buyback_count = 15
    observer_uses = 16
    sentry_uses = 17

    lane_efficiency = 18
    lane_efficiency_pct = 19

    first_blood_claimed = 20
    first_kill_time = 21

    died_first = 22
    first_death_time = 23

    lost_tower_first = 24
    lost_tower_lane = 25
    lost_tower_time = 26

    destroyed_tower_first = 27
    destroyed_tower_lane = 28
    destroyed_tower_time = 29

    TYPES = [
        (total_gold, "TOTAL_GOLD"),
        (total_xp, "TOTAL_XP"),
        (kills_per_min, "KILLS_PER_MIN"),
        (kda, "KDA"),
        (neutral_kills, "NEUTRAL_KILLS"),
        (tower_kills, "TOWER_KILLS"),
        (courier_kills, "COURIER_KILLS"),
        (lane_kills, "LANE_KILLS"),
        (hero_kills, "HERO_KILLS"),
        (observer_kills, "OBSERVER_KILLS"),
        (sentry_kills, "SENTRY_KILLS"),
        (roshan_kills, "ROSHAN_KILLS"),
        (runes_picked_up, "RUNES_PICKED_UP"),
        (ancient_kills, "ANCIENT_KILLS"),
        (buyback_count, "BUYBACK_COUNT"),
        (observer_uses, "OBSERVER_USES"),
        (sentry_uses, "SENTRY_USES"),
        (lane_efficiency, "LANE_EFFICIENCY"),
        (lane_efficiency_pct, "LANE_EFFICIENCY_PCT"),
        (first_blood_claimed, "FIRST_BLOOD_CLAIMED"),
        (first_kill_time, "FIRST_KILL_TIME"),
        (died_first, "DIED_FIRST"),
        (first_death_time, "FIRST_DEATH_TIME"),
        (lost_tower_first, "LOST_TOWER_FIRST"),
        (lost_tower_lane, "LOST_TOWER_LANE"),
        (lost_tower_time, "LOST_TOWER_TIME"),
        (destroyed_tower_first, "DESTROYED_TOWER_FIRST"),
        (destroyed_tower_lane, "DESTROYED_TOWER_LANE"),
        (destroyed_tower_time, "DESTROYED_TOWER_TIME"),
    ]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    is_active: bool = Field(default=True)
