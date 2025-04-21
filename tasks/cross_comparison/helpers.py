from collections import namedtuple
from typing import Any

from constants.calculation.cross_comparison import CrossComparisonPositionConstant
from constants.position import PositionConstant, POSITION_OPPONENTS
from modules.query_creators.const_map import CCOMPARISON_MODELS
from utils.helpers import unique_list


APPEND_CONST = "___APPEND_CONST"


class CrossComparisonKeyCreator:
    def __init__(self, type_id: int):
        self.type_id = type_id
        self.models = CCOMPARISON_MODELS[type_id]
        self.fields = [item.field_name for item in self.models if not item.auxiliary]


    def get_fields(self):
        return self.fields


    def create_key(self, data: dict, fields: list[str] | None = None, *, append: Any = APPEND_CONST) -> tuple:
        """Get a dictionary and extract values from it according to the fields set"""
        fields_to_use = fields or self.fields
        output = [data[field] for field in fields_to_use]

        if append != APPEND_CONST:
            output.append(append)

        return tuple(output)


    def create_dict(self, data: dict, fields: list[str] | None = None) -> dict:
        """Get a dictionary and recreate using only required fields"""
        fields_to_use = fields or self.fields
        output = { field: data[field] for field in fields_to_use }

        return output


ComparisonItem = namedtuple('ComparisonItem', ['cpd', 'cps'])

COMPARISON_NAME_MAP = {
    'hero_id': ComparisonItem(cpd='hero_cpd_id', cps='hero_cps_id'),
    'player_id': ComparisonItem(cpd='player_cpd_id', cps='player_cps_id'),
    'position_id': ComparisonItem(cpd='position_cpd_id', cps='position_cps_id'),
    'facet_id': ComparisonItem(cpd='facet_cpd_id', cps='facet_cps_id'),
}

COMPARISON_TYPE_POSITION_MAP = {
    CrossComparisonPositionConstant.SUPPORT: unique_list(
        POSITION_OPPONENTS[PositionConstant.SOFT_SUPPORT.value],
        POSITION_OPPONENTS[PositionConstant.HARD_SUPPORT.value]
    ),
    CrossComparisonPositionConstant.CARRY: unique_list(
        POSITION_OPPONENTS[PositionConstant.CARRY.value],
        POSITION_OPPONENTS[PositionConstant.OFFLANE.value]
    ),
    CrossComparisonPositionConstant.MIDDLE: unique_list(
        POSITION_OPPONENTS[PositionConstant.MIDDLE.value]
    ),
}
