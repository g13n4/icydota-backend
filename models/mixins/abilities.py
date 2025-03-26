from sqlmodel import Field

from constants.abilities.total import AbilityTotals


class AbilityTotalDataMixin:
    """Mixin that contains dynamically created fields for "AbilityTotalData" class"""
    __mixin__ = True


for ability_total_field in AbilityTotals.VALUES:
    setattr(AbilityTotalDataMixin, ability_total_field.name, Field(default=None, nullable=True, primary_key=False))
    AbilityTotalDataMixin.__annotations__[ability_total_field.name] = ability_total_field.value_type
