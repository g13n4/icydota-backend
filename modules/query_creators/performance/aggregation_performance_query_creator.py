from constants.api import PoTEnum
from models import AggregationType, ByTeamType, ComparisonType
from models.performance import Performance
from modules.query_creators.const_map import AGGREGATION_MODELS
from modules.query_creators.helpers import combine_select
from modules.query_creators.performance.query_creator_mixin import PerformanceQueryCreatorMixin


class APIAggregationPerformanceQueryCreator(PerformanceQueryCreatorMixin):
    def _set_aggregation_match_query_data(
            self,
            league_id: int | None,
            patch_id: int | None,
            aggregation_type: int,
    ):
        if league_id:
            self.where.append(AggregationType.league_id == league_id)
        else:
            self.where.append(AggregationType.patch_id == patch_id)

        self.joins.add(AggregationType, Performance.id == AggregationType.performance_id)

        self.where.append(AggregationType.type_id == aggregation_type)

        for agg_item in AGGREGATION_MODELS[aggregation_type]:
            self.models.add(agg_item.model_data, agg_item.model_data_name, True)
            self.joins.add(agg_item.model, getattr(AggregationType, agg_item.associated_field) == agg_item.join_field)


    def _set_aggregation_team_query_data(
            self,
            league_id: int | None,
            patch_id: int | None,
            is_flat: bool | None = None,
    ):
        if league_id:
            self.where.append(ByTeamType.league_id == league_id)
        else:
            self.where.append(ByTeamType.patch_id == patch_id)

        self._set_by_team_model(is_flat=is_flat)


    def get_query(
            self,
            league_id: int | None,
            pot: PoTEnum,
            patch_id: int | None,
            aggregation_type: int,
            calculation_type_id: int
    ):
        self._set_data_model(calculation_type_id=calculation_type_id, header=False)

        if pot.isPlayer():
            self._set_aggregation_match_query_data(
                league_id=league_id,
                patch_id=patch_id,
                aggregation_type=aggregation_type,
            )

            self.where.append(Performance.type_id == Performance.const.game.AGGREGATION)
        else:
            self._set_aggregation_team_query_data(league_id=league_id, patch_id=patch_id)
            self.where.append(Performance.type_id == Performance.const.team.TEAM_MATCH_AGGREGATION)

        return combine_select(self.models.get_models(), self.joins.data, self.where)


    def get_comparison_query(
            self,
            pot: PoTEnum,
            patch_id: int | None,
            league_id: int | None,
            aggregation_type: int,
            calculation_type_id: int,
            is_flat: bool,
    ):
        self._set_data_model(calculation_type_id=calculation_type_id, header=False)

        if pot.isPlayer():
            self._set_aggregation_match_query_data(
                league_id=league_id,
                patch_id=patch_id,
                aggregation_type=aggregation_type,
            )
            self.where.append(ComparisonType.is_flat == is_flat)
            self.joins.add(ComparisonType, Performance.id == ComparisonType.performance_id)

            self.where.append(Performance.type_id == Performance.const.game.AGGREGATION_COMPARISON)
        else:
            self._set_aggregation_team_query_data(league_id=league_id, patch_id=patch_id, is_flat=is_flat)

            self.where.append(Performance.type_id == Performance.const.team.TEAM_MATCH_AGGREGATION_COMPARISON)

        return combine_select(self.models.get_models(), self.joins.data, self.where)
