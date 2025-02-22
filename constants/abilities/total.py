from typing import Any, ClassVar

from pydantic import condecimal, BaseModel

from constants.helpers import get_only_names
from helpers import to_proper_name


class AbilityTotal(BaseModel):
    value_type: Any

    index: int
    name: str | None = None
    description: str | None = None


def set_total_name(klass: object):
    values = []
    for name, type_ in klass.__annotations__.items():
        if type_ is AbilityTotal:
            value = getattr(klass, name)
            value.name = name
            if value.description is None:
                value.description = to_proper_name(name)

            values.append(value)

    setattr(klass, 'VALUES', values)
    setattr(klass, 'VALUES_NAMES', get_only_names(values))

    return klass


@set_total_name
class AbilityTotals:
    to_heroes: AbilityTotal = AbilityTotal(value_type=condecimal(max_digits=10, decimal_places=2), index=1)
    inst_heroes: AbilityTotal = AbilityTotal(value_type=condecimal(max_digits=10, decimal_places=2), index=2)

    to_creeps: AbilityTotal = AbilityTotal(value_type=condecimal(max_digits=10, decimal_places=2), index=3)
    inst_creeps: AbilityTotal = AbilityTotal(value_type=condecimal(max_digits=10, decimal_places=2), index=4)

    to_neutrals: AbilityTotal = AbilityTotal(value_type=condecimal(max_digits=10, decimal_places=2), index=5)
    inst_neutrals: AbilityTotal = AbilityTotal(value_type=condecimal(max_digits=10, decimal_places=2), index=6)

    VALUES: ClassVar[list[AbilityTotal]]
    VALUES_NAMES: ClassVar[list[str]]
