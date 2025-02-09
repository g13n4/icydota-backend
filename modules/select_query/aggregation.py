from models import Hero, Player, Position, AggregationType
from models.performance import PerformanceTotalData, PerformanceWindowData, PerformanceWindowTable, GamePerformance, \
    GamePerformanceType
from modules.select_query.helpers import JoinList, combine_select


def aggregation_query_constructor(league_id: int,
                                  aggregation_type: str,
                                  data_type: int,
                                  **kwargs) -> tuple[list, JoinList, list]:
    models = []
    joins = JoinList()
    where = [AggregationType.league_id == league_id, ]

    if data_type == 0:
        models.append(PerformanceTotalData)
        joins.add(GamePerformance, PerformanceTotalData.game_performance_id == GamePerformance.id)
    else:
        models.append(PerformanceWindowData)
        joins.add(GamePerformance, PerformanceWindowData.game_performance_id == GamePerformance.id)

        models.append(PerformanceWindowTable)
        joins.add(PerformanceWindowTable, PerformanceWindowData.performance_table_id == PerformanceWindowTable.id, True)
        where.append(PerformanceWindowData.data_type_id == data_type)

    joins.add(AggregationType, GamePerformance.aggregation_id == AggregationType.id)

    for agg_model in AGG_MODEL[aggregation_type]:
        models.append(agg_model)

    return models, joins, where


def get_aggregation_query(league_id: int, aggregation_type: str, data_type: int, basic_aggregation: bool, **kwargs):
    models, joins, where = aggregation_query_constructor(league_id, aggregation_type, data_type, **kwargs)

    if basic_aggregation:
        where.append(GamePerformance.performance_type_id == GamePerformanceType.const.AGGREGATION)
    else:
        where.append(GamePerformance.performance_type_id == GamePerformanceType.const.HERO_PLAYER_AGGREGATION)
    where.append(AggregationType.by_player_and_hero == basic_aggregation)

    return combine_select(models, joins, where)
