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


ModelItem = namedtuple('ModelItem', ['model', 'name', 'is_header'])


class ModelList:
    def __init__(self, iterable = None):
        self.data: list[ModelItem] = []
        if iterable is not None:
            for item in iterable:
                self.data.append(item)

    def add(self, model, name: str | None = None, is_header: bool = False):
        if name is None:
            name = model.__name__.lower()
        self.data.append(ModelItem(model, name, is_header))

    def __iter__(self):
        return iter(self.data)

    def get_models(self) -> list:
        return [item.model for item in self.data]

    def get_names(self, only_header: bool = False) -> list[str]:
        if only_header:
            return [item.name for item in self.data if item.is_header]
        else:
            return [item.name for item in self.data]


def combine_select(models: list, joins: list | JoinList, where_clauses: list):
    select_qr = select(*models)
    for join_ in joins:
        select_qr = select_qr.join(**join_)
    select_qr = select_qr.where(*where_clauses)
    return select_qr

# Use the value from the from_model model instead of the actual model if it's set
AggItem = namedtuple('AggItem', ['model', 'associated_field', 'from_model'])


class PerformanceQueryCreator:

    AGG_HERO: ClassVar[AggItem] = AggItem(Hero, 'hero_id', AggregationType)
    AGG_PLAYER: ClassVar[AggItem] = AggItem(Player, 'player_id', None)
    AGG_POSITION: ClassVar[AggItem] = AggItem(Position, 'hero_id', AggregationType)
    AGG_FACET: ClassVar[AggItem] = AggItem(Facet, 'facet_id', None)

    AGGREGATION_MODELS: ClassVar[dict] = {
    AggregationConstant.BY_HERO: AGG_HERO,
    AggregationConstant.BY_PLAYER: AGG_PLAYER,
    AggregationConstant.BY_POSITION: AGG_POSITION,
    AggregationConstant.BY_HERO_PLAYER: [ AGG_HERO, AGG_POSITION, ],
    AggregationConstant.BY_HERO_FACET: [  AGG_HERO, AGG_FACET ],
    AggregationConstant.BY_HERO_FACET_PLAYER: [
        AGG_HERO,
        AGG_FACET,
        AGG_PLAYER,
    ],
    }

    CCOMPARISON_MODELS: ClassVar[dict] = {
        "hero": [(Hero.name, 'hero'), (Hero.id, 'hero_id'), (AggregationType.hero_cross_cps_id, 'opponent_id')],
        "player": [
            (Player.nickname, 'Player'),
            (Player.account_id, 'account_id'),
            (AggregationType.player_cross_cps_id, 'opponent_id')],
    }

    def __init__(self):
        self.data_model = None
        self.data_model_name = None
        self.is_header = False

        self.models = ModelList()
        self.joins = JoinList()
        self.where = []


    def _set_model(self, data_type: int):
        if data_type == 0:
            self.data_model = PerformanceTotalData
            self.data_model_name = 'total_data'
            self.is_header = True
        else:
            self.data_model = PerformanceWindowData
            self.data_model_name = 'window_data'


    def _set_data_model(self, data_type: int, field: str | None = None):
        self._set_model(data_type)

        if field is None:
            self.models.add(self.data_model, self.data_model_name, self.is_header)
        else:
            self.models.add(getattr(self.data_model, field), field)

        self.joins.add(GamePerformance, self.data_model.game_performance_id == GamePerformance.id)

        if data_type > 0:
            self.models.add(PerformanceWindowTable, 'window_table', True)
            self.joins.add(
                PerformanceWindowTable,
                PerformanceWindowData.performance_table_id == PerformanceWindowTable.id,
                True
            )
            self.where.append(PerformanceWindowData.data_type_id == data_type)


    def _set_comparison_model(self,  flat: bool, basic: bool | None = None, name: None | str = None):
        self.models.add(ComparisonType.cps_name_short, name or 'opponent', True)
        self.joins.add(ComparisonType, GamePerformance.comparison_id == ComparisonType.id)

        self.where.append(ComparisonType.basic == basic)
        self.where.append(ComparisonType.flat == flat)


    def _set_match_select_query_data(
            self,
            data_type: int,
            match_id: int | None = None,
            **kwargs) -> None:
        self._set_data_model(data_type=data_type)

        self.models.add(PlayerGameData.dire, 'side',True)
        self.joins.add(PlayerGameData, GamePerformance.player_game_data_id == PlayerGameData.id)

        self.models.add(Position.name, 'position',True)
        self.joins.add(Position, PlayerGameData.position_id == Position.id)

        self.models.add(PlayerGameData.hero_id, 'hero_id', True)

        self.models.add(Player.nickname, 'player', True)
        self.joins.add(Player, PlayerGameData.player_id == Player.account_id)

        self.where.append(PlayerGameData.game_id == match_id)


    def get_match_query(self, match_id: int, data_type: int, **kwargs):
        self._set_match_select_query_data(data_type=data_type, match_id=match_id)
        self.where.insert(0, GamePerformance.performance_type_id == GamePerformance.const.MATCH_DATA)
        return combine_select(self.models.get_models(), self.joins.data, self.where)


    def get_match_comparison_query(self, match_id: int, data_type: int,  basic: bool, flat: bool ,**kwargs):
        self._set_match_select_query_data(data_type=data_type, match_id=match_id)
        self._set_comparison_model(basic=basic, flat=flat, name='compared_to')
        self.where.append(GamePerformance.performance_type_id == GamePerformance.const.MATCH_DATA_COMPARISON)
        return combine_select(self.models.get_models(), self.joins.data, self.where)


    def _set_aggregation_select_query_data(self, league_id: int, aggregation_type: int, data_type: int, **kwargs):
        self._set_data_model(data_type=data_type)

        self.where.append(AggregationType.league_id == league_id)

        self.joins.add(AggregationType, GamePerformance.aggregation_id == AggregationType.id)

        for agg_model, agg_mode_name in self.AGGREGATION_MODELS[aggregation_type]:
            if agg_mode_name is not None:
                agg_model = getattr(agg_model, agg_mode_name)
            self.models.add(agg_model, agg_mode_name)


    def get_aggregation_query(self, league_id: int, aggregation_type: int, data_type: int, **kwargs):
        self._set_aggregation_select_query_data(league_id=league_id, aggregation_type=aggregation_type, data_type=data_type)
        self.where.append(AggregationType.type == aggregation_type)
        return combine_select(self.models.get_models(), self.joins.data, self.where)


    def get_aggregation_comparison_query(self, league_id: int, aggregation_type: int, data_type: int, flat: bool, **kwargs):
        self._set_aggregation_select_query_data(league_id=league_id, aggregation_type=aggregation_type, data_type=data_type)
        self._set_comparison_model(flat=flat)
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


    def get_cross_comparison_query(self,
                                   league_id: int,
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

    def get_model_names(self, only_header: bool = False) -> list[str]:
        return self.models.get_names(only_header=only_header)
