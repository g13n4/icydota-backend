from models import AggregationType, ComparisonType
from models.performance import GamePerformance, GamePerformanceType
from modules.select_query.aggregation import aggregation_query_constructor
from modules.select_query.helpers import combine_select


def get_aggregation_query(league_id: int, aggregation_type: str, data_type: int, basic: bool, flat: bool, basic_aggregation: bool, **kwargs):
    models, joins, where = aggregation_query_constructor(league_id, aggregation_type, data_type, **kwargs)

    models.append(ComparisonType.cps_name_short)
    joins.add(ComparisonType, GamePerformance.comparison_id == ComparisonType.id)

    where.append(ComparisonType.basic == basic)
    where.append(ComparisonType.flat == flat)

    if basic_aggregation:
        where.append(GamePerformance.performance_type_id == GamePerformanceType.const.AGGREGATION_COMPARISON)
    else:
        where.append(GamePerformance.performance_type_id == GamePerformanceType.const.HERO_PLAYER_AGGREGATION_COMPARISONN)
    where.append(AggregationType.by_player_and_hero == basic_aggregation)

    return combine_select(models, joins, where)
