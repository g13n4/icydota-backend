from typing import Any, ClassVar

from pydantic import condecimal, BaseModel

from constants.helpers import get_only_names
from helpers import to_proper_name


class SPItem(BaseModel):
    """SidePerformanceItem"""

    value_type: Any

    index: int
    name: str | None = None
    description: str | None = None


def set_values_and_name(klass: object):
    values = []
    for name, type_ in klass.__annotations__.items():
        if type_ is SPItem:
            value = getattr(klass, name)
            value.name = name

            if value.description is None:
                value.description = to_proper_name(name)

            values.append(value)

    setattr(klass, 'VALUES', values)
    setattr(klass, 'VALUES_NAMES', get_only_names(values))

    return klass


@set_values_and_name
class SidePerformance:
    gold: SPItem = SPItem(value_type=int, index=1)
    xp: SPItem = SPItem(value_type=int, index=2, description="XP")
    hero_kills: SPItem = SPItem(value_type=condecimal(max_digits=4, decimal_places=2), index=3)
    kills_per_min: SPItem = SPItem(value_type=int, index=4, description="KPM")
    neutral_kills: SPItem = SPItem(value_type=int, index=5)

    roshan_kills: SPItem = SPItem(value_type=int, index=6, description="Roshan")
    runes_picked_up: SPItem = SPItem(value_type=int, index=7, description="Runes")

    observer_kills: SPItem = SPItem(value_type=int, index=8, description="Observers killed")
    observer_uses: SPItem = SPItem(value_type=int, index=9, description="Observers placed")

    sentry_kills: SPItem = SPItem(value_type=int, index=10, description="Sentries killed")
    sentry_uses: SPItem = SPItem(value_type=int, index=11, description="Sentries placed")

    first_blood_claimed: SPItem = SPItem(value_type=bool, index=12, description="FB")

    VALUES: ClassVar[list[SPItem]]
    VALUES_NAMES: ClassVar[list[str]]
