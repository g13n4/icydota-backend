from models import Hero, Player, AggregationType, ComparisonType
from models.performance import PerformanceTotalData, PerformanceWindowData, PerformanceWindowTable, GamePerformance, \
    GamePerformanceType
from modules.select_query.helpers import JoinList, combine_select

AGG_MODEL = {
    "hero": [Hero.name, Hero.id, AggregationType.hero_cross_cps_id],
    "player": [Player.nickname, Player.account_id, AggregationType.player_cross_cps_id],
}


def crosscomparison_query_constructor(league_id: int,
                                                aggregation_type: str,
                                                position: str,
                                                data_field: str,
                                                data_type: int,
                                                flat: bool,
                                  **kwargs) -> tuple[list, JoinList, list]:
    models = []
    joins = JoinList()
    where = [AggregationType.league_id == league_id,
             ComparisonType.flat == flat,
             GamePerformanceType.const.CROSS_COMPARISON]

    if data_type == 0:
        models.append(getattr(PerformanceTotalData, data_field))
        joins.add(GamePerformance, PerformanceTotalData.game_performance_id == GamePerformance.id)
    else:
        models.append(PerformanceWindowData)
        joins.add(GamePerformance, PerformanceWindowData.game_performance_id == GamePerformance.id)

        models.append(getattr(PerformanceWindowTable, data_field))
        joins.add(PerformanceWindowTable, PerformanceWindowData.performance_table_id == PerformanceWindowTable.id, True)
        where.append(PerformanceWindowData.data_type_id == data_type)

    joins.add(AggregationType, GamePerformance.aggregation_id == AggregationType.id)

    for agg_model in AGG_MODEL[aggregation_type]:
        models.append(agg_model)

    if aggregation_type == "player":
        joins.add(Player, onclause=AggregationType.player_id == Player.account_id)
        where.append(AggregationType.pos_player_cross == True)
    elif aggregation_type == "hero":
        joins.add(Hero, onclause=AggregationType.hero_id == Hero.id)
        where.append((AggregationType.pos_hero_cross == True, 1))
    else:
        raise ValueError("Invalid aggregation type")


    if position == 'support':
        where.append(AggregationType.sup_cross == True)
    elif position == 'core':
        where.append(AggregationType.carry_cross == True)
    elif position == 'mid':
        where.append(AggregationType.mid_cross == True)
    else:
        raise ValueError("Invalid position")

    return models, joins, where


def get_crosscomparison_query(league_id: int,
                                                aggregation_type: str,
                                                position: str,
                                                data_field: str,
                                                data_type: int,
                                                flat: bool,
                                  **kwargs):
    models, joins, where = crosscomparison_query_constructor(league_id,
                                                aggregation_type,
                                                position,
                                                data_field,
                                                data_type,
                                                flat,
                                  **kwargs)

    return combine_select(models, joins, where)
