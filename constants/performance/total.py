from typing import Optional, ClassVar

from pydantic import condecimal, BaseModel
from sqlmodel import Field, SQLModel


MINUTE = 60

class DecimalSize(BaseModel):
    max_digits: int
    decimal_places: int


class GameTotal(BaseModel):
    value_type: type | DecimalSize

    index: int 
    name: str = ''
    description: str = ''


class GameTotals:
    total_gold: GameTotal = GameTotal(value_type=DecimalSize(max_digits=10, decimal_places=2), index=0)
    total_xp: GameTotal = GameTotal(value_type=DecimalSize(max_digits=10, decimal_places=2), index=1)
    kills_per_min: GameTotal = GameTotal(value_type=DecimalSize(max_digits=8, decimal_places=7), index=2)
    kda: GameTotal = GameTotal(value_type=DecimalSize(max_digits=5, decimal_places=2), index=3)
    neutral_kills: GameTotal = GameTotal(value_type=DecimalSize(max_digits=10, decimal_places=2), index=4)
    tower_kills: GameTotal = GameTotal(value_type=DecimalSize(max_digits=10, decimal_places=2), index=5)
    courier_kills: GameTotal = GameTotal(value_type=DecimalSize(max_digits=10, decimal_places=2), index=6)
    lane_kills: GameTotal = GameTotal(value_type=DecimalSize(max_digits=10, decimal_places=2), index=7)
    hero_kills: GameTotal = GameTotal(value_type=DecimalSize(max_digits=10, decimal_places=2), index=8)
    observer_kills: GameTotal = GameTotal(value_type=DecimalSize(max_digits=10, decimal_places=2), index=9)
    sentry_kills: GameTotal = GameTotal(value_type=DecimalSize(max_digits=10, decimal_places=2), index=10)
    roshan_kills: GameTotal = GameTotal(value_type=DecimalSize(max_digits=10, decimal_places=2), index=11)
    runes_picked_up: GameTotal = GameTotal(value_type=DecimalSize(max_digits=10, decimal_places=2), index=12)
    ancient_kills: GameTotal = GameTotal(value_type=DecimalSize(max_digits=10, decimal_places=2), index=13)
    buyback_count: GameTotal = GameTotal(value_type=DecimalSize(max_digits=10, decimal_places=2), index=14)
    observer_uses: GameTotal = GameTotal(value_type=DecimalSize(max_digits=10, decimal_places=2), index=15)
    sentry_uses: GameTotal = GameTotal(value_type=DecimalSize(max_digits=10, decimal_places=2), index=16)
    lane_efficiency: GameTotal = GameTotal(value_type=DecimalSize(max_digits=10, decimal_places=2), index=17)
    lane_efficiency_pct: GameTotal = GameTotal(value_type=DecimalSize(max_digits=10, decimal_places=2), index=18)
    first_blood_claimed: GameTotal = GameTotal(value_type=DecimalSize(max_digits=5, decimal_places=2), index=19)
    died_first: GameTotal = GameTotal(value_type=DecimalSize(max_digits=5, decimal_places=2), index=20)
    lost_tower_first: GameTotal = GameTotal(value_type=DecimalSize(max_digits=5, decimal_places=2), index=21)
    destroyed_tower_first: GameTotal = GameTotal(value_type=DecimalSize(max_digits=5, decimal_places=2), index=22)
    first_kill_time: GameTotal = GameTotal(value_type=int, index=23)
    first_death_time: GameTotal = GameTotal(value_type=int, index=24)
    lost_tower_lane: GameTotal = GameTotal(value_type=int, index=25)
    lost_tower_time: GameTotal = GameTotal(value_type=int, index=26)
    destroyed_tower_lane: GameTotal = GameTotal(value_type=int, index=27)
    destroyed_tower_time: GameTotal = GameTotal(value_type=int, index=28)


class TotalMeta(type(SQLModel)):
    def __new__(cls, name, bases, dct, **kwargs):
        # setting const and fields for the class
        # ClassVar for const object and filling fields
        cls.const = type('Const', (object,), {})
        cls.__annotations__['const'] = ClassVar[object]

        counter = 1
        for name, annotation_type in GameTotals.__annotations__.items():
            cls_field_value = getattr(GameTotals, name)
            if isinstance(annotation_type, DecimalSize):
                # create it for pydantic
                setattr(cls, name, Field(default=None, primary_key=True))
                cls.__annotations__[name] = condecimal(
                    max_digits=cls_field_value.max_digits,
                    decimal_places=cls_field_value.decimal_places,
                )
            else:
                cls.__annotations__[name] = Optional[int]

            cls_field_value.name=name
            counter += 1


            setattr(cls.const, name, cls_field_value)
            cls.const.__annotations__[name] = annotation_type


        return super().__new__(cls, name, bases, dct, **kwargs)
