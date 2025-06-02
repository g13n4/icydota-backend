from typing import Literal

from constants.calculation.game.calculation_type.damage import DamageCalculations
from constants.calculation.game.calculation_type.deward import DewardCalculations
from constants.calculation.game.calculation_type.gold import GoldCalculations
from constants.calculation.game.calculation_type.helpers import CalculationItem
from constants.calculation.game.calculation_type.interval import IntervalCalculations
from constants.calculation.game.calculation_type.pings import PingsCalculations
from constants.calculation.game.calculation_type.wards import WardsCalculations
from constants.calculation.game.calculation_type.xp import XPCalculations
from constants.helpers import Item


class WindowCalculationsIterator:
    def __init__(self, values: list[CalculationItem]):
        self._values = values


    def __iter__(self):
        yield from self._values


    def __len__(self):
        return len(self._values)


    def __call__(
            self,
            only_active: bool = False,
            only_calculated_later: bool = False,
            only_calculated_normally: bool = False,

            only_category: int | Item | None = None,

            only_field: Literal["name", "value", "db_id", "index"] | None = None,
    ):
        for item in self._values:
            if only_active and not item.is_active:
                continue
            if (
                    only_calculated_later and
                    not (
                            item.postprocessing is not None and item.postprocessing.calculated_later
                    )
            ):
                continue
            if (
                    only_calculated_normally and
                    item.postprocessing is not None and
                    item.postprocessing.calculated_later
            ):
                continue

            if only_category is not None and only_category != item.category:
                continue

            if only_field is None:
                yield item
            else:
                yield getattr(item, only_field)


class WindowCalculations(
    IntervalCalculations,
    PingsCalculations,
    DamageCalculations,
    WardsCalculations,
    DewardCalculations,
    XPCalculations,
    GoldCalculations
):
    _VALUES: list[CalculationItem] = (
            IntervalCalculations.VALUES +
            PingsCalculations.VALUES +
            DamageCalculations.VALUES +
            WardsCalculations.VALUES +
            DewardCalculations.VALUES +
            XPCalculations.VALUES +
            GoldCalculations.VALUES
    )

    DB_INDEX_MAP: dict[int, int]
    VALUES: WindowCalculationsIterator
    VALUES_NAMES: list[str]


WindowCalculations.VALUES = WindowCalculationsIterator(WindowCalculations._VALUES)
WindowCalculations.VALUES_NAMES = list(WindowCalculations.VALUES(only_field="name"))


WindowCalculations.DB_INDEX_MAP = {
    item.value: item.db_id for item in WindowCalculations.VALUES
}
