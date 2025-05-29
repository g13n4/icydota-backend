from constants.api import PoTEnum
from models import AggregationType
from models.performance import Performance
from modules.query_creators.const_map import AGGREGATION_MODELS
from modules.query_creators.helpers import combine_select
from modules.query_creators.performance.query_creator_mixin import PerformanceQueryCreatorMixin


class APIAggregationPerformanceQueryCreator(PerformanceQueryCreatorMixin):
    def _set_aggregation_select_query_data(
            self,
            league_id: int | None,
            patch_id: int | None,
            aggregation_type: int,
            calculation_type_id: int,
    ):
        self._set_data_model(calculation_type_id=calculation_type_id)

        if league_id:
            self.where.append(AggregationType.league_id == league_id)
        else:
            self.where.append(AggregationType.patch_id == patch_id)

        self.joins.add(AggregationType, Performance.id == AggregationType.performance_id)

        for agg_item in AGGREGATION_MODELS[aggregation_type]:
            if agg_item.from_model is not None:
                agg_model = getattr(agg_item.from_model, agg_item.associated_field)
            else:
                agg_model = agg_item.model
            self.models.add(agg_model, agg_item.associated_field)


    def get_aggregation_query(
            self,
            league_id: int | None,
            pot: PoTEnum,
            patch_id: int | None,
            aggregation_type: int,
            calculation_type_id: int
    ):
        self._set_aggregation_select_query_data(
            league_id=league_id,
            patch_id=patch_id,
            aggregation_type=aggregation_type,
            calculation_type_id=calculation_type_id
        )

        if pot.isPlayer():
            self.where.append(Performance.type_id == Performance.const.game.AGGREGATION)
        else:
            self.where.append(Performance.type_id == Performance.const.team.TEAM_MATCH_AGGREGATION)

        return combine_select(self.models.get_models(), self.joins.data, self.where)


    def get_aggregation_comparison_query(
            self,
            pot: PoTEnum,
            patch_id: int | None,
            league_id: int | None,
            aggregation_type: int,
            calculation_type_id: int,
            is_flat: bool,
    ):
        self._set_aggregation_select_query_data(
            league_id=league_id,
            patch_id=patch_id,
            aggregation_type=aggregation_type,
            calculation_type_id=calculation_type_id
        )
        self._set_comparison_model(is_flat=is_flat)
        self.where.append(AggregationType.type_id == aggregation_type)

        if pot.isPlayer():
            self.where.append(Performance.type_id == Performance.const.game.AGGREGATION_COMPARISON)
        else:
            self.where.append(Performance.type_id == Performance.const.team.TEAM_MATCH_AGGREGATION_COMPARISON)

        return combine_select(self.models.get_models(), self.joins.data, self.where)
