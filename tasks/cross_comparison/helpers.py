from collections import namedtuple

from constants.calculation.cross_comparison import CrossComparisonPositionConstant
from constants.position import PositionConstant, POSITION_OPPONENTS
from utils.helpers import unique_list


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
