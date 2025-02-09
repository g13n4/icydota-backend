from models import ComparisonType
from models.performance import GamePerformance, GamePerformanceType
from modules.select_query.helpers import combine_select
from modules.select_query.match_data import match_data_query_constructor


def get_match_data_comparison_query(match_id: int, data_type: int, basic: bool, flat: bool , **kwargs):
    models, joins, where = match_data_query_constructor(match_id, data_type, **kwargs)

    models.append(ComparisonType.cps_name_short)
    joins.add(ComparisonType, GamePerformance.comparison_id == ComparisonType.id)

    where.append(ComparisonType.basic == basic)
    where.append(ComparisonType.flat == flat)
    where.append(GamePerformance.performance_type_id == GamePerformanceType.const.MATCH_DATA_COMPARISON)

    return combine_select(models, joins, where)
