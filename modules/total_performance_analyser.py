import re
from typing import Set, Optional, List, Any
from decimal import Decimal
import numpy as np
import pandas as pd


class IncorrectDataError(Exception):
    pass


class ExcessiveDataError(Exception):
    pass


class IncorrectSlotValueError(Exception):
    pass


def _check_slot(slot: Any) -> bool:
    if type(slot) is int and (0 <= slot <= 9):
        return True

    return False

def _check_slots(*args) -> None:
    for arg in args:
        if not _check_slot(arg):
            raise IncorrectSlotValueError(f"Slot value can't be {arg}")


def _get_fields(object) -> Set[str]:
    fields = [x for x in object.schema()['properties'].keys() if not re.search(r'(^|_)id$', x)]
    return set(fields)


class TotalPerformanceAnalyser:
    def __init__(self, total_performance_data_dict: dict):

        fields = _get_fields(total_performance_data_dict[0])
        fields = [x for x in fields if not x.endswith('lane')]  # removing fields lost_tower_lane

        total_performance_data = [{'slot': slot, **data.dict(include=fields)}
                                  for slot, data in total_performance_data_dict.items()]

        self.data_pd = pd.DataFrame(total_performance_data)
        self.data_pd.set_index('slot', inplace=True)
        self.data_pd.fillna(0, inplace=True)

        self.data = {slot: self.data_pd.loc[slot].astype(np.float32) for slot in self.data_pd.index}

    def _compare(self, comparandum_series: pd.Series, comparans_series: pd.Series, flat: bool):
        comp_func = np.subtract if flat else np.divide
        data = comp_func(comparandum_series, comparans_series)
        data.replace([np.inf, -np.inf, np.nan], 0, inplace=True)

        return {k: Decimal(v) for k, v in data.to_dict().items()}


    def compare_to_many(self, comparandum: int, comparans_list: Optional[List[int]], flat: bool,) -> dict:
        _check_slots(comparandum, *comparans_list)

        comparandum_data: pd.Series = self.data[comparandum]

        copmparans_base: pd.Series = pd.Series(index=comparandum_data.index, data=0)
        for comparans in comparans_list:
            copmparans_base += self.data[comparans]
        comparans_data = copmparans_base / len(comparans_list)

        return self._compare(comparandum_data, comparans_data, flat)

    def compare_to_one(self, comparandum: int, comparans: int, flat: bool, ) -> dict:
        _check_slots(comparandum, comparans)

        comparandum_data: pd.Series = self.data[comparandum]
        comparans_data: pd.Series = self.data[comparans]
        return self._compare(comparandum_data, comparans_data, flat)

