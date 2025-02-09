from collections import namedtuple

from sqlmodel import select
from typing_extensions import ClassVar

from constants.aggregation import AggregationConstant
from models import PlayerGameData, Hero, Player, Position, Facet, ComparisonType, AggregationType
from models.performance import PerformanceTotalData, PerformanceWindowData, GamePerformance, \
    PerformanceWindowTable


def create_join_dict(target, onclause, isouter: bool = False):
    return {
            "target": target,
            "onclause": onclause,
            "isouter": isouter,
        }


class JoinList:
    def __init__(self, iterable = None):
        self.data = []
        if iterable is not None:
            for item in iterable:
                self.data.append(item)

    def add(self, target, onclause, isouter: bool = False):
        self.data.append(create_join_dict(target=target, onclause=onclause, isouter=isouter))

    def __iter__(self):
        return iter(self.data)


ModelItem = namedtuple('ModelItem', ['model', 'name'])


class ModelList:
    def __init__(self, iterable = None):
        self.data: list[ModelItem] = []
        if iterable is not None:
            for item in iterable:
                self.data.append(item)

    def add(self, model, name: str | None = None):
        if name is None:
            name = model.__name__.lower()
        self.data.append((model, name))

    def __iter__(self):
        return iter(self.data)

    def get_models(self) -> list:
        return [item.model for item in self.data]

    def get_names(self) -> list:
        return [item.name for item in self.data]


def combine_select(models: list, joins: list | JoinList, where_clauses: list):
    select_qr = select(*models)
    for join_ in joins:
        select_qr = select_qr.join(**join_)
    select_qr = select_qr.where(*where_clauses)
    return select_qr


class PerformanceQueryCreator:

    AGGREGATION_MODELS: ClassVar[dict] = {
    AggregationConstant.BY_HERO: [Hero],
    AggregationConstant.BY_PLAYER: [Player],
    AggregationConstant.BY_POSITION: [Position],
    AggregationConstant.BY_HERO_PLAYER: [Hero, Position  ],
    AggregationConstant.BY_HERO_FACET: [ Hero, Facet ],
    AggregationConstant.BY_HERO_FACET_PLAYER: [Hero, Facet, Player ],
    }

    CCOMPARISON_MODELS: ClassVar[dict] = {
        "hero": [(Hero.name, 'hero'), (Hero.id, 'hero_id'), (AggregationType.hero_cross_cps_id, 'opponent_id')],
        "player": [
            (Player.nickname, 'player'),
            (Player.account_id, 'account_id'),
            (AggregationType.player_cross_cps_id, 'opponent_id')],
    }

    def __init__(self):
        self.data_model = None
        self.models = ModelList()
        self.joins = JoinList()
        self.where = []


    def _set_model(self, data_type: int):
        if data_type == 0:
            self.data_model = PerformanceTotalData
        else:
            self.data_model = PerformanceWindowData


    def _set_data_model(self, data_type: int, field: str | None = None):
        self._set_model(data_type)

        if field is None:
            data_model = self.data_model
            data_model_field = 'model'
        else:
            data_model = getattr(self.data_model, field)
            data_model_field = field

        self.models.add(data_model, data_model_field)
        self.joins.add(GamePerformance, self.data_model.game_performance_id == GamePerformance.id)

        if data_type > 0:
            self.models.add(PerformanceWindowTable, 'model')
            self.joins.add(
                PerformanceWindowTable,
                PerformanceWindowData.performance_table_id == PerformanceWindowTable.id,
                True
            )
            self.where.append(PerformanceWindowData.data_type_id == data_type)


    def _set_comparison_model(self, basic: bool, flat: bool):
        self.models.add(ComparisonType.cps_name_short, 'opponent')
        self.joins.add(ComparisonType, GamePerformance.comparison_id == ComparisonType.id)

        self.where.append(ComparisonType.basic == basic)
        self.where.append(ComparisonType.flat == flat)


    def _set_match_select_query_data(
            self,
            data_type: int,
            match_id: int | None = None,
            **kwargs) -> None:
        self._set_data_model(data_type=data_type)

        self.models.add(PlayerGameData.dire, 'side')
        self.joins.add(PlayerGameData, GamePerformance.player_game_data_id == PlayerGameData.id)

        self.models.add(Position.name, 'position')
        self.joins.add(Position, PlayerGameData.position_id == Position.id)

        self.models.add(Hero.name, 'hero')
        self.joins.add(Hero, PlayerGameData.hero_id == Hero.id)

        self.models.add(Player.nickname, 'player')
        self.joins.add(Player, PlayerGameData.player_id == Player.account_id)

        self.where.append(PlayerGameData.game_id == match_id)


    def get_match_query(self, match_id: int, data_type: int, **kwargs):
        self._set_match_select_query_data(data_type=data_type, match_id=match_id)
        self.where.insert(0, GamePerformance.performance_type_id == GamePerformance.const.MATCH_DATA)
        return combine_select(self.models.get_models(), self.joins.data, self.where)


    def get_match_comparison_query(self, match_id: int, data_type: int,  basic: bool, flat: bool ,**kwargs):
        self._set_match_select_query_data(data_type=data_type, match_id=match_id)
        self._set_comparison_model(basic=basic, flat=flat)
        self.where.append(GamePerformance.performance_type_id == GamePerformance.const.MATCH_DATA_COMPARISON)
        return combine_select(self.models.get_models(), self.joins.data, self.where)


    def _set_aggregation_select_query_data(self, league_id: int, aggregation_type: int, data_type: int, **kwargs):
        self._set_data_model(data_type=data_type)

        self.where.append(AggregationType.league_id == league_id)

        self.joins.add(AggregationType, GamePerformance.aggregation_id == AggregationType.id)

        for agg_model in self.AGGREGATION_MODELS[aggregation_type]:
            self.models.add(agg_model)


    def get_aggregation_query(self, league_id: int, aggregation_type: int, data_type: int, **kwargs):
        self._set_aggregation_select_query_data(league_id=league_id, aggregation_type=aggregation_type, data_type=data_type)
        self.where.append(AggregationType.type == aggregation_type)
        return combine_select(self.models.get_models(), self.joins.data, self.where)


    def get_aggregation_comparison_query(self, league_id: int, aggregation_type: int, data_type: int, basic: bool, flat: bool, **kwargs):
        self._set_aggregation_select_query_data(league_id=league_id, aggregation_type=aggregation_type, data_type=data_type)
        self._set_comparison_model(basic=basic, flat=flat)
        self.where.append(AggregationType.type == aggregation_type)
        return combine_select(self.models.get_models(), self.joins.data, self.where)


    def _set_cross_comparison_query_data(self, league_id: int,
                                                aggregation_type: str,
                                                position: str,
                                                data_field: str,
                                                data_type: int,
                                                flat: bool,
                                   **kwargs):
        self._set_data_model(data_type=data_type, field=data_field)

        self.where.append(AggregationType.league_id == league_id)
        self.where.append(ComparisonType.flat == flat)
        self.where.append(GamePerformance.performance_type_id == GamePerformance.const.CROSS_COMPARISON)

        for model, model_name in self.CCOMPARISON_MODELS[aggregation_type]:
            self.models.add(model, model_name)

        self.joins.add(AggregationType, GamePerformance.aggregation_id == AggregationType.id)
        self.joins.add(ComparisonType, GamePerformance.comparison_id == ComparisonType.id)


        if aggregation_type == "player":
            self.joins.add(Player, onclause=AggregationType.player_id == Player.account_id)
            self.where.append(AggregationType.pos_player_cross == True)
        else:
            self.joins.add(Hero, onclause=AggregationType.hero_id == Hero.id)
            self.where.append(AggregationType.pos_hero_cross == True)

        if position == 'support':
            self.where.append(AggregationType.sup_cross == True)
        elif position == 'core':
            self.where.append(AggregationType.carry_cross == True)
        else:
            self.where.append(AggregationType.mid_cross == True)


    def get_cross_comparison_query(self,  league_id: int,
                                                aggregation_type: str,
                                                position: str,
                                                data_field: str,
                                                data_type: int,
                                                flat: bool,
                                   **kwargs):


        self._set_cross_comparison_query_data(
            league_id=league_id,
            aggregation_type=aggregation_type,
            position=position,
            data_field=data_field,
            data_type=data_type,
            flat=flat,
            **kwargs,
        )

        return combine_select(self.models.get_models(), self.joins.data, self.where)
