from models import PlayerGameData, Hero, Player, Position, Facet, ComparisonType, AggregationType, CrossComparisonType
from models.performance import PerformanceTotalData, PerformanceWindowData, Performance, \
    PerformanceWindowTable
from modules.query_creators.helpers import ModelList, JoinList, combine_select
from modules.query_creators.const_map import AGGREGATION_MODELS, CCOMPARISON_MODELS, CCOMPARISON_JOIN


class APIPerformanceQueryCreator:
    def __init__(self):
        self.data_model = None
        self.data_model_name = None
        self.is_header = False

        self.models = ModelList()
        self.joins = JoinList()
        self.where = []


    def _set_model(self, calculation_type_id: int):
        if calculation_type_id == 0:
            self.data_model = PerformanceTotalData
            self.data_model_name = 'total_data'
            self.is_header = True
        else:
            self.data_model = PerformanceWindowData
            self.data_model_name = 'window_data'


    def _set_data_model(self, calculation_type_id: int, field: str | None = None):
        self._set_model(calculation_type_id)

        if field is None:
            self.models.add(self.data_model, self.data_model_name, self.is_header)
        else:
            self.models.add(getattr(self.data_model, field), field)

        self.joins.add(Performance, self.data_model.game_performance_id == Performance.id)

        if calculation_type_id > 0:
            self.models.add(PerformanceWindowTable, 'window_table', True)
            self.joins.add(
                PerformanceWindowTable,
                PerformanceWindowData.performance_table_id == PerformanceWindowTable.id,
                True
            )
            self.where.append(PerformanceWindowData.calc_type_id == calculation_type_id)


    def _set_comparison_model(self, is_flat: bool, basic: bool | None = None, name: None | str = None):
        self.models.add(ComparisonType.cps_name_short, name or 'opponent', True)
        self.joins.add(ComparisonType, Performance.id == ComparisonType.performance_id)

        self.where.append(ComparisonType.basic == basic)
        self.where.append(ComparisonType.is_flat == is_flat)


    def _set_match_select_query_data(
            self,
            calculation_type_id: int,
            match_id: int | None = None,
            **kwargs
    ) -> None:
        self._set_data_model(calculation_type_id=calculation_type_id)

        self.models.add(PlayerGameData.dire, 'side', True)
        self.joins.add(PlayerGameData, Performance.player_game_data_id == PlayerGameData.id)

        self.models.add(Position.name, 'position', True)
        self.joins.add(Position, PlayerGameData.position_id == Position.id)

        self.models.add(PlayerGameData.hero_id, 'hero_id', True)

        self.models.add(Player.nickname, 'player', True)
        self.joins.add(Player, PlayerGameData.player_id == Player.account_id)

        self.where.append(PlayerGameData.game_id == match_id)


    def get_match_query(self, match_id: int, calculation_type_id: int, **kwargs):
        self._set_match_select_query_data(calculation_type_id=calculation_type_id, match_id=match_id)
        self.where.insert(0, Performance.type_id == Performance.const.game.MATCH_DATA)
        return combine_select(self.models.get_models(), self.joins.data, self.where)


    def get_match_comparison_query(self, match_id: int, calculation_type_id: int, basic: bool, is_flat: bool, **kwargs):
        self._set_match_select_query_data(calculation_type_id=calculation_type_id, match_id=match_id)
        self._set_comparison_model(basic=basic, is_flat=is_flat, name='compared_to')
        self.where.append(Performance.type_id == Performance.const.game.MATCH_DATA_COMPARISON)
        return combine_select(self.models.get_models(), self.joins.data, self.where)


    def _set_aggregation_select_query_data(
            self,
            league_id: int,
            aggregation_type: int,
            calculation_type_id: int,
            **kwargs
    ):
        self._set_data_model(calculation_type_id=calculation_type_id)

        self.where.append(AggregationType.league_id == league_id)

        self.joins.add(AggregationType, Performance.id == AggregationType.performance_id)

        for agg_item in AGGREGATION_MODELS[aggregation_type]:
            if agg_item.from_model is not None:
                agg_model = getattr(agg_item.from_model, agg_item.associated_field)
            else:
                agg_model = agg_item.model
            self.models.add(agg_model, agg_item.associated_field)


    def get_aggregation_query(self, league_id: int, aggregation_type: int, calculation_type_id: int, **kwargs):
        self._set_aggregation_select_query_data(
            league_id=league_id,
            aggregation_type=aggregation_type,
            calculation_type_id=calculation_type_id
        )
        self.where.append(AggregationType.type_id == aggregation_type)
        return combine_select(self.models.get_models(), self.joins.data, self.where)


    def get_aggregation_comparison_query(
            self,
            league_id: int,
            aggregation_type: int,
            calculation_type_id: int,
            is_flat: bool,
            **kwargs
    ):
        self._set_aggregation_select_query_data(
            league_id=league_id,
            aggregation_type=aggregation_type,
            calculation_type_id=calculation_type_id
        )
        self._set_comparison_model(is_flat=is_flat)
        self.where.append(AggregationType.type_id == aggregation_type)
        return combine_select(self.models.get_models(), self.joins.data, self.where)


    def _set_cross_comparison_query_data(
            self, league_id: int,
            aggregation_type_id: int,
            position_id: int,
            data_field: str,
            calculation_type_id: int,
            is_flat: bool | None,
            **kwargs
    ):
        self._set_data_model(calculation_type_id=calculation_type_id, field=data_field)

        self.where.append(AggregationType.league_id == league_id)
        self.where.append(ComparisonType.is_flat == is_flat)

        self.where.append(Performance.type_id == Performance.const.game.CROSS_COMPARISON)

        for item in CCOMPARISON_MODELS[aggregation_type_id]:
            self.models.add(item.field, item.field_name)

        self.joins.add(ComparisonType, Performance.id == ComparisonType.performance_id)
        self.joins.add(CrossComparisonType, Performance.id == CrossComparisonType.performance_id)

        self.where.append(CrossComparisonType.position_aggregation_id == position_id)

        for model, join in CCOMPARISON_JOIN[aggregation_type_id]:
            self.joins.add(model, onclause=join)


    def get_cross_comparison_query(
            self,
            league_id: int,
            aggregation_type_id: int,
            position_id: int,
            data_field: str,
            calculation_type_id: int,
            is_flat: bool,
            **kwargs
    ):


        self._set_cross_comparison_query_data(
            league_id=league_id,
            aggregation_type_id=aggregation_type_id,
            position_id=position_id,
            data_field=data_field,
            calculation_type_id=calculation_type_id,
            is_flat=is_flat,
            **kwargs,
        )

        return combine_select(self.models.get_models(), self.joins.data, self.where)


    def get_model_names(self, only_header: bool = False) -> list[str]:
        return self.models.get_names(only_header=only_header)
