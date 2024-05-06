from math import floor
from typing import Any, Optional, List
import re


class IncorrectDataCombination(Exception):
    pass


class TableMinMaxFinder:
    """
    Collecting data of maximum and minimum values of the columns and set an index number to it:
    Index values go from 0 to N where N is the index number of a list value where the colour is located
    i.e. colours = [white, blue, red, black] - table colours, index 0 means that the colour front-end needs to pick is white
    because white is colours[0]
    """

    def __init__(self, index_steps: int = 10):
        self.data = dict()
        self.index_steps = index_steps


    def add(self, column: str, value: int | float | None) -> None:
        if not value:
            return

        if column not in self.data.keys():
            self.data[column] = {
                'min': value,
                'max': value,
            }
            return

        self.data[column]["max"] = max(self.data[column]["max"], value)
        self.data[column]["min"] = min(self.data[column]["min"], value)


    def _calculate_index(self, column: str, value: int | float | None) -> int:
        max_value = self.data[column]["max"]
        min_value = self.data[column]["min"]

        left_side = (value - min_value)
        right_side = (max_value - min_value)

        if not left_side or not right_side:
            # RETURN 9 - SET VALUE COLOUR TO MAX
            return 9

        return floor((left_side / right_side) * self.index_steps)


    def get_index(self, column: str, value: Any) -> Optional[int]:
        if value is None or column not in self.data.keys():
            return None

        return self._calculate_index(value=value, column=column)


    def has_totals(self) -> bool:
        for col_name in self.data.keys():
            if re.match(r'[g|l]total', col_name):
                return True
        return False


    def insert_index_in_dict(self, item: dict, column: str, value: int | float, inplace: bool = False) -> Optional[dict]:
        item[f'_index_{column}'] = self.get_index(value=value, column=column)
        if inplace:
            return None
        else:
            return item


    def insert_index_in_dict_bulk(self, data: List[dict], include: List[str] = None, exclude: List[str] = None, inplace: bool = False):
        if (include is None and exclude is None) or (isinstance(include, list) and isinstance(exclude, list)):
            raise IncorrectDataCombination("Only include or exclude should be set")
        elif (include is None and exclude is None):
            raise IncorrectDataCombination("No values are passed")

        if not inplace:
            processed_data = []
            for item in data:
                new_item = dict()
                for field_name, field_value in item.items():
                    if (include and field_name in include) or (not (exclude and field_name in exclude)):
                        self.insert_index_in_dict(new_item, column=field_name, value=field_value, inplace=True)
                new_item.update(item)
                processed_data.append(new_item)

            return processed_data
        else:
            # FIRST CREATE A LIST OF COLUMNS TO WORK WITH
            fields_to_process = [field_name for field_name in data[0].keys()
                                 if (include and field_name in include) or (not (exclude and field_name in exclude))]
            # MUTATE DICTS
            [self.insert_index_in_dict(item, column=field, value=item[field], inplace=True)
             for item in data for field in fields_to_process]


    def get_minmax_values(self) -> List[dict]:
        return [{'col': col, **col_data} for col, col_data in self.data.items()]
